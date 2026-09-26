'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  PhoneCall, PhoneOff, Volume2, VolumeX, ShieldCheck,
  User, Sparkles, MessageSquare, ArrowRight, BookmarkCheck, CheckCircle2,
  Mic, MicOff, Send, Radio
} from 'lucide-react';
import { CallRecord, Message } from '@/lib/types';
import {
  startNewCall, sendAudioTurn, completeCall,
  getAudioFullUrl, getCallWebSocketUrl, sendDialogTurn
} from '@/lib/api';
import { AudioRecorder } from '@/lib/audioRecorder';
import { useRole } from '@/lib/useRole';

interface FloatingTranscriptItem {
  id: string;
  role: 'human' | 'ai';
  text: string;
  timestamp: string;
  isFading?: boolean;
}

export default function CallSimulator() {
  const router = useRouter();
  const { session } = useRole();
  const [activeCall, setActiveCall] = useState<CallRecord | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [floatingTranscripts, setFloatingTranscripts] = useState<FloatingTranscriptItem[]>([]);
  const [callDuration, setCallDuration] = useState(0);
  const [mode, setMode] = useState<'idle' | 'recording' | 'thinking' | 'speaking'>('idle');
  const [isMuted, setIsMuted] = useState(false);
  const [micErrorMessage, setMicErrorMessage] = useState<string | null>(null);
  const [callContextSummary, setCallContextSummary] = useState<string | null>(null);
  const [audioLevel, setAudioLevel] = useState(0);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const audioRecorderRef = useRef<AudioRecorder | null>(null);

  // Synchronized state refs for callbacks
  const activeCallRef = useRef<CallRecord | null>(null);
  const modeRef = useRef<'idle' | 'recording' | 'thinking' | 'speaking'>('idle');
  const isMutedRef = useRef(false);
  const hasSpokenRef = useRef(false);
  const speechStartTimeRef = useRef(0);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const ambientNoiseFloorRef = useRef(0.015);
  const isSubmittingRef = useRef(false);
  const lastPlayedAudioUrlRef = useRef<string | null>(null);
  const fadeTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isFarewellPendingRef = useRef(false);

  const isFarewellText = (text?: string): boolean => {
    if (!text) return false;
    const t = text.toLowerCase();
    return (
      t.includes('rahmat') ||
      t.includes('raxmat') ||
      t.includes('rahmad') ||
      t.includes('raxmad') ||
      t.includes('tashakkur') ||
      t.includes('arzimaydi') ||
      t.includes('salomat') ||
      t.includes("sog' bo'ling") ||
      t.includes('sog boling') ||
      t.includes('sogʻ boʻling') ||
      t.includes('xayr') ||
      t.includes('xayir') ||
      t.includes('minnatdor') ||
      t.includes('yaxshi qoling')
    );
  };

  // Keep refs up to date
  useEffect(() => {
    activeCallRef.current = activeCall;
  }, [activeCall]);

  useEffect(() => {
    modeRef.current = mode;
  }, [mode]);

  useEffect(() => {
    isMutedRef.current = isMuted;
  }, [isMuted]);

  // Add floating transcript helper with strict deduplication
  const addFloatingTranscript = (role: 'human' | 'ai', text: string) => {
    if (!text || !text.trim()) return;
    const cleanText = text.trim();

    if (fadeTimerRef.current) {
      clearTimeout(fadeTimerRef.current);
      fadeTimerRef.current = null;
    }

    setFloatingTranscripts((prev) => {
      // Check if recent transcript already has same role and text
      const isDuplicate = prev.slice(-4).some((item) => item.role === role && item.text === cleanText);
      if (isDuplicate) return prev;

      const newItem: FloatingTranscriptItem = {
        id: `tr-${Date.now()}-${Math.random()}`,
        role,
        text: cleanText,
        timestamp: new Date().toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        isFading: false,
      };

      return [...prev.slice(-5).map((t) => ({ ...t, isFading: false })), newItem];
    });
  };

  // Initialize AudioRecorder with responsive adaptive VAD
  useEffect(() => {
    audioRecorderRef.current = new AudioRecorder((level) => {
      setAudioLevel(Math.min(100, Math.round(level * 350)));

      // Lock VAD if not in recording mode or already submitting or AI is speaking
      if (modeRef.current !== 'recording' || isSubmittingRef.current) return;

      // Track ambient baseline noise floor before user starts speaking
      if (!hasSpokenRef.current) {
        ambientNoiseFloorRef.current = Math.min(0.04, ambientNoiseFloorRef.current * 0.92 + level * 0.08);
      }

      // Balanced speech & silence thresholds prioritizing conversational quality
      const SPEECH_TRIGGER = Math.max(0.034, ambientNoiseFloorRef.current * 1.45 + 0.008);
      const SILENCE_DURATION_MS = 1200; // 1.2s balanced silence window for natural pauses

      if (level > SPEECH_TRIGGER) {
        if (!hasSpokenRef.current) {
          hasSpokenRef.current = true;
          speechStartTimeRef.current = Date.now();
        }
        // Cancel silence countdown when user resumes speaking
        if (silenceTimerRef.current && level > SPEECH_TRIGGER * 1.2) {
          clearTimeout(silenceTimerRef.current);
          silenceTimerRef.current = null;
        }
      } else if (hasSpokenRef.current) {
        // level <= SPEECH_TRIGGER: user is pausing or finished speaking
        const spokenDuration = Date.now() - speechStartTimeRef.current;
        if (spokenDuration > 450 && !silenceTimerRef.current) {
          silenceTimerRef.current = setTimeout(() => {
            stopRecordingAndSend();
          }, SILENCE_DURATION_MS);
        }
      }
    });

    return () => {
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      if (fadeTimerRef.current) clearTimeout(fadeTimerRef.current);
      if (audioRecorderRef.current) audioRecorderRef.current.cancel();
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // Call duration timer
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

  // WebSocket connection for live messages
  useEffect(() => {
    if (!activeCall) return;

    try {
      const wsUrl = getCallWebSocketUrl(activeCall.id);
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'ai_response') {
            const aiMsg = data.message;
            setMessages((prev) => {
              if (prev.some((m) => m.id === aiMsg.id)) return prev;
              return [...prev, aiMsg];
            });
            addFloatingTranscript('ai', aiMsg.text);

            const isWsFarewell = Boolean(
              data.is_farewell ||
              data.status === 'completed' ||
              isFarewellText(aiMsg.text) ||
              isFarewellPendingRef.current
            );
            if (isWsFarewell) {
              isFarewellPendingRef.current = true;
            }

            if (aiMsg.audio_url && !isMutedRef.current) {
              playAudioResponse(aiMsg.audio_url, isWsFarewell, "Fuqaro minnatdorchilik bildirib suhbatni yakunladi.");
            }
          } else if (data.type === 'new_message') {
            const msg = data.message;
            setMessages((prev) => {
              if (prev.some((m) => m.id === msg.id)) return prev;
              return [...prev, msg];
            });
            const role = msg.role === 'citizen' || msg.role === 'user' ? 'human' : 'ai';
            addFloatingTranscript(role, msg.text);
          } else if (data.type === 'ai_thinking') {
            setMode('thinking');
          } else if (data.type === 'call_completed') {
            isFarewellPendingRef.current = true;
            if (audioRecorderRef.current && audioRecorderRef.current.isRecording()) {
              audioRecorderRef.current.stop().catch(() => {});
            }
            if (silenceTimerRef.current) {
              clearTimeout(silenceTimerRef.current);
              silenceTimerRef.current = null;
            }
            setActiveCall((prev) => (prev ? { ...prev, status: 'completed' } : null));
            activeCallRef.current = null;
            setCallContextSummary(data.summary || "Fuqaro minnatdorchilik bildirib suhbatni yakunladi.");
            setMode('idle');
            modeRef.current = 'idle';
          }
        } catch {
          // ignore
        }
      };

      wsRef.current = ws;
      return () => {
        ws.close();
      };
    } catch {
      // ws fallback
    }
  }, [activeCall?.id]);

  // Play audio response safely without interruption
  const playAudioResponse = (urlPath: string, isFarewell: boolean = false, summaryText?: string) => {
    if (!urlPath) return;

    if (isFarewell || isFarewellPendingRef.current) {
      isFarewellPendingRef.current = true;
    }

    // Deduplicate if already playing this URL
    if (lastPlayedAudioUrlRef.current === urlPath && modeRef.current === 'speaking') {
      if (isFarewell) {
        isFarewellPendingRef.current = true;
      }
      return;
    }
    lastPlayedAudioUrlRef.current = urlPath;

    // Lock mode to speaking so microphone recording doesn't listen to AI output
    setMode('speaking');
    modeRef.current = 'speaking';

    if (fadeTimerRef.current) {
      clearTimeout(fadeTimerRef.current);
      fadeTimerRef.current = null;
    }
    // Ensure all floating transcripts remain 100% visible while AI is speaking
    setFloatingTranscripts((prev) => prev.map((t) => ({ ...t, isFading: false })));

    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    // Cancel any active microphone recording while AI speaks
    if (audioRecorderRef.current && audioRecorderRef.current.isRecording()) {
      audioRecorderRef.current.cancel();
    }

    const fullUrl = getAudioFullUrl(urlPath);
    if (!audioRef.current) {
      audioRef.current = new Audio();
    }

    const audio = audioRef.current;
    audio.pause();
    audio.currentTime = 0;
    audio.src = fullUrl;

    const finalizeCallIfFarewell = (): boolean => {
      if (isFarewell || isFarewellPendingRef.current) {
        isFarewellPendingRef.current = false;
        if (audioRecorderRef.current && audioRecorderRef.current.isRecording()) {
          audioRecorderRef.current.stop().catch(() => {});
        }
        if (silenceTimerRef.current) {
          clearTimeout(silenceTimerRef.current);
          silenceTimerRef.current = null;
        }
        setActiveCall((prev) => (prev ? { ...prev, status: 'completed' } : null));
        activeCallRef.current = null;
        setCallContextSummary(summaryText || "Fuqaro minnatdorchilik bildirib suhbatni yakunladi.");
        return true;
      }
      return false;
    };

    audio.onended = () => {
      setMode('idle');
      modeRef.current = 'idle';

      // Delay fade-out animation until 4 seconds after AI speech has concluded
      if (fadeTimerRef.current) clearTimeout(fadeTimerRef.current);
      fadeTimerRef.current = setTimeout(() => {
        setFloatingTranscripts((prev) =>
          prev.map((t) => ({ ...t, isFading: true }))
        );
      }, 4000);

      if (finalizeCallIfFarewell()) {
        return;
      }

      // After AI finishes speaking, pause briefly and auto-start hands-free recording for next question
      setTimeout(() => {
        startRecording();
      }, 400);
    };

    audio.onerror = (e) => {
      console.warn("Audio playback error:", e);
      setMode('idle');
      modeRef.current = 'idle';

      // Delay fade-out animation until 4 seconds after audio error
      if (fadeTimerRef.current) clearTimeout(fadeTimerRef.current);
      fadeTimerRef.current = setTimeout(() => {
        setFloatingTranscripts((prev) =>
          prev.map((t) => ({ ...t, isFading: true }))
        );
      }, 4000);

      if (finalizeCallIfFarewell()) {
        return;
      }
      setTimeout(() => startRecording(), 600);
    };

    audio.play().catch((err) => {
      console.warn("Audio play rejected by browser:", err);
      setMode('idle');
      modeRef.current = 'idle';

      // Delay fade-out animation until 4 seconds after audio rejection
      if (fadeTimerRef.current) clearTimeout(fadeTimerRef.current);
      fadeTimerRef.current = setTimeout(() => {
        setFloatingTranscripts((prev) =>
          prev.map((t) => ({ ...t, isFading: true }))
        );
      }, 4000);

      if (finalizeCallIfFarewell()) {
        return;
      }
      setTimeout(() => startRecording(), 600);
    });
  };

  // Start Call (Green button)
  const handleStartCall = async () => {
    try {
      setMode('thinking');
      const citizenName = session.citizenName || 'Fuqaro';
      const citizenPhone = session.citizenPhone || '+998 (90) 123-45-67';

      const call = await startNewCall(citizenName, citizenPhone);
      activeCallRef.current = call;
      setActiveCall(call);
      setMessages(call.messages || []);
      setFloatingTranscripts([]);
      if (fadeTimerRef.current) {
        clearTimeout(fadeTimerRef.current);
        fadeTimerRef.current = null;
      }
      setCallDuration(0);
      setCallContextSummary(null);
      lastPlayedAudioUrlRef.current = null;
      isFarewellPendingRef.current = false;
      setMode('idle');

      // Start recording immediately
      await startRecording(call);
    } catch (err) {
      setMode('idle');
      alert("Qo'ng'iroqni boshlab bo'lmadi. Server aloqasini tekshiring.");
    }
  };

  // End Call (Red button)
  const handleEndCall = async () => {
    const currentCall = activeCallRef.current || activeCall;
    if (!currentCall) return;

    try {
      if (fadeTimerRef.current) {
        clearTimeout(fadeTimerRef.current);
        fadeTimerRef.current = null;
      }
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = null;
      }
      if (audioRecorderRef.current && audioRecorderRef.current.isRecording()) {
        await audioRecorderRef.current.stop().catch(() => {});
      }
      if (audioRef.current) {
        audioRef.current.pause();
      }

      const summaryRes = await completeCall(currentCall.id, "Muloqot fuqaro tomonidan yakunlandi.");
      setActiveCall((prev) => (prev ? { ...prev, status: 'completed' } : null));
      activeCallRef.current = null;
      setCallContextSummary(summaryRes?.resolution_summary || summaryRes?.summary || "Fuqaroga ta'lim qonunchiligi bo'yicha rasmiy maslahat berildi.");
      setMode('idle');
    } catch {
      setActiveCall((prev) => (prev ? { ...prev, status: 'completed' } : null));
      activeCallRef.current = null;
      setCallContextSummary("Fuqaro murojaati bo'yicha ta'lim qonunchiligi maslahati yakunlandi.");
      setMode('idle');
    }
  };

  // Start hands-free recording
  const startRecording = async (targetCall?: CallRecord) => {
    const call = targetCall || activeCallRef.current;
    if (!call || call.status === 'completed' || modeRef.current === 'speaking' || isFarewellPendingRef.current) return;

    try {
      setMicErrorMessage(null);
      if (!audioRecorderRef.current) {
        audioRecorderRef.current = new AudioRecorder();
      }
      hasSpokenRef.current = false;
      speechStartTimeRef.current = 0;
      ambientNoiseFloorRef.current = 0.015;
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = null;
      }
      await audioRecorderRef.current.start();
      setMode('recording');
      modeRef.current = 'recording';
    } catch (err: any) {
      setMode('idle');
      modeRef.current = 'idle';
      setMicErrorMessage("Mikrofondan foydalanishga ruxsat bering.");
      setTimeout(() => setMicErrorMessage(null), 5000);
    }
  };

  // Stop recording & submit turn
  const stopRecordingAndSend = async () => {
    if (isSubmittingRef.current || modeRef.current !== 'recording') return;
    isSubmittingRef.current = true;

    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    setMode('thinking');
    modeRef.current = 'thinking';

    try {
      if (!audioRecorderRef.current) throw new Error('Audio recorder unavailable');
      const audioBlob = await audioRecorderRef.current.stop();

      const currentCall = activeCallRef.current || activeCall;
      if (!currentCall || audioBlob.size < 500) {
        setMode('idle');
        modeRef.current = 'idle';
        isSubmittingRef.current = false;
        setTimeout(() => startRecording(), 400);
        return;
      }

      const res = await sendAudioTurn(currentCall.id, audioBlob, true, 'Gulnoza');
      const isFarewell = Boolean(
        res.status === 'completed' ||
        res.intent === 'Xayrlashuv' ||
        isFarewellText(res.transcribed_text) ||
        isFarewellText(res.ai_text)
      );

      if (isFarewell) {
        isFarewellPendingRef.current = true;
      }

      if (res.transcribed_text && res.transcribed_text !== '(Tushunarsiz ovoz)') {
        const userMsg: Message = {
          id: `msg-${Date.now()}`,
          role: 'citizen',
          text: res.transcribed_text,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, userMsg]);
        addFloatingTranscript('human', res.transcribed_text);
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
        addFloatingTranscript('ai', res.ai_text);
      }

      if (res.audio_url && !isMutedRef.current) {
        playAudioResponse(res.audio_url, isFarewell, "Fuqaro minnatdorchilik bildirib suhbatni yakunladi.");
      } else if (isFarewell) {
        isFarewellPendingRef.current = false;
        if (audioRecorderRef.current && audioRecorderRef.current.isRecording()) {
          audioRecorderRef.current.stop().catch(() => {});
        }
        if (silenceTimerRef.current) {
          clearTimeout(silenceTimerRef.current);
          silenceTimerRef.current = null;
        }
        setActiveCall((prev) => (prev ? { ...prev, status: 'completed' } : null));
        activeCallRef.current = null;
        setCallContextSummary("Fuqaro minnatdorchilik bildirib suhbatni yakunladi.");
        setMode('idle');
        modeRef.current = 'idle';
      } else {
        setMode('idle');
        modeRef.current = 'idle';
        if (fadeTimerRef.current) clearTimeout(fadeTimerRef.current);
        fadeTimerRef.current = setTimeout(() => {
          setFloatingTranscripts((prev) => prev.map((t) => ({ ...t, isFading: true })));
        }, 4000);
        setTimeout(() => startRecording(), 600);
      }
    } catch (err: any) {
      setMode('idle');
      modeRef.current = 'idle';
      setMicErrorMessage(err.message || 'Ovoz yuborishda xatolik yuz berdi');
      setTimeout(() => setMicErrorMessage(null), 4000);
      setTimeout(() => startRecording(), 800);
    } finally {
      isSubmittingRef.current = false;
    }
  };

  // Format seconds mm:ss
  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const s = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const isCallActive = !!(activeCall && activeCall.status !== 'completed');

  return (
    <div className="relative flex-1 w-full h-full bg-slate-50 flex flex-col justify-between overflow-hidden select-none pb-20">
      <audio ref={audioRef} className="hidden" preload="auto" />

      {/* Top Banner: User Profile Header */}
      <div className="w-full bg-white border-b border-slate-200 px-4 sm:px-8 py-3 flex items-center justify-between shadow-2xs shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold shadow-xs">
            <User className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-extrabold text-slate-900">
                {session.citizenName || 'Fuqaro Murojaatchi'}
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                Ovozli Rejim
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium">
              SözLab Avtonom Ovozli Maslahat • Hands-Free VAD (1.4s)
            </p>
          </div>
        </div>

        {isCallActive && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-blue-50 border border-blue-200 text-blue-700 text-xs font-mono font-bold">
              <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping" />
              <span>{formatTime(callDuration)}</span>
            </div>

            <button
              onClick={() => setIsMuted(!isMuted)}
              className={`p-2 rounded-xl border transition ${
                isMuted
                  ? 'bg-amber-50 border-amber-200 text-amber-700'
                  : 'bg-slate-100 border-slate-200 text-slate-700 hover:bg-slate-200'
              }`}
              title={isMuted ? "Ovozni yoqish" : "Ovozni o'chirish"}
            >
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>
          </div>
        )}
      </div>

      {/* Main Center Call Stage & Spawning Live Transcripts */}
      <div className="flex-1 max-w-3xl w-full mx-auto px-4 py-4 flex flex-col justify-between items-center relative overflow-hidden">
        {/* Floating Transcripts Stream (Spawning from bottom, going up, fading out) */}
        <div className="w-full flex-1 flex flex-col justify-end space-y-3 pointer-events-none mb-4 overflow-hidden min-h-[220px]">
          {floatingTranscripts.map((item) => {
            const isSpeaking = mode === 'speaking';
            const isFrozen = isSpeaking && !item.isFading;
            return (
              <div
                key={item.id}
                className={`p-3.5 sm:p-4 rounded-2xl border shadow-md backdrop-blur-md transition-all select-text pointer-events-auto ${
                  isFrozen
                    ? 'animate-transcript-enter opacity-100 translate-y-0 scale-100 ring-1 ring-blue-400/40 shadow-blue-500/10'
                    : item.isFading
                    ? 'animate-transcript-exit'
                    : 'animate-transcript-enter'
                } ${
                  item.role === 'human'
                    ? 'bg-emerald-50/95 border-emerald-200 text-emerald-950 self-start max-w-[88%]'
                    : 'bg-blue-50/95 border-blue-200 text-blue-950 self-end max-w-[88%]'
                }`}
              >
                <div className="flex items-center justify-between gap-4 mb-1">
                  <span className={`text-[10px] font-black uppercase tracking-wider flex items-center gap-1.5 ${
                    item.role === 'human' ? 'text-emerald-700' : 'text-blue-700'
                  }`}>
                    {item.role === 'human' ? '🗣️ Siz' : '🤖 AI Maslahatchi'}
                    {isFrozen && item.role === 'ai' && (
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-ping" />
                    )}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">{item.timestamp}</span>
                </div>
                <p className="text-xs sm:text-sm font-semibold leading-relaxed">
                  {item.text}
                </p>
              </div>
            );
          })}

          {floatingTranscripts.length === 0 && !isCallActive && (
            <div className="text-center my-auto py-6 animate-fade-in">
              <div className="w-16 h-16 rounded-3xl bg-[#035B60]/10 border border-[#035B60]/20 text-[#035B60] mx-auto flex items-center justify-center mb-3 shadow-md shadow-[#035B60]/10">
                <PhoneCall className="w-8 h-8 text-[#035B60]" />
              </div>
              <h2 className="text-lg font-black text-slate-900">
                SözLab Ovozli Muloqot
              </h2>
              <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 leading-relaxed">
                Tugmani bosib muloqotni boshlang. Savolingizni berganingizdan so&apos;ng javob va moddalar transkripti ekranda suzib chiqadi.
              </p>
            </div>
          )}
        </div>

        {/* Error notice if microphone blocked */}
        {micErrorMessage && (
          <div className="mb-3 px-4 py-2 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs font-semibold shadow-xs">
            {micErrorMessage}
          </div>
        )}

        {/* Action Controls */}
        <div className="w-full max-w-xs flex flex-col items-center gap-3 shrink-0">
          {!isCallActive ? (
            <button
              onClick={handleStartCall}
              className="w-full py-3.5 px-6 rounded-2xl bg-[#035B60] hover:bg-[#02373A] text-white font-black text-sm sm:text-base shadow-xl shadow-[#035B60]/25 transition active:scale-95 flex items-center justify-center gap-3"
            >
              <PhoneCall className="w-5 h-5 animate-bounce" />
              <span>Qo&apos;ng&apos;iroqni Boshlash</span>
            </button>
          ) : (
            <div className="w-full flex flex-col gap-2">
              {/* Manual Speak/Send Action during Call */}
              {mode === 'recording' && (
                <button
                  onClick={stopRecordingAndSend}
                  className="w-full py-2.5 px-4 rounded-xl bg-[#FC6F01] hover:bg-[#E56300] text-white font-bold text-xs shadow-md shadow-[#FC6F01]/20 transition active:scale-95 flex items-center justify-center gap-2"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Gapirdim (Javobni Olish)</span>
                </button>
              )}

              {/* End Call Button */}
              <button
                onClick={handleEndCall}
                className="w-full py-3 px-6 rounded-2xl bg-rose-600 hover:bg-rose-700 text-white font-black text-sm shadow-xl shadow-rose-500/25 transition active:scale-95 flex items-center justify-center gap-2.5 animate-pulse"
              >
                <PhoneOff className="w-5 h-5" />
                <span>Qo&apos;ng&apos;iroqni Yakunlash</span>
              </button>
            </div>
          )}

          {/* Status Indicator & Live Volume Meter */}
          <div className="flex items-center gap-2 text-[11px] font-bold text-slate-500">
            <span className={`w-2.5 h-2.5 rounded-full transition-colors ${
              mode === 'recording'
                ? 'bg-emerald-500 animate-ping'
                : mode === 'thinking'
                ? 'bg-blue-500 animate-pulse'
                : mode === 'speaking'
                ? 'bg-amber-500 animate-bounce'
                : 'bg-slate-300'
            }`} />
            <span>
              {mode === 'recording'
                ? `Tinglamoqda (VAD ${audioLevel}%)`
                : mode === 'thinking'
                ? 'Qidirmoqda...'
                : mode === 'speaking'
                ? 'AI Javob bermoqda...'
                : 'Tayyor'}
            </span>
          </div>
        </div>

        {/* Call Context Summary Card for User Follow-Up */}
        {callContextSummary && (
          <div className="w-full max-w-xl mt-4 p-4 rounded-2xl bg-white border border-blue-200 shadow-md text-slate-900 animate-fade-in shrink-0">
            <div className="flex items-center gap-2 mb-1 text-blue-700">
              <BookmarkCheck className="w-4 h-4 text-blue-600" />
              <h3 className="font-extrabold text-xs">Muloqot Xulosasi</h3>
            </div>
            <p className="text-xs text-slate-700 leading-relaxed font-medium mb-2">
              {callContextSummary}
            </p>
            <div className="flex items-center justify-between text-[10px] pt-2 border-t border-slate-100 text-slate-500">
              <span>Saqlangan vaqt: {new Date().toLocaleTimeString('uz-UZ')}</span>
              <button
                onClick={() => router.push('/chat')}
                className="text-blue-600 font-bold hover:underline flex items-center gap-1"
              >
                <span>AI Chatda davom ettirish</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
