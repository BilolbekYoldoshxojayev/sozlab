'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  Mic, MicOff, PhoneOff, PhoneCall, Volume2, VolumeX,
  Headset, Sparkles, RefreshCw, CheckCircle2, Clock,
  ChevronUp, ChevronDown, Send, MessageSquare, ArrowRight, Home,
  AlertCircle, ShieldCheck
} from 'lucide-react';
import { CallRecord, Message, DialogTurnResponse, AudioTurnResponse, TopicCategory } from '@/lib/types';
import {
  startNewCall, sendDialogTurn, sendAudioTurn, transferToOperator,
  completeCall, getAudioFullUrl, getCallWebSocketUrl
} from '@/lib/api';
import { AudioRecorder } from '@/lib/audioRecorder';
import { useRole } from '@/lib/useRole';
import { WebRTCManager } from '@/lib/webrtcManager';

const QUICK_PROMPTS = [
  {
    category: 'Qabul & Kvota',
    text: 'OTMlarga qabul qachon boshlanadi va nechta yo\'nalish tanlash mumkin?',
  },
  {
    category: 'Super-kontrakt',
    text: 'Super-kontrakt arizasini qayerdan yuboraman va to\'lovi qancha?',
  },
  {
    category: 'Yotoqxona (TTJ)',
    text: 'Talabalar turar joyiga my.gov.uz orqali ariza topshirish va ijara kompensatsiyasi qanday olinadi?',
  },
  {
    category: 'Nostrifikatsiya',
    text: 'Xorijiy diplomni tan olish tartibi qanday? TOP-1000 oliygohlar imtihonsiz o\'tadimi?',
  },
  {
    category: 'Grant & GPA',
    text: 'Davlat granti har yili qayta taqsimlanadimi? GPA ballim tushib ketsa nima bo\'ladi?',
  },
  {
    category: 'Ta\'lim Krediti',
    text: 'Talabalar uchun foizsiz ta\'lim krediti kimlarga va qanday tartibda ajratiladi?',
  },
  {
    category: 'Operator Talab',
    text: 'Mening arizamda muammo bor, iltimos meni zudlik bilan operatorga ulang!',
  }
];

