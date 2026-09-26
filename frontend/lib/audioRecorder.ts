// Audio Recorder using MediaRecorder API and Web Audio API for Live Waveform & Vocal Bandpass Isolation

export interface AudioRecorderState {
  isRecording: boolean;
  durationMs: number;
}

export class AudioRecorder {
  private mediaStream: MediaStream | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private animationFrameId: number | null = null;
  private onLevelChange?: (level: number) => void;
  private startTime: number = 0;

  constructor(onLevelChange?: (level: number) => void) {
    this.onLevelChange = onLevelChange;
  }

  static isSupported(): boolean {
    return (
      typeof window !== 'undefined' &&
      !!navigator.mediaDevices &&
      !!navigator.mediaDevices.getUserMedia &&
      typeof MediaRecorder !== 'undefined'
    );
  }

  async start(): Promise<void> {
    if (!AudioRecorder.isSupported()) {
      throw new Error('Brauzeringiz ovoz yozishni qo\'llab-quvvatlamaydi (MediaRecorder yo\'q).');
    }

    try {
      // Near-field speech capture: strict echo cancellation & noise suppression, autoGainControl: false
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false, // Don't boost distant background chatter
          channelCount: 1,
          sampleRate: 48000,
        },
      });

      // Set up AudioContext with Vocal Bandpass Filters (150Hz - 3400Hz)
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      this.audioContext = new AudioCtx();
      const source = this.audioContext.createMediaStreamSource(this.mediaStream);

      // 1. Highpass filter: cuts low-frequency rumble, hum, air conditioning (< 150Hz)
      const highpass = this.audioContext.createBiquadFilter();
      highpass.type = 'highpass';
      highpass.frequency.value = 150;

      // 2. Lowpass filter: cuts high-frequency hiss, clicks, background clatter (> 3400Hz)
      const lowpass = this.audioContext.createBiquadFilter();
      lowpass.type = 'lowpass';
      lowpass.frequency.value = 3400;

      // 3. Connect filter chain to AnalyserNode
      source.connect(highpass);
      highpass.connect(lowpass);

      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      lowpass.connect(this.analyser);

      const bufferLength = this.analyser.fftSize;
      const timeData = new Uint8Array(bufferLength);

      const checkAudioLevel = () => {
        if (!this.analyser || !this.mediaRecorder || this.mediaRecorder.state !== 'recording') {
          return;
        }
        this.analyser.getByteTimeDomainData(timeData);
        let sumSquares = 0;
        for (let i = 0; i < bufferLength; i++) {
          const normSample = (timeData[i] - 128) / 128.0;
          sumSquares += normSample * normSample;
        }
        const rms = Math.sqrt(sumSquares / bufferLength);
        if (this.onLevelChange) {
          this.onLevelChange(rms);
        }
        this.animationFrameId = requestAnimationFrame(checkAudioLevel);
      };

      // Select best supported MIME type
      const mimeTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
        'audio/mp4',
        'audio/wav',
      ];
      let selectedMimeType = '';
      for (const mime of mimeTypes) {
        if (MediaRecorder.isTypeSupported(mime)) {
          selectedMimeType = mime;
          break;
        }
      }

      this.mediaRecorder = selectedMimeType
        ? new MediaRecorder(this.mediaStream, { mimeType: selectedMimeType })
        : new MediaRecorder(this.mediaStream);

      this.audioChunks = [];
      this.mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.start(200); // 200ms slice
      this.startTime = Date.now();
      checkAudioLevel();
    } catch (err) {
      this.cleanup();
      throw err;
    }
  }

  stop(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
        this.cleanup();
        reject(new Error('Yozish faol emas.'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        const mimeType = this.mediaRecorder?.mimeType || 'audio/webm';
        const audioBlob = new Blob(this.audioChunks, { type: mimeType });
        this.cleanup();
        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  }

  isRecording(): boolean {
    return !!this.mediaRecorder && this.mediaRecorder.state === 'recording';
  }

  cancel(): void {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      try {
        this.mediaRecorder.stop();
      } catch {
        // ignore
      }
    }
    this.cleanup();
  }

  private cleanup(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
    if (this.onLevelChange) {
      this.onLevelChange(0);
    }
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close().catch(() => {});
      this.audioContext = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }
    this.analyser = null;
    this.audioChunks = [];
  }
}
