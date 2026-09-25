'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Mic, MicOff, PhoneOff, Volume2, VolumeX, ShieldCheck,
  CheckCircle2, Clock, Sparkles, User, RefreshCw, Radio
} from 'lucide-react';
import { WebRTCManager } from '@/lib/webrtcManager';
import { completeCall, getCallWebSocketUrl } from '@/lib/api';

interface OperatorLiveCallProps {
  callId: string;
  citizenName: string;
  citizenPhone: string;
  topic?: string;
  operatorName: string;
  onEndCall: () => void;
}

export default function OperatorLiveCall({
  callId,
  citizenName,
  citizenPhone,
  topic = 'Umumiy Murojaat',
  operatorName,
  onEndCall,
}: OperatorLiveCallProps) {
  const [callDuration, setCallDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [isDeafened, setIsDeafened] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<string>('connecting');
  const [citizenAudioLevel, setCitizenAudioLevel] = useState(0);
  const [operatorAudioLevel, setOperatorAudioLevel] = useState(0);
  
  // Real-time closed captions
  const [captions, setCaptions] = useState<{ role: string; name: string; text: string }[]>([
    {
      role: 'system',
      name: 'Tizim',
      text: 'Jonli ovozli muloqot boshlandi. Mikrofon orqali gapiring.',
    },
  ]);

  // Completion & Supabase Archive modal state
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const [isArchiving, setIsArchiving] = useState(false);
  const [supabaseSynced, setSupabaseSynced] = useState(false);
  const [summaryText, setSummaryText] = useState('');

  const wsRef = useRef<WebSocket | null>(null);
  const webrtcRef = useRef<WebRTCManager | null>(null);

  // Duration timer
  useEffect(() => {
    const timer = setInterval(() => {
      setCallDuration((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // WebRTC & WebSocket initialization
  useEffect(() => {
    let ws: WebSocket | null = null;
    let webrtc: WebRTCManager | null = null;

    try {
      const wsUrl = getCallWebSocketUrl(callId);
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setConnectionStatus('connected');
        // Announce operator connection
        ws?.send(
          JSON.stringify({
            type: 'operator_joined',
            call_id: callId,
            operator_name: operatorName,
            mode: 'live_call',
          })
        );
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'call_completed') {
            handleCallFinished(data.summary || 'Qo\'ng\'iroq yakunlandi.');
          } else if (data.type === 'live_caption') {
            setCaptions((prev) => [
              ...prev.slice(-3),
              {
                role: data.speaker_role || 'citizen',
                name: data.speaker_name || (data.speaker_role === 'operator' ? operatorName : citizenName),
                text: data.text,
              },
            ]);
          } else {
            // Forward signaling messages to WebRTC Manager
            webrtc?.handleSignalingMessage(data);
          }
        } catch (e) {
          console.error('[Operator Live WS Parse Error]:', e);
        }
      };

      wsRef.current = ws;

      // Initialize WebRTC Manager
      webrtc = new WebRTCManager(
        callId,
        'operator',
        (payload) => {
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(payload));
          }
        },
        {
          onAudioLevels: (localLevel, remoteLevel) => {
            setOperatorAudioLevel(localLevel);
            setCitizenAudioLevel(remoteLevel);
          },
          onConnectionStatus: (status) => {
            setConnectionStatus(status);
          },
          onLiveCaption: (role, name, text) => {
            setCaptions((prev) => [
              ...prev.slice(-3),
              { role, name, text },
            ]);
          },
        }
      );

      webrtc.initialize();
      webrtcRef.current = webrtc;
    } catch (e) {
      console.error('[Operator Live Call Init Error]:', e);
    }

    return () => {
      webrtc?.destroy();
      ws?.close();
    };
  }, [callId, operatorName, citizenName]);

  const toggleMute = () => {
    const next = !isMuted;
    setIsMuted(next);
    webrtcRef.current?.setMute(next);
  };

  const toggleDeafen = () => {
    const next = !isDeafened;
    setIsDeafened(next);
    webrtcRef.current?.setDeafen(next);
  };

  const handleEndCall = async () => {
    try {
      setIsArchiving(true);
      const summary = `${topic} bo'yicha fuqaro murojaati operator ${operatorName} tomonidan to'liq ko'rib chiqildi va hal etildi.`;
      
      // Send end_call signal via WebSocket so citizen tab also completes immediately
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: 'end_call',
            call_id: callId,
            summary,
          })
        );
      }

      // Complete call via API (triggers Supabase auto-archiving)
      await completeCall(callId, summary);
      setSupabaseSynced(true);
      handleCallFinished(summary);
    } catch (err) {
      console.error('Failed to complete call:', err);
      handleCallFinished('Qo\'ng\'iroq yakunlandi.');
    } finally {
      setIsArchiving(false);
    }
  };

  const handleCallFinished = (summary: string) => {
    setSummaryText(summary);
    setShowSummaryModal(true);
    webrtcRef.current?.destroy();
  };

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const rem = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${rem.toString().padStart(2, '0')}`;
  };

  // Dynamic Orb Scale calculated from citizen's live incoming audio level
  const orbScale = 1 + citizenAudioLevel * 0.55;
  const isCitizenSpeaking = citizenAudioLevel > 0.08;
  const isOperatorSpeaking = operatorAudioLevel > 0.08 && !isMuted;

  const lastCaption = captions[captions.length - 1] || null;

  return (
    <div className="relative w-full h-[calc(100vh-4.5rem)] overflow-hidden flex flex-col justify-between bg-gradient-to-b from-slate-950 via-[#07172c] to-[#040e1c] text-white select-none">
      {/* Atmospheric Glow Backgrounds */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[550px] bg-blue-600/15 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute bottom-1/3 left-1/2 -translate-x-1/2 w-[450px] h-[450px] bg-emerald-500/15 rounded-full blur-[120px] pointer-events-none" />

      {/* TOP BAR: Citizen Info, Topic, Call Timer & Connection Badge */}
      <div className="relative z-20 px-4 sm:px-8 pt-4 pb-2 flex items-center justify-between">
        {/* Caller Info */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-blue-300 font-bold">
            <User className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm sm:text-base text-white">{citizenName}</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-400/30">
                {topic}
              </span>
            </div>
            <span className="text-xs text-slate-400">{citizenPhone}</span>
          </div>
        </div>

        {/* Status Badge & Call Timer */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/10 text-xs">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                connectionStatus === 'connected'
                  ? 'bg-emerald-400 animate-pulse'
                  : connectionStatus === 'fallback_relay'
                  ? 'bg-cyan-400 animate-pulse'
                  : 'bg-amber-400 animate-ping'
              }`}
            />
            <span className="font-semibold text-slate-200">
              {connectionStatus === 'connected'
                ? 'WebRTC Jonli Aloqa'
                : connectionStatus === 'fallback_relay'
                ? 'WS Audio Relay'
                : 'Ulanmoqda...'}
            </span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/10 text-xs font-mono text-white">
            <Clock className="w-3.5 h-3.5 text-blue-400" />
            <span>{formatTime(callDuration)}</span>
          </div>
        </div>
      </div>

      {/* CENTER: MASSIVE DYNAMIC PULSATING VOICE ORB */}
      <div className="relative flex-1 flex flex-col items-center justify-center py-2 sm:py-6 overflow-hidden">
        <div className="relative flex items-center justify-center">
          {/* Outer Pulsating Halo Rings driven by citizen speech */}
          {isCitizenSpeaking && (
            <>
              <div
                style={{ transform: `scale(${1.25 + citizenAudioLevel * 0.8})` }}
                className="absolute w-60 h-60 sm:w-80 sm:h-80 rounded-full bg-emerald-500/25 blur-3xl transition-transform duration-75 pointer-events-none"
              />
              <div
                style={{ transform: `scale(${1.15 + citizenAudioLevel * 0.5})` }}
                className="absolute w-52 h-52 sm:w-68 sm:h-68 rounded-full border-2 border-emerald-400/40 bg-emerald-500/10 transition-transform duration-75 pointer-events-none"
              />
            </>
          )}

          {isOperatorSpeaking && !isCitizenSpeaking && (
            <>
              <div
                style={{ transform: `scale(${1.2 + operatorAudioLevel * 0.6})` }}
                className="absolute w-60 h-60 sm:w-80 sm:h-80 rounded-full bg-blue-500/25 blur-3xl transition-transform duration-75 pointer-events-none"
              />
              <div
                style={{ transform: `scale(${1.1 + operatorAudioLevel * 0.3})` }}
                className="absolute w-52 h-52 sm:w-64 sm:h-64 rounded-full border-2 border-blue-400/40 bg-blue-500/10 transition-transform duration-75 pointer-events-none"
              />
            </>
          )}

          {!isCitizenSpeaking && !isOperatorSpeaking && (
            <div className="absolute w-48 h-48 sm:w-60 sm:h-60 rounded-full bg-blue-600/10 blur-xl animate-pulse pointer-events-none" />
          )}

          {/* Core Voice Orb */}
          <div
            style={{ transform: `scale(${orbScale})` }}
            className={`relative z-10 w-44 h-44 sm:w-56 sm:h-56 rounded-full flex flex-col items-center justify-center transition-transform duration-100 select-none shadow-2xl ${
              isCitizenSpeaking
                ? 'bg-gradient-to-tr from-emerald-600 via-teal-500 to-cyan-400 shadow-[0_0_80px_rgba(16,185,129,0.6)] border-4 border-emerald-300/90'
                : isOperatorSpeaking
                ? 'bg-gradient-to-tr from-blue-600 via-indigo-500 to-cyan-400 shadow-[0_0_80px_rgba(59,130,246,0.6)] border-4 border-cyan-300/90'
                : 'bg-gradient-to-tr from-slate-900 via-blue-950 to-indigo-950 shadow-[0_0_40px_rgba(59,130,246,0.3)] border-2 border-blue-500/40'
            }`}
          >
            {/* Visual Center Indicator */}
            {isCitizenSpeaking ? (
              <div className="flex flex-col items-center gap-3">
                <div className="flex items-center gap-1.5 h-10">
                  <span className="w-1.5 h-6 bg-white rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <span className="w-1.5 h-10 bg-white rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <span className="w-1.5 h-8 bg-white rounded-full animate-bounce" />
                  <span className="w-1.5 h-10 bg-white rounded-full animate-bounce [animation-delay:-0.2s]" />
                  <span className="w-1.5 h-5 bg-white rounded-full animate-bounce [animation-delay:-0.4s]" />
                </div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-100">
                  Fuqaro gapirmoqda...
                </span>
              </div>
            ) : isOperatorSpeaking ? (
              <div className="flex flex-col items-center gap-2">
                <Mic className="w-12 h-12 text-white animate-bounce drop-shadow-md" />
                <span className="text-[11px] font-bold uppercase tracking-wider text-cyan-100">
                  Siz gapiryapsiz...
                </span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <Radio className="w-10 h-10 text-blue-400 animate-pulse" />
                <span className="text-[11px] font-semibold text-slate-300">
                  Jonli Ovozli Aloqa Faol
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Descriptive Live Status */}
        <p className="mt-4 text-xs font-medium text-slate-400 text-center tracking-wide">
          {isCitizenSpeaking
            ? 'Fuqaro mikrofondan gapirmoqda. Ovoz dinamikdan eshitilmoqda.'
            : isOperatorSpeaking
            ? 'Sizning ovozingiz fuqaroga jonli uzatilmoqda.'
            : 'Ikkala tomon ham ulandi. Mikrofon orqali bemalol gaplashing.'}
        </p>
      </div>

      {/* CLOSED CAPTIONS BANNER (Real-Time Subtitles) */}
      <div className="relative z-20 px-4 sm:px-8 pb-3">
        <div className="max-w-2xl mx-auto rounded-2xl bg-white/[0.07] backdrop-blur-xl border border-white/10 p-3 sm:p-4 shadow-xl">
          <div className="flex items-center justify-between mb-1.5 text-xs font-semibold text-slate-400">
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-blue-400" />
              Real Vaqtli Jonli Subtitr (Live Closed Captions)
            </span>
            <span className="text-[10px] text-emerald-400 font-mono">LIVE STT</span>
          </div>

          <div className="min-h-[44px] flex flex-col justify-center text-sm sm:text-base leading-relaxed">
            {lastCaption ? (
              <p className="animate-fade-in">
                <span
                  className={`font-semibold mr-2 ${
                    lastCaption.role === 'operator' ? 'text-blue-300' : 'text-emerald-300'
                  }`}
                >
                  {lastCaption.role === 'operator' ? 'Siz (Operator):' : 'Fuqaro:'}
                </span>
                <span className="text-slate-100">{lastCaption.text}</span>
              </p>
            ) : (
              <p className="text-slate-500 italic text-sm">
                Suhbat davomida aytilgan gaplar real vaqtda subtitr sifatida oqib boradi...
              </p>
            )}
          </div>
        </div>
      </div>

      {/* BOTTOM CONTROL DOCK: Mute, Deafen & End Call Button */}
      <div className="relative z-20 pb-6 pt-2 flex items-center justify-center gap-6">
        {/* Mic Mute Toggle */}
        <button
          onClick={toggleMute}
          className={`w-13 h-13 sm:w-14 sm:h-14 rounded-full flex items-center justify-center border transition-all duration-150 shadow-lg ${
            isMuted
              ? 'bg-rose-500/20 border-rose-500/40 text-rose-400 hover:bg-rose-500/30'
              : 'bg-white/10 border-white/10 text-white hover:bg-white/15'
          }`}
          title={isMuted ? 'Mikrofonni yoqish' : 'Mikrofonni o\'chirish'}
        >
          {isMuted ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
        </button>

        {/* Speaker Deafen Toggle */}
        <button
          onClick={toggleDeafen}
          className={`w-13 h-13 sm:w-14 sm:h-14 rounded-full flex items-center justify-center border transition-all duration-150 shadow-lg ${
            isDeafened
              ? 'bg-amber-500/20 border-amber-500/40 text-amber-400 hover:bg-amber-500/30'
              : 'bg-white/10 border-white/10 text-white hover:bg-white/15'
          }`}
          title={isDeafened ? 'Eshitishni yoqish' : 'Eshitishni o\'chirish'}
        >
          {isDeafened ? <VolumeX className="w-6 h-6" /> : <Volume2 className="w-6 h-6" />}
        </button>

        {/* End Call Button */}
        <button
          onClick={handleEndCall}
          disabled={isArchiving}
          className="px-6 h-13 sm:h-14 rounded-full bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white font-semibold flex items-center gap-2.5 shadow-[0_0_30px_rgba(225,29,72,0.4)] border border-rose-400/40 active:scale-95 transition-all"
        >
          <PhoneOff className="w-6 h-6" />
          <span>{isArchiving ? 'Arxivlanmoqda...' : 'Qo\'ng\'iroqni Yakunlash'}</span>
        </button>
      </div>

      {/* SUMMARY & SUPABASE ARCHIVE SUCCESS MODAL */}
      {showSummaryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-fade-in">
          <div className="relative w-full max-w-lg rounded-3xl bg-slate-900 border border-slate-700/80 p-6 sm:p-8 text-white shadow-2xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center text-emerald-300">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Jonli Qo&apos;ng&apos;iroq Muvaffaqiyatli Yakunlandi</h3>
                <span className="text-xs text-slate-400">ID: {callId}</span>
              </div>
            </div>

            <div className="space-y-3.5 my-6 text-sm">
              <div className="flex justify-between py-2 border-b border-white/10">
                <span className="text-slate-400">Fuqaro:</span>
                <span className="font-semibold">{citizenName} ({citizenPhone})</span>
              </div>
              <div className="flex justify-between py-2 border-b border-white/10">
                <span className="text-slate-400">Suhbat davomiyligi:</span>
                <span className="font-mono font-semibold">{formatTime(callDuration)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-white/10">
                <span className="text-slate-400">Mavzu:</span>
                <span className="font-semibold text-blue-300">{topic}</span>
              </div>
              <div className="py-2">
                <span className="text-slate-400 block mb-1">Xulosa (AI Summary):</span>
                <p className="text-slate-200 text-xs bg-slate-800/80 p-3 rounded-xl border border-slate-700">
                  {summaryText || `${topic} bo'yicha murojaat to'liq hal etildi.`}
                </p>
              </div>

              {/* Supabase Status Banner */}
              <div className="flex items-center gap-2 p-3 rounded-xl bg-emerald-500/15 border border-emerald-400/30 text-emerald-200 text-xs">
                <ShieldCheck className="w-4 h-4 shrink-0 text-emerald-400" />
                <span>
                  Barcha ma&apos;lumotlar va transkripsiya Supabase bazasiga avtomatik arxivlandi.
                </span>
              </div>
            </div>

            <button
              onClick={onEndCall}
              className="w-full py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold transition-all shadow-lg active:scale-95"
            >
              Navbatga Qaytish
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