export default function CallSimulator() {
  const router = useRouter();
  const { session } = useRole();
  const [activeCall, setActiveCall] = useState<CallRecord | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [callDuration, setCallDuration] = useState(0);
  const [mode, setMode] = useState<'idle' | 'recording' | 'thinking' | 'speaking'>('idle');
  const [isMuted, setIsMuted] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState('uz-UZ-MadinaNeural');
  const [wsConnected, setWsConnected] = useState(false);
  const [audioInputLevel, setAudioInputLevel] = useState(0);
  const [micErrorMessage, setMicErrorMessage] = useState<string | null>(null);
  const [isQuickPromptsOpen, setIsQuickPromptsOpen] = useState(false);
  const [customInputText, setCustomInputText] = useState('');
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const [operatorAudioLevel, setOperatorAudioLevel] = useState(0);
  const [liveOperatorCaption, setLiveOperatorCaption] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const audioRecorderRef = useRef<AudioRecorder | null>(null);
  const webrtcRef = useRef<WebRTCManager | null>(null);

  // Initialize AudioRecorder
  useEffect(() => {
    audioRecorderRef.current = new AudioRecorder((level) => {
      setAudioInputLevel(level);
    });

    return () => {
      if (audioRecorderRef.current) {
        audioRecorderRef.current.cancel();
      }
    };
  }, []);

  // Duration Timer
  useEffect(() => {
    let interval: NodeJS.Timeout | undefined;
    if (activeCall && activeCall.status !== 'completed') {
      interval = setInterval(() => {
        setCallDuration((prev) => prev + 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [activeCall?.status]);

  // WebSocket Connection
  useEffect(() => {
    if (!activeCall) return;

    try {
      const wsUrl = getCallWebSocketUrl(activeCall.id);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setWsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'ai_response') {
            const aiMsg = data.message;
            setMessages((prev) => [...prev, aiMsg]);
            setMode('speaking');

            if (aiMsg.audio_url && !isMuted) {
              playAudioResponse(aiMsg.audio_url);
            } else {
              setMode('idle');
            }
          } else if (data.type === 'new_message') {
            if (data.message.role !== 'citizen') {
              setMessages((prev) => [...prev, data.message]);
            }
          } else if (data.type === 'call_transferred') {
            setActiveCall((prev) => (prev ? { ...prev, status: 'waiting_operator' } : null));
          } else if (data.type === 'queue_update') {
            setActiveCall((prev) =>
              prev ? { ...prev, status: 'waiting_operator', queue_position: data.queue_position || data.position } : null
            );
          } else if (data.type === 'operator_assigned' || data.type === 'operator_joined') {
            setActiveCall((prev) =>
              prev
                ? {
                    ...prev,
                    status: 'operator_handling',
                    assigned_operator: data.operator_name,
                    queue_position: undefined,
                  }
                : null
            );
          } else if (data.type === 'live_caption') {
            if (data.speaker_role === 'operator') {
              setLiveOperatorCaption(data.text);
            }
          } else if (data.type === 'call_completed') {
            setActiveCall((prev) => (prev ? { ...prev, status: 'completed' } : null));
            setMode('idle');
            setShowSummaryModal(true);
            webrtcRef.current?.destroy();
          } else {
            webrtcRef.current?.handleSignalingMessage(data);
          }
        } catch (e) {
          console.error('[WS Parse Error]:', e);
        }
      };

      ws.onclose = () => setWsConnected(false);
      ws.onerror = () => setWsConnected(false);

      wsRef.current = ws;

      return () => {
        ws.close();
      };
    } catch (e) {
      console.error('[WS Init Error]:', e);
    }
  }, [activeCall?.id, isMuted]);

  // WebRTC initialization when call transfers to operator
  useEffect(() => {
    if (activeCall?.status !== 'operator_handling' || !activeCall?.id) {
      if (webrtcRef.current) {
        webrtcRef.current.destroy();
        webrtcRef.current = null;
      }
      return;
    }

    const webrtc = new WebRTCManager(
      activeCall.id,
      'citizen',
      (payload) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify(payload));
        }
      },
      {
        onAudioLevels: (localLevel, remoteLevel) => {
          setAudioInputLevel(localLevel);
          setOperatorAudioLevel(remoteLevel);
        },
        onLiveCaption: (role, name, text) => {
          if (role === 'operator') {
            setLiveOperatorCaption(text);
          }
        },
      }
    );

    webrtc.initialize();
    webrtcRef.current = webrtc;

    return () => {
      webrtc.destroy();
      webrtcRef.current = null;
    };
  }, [activeCall?.status, activeCall?.id]);

  const playAudioResponse = (relativeUrl: string) => {
    const fullUrl = getAudioFullUrl(relativeUrl);
    if (audioRef.current) {
      audioRef.current.src = fullUrl;
      audioRef.current.play().catch((err) => {
        console.warn('Audio autoplay blocked, user interaction required:', err);
        setMode('idle');
      });
      setMode('speaking');
    }
  };

  const handleStartCall = async () => {
    try {
      setMicErrorMessage(null);
      setShowSummaryModal(false);
      const callerName = session.citizenName || 'Fuqaro (Abituriyent)';
      const callerPhone = session.citizenPhone || '+998 (90) 777-88-99';
      const call = await startNewCall(callerName, callerPhone);
      setActiveCall(call);
      setMessages(call.messages);
      setCallDuration(0);

      // Speak initial greeting
      const greetingText = call.messages[0]?.text;
      if (greetingText) {
        sendDialogTurn(call.id, 'Salom', true, selectedVoice).then((res) => {
          if (res.audio_url && !isMuted) {
            playAudioResponse(res.audio_url);
          }
        }).catch(() => {});
      }
    } catch (err) {
      console.error('Failed to start call:', err);
    }
  };

  const handleEndCall = async () => {
    if (activeCall) {
      try {
        await completeCall(activeCall.id, 'Fuqaro tomonidan qo\'ng\'iroq yakunlandi.');
      } catch {
        // ignore
      }
      setActiveCall((prev) => (prev ? { ...prev, status: 'completed' } : null));
      if (wsRef.current) {
        wsRef.current.close();
      }
    }
    if (audioRecorderRef.current) {
      audioRecorderRef.current.cancel();
    }
    setMode('idle');
    setShowSummaryModal(true);
  };

  const handleSendMessage = async (textToSend: string) => {
    const text = textToSend.trim();
    if (!text || !activeCall) return;

    setCustomInputText('');
    setIsQuickPromptsOpen(false);
    setMode('thinking');

    // Optimistic citizen message
    const tempCitizenMsg: Message = {
      id: `client-${Date.now()}`,
      role: 'citizen',
      text: text,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempCitizenMsg]);

    try {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: 'user_speech',
            text: text,
            voice: selectedVoice,
          })
        );
      } else {
        const res: DialogTurnResponse = await sendDialogTurn(
          activeCall.id,
          text,
          !isMuted,
          selectedVoice
        );

        const aiMsg: Message = {
          id: `ai-${Date.now()}`,
          role: 'ai',
          text: res.ai_text,
          timestamp: new Date().toISOString(),
          audio_url: res.audio_url,
          sentiment: res.sentiment,
          detected_topic: res.topic,
        };

        setMessages((prev) => [...prev, aiMsg]);

        if (res.audio_url && !isMuted) {
          playAudioResponse(res.audio_url);
        } else {
          setMode('idle');
        }

        if (res.requires_operator) {
          setActiveCall((prev) => (prev ? { ...prev, status: 'waiting_operator' } : null));
        }
      }
    } catch (e) {
      console.error('[Send Message Error]:', e);
      setMode('idle');
    }
  };

  // Toggle Microphone Recording
  const toggleRecording = async () => {
    if (!activeCall || activeCall.status === 'completed') {
      await handleStartCall();
      return;
    }

    if (mode === 'recording') {
      // STOP recording and send audio blob to server
      try {
        setMode('thinking');
        if (!audioRecorderRef.current) return;
        const audioBlob = await audioRecorderRef.current.stop();

        // Send audio turn to backend
        const res: AudioTurnResponse = await sendAudioTurn(
          activeCall.id,
          audioBlob,
          !isMuted,
          selectedVoice
        );

        // Append transcribed citizen message
        const citizenText = res.user_text || res.transcribed_text || '(Ovozli murojaat)';
        const citizenMsg: Message = {
          id: `audio-user-${Date.now()}`,
          role: 'citizen',
          text: citizenText,
          timestamp: new Date().toISOString(),
          sentiment: res.sentiment,
        };

        // Append bot message
        const botText = res.bot_text || res.ai_text || 'Javob qabul qilindi.';
        const aiMsg: Message = {
          id: `audio-bot-${Date.now()}`,
          role: 'ai',
          text: botText,
          timestamp: new Date().toISOString(),
          audio_url: res.audio_url,
          sentiment: res.sentiment,
        };

        setMessages((prev) => [...prev, citizenMsg, aiMsg]);

        if (res.status === 'waiting_operator') {
          setActiveCall((prev) => (prev ? { ...prev, status: 'waiting_operator', queue_position: res.queue_position } : null));
        } else if (res.status === 'operator_handling') {
          setActiveCall((prev) => (prev ? { ...prev, status: 'operator_handling', assigned_operator: res.operator_name } : null));
        } else if (res.status === 'completed') {
          setActiveCall((prev) => (prev ? { ...prev, status: 'completed' } : null));
          setShowSummaryModal(true);
        }

        if (res.audio_url && !isMuted) {
          playAudioResponse(res.audio_url);
        } else {
          setMode('idle');
        }
      } catch (err: unknown) {
        console.error('Audio recording upload failed:', err);
        setMode('idle');
        setMicErrorMessage('Ovozli xabarni yuborishda xatolik yuz berdi. Iltimos qaytadan urining.');
      }
    } else {
      // START recording
      try {
        setMicErrorMessage(null);
        if (!AudioRecorder.isSupported()) {
          setMicErrorMessage('Brauzeringiz mikrofon orqali yozishni qo\'llab-quvvatlamaydi.');
          return;
        }
        await audioRecorderRef.current?.start();
        setMode('recording');
      } catch (err: unknown) {
        console.warn('Microphone start error:', err);
        setMicErrorMessage('Mikrofon ruxsatnomasi berilmadi yoki mavjud emas. Quyidagi tezkor savollardan foydalanishingiz mumkin.');
        setMode('idle');
      }
    }
  };

  const handleTransferToOperator = async () => {
    if (!activeCall) return;
    try {
      const res = await transferToOperator(activeCall.id, 'Fuqaro mustaqil ravishda operatorni tanladi');
      setActiveCall(res);
      const sysMsg: Message = {
        id: `sys-${Date.now()}`,
        role: 'system',
        text: res.status === 'operator_handling'
          ? `Qo'ng'iroq muvaffaqiyatli ${res.assigned_operator || 'operator'} ga ulandi!`
          : `Qo'ng'iroq operator navbatiga qo'yildi. Siz navbatda ${res.queue_position || 1}-o'rindasiz.`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, sysMsg]);
    } catch (e) {
      console.error('Transfer failed:', e);
    }
  };

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remainingSecs = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${remainingSecs.toString().padStart(2, '0')}`;
  };

  // Determine latest turn messages for live Closed Captions
  const lastAiOrOpMessage = [...messages].reverse().find((m) => m.role === 'ai' || m.role === 'operator');
  const lastCitizenMessage = [...messages].reverse().find((m) => m.role === 'citizen');

  // Live Operator Call Mode flags
  const isOperatorActive = activeCall?.status === 'operator_handling';
  const isOperatorSpeaking = operatorAudioLevel > 0.08;
  const isCitizenSpeaking = audioInputLevel > 0.08;

  // Closed caption display text
  let liveCaptionSpeaker = 'SözLab AI';
  let liveCaptionText = 'O\'zbek tilida gapiring, sun\'iy intellekt darhol javob beradi...';

  if (isOperatorActive) {
    liveCaptionSpeaker = isOperatorSpeaking ? (activeCall.assigned_operator || 'Operator') : 'Siz (Fuqaro)';
    liveCaptionText = liveOperatorCaption || (isOperatorSpeaking ? 'Operator mikrofondan gapirmoqda...' : 'Operator bilan jonli audio muloqot faol. Bemalol gapiring...');
  } else if (mode === 'recording') {
    liveCaptionSpeaker = 'Siz (Fuqaro)';
    liveCaptionText = 'Tinglanmoqda... Istalgan savolingizni bering.';
  } else if (mode === 'thinking') {
    liveCaptionSpeaker = 'SözLab AI';
    liveCaptionText = 'Javob shakllantirilmoqda...';
  } else if (mode === 'speaking' && lastAiOrOpMessage) {
    liveCaptionSpeaker = lastAiOrOpMessage.role === 'operator' ? (activeCall?.assigned_operator || 'Operator') : 'SözLab AI';
    liveCaptionText = lastAiOrOpMessage.text;
  } else if (lastAiOrOpMessage) {
    liveCaptionSpeaker = lastAiOrOpMessage.role === 'operator' ? (activeCall?.assigned_operator || 'Operator') : 'SözLab AI';
    liveCaptionText = lastAiOrOpMessage.text;
  } else if (lastCitizenMessage) {
    liveCaptionSpeaker = 'Siz (Fuqaro)';
    liveCaptionText = lastCitizenMessage.text;
  }

  // Voice Orb Scale Calculation
  const orbScale = isOperatorActive
    ? isOperatorSpeaking
      ? 1 + operatorAudioLevel * 0.55
      : isCitizenSpeaking
      ? 1 + audioInputLevel * 0.45
      : 1
    : mode === 'recording'
    ? 1 + audioInputLevel * 0.45
    : 1;

  return (
    <div className="relative w-full h-[calc(100vh-4.5rem)] overflow-hidden flex flex-col justify-between bg-gradient-to-b from-slate-950 via-[#07172c] to-[#040e1c] text-white select-none">
      {/* Hidden audio element for TTS playback */}
      <audio
        ref={audioRef}
        onEnded={() => setMode('idle')}
        onError={() => setMode('idle')}
        className="hidden"
      />

      {/* Atmospheric Background Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/3 left-1/2 -translate-x-1/2 w-[400px] h-[400px] bg-emerald-500/10 rounded-full blur-[100px] pointer-events-none" />

      {/* TOP MINIMAL BAR: Status, Timer, Voice Picker, Quick Questions */}
      <div className="relative z-20 px-4 sm:px-8 pt-4 pb-2 flex items-center justify-between">
        {/* Caller & Connection Status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/10 text-xs">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                activeCall && activeCall.status !== 'completed'
                  ? activeCall.status === 'waiting_operator'
                    ? 'bg-amber-400 animate-ping'
                    : 'bg-emerald-400 animate-pulse'
                  : 'bg-slate-400'
              }`}
            />
            <span className="font-semibold text-slate-200">
              {activeCall
                ? activeCall.status === 'ai_handling'
                  ? 'AI Yordamchi'
                  : activeCall.status === 'waiting_operator'
                  ? `Navbatda (#${activeCall.queue_position || 1})`
                  : activeCall.status === 'operator_handling'
                  ? `Operator: ${activeCall.assigned_operator || 'Jonli'}`
                  : 'Yakunlangan'
                : 'Qo\'ng\'iroq Kutilmoqda'}
            </span>
            <span className="text-slate-400">•</span>
            <span className="font-mono text-emerald-300 font-bold">
              {formatTime(callDuration)}
            </span>
          </div>

          {/* WS Status Badge */}
          <span className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-[11px] text-slate-300">
            <span className={`w-1.5 h-1.5 rounded-full ${wsConnected ? 'bg-emerald-400' : 'bg-amber-400'}`} />
            <span>{wsConnected ? 'Jonli Oqim' : 'Standart'}</span>
          </span>
        </div>

        {/* Center / Right controls */}
        <div className="flex items-center gap-2">
          {/* Voice Model Selector Pill */}
          <div className="flex items-center bg-white/10 backdrop-blur-md border border-white/10 rounded-full px-2.5 py-1 text-xs">
            <Volume2 className="w-3.5 h-3.5 text-blue-400 mr-1.5" />
            <select
              value={selectedVoice}
              onChange={(e) => setSelectedVoice(e.target.value)}
              className="bg-transparent text-slate-200 font-semibold text-xs focus:outline-none cursor-pointer pr-1"
            >
              <option value="uz-UZ-MadinaNeural" className="bg-slate-900 text-white">Madina (Ayol)</option>
              <option value="uz-UZ-SardorNeural" className="bg-slate-900 text-white">Sardor (Erkak)</option>
            </select>
          </div>

          {/* Quick Prompts Toggle */}
          {!isOperatorActive && (
            <button
              onClick={() => setIsQuickPromptsOpen((prev) => !prev)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/10 hover:bg-white/15 backdrop-blur-md border border-white/10 text-xs font-semibold text-amber-300 transition active:scale-95"
              title="Tezkor savollar panelini ochish"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span className="hidden sm:inline">Tezkor Savollar</span>
              {isQuickPromptsOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>
      </div>

      {/* Mic error notice */}
      {micErrorMessage && (
        <div className="relative z-30 mx-auto max-w-md px-4 py-2 rounded-xl bg-amber-500/20 border border-amber-400/40 text-amber-200 text-xs flex items-center gap-2 animate-fade-in">
          <AlertCircle className="w-4 h-4 shrink-0 text-amber-400" />
          <span>{micErrorMessage}</span>
        </div>
      )}

      {/* CENTER: LARGE DYNAMIC PULSATING VOICE ORB */}
      <div className="relative flex-1 flex flex-col items-center justify-center py-2 sm:py-6 overflow-hidden">
        <div className="relative flex items-center justify-center">
          {/* Outer Pulsating Halo Rings */}
          {mode === 'recording' && (
            <>
              <div
                style={{ transform: `scale(${1.2 + audioInputLevel * 0.7})` }}
                className="absolute w-56 h-56 sm:w-72 sm:h-72 rounded-full bg-emerald-500/20 blur-2xl transition-transform duration-75 pointer-events-none"
              />
              <div
                style={{ transform: `scale(${1.1 + audioInputLevel * 0.4})` }}
                className="absolute w-52 h-52 sm:w-64 sm:h-64 rounded-full border-2 border-emerald-400/40 bg-emerald-500/10 transition-transform duration-75 pointer-events-none"
              />
            </>
          )}

          {mode === 'speaking' && (
            <>
              <div className="absolute w-60 h-60 sm:w-80 sm:h-80 rounded-full bg-blue-500/25 blur-3xl animate-pulse pointer-events-none" />
              <div className="absolute w-52 h-52 sm:w-68 sm:h-68 rounded-full border border-cyan-400/30 animate-ping pointer-events-none opacity-40" />
            </>
          )}

          {mode === 'thinking' && (
            <div className="absolute w-56 h-56 sm:w-72 sm:h-72 rounded-full border-2 border-dashed border-amber-400/60 animate-spin pointer-events-none" />
          )}

          {mode === 'idle' && (
            <div className="absolute w-48 h-48 sm:w-60 sm:h-60 rounded-full bg-blue-600/10 blur-xl animate-pulse pointer-events-none" />
          )}

          {/* Core Voice Orb */}
          <div
            onClick={toggleRecording}
            style={{ transform: `scale(${orbScale})` }}
            className={`cursor-pointer relative z-10 w-44 h-44 sm:w-56 sm:h-56 rounded-full flex flex-col items-center justify-center transition-all duration-150 select-none shadow-2xl active:scale-95 ${
              mode === 'recording'
                ? 'bg-gradient-to-tr from-emerald-600 via-teal-500 to-cyan-400 shadow-[0_0_70px_rgba(16,185,129,0.55)] border-4 border-emerald-300/80'
                : mode === 'speaking'
                ? 'bg-gradient-to-tr from-blue-600 via-indigo-500 to-cyan-400 shadow-[0_0_70px_rgba(59,130,246,0.55)] border-4 border-cyan-300/80 animate-pulse'
                : mode === 'thinking'
                ? 'bg-gradient-to-tr from-amber-600 via-orange-500 to-yellow-400 shadow-[0_0_60px_rgba(245,158,11,0.5)] border-4 border-amber-300/80'
                : 'bg-gradient-to-tr from-slate-900 via-blue-950 to-indigo-950 shadow-[0_0_40px_rgba(59,130,246,0.3)] border-2 border-blue-500/40 hover:border-blue-400 hover:shadow-[0_0_50px_rgba(59,130,246,0.5)]'
            }`}
          >
            {/* Visual Centerpiece Icon/Wave */}
            {mode === 'recording' ? (
              <div className="flex flex-col items-center gap-2">
                <Mic className="w-12 h-12 sm:w-16 sm:h-16 text-white drop-shadow-md animate-bounce" />
                <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-100">
                  Tinglanmoqda...
                </span>
              </div>
            ) : mode === 'speaking' ? (
              <div className="flex flex-col items-center gap-3">
                <div className="flex items-center gap-1.5 h-10">
                  <span className="w-1.5 h-6 bg-white rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <span className="w-1.5 h-10 bg-white rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <span className="w-1.5 h-8 bg-white rounded-full animate-bounce" />
                  <span className="w-1.5 h-10 bg-white rounded-full animate-bounce [animation-delay:-0.2s]" />
                  <span className="w-1.5 h-5 bg-white rounded-full animate-bounce [animation-delay:-0.4s]" />
                </div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-cyan-100">
                  SözLab AI Javobi
                </span>
              </div>
            ) : mode === 'thinking' ? (
              <div className="flex flex-col items-center gap-2">
                <RefreshCw className="w-12 h-12 sm:w-14 sm:h-14 text-white animate-spin" />
                <span className="text-[11px] font-bold uppercase tracking-wider text-amber-100">
                  O&apos;ylamoqda...
                </span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-blue-500/20 border border-blue-400/40 flex items-center justify-center text-blue-300">
                  <PhoneCall className="w-7 h-7 sm:w-8 sm:h-8" />
                </div>
                <span className="text-[11px] font-semibold text-slate-300">
                  {activeCall ? 'Gapirish uchun bosing' : 'Qo\'ng\'iroqni boshlash'}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Dynamic Orb Helper Description */}
        <p className="mt-4 text-xs font-medium text-slate-400 text-center tracking-wide">
          {mode === 'recording'
            ? 'Ovoz balandligi darajasiga qarab orb kengayadi. To\'xtatish uchun qayta bosing.'
            : mode === 'speaking'
            ? 'AI javobini tinglamoqdasiz. Ovozli javob to\'xtagach gapirishingiz mumkin.'
            : mode === 'thinking'
            ? 'Gemini multimodal tahlili ishlamoqda...'
            : activeCall
            ? 'Oliy ta\'lim vazirligi 1006 ishonch liniyasi faol.'
            : 'Vazirlik ovozli AI call-markaziga ulanish uchun bosing.'}
        </p>
      </div>

      {/* CLOSED CAPTIONS: SLEEK 2-LINE LIVE SUBTITLE BOX */}
      <div className="relative z-20 px-4 sm:px-8 my-2">
        <div className="max-w-2xl mx-auto rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-white/10 p-4 shadow-xl">
          <div className="flex items-center justify-between mb-1.5">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-300">
                {liveCaptionSpeaker}
              </span>
            </div>
            <span className="text-[10px] text-slate-400">
              Jonli Subtitr (Closed Captions)
            </span>
          </div>

          <p className="text-xs sm:text-sm font-medium text-slate-100 line-clamp-2 leading-relaxed min-h-[2.5rem]">
            {liveCaptionText}
          </p>
        </div>
      </div>

      {/* FLOATING GLASSMORPHIC BOTTOM CONTROL DOCK */}
      <div className="relative z-30 px-4 sm:px-8 pb-5 pt-2">
        <div className="max-w-lg mx-auto bg-slate-900/85 backdrop-blur-2xl border border-white/15 rounded-3xl p-3 sm:p-4 shadow-2xl flex items-center justify-center gap-4 sm:gap-6">
          {/* Button 1: Mute / Unmute */}
          <button
            onClick={() => setIsMuted((prev) => !prev)}
            className={`w-12 h-12 sm:w-14 sm:h-14 rounded-full flex flex-col items-center justify-center transition-all active:scale-95 border ${
              isMuted
                ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
                : 'bg-white/10 border-white/15 text-slate-200 hover:bg-white/20'
            }`}
            title={isMuted ? 'Ovozni yoqish' : 'Ovozni o\'chirish (Mute)'}
          >
            {isMuted ? <VolumeX className="w-5 h-5 sm:w-6 sm:h-6" /> : <Volume2 className="w-5 h-5 sm:w-6 sm:h-6" />}
            <span className="text-[9px] mt-0.5 font-semibold text-slate-300">
              {isMuted ? 'Mute' : 'Ovoz'}
            </span>
          </button>

          {/* Button 2: Speak / Microphone (Main Action) */}
          <button
            onClick={toggleRecording}
            disabled={mode === 'thinking'}
            className={`w-16 h-16 sm:w-20 sm:h-20 rounded-full flex flex-col items-center justify-center shadow-xl transition-all active:scale-95 disabled:opacity-50 ${
              mode === 'recording'
                ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/40 animate-pulse border-2 border-rose-300'
                : !activeCall || activeCall.status === 'completed'
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/40 border-2 border-emerald-300'
                : 'bg-gradient-to-tr from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-white shadow-emerald-500/30 border-2 border-emerald-200'
            }`}
            title={mode === 'recording' ? 'Yozishni to\'xtatish' : 'Gapirish (Mikrofon)'}
          >
            {mode === 'recording' ? (
              <>
                <MicOff className="w-7 h-7 sm:w-8 sm:h-8" />
                <span className="text-[9px] font-bold mt-0.5">To&apos;xtatish</span>
              </>
            ) : mode === 'thinking' ? (
              <>
                <RefreshCw className="w-6 h-6 sm:w-7 sm:h-7 animate-spin" />
                <span className="text-[9px] font-bold mt-0.5">Kuting</span>
              </>
            ) : (
              <>
                <Mic className="w-7 h-7 sm:w-8 sm:h-8" />
                <span className="text-[9px] font-bold mt-0.5">
                  {!activeCall ? 'Boshlash' : 'Gapirish'}
                </span>
              </>
            )}
          </button>

          {/* Button 3: Operatorga ulash (Transfer) */}
          <button
            onClick={handleTransferToOperator}
            disabled={!activeCall || activeCall.status === 'completed' || activeCall.status === 'operator_handling'}
            className={`w-12 h-12 sm:w-14 sm:h-14 rounded-full flex flex-col items-center justify-center transition-all active:scale-95 border disabled:opacity-40 disabled:cursor-not-allowed ${
              activeCall?.status === 'operator_handling'
                ? 'bg-blue-600 border-blue-400 text-white shadow-lg shadow-blue-600/30'
                : activeCall?.status === 'waiting_operator'
                ? 'bg-amber-500/20 border-amber-500/50 text-amber-300 animate-pulse'
                : 'bg-white/10 border-white/15 text-slate-200 hover:bg-white/20'
            }`}
            title="Inson-operatorga yo'naltirish"
          >
            <Headset className="w-5 h-5 sm:w-6 sm:h-6" />
            <span className="text-[9px] mt-0.5 font-semibold text-slate-300">
              {activeCall?.status === 'operator_handling' ? 'Ulangan' : 'Operator'}
            </span>
          </button>

          {/* Button 4: Red "Tugatish" (End Call) */}
          <button
            onClick={handleEndCall}
            disabled={!activeCall || activeCall.status === 'completed'}
            className="w-12 h-12 sm:w-14 sm:h-14 rounded-full flex flex-col items-center justify-center bg-rose-600/90 hover:bg-rose-600 text-white shadow-lg shadow-rose-600/30 transition-all active:scale-95 border border-rose-500 disabled:opacity-40 disabled:cursor-not-allowed"
            title="Qo'ng'iroqni tugatish"
          >
            <PhoneOff className="w-5 h-5 sm:w-6 sm:h-6" />
            <span className="text-[9px] mt-0.5 font-semibold text-rose-100">
              Tugatish
            </span>
          </button>
        </div>
      </div>

      {/* QUICK DEMO PROMPTS & TEXT INPUT DRAWER */}
      {isQuickPromptsOpen && (
        <div className="absolute inset-x-0 bottom-24 z-40 max-w-3xl mx-auto px-4 animate-in slide-in-from-bottom duration-200">
          <div className="bg-slate-900/95 backdrop-blur-2xl border border-slate-700 rounded-3xl p-5 shadow-2xl text-white">
            <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  Tezkor Demo Savollar (1-klik orqali yuborish)
                </h4>
              </div>
              <button
                onClick={() => setIsQuickPromptsOpen(false)}
                className="text-xs text-slate-400 hover:text-white"
              >
                Yopish ✕
              </button>
            </div>

            {/* Quick buttons grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-52 overflow-y-auto pr-1">
              {QUICK_PROMPTS.map((p, idx) => (
                <button
                  key={idx}
                  disabled={!activeCall || activeCall.status === 'completed' || mode === 'thinking'}
                  onClick={() => handleSendMessage(p.text)}
                  className="text-left p-2.5 rounded-xl border border-slate-800 bg-slate-800/60 hover:bg-blue-900/40 hover:border-blue-500/50 transition-all text-xs group disabled:opacity-40"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-bold text-blue-300 bg-blue-500/20 px-1.5 py-0.5 rounded">
                      {p.category}
                    </span>
                    <span className="text-[10px] text-slate-400 group-hover:text-blue-300">
                      Yuborish →
                    </span>
                  </div>
                  <p className="text-slate-200 line-clamp-1 text-[11px]">
                    {p.text}
                  </p>
                </button>
              ))}
            </div>

            {/* Optional text message input */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage(customInputText);
              }}
              className="mt-3 pt-3 border-t border-slate-800 flex items-center gap-2"
            >
              <input
                type="text"
                value={customInputText}
                onChange={(e) => setCustomInputText(e.target.value)}
                disabled={!activeCall || activeCall.status === 'completed' || mode === 'thinking'}
                placeholder="Yoki savolingizni matn ko'rinishida yozing..."
                className="flex-1 bg-slate-800/80 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={!customInputText.trim() || !activeCall || activeCall.status === 'completed' || mode === 'thinking'}
                className="p-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold transition disabled:opacity-40"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* POST-CALL SUMMARY MODAL */}
      {showSummaryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-xl animate-fade-in">
          <div className="relative w-full max-w-lg bg-slate-900 border border-slate-700 rounded-3xl p-6 sm:p-8 shadow-2xl text-white">
            <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-emerald-500/20">
              <CheckCircle2 className="w-8 h-8 text-emerald-400" />
            </div>

            <h3 className="text-xl sm:text-2xl font-extrabold text-center text-white">
              Suhbat Yakunlandi
            </h3>
            <p className="text-xs text-slate-300 text-center mt-1">
              Oliy ta&apos;lim, fan va innovatsiyalar vazirligi call-markazi muloqot xulosasi
            </p>

            {/* Summary Details Grid */}
            <div className="mt-6 bg-slate-800/60 border border-slate-700/60 rounded-2xl p-4 space-y-3 text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-slate-700/50">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-blue-400" />
                  Suhbat davomiyligi:
                </span>
                <span className="font-mono font-bold text-white">
                  {formatTime(callDuration)}
                </span>
              </div>

              <div className="flex items-center justify-between pb-2 border-b border-slate-700/50">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  Asosiy mavzu:
                </span>
                <span className="font-semibold text-amber-300">
                  {activeCall?.primary_topic || 'Umumiy Murojaat'}
                </span>
              </div>

              <div className="flex items-center justify-between pb-2 border-b border-slate-700/50">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  Xizmat turi:
                </span>
                <span className="font-semibold text-emerald-300">
                  {activeCall?.assigned_operator ? `Operator (${activeCall.assigned_operator})` : 'SözLab AI Agent'}
                </span>
              </div>

              <div className="pt-1">
                <span className="text-slate-400 block mb-1">Xulosa va tavsiya:</span>
                <p className="text-[11px] text-slate-200 bg-slate-900/60 p-2.5 rounded-xl border border-slate-700/50 leading-relaxed">
                  {activeCall?.resolution_summary || 'Fuqaroning ta\'lim me\'yorlari bo\'yicha barcha savollariga to\'liq va rasmiy javob berildi.'}
                </p>
              </div>

              {/* Supabase Archiving Badge */}
              <div className="flex items-center gap-2 p-2.5 rounded-xl bg-emerald-500/15 border border-emerald-400/30 text-emerald-200 text-xs">
                <ShieldCheck className="w-4 h-4 shrink-0 text-emerald-400" />
                <span>Barcha ma&apos;lumotlar va to&apos;liq transkripsiya Supabase bazasiga avtomatik arxivlandi.</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-6 grid grid-cols-2 gap-3">
              <button
                onClick={handleStartCall}
                className="py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2 transition active:scale-95"
              >
                <PhoneCall className="w-4 h-4" />
                <span>Yangi Qo&apos;ng&apos;iroq</span>
              </button>

              <button
                onClick={() => router.push('/')}
                className="py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold text-xs flex items-center justify-center gap-2 transition active:scale-95"
              >
                <Home className="w-4 h-4" />
                <span>Bosh Sahifa</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
