'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  Mic, MicOff, PhoneOff, PhoneCall, Volume2, VolumeX,
  Sparkles, RefreshCw, Send, ArrowRight, ShieldCheck,
  BookOpen, ExternalLink, HelpCircle
} from 'lucide-react';
import { CallRecord, Message } from '@/lib/types';
import {
  startNewCall, sendDialogTurn, sendAudioTurn,
  completeCall, getAudioFullUrl, getCallWebSocketUrl
} from '@/lib/api';
import { AudioRecorder } from '@/lib/audioRecorder';
import { useRole } from '@/lib/useRole';

const OFFICIAL_50_FAQ_PROMPTS = [
  {
    category: 'Maktab & Pul Yig\'ish (Savol 2)',
    text: "Maktabda o'quvchilardan yoki ota-onalardan pul yig'ish (fond, ta'mirlash) qonuniymi?",
  },
  {
    category: 'Pedagoglar Huquqi (Savol 9)',
    text: "O'qituvchini majburiy mehnatga (ko'cha tozalash, hashar, obuna) jalb qilish mumkinmi?",
  },
  {
    category: 'Magistratura Kontrakti (Savol 20)',
    text: "Davlat OTMlari magistraturasida o'qiyotgan xotin-qizlar kontrakti qanday qoplanadi?",
  },
  {
    category: '1-Sinfga Qabul (Savol 1)',
    text: "Bolani 1-sinfga qabul qilish tartibi va yoshi qanday belgilangan?",
  },
  {
    category: 'Yangi Grant Tizimi (Savol 19)',
    text: "2024–2026-yillarda davlat grantlari har yili GPA reytingi bo'yicha qanday qayta taqsimlanadi?",
  },
  {
    category: 'Talaba Ijarasi (Savol 23)',
    text: "Ijara xonadonida yashaydigan talabalarga davlat tomonidan 50 foiz kompensatsiya qanday to'lanadi?",
  },
  {
    category: '1 Stavka Dars Soati (Savol 33)',
    text: "Umumta'lim maktablarida o'qituvchilar uchun 1 stavka dars soati necha soat qilib belgilangan?",
  },
  {
    category: 'Inklyuziv Ta\'lim (Savol 38)',
    text: "Nogironligi bo'lgan bolalar oddiy umumta'lim maktablarida inklyuziv ta'lim ola biladimi?",
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
  const [wsConnected, setWsConnected] = useState(false);
  const [audioInputLevel, setAudioInputLevel] = useState(0);
  const [micErrorMessage, setMicErrorMessage] = useState<string | null>(null);
  const [isQuickPromptsOpen, setIsQuickPromptsOpen] = useState(false);
  const [customInputText, setCustomInputText] = useState('');
  const [showSummaryModal, setShowSummaryModal] = useState(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const audioRecorderRef = useRef<AudioRecorder | null>(null);

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
              setTimeout(() => setMode('idle'), 2500);
            }
          } else if (data.type === 'new_message') {
            const msg = data.message;
            setMessages((prev) => {
              if (prev.some((m) => m.id === msg.id)) return prev;
              return [...prev, msg];
            });
          } else if (data.type === 'ai_thinking') {
            setMode('thinking');
          } else if (data.type === 'call_completed') {
            setActiveCall((prev) => (prev ? { ...prev, status: 'completed' } : null));
            setShowSummaryModal(true);
            setMode('idle');
          }
        } catch {
          // ignore
        }
      };

      ws.onerror = () => {
        setWsConnected(false);
      };

      ws.onclose = () => {
        setWsConnected(false);
      };

      wsRef.current = ws;

      return () => {
        ws.close();
      };
    } catch {
      // ws fallback
    }
  }, [activeCall?.id, isMuted]);

  // Play audio response with barge-in support
  const playAudioResponse = (urlPath: string) => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
    const fullUrl = getAudioFullUrl(urlPath);
    const audio = new Audio(fullUrl);
    audioRef.current = audio;

    audio.onended = () => {
      setMode('idle');
    };

    audio.onerror = () => {
      setMode('idle');
    };

    audio.play().catch(() => {
      setMode('idle');
    });
  };

  // Start Call
  const handleStartCall = async () => {
    try {
      setMode('thinking');
      const citizenName = session.citizenName || 'Fuqaro';
      const citizenPhone = session.citizenPhone || '+998 (90) 123-45-67';

      const call = await startNewCall(citizenName, citizenPhone);
      setActiveCall(call);
      setMessages(call.messages || []);
      setCallDuration(0);
      setMode('idle');

      // Synthesize initial greeting
      const initMsg = call.messages?.[0];
      if (initMsg?.text && !isMuted) {
        setMode('speaking');
        try {
          const res = await sendDialogTurn(call.id, 'Assalomu alaykum', true, 'Gulnoza');
          if (res.audio_url) {
            playAudioResponse(res.audio_url);
          } else {
            setMode('idle');
          }
        } catch {
          setMode('idle');
        }
      }
    } catch (err) {
      setMode('idle');
      alert("Qo'ng'iroqni boshlab bo'lmadi. Server bilan aloqani tekshiring.");
    }
  };

  // End Call
  const handleEndCall = async () => {
    if (!activeCall) return;
    try {
      if (audioRecorderRef.current && audioRecorderRef.current.isRecording()) {
        await audioRecorderRef.current.stop();
      }
      if (audioRef.current) {
        audioRef.current.pause();
      }

      await completeCall(activeCall.id, "Muloqot fuqaro tomonidan yakunlandi.");
      setActiveCall((prev) => (prev ? { ...prev, status: 'completed' } : null));
      setShowSummaryModal(true);
      setMode('idle');
    } catch {
      setActiveCall((prev) => (prev ? { ...prev, status: 'completed' } : null));
      setShowSummaryModal(true);
      setMode('idle');
    }
  };

  // Microphone toggle (Barge-in supported: stops previous audio and immediately listens)
  const toggleRecording = async () => {
    if (!activeCall || activeCall.status === 'completed') return;

    // Barge-in: interrupt playing audio
    if (audioRef.current) {
      audioRef.current.pause();
    }

    if (mode === 'recording') {
      // Stop recording and send audio
      setMode('thinking');
      try {
        if (!audioRecorderRef.current) throw new Error('Audio recorder unavailable');
        const audioBlob = await audioRecorderRef.current.stop();
        setAudioInputLevel(0);

        if (audioBlob.size < 500) {
          setMode('idle');
          return;
        }

        const res = await sendAudioTurn(activeCall.id, audioBlob, true, 'Gulnoza');

        if (res.transcribed_text) {
          const userMsg: Message = {
            id: `msg-${Date.now()}`,
            role: 'citizen',
            text: res.transcribed_text,
            timestamp: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, userMsg]);
        }

        if (res.ai_text) {
          const aiMsg: Message = {
            id: `ai-${Date.now()}`,
            role: 'ai',
            text: res.ai_text,
            timestamp: new Date().toISOString(),
            audio_url: res.audio_url,
          };
          setMessages((prev) => [...prev, aiMsg]);
        }

        if (res.audio_url && !isMuted) {
          setMode('speaking');
          playAudioResponse(res.audio_url);
        } else {
          setMode('idle');
        }
      } catch (err: any) {
        setMode('idle');
        setMicErrorMessage(err.message || 'Ovoz yozishda xatolik');
        setTimeout(() => setMicErrorMessage(null), 4000);
      }
    } else {
      // Start recording
      try {
        setMicErrorMessage(null);
        if (!audioRecorderRef.current) throw new Error('Audio recorder unavailable');
        await audioRecorderRef.current.start();
        setMode('recording');
      } catch (err: any) {
        setMode('idle');
        setMicErrorMessage("Mikrofon ruxsati berilmadi. Iltimos, brauzerda mikrofonga ruxsat bering.");
        setTimeout(() => setMicErrorMessage(null), 5000);
      }
    }
  };

  // Text Prompt Send
  const handleSendTextPrompt = async (textToSend: string) => {
    if (!activeCall || activeCall.status === 'completed' || !textToSend.trim()) return;

    // Barge-in: interrupt playing audio
    if (audioRef.current) {
      audioRef.current.pause();
    }

    setMode('thinking');
    const promptText = textToSend.trim();
    setCustomInputText('');

    const userMsg: Message = {
      id: `msg-${Date.now()}`,
      role: 'citizen',
      text: promptText,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await sendDialogTurn(activeCall.id, promptText, true, 'Gulnoza');

      const aiMsg: Message = {
        id: `ai-${Date.now()}`,
        role: 'ai',
        text: res.ai_text,
        timestamp: new Date().toISOString(),
        audio_url: res.audio_url,
      };
      setMessages((prev) => [...prev, aiMsg]);

      if (res.audio_url && !isMuted) {
        setMode('speaking');
        playAudioResponse(res.audio_url);
      } else {
        setMode('idle');
      }
    } catch {
      setMode('idle');
    }
  };

  // Format seconds to mm:ss
  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const s = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // Latest messages for subtitle display
  const latestAiMessage = [...messages].reverse().find((m) => m.role === 'ai');
  const latestCitizenMessage = [...messages].reverse().find((m) => m.role === 'citizen');

  return (
    <div className="relative h-[calc(100vh-4rem)] w-full overflow-hidden bg-zinc-950 text-zinc-100 flex flex-col justify-between select-none">
      {/* Top Status Bar */}
      <div className="w-full px-4 sm:px-8 py-3.5 border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-md flex items-center justify-between z-20">
        <div className="flex items-center gap-3">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">
                1006 / 1007 Yagona Ovozli Markaz
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 font-mono">
                100% Avtonom AI
              </span>
            </div>
            <p className="text-[11px] text-zinc-500 font-mono">
              VoiceLab Studio • Gulnoza (O&apos;zbek) • 50 ta Rasmiy FAQ Baza
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {activeCall && activeCall.status !== 'completed' && (
            <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-zinc-900 border border-zinc-800 text-xs font-mono text-zinc-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>{formatTime(callDuration)}</span>
            </div>
          )}

          <button
            onClick={() => setIsMuted(!isMuted)}
            className={`p-2 rounded-lg border transition ${
              isMuted
                ? 'bg-zinc-800 border-zinc-700 text-zinc-400'
                : 'bg-zinc-900 border-zinc-800 text-zinc-300 hover:text-white'
            }`}
            title={isMuted ? "Ovozni yoqish" : "Ovozni o'chirish"}
          >
            {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Main Center Stage: Acoustic Voice Orb & Real-Time Captions */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 relative z-10">
        {!activeCall ? (
          /* Idle Call Initiation Banner */
          <div className="text-center max-w-lg mx-auto animate-fade-in">
            <div className="w-20 h-20 mx-auto rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-200 mb-6 shadow-xl">
              <PhoneCall className="w-10 h-10 text-zinc-200" />
            </div>

            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mb-2">
              SözLab Ovozli Maslahatchi
            </h1>
            <p className="text-xs sm:text-sm text-zinc-400 mb-8 leading-relaxed">
              O&apos;zbekiston Respublikasi ta&apos;lim qonunchiligi (Maktab, Bog&apos;cha, OTM qabuli, Davlat grantlari, Pedagoglar huquqlari) bo&apos;yicha savollaringizga rasmiy moddalar bilan to&apos;g&apos;ridan-to&apos;g&apos;ri ovozli javob oling.
            </p>

            <button
              onClick={handleStartCall}
              className="py-3.5 px-8 rounded-xl bg-zinc-100 hover:bg-white text-zinc-950 font-bold text-sm shadow-xl transition active:scale-95 flex items-center justify-center gap-2.5 mx-auto"
            >
              <PhoneCall className="w-4 h-4" />
              <span>Qo&apos;ng&apos;iroqni boshlash</span>
            </button>
          </div>
        ) : (
          /* Live Acoustic Orb Experience */
          <div className="flex flex-col items-center justify-center w-full max-w-2xl text-center">
            {/* Precision Monochrome Acoustic Voice Orb */}
            <div className="relative flex items-center justify-center w-64 h-64 sm:w-72 sm:h-72 my-4">
              {/* Outer Acoustic Pulse Rings */}
              <div
                className={`absolute inset-0 rounded-full border border-zinc-800 transition-all duration-700 ${
                  mode === 'recording'
                    ? 'scale-110 border-emerald-500/40 bg-emerald-500/5'
                    : mode === 'speaking'
                    ? 'scale-105 border-zinc-700/80 bg-zinc-800/10'
                    : 'scale-95 border-zinc-800/40'
                }`}
              />

              <div
                className={`absolute inset-6 rounded-full border border-zinc-800/80 transition-all duration-500 ${
                  mode === 'recording'
                    ? 'scale-105 border-emerald-500/60'
                    : mode === 'thinking'
                    ? 'rotate-180 border-dashed border-zinc-600'
                    : 'scale-95 border-zinc-800/60'
                }`}
              />

              {/* Core Orb Center */}
              <div
                className={`relative w-36 h-36 sm:w-40 sm:h-40 rounded-full border flex flex-col items-center justify-center transition-all duration-300 shadow-2xl cursor-pointer select-none ${
                  mode === 'recording'
                    ? 'bg-zinc-900 border-emerald-500 shadow-emerald-950/40 scale-105'
                    : mode === 'thinking'
                    ? 'bg-zinc-900 border-zinc-700 animate-pulse'
                    : mode === 'speaking'
                    ? 'bg-zinc-900 border-zinc-600 shadow-zinc-900/60'
                    : 'bg-zinc-900 border-zinc-800 hover:border-zinc-700'
                }`}
                onClick={toggleRecording}
              >
                {mode === 'recording' ? (
                  <Mic className="w-10 h-10 text-emerald-400 animate-pulse" />
                ) : mode === 'thinking' ? (
                  <RefreshCw className="w-8 h-8 text-zinc-400 animate-spin" />
                ) : mode === 'speaking' ? (
                  <Volume2 className="w-10 h-10 text-zinc-200" />
                ) : (
                  <Mic className="w-10 h-10 text-zinc-400" />
                )}

                <span className="text-[11px] font-medium tracking-wide mt-2 text-zinc-300">
                  {mode === 'recording'
                    ? 'Tinglamoqda...'
                    : mode === 'thinking'
                    ? 'Qidirmoqda...'
                    : mode === 'speaking'
                    ? 'Javob bermoqda'
                    : 'Gapirish uchun bosing'}
                </span>
              </div>
            </div>

            {/* Error Notification if mic is blocked */}
            {micErrorMessage && (
              <div className="mb-4 px-3.5 py-1.5 rounded-lg bg-zinc-900 border border-red-500/30 text-red-400 text-xs">
                {micErrorMessage}
              </div>
            )}

            {/* Real-Time Subtitles & Legal Citations */}
            <div className="w-full min-h-[110px] flex flex-col items-center justify-center mt-2 px-4">
              {latestCitizenMessage && (
                <div className="text-xs text-zinc-400 mb-2 font-mono flex items-center gap-1.5">
                  <span className="text-zinc-500">Siz:</span>
                  <span className="text-zinc-300 italic">&ldquo;{latestCitizenMessage.text}&rdquo;</span>
                </div>
              )}

              {latestAiMessage ? (
                <div className="max-w-xl animate-fade-in">
                  <p className="text-sm sm:text-base font-medium text-zinc-100 leading-relaxed">
                    {latestAiMessage.text}
                  </p>

                  {/* Interactive Legal Citation Badges */}
                  <div className="flex flex-wrap items-center justify-center gap-1.5 mt-3">
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-zinc-400">
                      <ShieldCheck className="w-3 h-3 text-emerald-400" />
                      <span>Rasmiy Ta&apos;lim Qonunchiligi</span>
                    </span>
                    <a
                      href="https://lex.uz"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-zinc-400 hover:text-zinc-200 transition"
                    >
                      <span>lex.uz</span>
                      <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-zinc-500 italic font-mono">
                  Mikrofon tugmasini bosing yoki quyidagi rasmiy savollardan birini tanlang.
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Bottom Interactive Control Center */}
      {activeCall && activeCall.status !== 'completed' && (
        <div className="w-full border-t border-zinc-800/80 bg-zinc-950/90 backdrop-blur-md px-4 sm:px-8 py-3.5 z-20">
          <div className="max-w-3xl mx-auto flex flex-col gap-3">
            {/* Quick Prompts Carousel Accordion */}
            {isQuickPromptsOpen && (
              <div className="p-3 bg-zinc-900/90 border border-zinc-800 rounded-xl mb-1 max-h-48 overflow-y-auto space-y-1.5 animate-fade-in">
                <div className="flex items-center justify-between text-[11px] text-zinc-400 font-mono px-1 pb-1 border-b border-zinc-800">
                  <span>TOP-50 RASMIY SAVOL-JAVOB BAZASI (YURIDIK TIZIM)</span>
                  <span className="text-zinc-500">Bosish orqali yuborish</span>
                </div>
                {OFFICIAL_50_FAQ_PROMPTS.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      handleSendTextPrompt(item.text);
                      setIsQuickPromptsOpen(false);
                    }}
                    className="w-full text-left p-2 rounded-lg bg-zinc-950/70 hover:bg-zinc-800 border border-zinc-800/80 text-xs text-zinc-300 transition flex items-center justify-between group"
                  >
                    <div>
                      <span className="text-[10px] font-mono text-zinc-500 block uppercase">
                        {item.category}
                      </span>
                      <span className="text-zinc-200 line-clamp-1 group-hover:text-white">
                        {item.text}
                      </span>
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-zinc-500 group-hover:text-zinc-200 shrink-0 ml-2" />
                  </button>
                ))}
              </div>
            )}

            {/* Input Bar & Controls */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsQuickPromptsOpen(!isQuickPromptsOpen)}
                className={`px-3 py-2 rounded-lg border text-xs font-medium flex items-center gap-1.5 transition shrink-0 ${
                  isQuickPromptsOpen
                    ? 'bg-zinc-800 border-zinc-700 text-white'
                    : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-white'
                }`}
                title="Rasmiy savollar ro'yxati"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">50 FAQ</span>
              </button>

              <div className="relative flex-1">
                <input
                  type="text"
                  value={customInputText}
                  onChange={(e) => setCustomInputText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSendTextPrompt(customInputText);
                  }}
                  placeholder="Yoki savolingizni matn ko'rinishida yozing..."
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3.5 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-700 font-sans"
                />
                {customInputText.trim() && (
                  <button
                    onClick={() => handleSendTextPrompt(customInputText)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-zinc-400 hover:text-white"
                  >
                    <Send className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {/* Main Mic Action Button */}
              <button
                onClick={toggleRecording}
                className={`p-2.5 rounded-lg border transition flex items-center justify-center shrink-0 ${
                  mode === 'recording'
                    ? 'bg-emerald-600 border-emerald-500 text-white animate-pulse'
                    : 'bg-zinc-900 border-zinc-800 text-zinc-200 hover:border-zinc-700'
                }`}
                title={mode === 'recording' ? "To'xtatish va yuborish" : "Gapirish"}
              >
                {mode === 'recording' ? (
                  <MicOff className="w-4 h-4 text-white" />
                ) : (
                  <Mic className="w-4 h-4 text-zinc-300" />
                )}
              </button>

              {/* End Call Button */}
              <button
                onClick={handleEndCall}
                className="px-3.5 py-2 rounded-lg bg-red-950/80 hover:bg-red-900 border border-red-800/80 text-red-200 text-xs font-semibold flex items-center gap-1.5 transition shrink-0 active:scale-95"
                title="Qo'ng'iroqni yakunlash"
              >
                <PhoneOff className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Yakunlash</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Post-Call Summary Modal */}
      {showSummaryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in">
          <div className="w-full max-w-md bg-zinc-950 border border-zinc-800 rounded-2xl shadow-2xl p-6 text-zinc-100 text-center">
            <div className="w-12 h-12 rounded-xl bg-zinc-900 border border-zinc-800 mx-auto flex items-center justify-center text-zinc-200 mb-4">
              <ShieldCheck className="w-6 h-6 text-emerald-400" />
            </div>

            <h3 className="text-lg font-bold text-white mb-1">
              Muloqot Muvaffaqiyatli Yakunlandi
            </h3>
            <p className="text-xs text-zinc-400 mb-4">
              Qo&apos;ng&apos;iroq davomiyligi: <strong className="text-zinc-200 font-mono">{formatTime(callDuration)}</strong>.
              Suhbat rasmiy ta&apos;lim qonunchiligi arxivida saqlandi.
            </p>

            <div className="space-y-2">
              <button
                onClick={() => {
                  setShowSummaryModal(false);
                  setActiveCall(null);
                  setMessages([]);
                  setCallDuration(0);
                }}
                className="w-full py-2.5 px-4 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 font-bold text-xs transition"
              >
                Yangi Qo&apos;ng&apos;iroq Boshlash
              </button>

              <button
                onClick={() => router.push('/history')}
                className="w-full py-2 px-4 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 text-xs font-medium transition"
              >
                50 ta Rasmiy FAQ To&apos;plamini Ko&apos;rish
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
