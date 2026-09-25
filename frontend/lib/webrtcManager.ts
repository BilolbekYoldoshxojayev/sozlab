/**
 * WebRTC and WebSocket Audio Relay Manager for SözLab
 * Provides resilient Full-Duplex Live Audio communication between Citizen and Operator
 * with automatic fallback to WebSocket Audio Streaming if WebRTC P2P is blocked by NAT/Firewall.
 */

export interface WebRTCManagerCallbacks {
  onAudioLevels?: (localLevel: number, remoteLevel: number) => void;
  onConnectionStatus?: (status: 'connecting' | 'connected' | 'disconnected' | 'failed' | 'fallback_relay') => void;
  onRemoteStream?: (stream: MediaStream) => void;
  onLiveCaption?: (speakerRole: string, speakerName: string, text: string) => void;
}

export class WebRTCManager {
  private pc: RTCPeerConnection | null = null;
  private localStream: MediaStream | null = null;
  private remoteStream: MediaStream | null = null;
  private remoteAudioElement: HTMLAudioElement | null = null;

  private audioCtx: AudioContext | null = null;
  private localAnalyser: AnalyserNode | null = null;
  private remoteAnalyser: AnalyserNode | null = null;
  private animFrameId: number | null = null;

  private mediaRecorder: MediaRecorder | null = null;
  private isMuted: boolean = false;
  private isDeafened: boolean = false;

  private role: 'operator' | 'citizen';
  private callId: string;
  private sendSignaling: (payload: any) => void;
  private callbacks: WebRTCManagerCallbacks;

  private isConnected: boolean = false;
  private isFallbackMode: boolean = false;

  constructor(
    callId: string,
    role: 'operator' | 'citizen',
    sendSignaling: (payload: any) => void,
    callbacks: WebRTCManagerCallbacks = {}
  ) {
    this.callId = callId;
    this.role = role;
    this.sendSignaling = sendSignaling;
    this.callbacks = callbacks;
  }

  /**
   * Initializes local microphone and sets up RTCPeerConnection
   */
  async initialize(): Promise<void> {
    try {
      this.callbacks.onConnectionStatus?.('connecting');

      // 1. Get user media (echo cancellation & noise suppression enabled)
      if (typeof navigator !== 'undefined' && navigator.mediaDevices?.getUserMedia) {
        try {
          this.localStream = await navigator.mediaDevices.getUserMedia({
            audio: {
              echoCancellation: true,
              noiseSuppression: true,
              autoGainControl: true,
            },
            video: false,
          });
        } catch (micErr) {
          console.warn('[WebRTC] Microphone permission denied or not found:', micErr);
        }
      }

      // 2. Setup AudioContext for real-time audio visualization
      this.setupAudioAnalysis();

      // 3. Setup RTCPeerConnection
      const rtcConfig: RTCConfiguration = {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' },
          { urls: 'stun:stun2.l.google.com:19302' },
        ],
      };

      this.pc = new RTCPeerConnection(rtcConfig);

      // Add local audio tracks if microphone is active
      if (this.localStream) {
        this.localStream.getAudioTracks().forEach((track) => {
          if (this.pc && this.localStream) {
            this.pc.addTrack(track, this.localStream);
          }
        });
      }

      // Handle ICE Candidates
      this.pc.onicecandidate = (event) => {
        if (event.candidate) {
          this.sendSignaling({
            type: 'webrtc_ice_candidate',
            action: 'webrtc_ice_candidate',
            call_id: this.callId,
            candidate: event.candidate.toJSON(),
            sender_role: this.role,
          });
        }
      };

      // Handle Remote Stream Track
      this.pc.ontrack = (event) => {
        const stream = event.streams[0] || new MediaStream([event.track]);
        this.remoteStream = stream;
        this.attachRemoteAudio(stream);
        this.callbacks.onRemoteStream?.(stream);
      };

      // Monitor Connection State
      this.pc.onconnectionstatechange = () => {
        const state = this.pc?.connectionState;
        if (state === 'connected') {
          this.isConnected = true;
          this.callbacks.onConnectionStatus?.('connected');
        } else if (state === 'disconnected') {
          this.callbacks.onConnectionStatus?.('disconnected');
        } else if (state === 'failed') {
          console.warn('[WebRTC] P2P connection failed, engaging WebSocket Audio Relay fallback...');
          this.startFallbackRelay();
        }
      };

      this.pc.oniceconnectionstatechange = () => {
        if (this.pc?.iceConnectionState === 'failed') {
          this.startFallbackRelay();
        }
      };

      // If Operator, create WebRTC offer after a short delay
      if (this.role === 'operator') {
        setTimeout(() => this.createOffer(), 600);
      }

      // Start level meter loop
      this.startAudioMeterLoop();

    } catch (err) {
      console.error('[WebRTC Init Error]:', err);
      this.startFallbackRelay();
    }
  }

  /**
   * Create and send SDP Offer
   */
  async createOffer(): Promise<void> {
    if (!this.pc) return;
    try {
      const offer = await this.pc.createOffer({
        offerToReceiveAudio: true,
        offerToReceiveVideo: false,
      });
      await this.pc.setLocalDescription(offer);

      this.sendSignaling({
        type: 'webrtc_offer',
        action: 'webrtc_offer',
        call_id: this.callId,
        sdp: offer.sdp,
        sender_role: this.role,
      });
    } catch (err) {
      console.error('[WebRTC Offer Error]:', err);
      this.startFallbackRelay();
    }
  }

  /**
   * Handle incoming SDP Offer
   */
  async handleOffer(sdp: string): Promise<void> {
    if (!this.pc) return;
    try {
      await this.pc.setRemoteDescription(new RTCSessionDescription({ type: 'offer', sdp }));
      const answer = await this.pc.createAnswer();
      await this.pc.setLocalDescription(answer);

      this.sendSignaling({
        type: 'webrtc_answer',
        action: 'webrtc_answer',
        call_id: this.callId,
        sdp: answer.sdp,
        sender_role: this.role,
      });
    } catch (err) {
      console.error('[WebRTC Handle Offer Error]:', err);
      this.startFallbackRelay();
    }
  }

  /**
   * Handle incoming SDP Answer
   */
  async handleAnswer(sdp: string): Promise<void> {
    if (!this.pc) return;
    try {
      await this.pc.setRemoteDescription(new RTCSessionDescription({ type: 'answer', sdp }));
    } catch (err) {
      console.error('[WebRTC Handle Answer Error]:', err);
    }
  }

  /**
   * Handle incoming ICE Candidate
   */
  async handleIceCandidate(candidateInit: RTCIceCandidateInit): Promise<void> {
    if (!this.pc) return;
    try {
      await this.pc.addIceCandidate(new RTCIceCandidate(candidateInit));
    } catch (err) {
      console.warn('[WebRTC Add ICE Error]:', err);
    }
  }

  /**
   * Process all incoming WebSocket signaling messages related to live call
   */
  async handleSignalingMessage(data: any): Promise<void> {
    const type = data.type || data.action;

    if (type === 'webrtc_offer' && data.sdp) {
      await this.handleOffer(data.sdp);
    } else if (type === 'webrtc_answer' && data.sdp) {
      await this.handleAnswer(data.sdp);
    } else if (type === 'webrtc_ice_candidate' && data.candidate) {
      await this.handleIceCandidate(data.candidate);
    } else if (type === 'peer_audio_chunk' && data.audio) {
      this.playRelayAudioChunk(data.audio);
    } else if (type === 'live_caption') {
      this.callbacks.onLiveCaption?.(
        data.speaker_role || 'citizen',
        data.speaker_name || 'Fuqaro',
        data.text || ''
      );
    }
  }

  /**
   * Set up Web Audio API analysers for local and remote microphone streams
   */
  private setupAudioAnalysis(): void {
    if (typeof window === 'undefined') return;
    try {
      const AudioCtxClass = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtxClass) return;

      this.audioCtx = new AudioCtxClass();

      if (this.localStream) {
        const localSource = this.audioCtx.createMediaStreamSource(this.localStream);
        this.localAnalyser = this.audioCtx.createAnalyser();
        this.localAnalyser.fftSize = 64;
        localSource.connect(this.localAnalyser);
      }
    } catch (e) {
      console.warn('[WebRTC Analyser Setup Warning]:', e);
    }
  }

  /**
   * Attaches remote stream to an audio element for playback
   */
  private attachRemoteAudio(stream: MediaStream): void {
    if (typeof window === 'undefined') return;
    try {
      if (!this.remoteAudioElement) {
        this.remoteAudioElement = new Audio();
        this.remoteAudioElement.autoplay = true;
      }
      this.remoteAudioElement.srcObject = stream;
      this.remoteAudioElement.play().catch((err) => {
        console.warn('[WebRTC Autoplay Notice]:', err);
      });

      // Attach remote analyser
      if (this.audioCtx) {
        try {
          const remoteSource = this.audioCtx.createMediaStreamSource(stream);
          this.remoteAnalyser = this.audioCtx.createAnalyser();
          this.remoteAnalyser.fftSize = 64;
          remoteSource.connect(this.remoteAnalyser);
        } catch {
          // ignore
        }
      }
    } catch (e) {
      console.warn('[WebRTC Attach Remote Audio]:', e);
    }
  }

  /**
   * Fallback WebSocket Audio Relay:
   * Chunks audio and streams via WebSocket if WebRTC P2P cannot establish.
   */
  private startFallbackRelay(): void {
    if (this.isFallbackMode) return;
    this.isFallbackMode = true;
    this.callbacks.onConnectionStatus?.('fallback_relay');

    if (!this.localStream || typeof MediaRecorder === 'undefined') return;

    try {
      let mimeType = 'audio/webm';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/mp4';
      }

      this.mediaRecorder = new MediaRecorder(this.localStream, { mimeType });
      this.mediaRecorder.ondataavailable = async (event) => {
        if (event.data && event.data.size > 0 && !this.isMuted) {
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64Audio = (reader.result as string).split(',')[1];
            if (base64Audio) {
              this.sendSignaling({
                type: 'peer_audio_chunk',
                action: 'peer_audio_chunk',
                call_id: this.callId,
                audio: base64Audio,
                sender_role: this.role,
              });
            }
          };
          reader.readAsDataURL(event.data);
        }
      };

      this.mediaRecorder.start(400); // 400ms slices for low-latency voice relay
    } catch (e) {
      console.warn('[Fallback Relay Setup Error]:', e);
    }
  }

  /**
   * Play received fallback audio chunk
   */
  private playRelayAudioChunk(base64Audio: string): void {
    if (this.isDeafened) return;
    try {
      const audioBlob = this.base64ToBlob(base64Audio, 'audio/webm');
      const blobUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(blobUrl);
      audio.play().catch(() => {});
      audio.onended = () => URL.revokeObjectURL(blobUrl);
    } catch (e) {
      console.warn('[Relay Audio Play Error]:', e);
    }
  }

  private base64ToBlob(base64: string, mimeType: string): Blob {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  }

  /**
   * Real-time level loop for Voice Orb dynamic scaling
   */
  private startAudioMeterLoop(): void {
    const localData = new Uint8Array(32);
    const remoteData = new Uint8Array(32);

    const updateLevels = () => {
      let localLevel = 0;
      let remoteLevel = 0;

      if (this.localAnalyser && !this.isMuted) {
        this.localAnalyser.getByteFrequencyData(localData);
        let sum = 0;
        for (let i = 0; i < localData.length; i++) {
          sum += localData[i];
        }
        localLevel = Math.min(1, (sum / localData.length) / 128);
      }

      if (this.remoteAnalyser && !this.isDeafened) {
        this.remoteAnalyser.getByteFrequencyData(remoteData);
        let sum = 0;
        for (let i = 0; i < remoteData.length; i++) {
          sum += remoteData[i];
        }
        remoteLevel = Math.min(1, (sum / remoteData.length) / 128);
      }

      this.callbacks.onAudioLevels?.(localLevel, remoteLevel);
      this.animFrameId = requestAnimationFrame(updateLevels);
    };

    this.animFrameId = requestAnimationFrame(updateLevels);
  }

  /**
   * Broadcast a live closed caption turn to peer
   */
  sendLiveCaption(text: string, speakerName: string): void {
    if (!text.trim()) return;
    this.sendSignaling({
      type: 'live_caption',
      action: 'live_caption',
      call_id: this.callId,
      speaker_role: this.role,
      speaker_name: speakerName,
      text: text.trim(),
    });
  }

  /**
   * Toggle local microphone mute
   */
  setMute(mute: boolean): void {
    this.isMuted = mute;
    if (this.localStream) {
      this.localStream.getAudioTracks().forEach((track) => {
        track.enabled = !mute;
      });
    }
  }

  /**
   * Toggle speaker deafen (mute incoming sound)
   */
  setDeafen(deafen: boolean): void {
    this.isDeafened = deafen;
    if (this.remoteAudioElement) {
      this.remoteAudioElement.muted = deafen;
    }
  }

  /**
   * Teardown and clean up all resources
   */
  destroy(): void {
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }

    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      try {
        this.mediaRecorder.stop();
      } catch {
        // ignore
      }
      this.mediaRecorder = null;
    }

    if (this.localStream) {
      this.localStream.getTracks().forEach((t) => t.stop());
      this.localStream = null;
    }

    if (this.remoteAudioElement) {
      this.remoteAudioElement.pause();
      this.remoteAudioElement.srcObject = null;
      this.remoteAudioElement = null;
    }

    if (this.pc) {
      this.pc.close();
      this.pc = null;
    }

    if (this.audioCtx) {
      try {
        this.audioCtx.close();
      } catch {
        // ignore
      }
      this.audioCtx = null;
    }
  }
}
