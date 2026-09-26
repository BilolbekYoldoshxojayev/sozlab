'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Headset, Mic, MicOff, PhoneOff, PhoneCall, Volume2, VolumeX,
  Clock, CheckCircle2, UserCheck, RefreshCw, Send, Play
} from 'lucide-react';
import { CallRecord, Message } from '@/lib/types';
import {
  fetchCalls, completeCall, operatorTakeover, operatorSendMessage,
  getAudioFullUrl, getCallWebSocketUrl, getOperatorWebSocketUrl
} from '@/lib/api';
import RoleProtectedPage from '@/components/RoleProtectedPage';

export default function OperatorConsolePage() {
  const [operatorStatus, setOperatorStatus] = useState<'online' | 'busy'>('online');
  const [operatorName, setOperatorName] = useState('Dilnoza Xasanova');

  const [queuedCalls, setQueuedCalls] = useState<CallRecord[]>([]);
  const [activeCall, setActiveCall] = useState<CallRecord | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [callDuration, setCallDuration] = useState(0);

  const [isMuted, setIsMuted] = useState(false);
  const [customText, setCustomText] = useState('');
  const [loading, setLoading] = useState(false);

  const [incomingCall, setIncomingCall] = useState<CallRecord | null>(null);
  const [countdown, setCountdown] = useState<number | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const operatorWsRef = useRef<WebSocket | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const loadQueue = async () => {
    try {
      setLoading(true);
      const allCalls = await fetchCalls();
      const waiting = allCalls.filter((c) => c.status === 'waiting_operator');
      setQueuedCalls(waiting);

      if (operatorStatus === 'online' && !activeCall && !incomingCall && waiting.length > 0) {
        triggerIncomingCountdown(waiting[0]);
      }
    } catch (e) {
      console.error('Failed to load queue:', e);
    } finally {
      setLoading(false);
    }

  };

  useEffect(() => {
    loadQueue();
    const interval = setInterval(loadQueue, 4000);
    return () => clearInterval(interval);
  }, [operatorStatus, activeCall, incomingCall]);

  useEffect(() => {
    try {
      const wsUrl = getOperatorWebSocketUrl();
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'call_requested' || data.type === 'new_waiting_call') {
            loadQueue();
          }
        } catch {}
      };

      operatorWsRef.current = ws;
      return () => ws.close();
    } catch {}
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout | undefined;
    if (activeCall && activeCall.status === 'operator_handling') {
      interval = setInterval(() => {
        setCallDuration((prev) => prev + 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [activeCall]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (!activeCall) return;

    try {
      const wsUrl = getCallWebSocketUrl(activeCall.id);
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'new_message' || data.type === 'ghost_message') {
            const msg: Message = data.message || {
              id: `msg-${Date.now()}`,
              role: data.role || 'citizen',
              text: data.text || '',
              timestamp: data.timestamp || new Date().toISOString(),
              audio_url: data.audio_url,
            };

            setMessages((prev) => {
              if (prev.some((m) => m.id === msg.id)) return prev;
              return [...prev, msg];
            });

            if (msg.audio_url && !isMuted && audioRef.current) {
              audioRef.current.src = getAudioFullUrl(msg.audio_url);
              audioRef.current.play().catch(() => {});
            }
          } else if (data.type === 'call_completed') {
            handleCallEnded();
          }
        } catch {}
      };

      wsRef.current = ws;
      return () => ws.close();
    } catch {}
  }, [activeCall?.id, isMuted]);

  const triggerIncomingCountdown = (call: CallRecord) => {
    setIncomingCall(call);
    setCountdown(3);
  };

  useEffect(() => {
    if (countdown === null) return;

    if (countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown((prev) => (prev !== null ? prev - 1 : null));
      }, 1000);
      return () => clearTimeout(timer);
    }

    if (countdown === 0 && incomingCall) {
      connectToCall(incomingCall);
      setIncomingCall(null);
      setCountdown(null);
    }
  }, [countdown, incomingCall]);

  const connectToCall = async (call: CallRecord) => {
    try {
      setOperatorStatus('busy');
      const updated = await operatorTakeover(call.id, operatorName);
      setActiveCall(updated);
      setMessages(updated.messages || []);
      setCallDuration(0);
      setQueuedCalls((prev) => prev.filter((c) => c.id !== call.id));
    } catch {
      setOperatorStatus('busy');
      const updatedCall: CallRecord = {
        ...call,
        status: 'operator_handling',
        assigned_operator: operatorName,
      };
      setActiveCall(updatedCall);
      setMessages(call.messages || []);
      setCallDuration(0);
    }
  };

  const handleEndCall = async () => {
    if (!activeCall) return;
    try {
      await completeCall(activeCall.id, "Muloqot inson operatori tomonidan yakunlandi.");
    } catch {}
    handleCallEnded();
  };

  const handleCallEnded = () => {
    setActiveCall(null);
    setMessages([]);
    setCallDuration(0);
    setOperatorStatus('online');
    loadQueue();
  };

  const handleSendMessage = async () => {
    if (!activeCall || !customText.trim()) return;
    const text = customText.trim();
    setCustomText('');

    const newMsg: Message = {
      id: `op-${Date.now()}`,
      role: 'operator',
      text,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newMsg]);

    try {
      await operatorSendMessage(activeCall.id, text, operatorName);
    } catch {}
  };

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const s = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <RoleProtectedPage allowedRoles={['operator', 'admin']}>
      <div className="space-y-6">
        <audio ref={audioRef} autoPlay className="hidden" />

        <div
          className="p-6 rounded-2xl border shadow-xl flex flex-col md:flex-row md:items-center md:justify-between gap-6 transition-colors"
          style={{ backgroundColor: '#0A0F1D', borderColor: '#1E3A5F' }}
        >
          <div>
            <div className="flex items-center space-x-2 text-blue-400 text-xs font-bold uppercase tracking-wider mb-2">
              <Headset className="w-4 h-4" />
              <span>Inson Operator Konsoli • SözLab 1006 / 1007</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              Operator Boshqaruv Markazi
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Operator: <strong className="text-white font-semibold">{operatorName}</strong>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-400">Holatingiz:</span>
            <button
              onClick={() => setOperatorStatus(operatorStatus === 'online' ? 'busy' : 'online')}
              className={`px-4 py-2.5 rounded-xl font-bold text-xs border flex items-center gap-2.5 transition active:scale-95 shadow-md ${
                operatorStatus === 'online'
                  ? 'bg-blue-600 hover:bg-blue-500 border-blue-400 text-white'
                  : 'bg-slate-800 hover:bg-slate-700 border-slate-600 text-slate-300'
              }`}
            >
              <span className={`w-2.5 h-2.5 rounded-full ${operatorStatus === 'online' ? 'bg-white animate-pulse' : 'bg-slate-500'}`} />
              <span>{operatorStatus === 'online' ? "Bo'sh (Qabul qilishga tayyor)" : 'Band'}</span>
            </button>

            <button
              onClick={loadQueue}
              className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition"
              title="Navbatni yangilash"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-5 rounded-2xl border shadow-sm p-6 flex flex-col justify-between transition-colors" style={{ backgroundColor: '#0F172A', borderColor: '#1E293B' }}>
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-[#1E3A5F] mb-4">
                <div className="flex items-center space-x-2">
                  <Clock className="w-5 h-5 text-blue-400" />
                  <h3 className="font-bold text-base text-white">Navbatdagi Fuqarolar (FIFO Queue)</h3>
                </div>
                <span className="text-xs font-bold text-blue-300 bg-blue-950/80 px-2.5 py-0.5 rounded-full border border-blue-800">
                  {queuedCalls.length} ta fuqaro
                </span>
              </div>

              {queuedCalls.length === 0 ? (
                <div className="py-16 text-center text-xs text-slate-400">
                  <CheckCircle2 className="w-10 h-10 text-blue-400 mx-auto mb-2 opacity-60" />
                  <p className="font-semibold text-sm text-slate-200">Hozirda navbatda fuqarolar yo&apos;q</p>
                  <p className="text-[11px] mt-1 text-slate-400">Barcha murojaatlar avtonom AI tomonidan hal qilinmoqda.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {queuedCalls.map((call, idx) => (
                    <div key={call.id} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-blue-500/50 transition flex items-center justify-between group">
                      <div className="flex items-center space-x-3">
                        <div className="w-9 h-9 rounded-xl bg-blue-600 text-white font-mono font-extrabold text-xs flex items-center justify-center shadow-md">
                          #{idx + 1}
                        </div>
                        <div>
                          <div className="font-bold text-xs text-white group-hover:text-blue-300 transition">{call.citizen_name}</div>
                          <div className="text-[11px] text-slate-400 font-mono">{call.citizen_phone}</div>
                          <span className="inline-block text-[10px] text-blue-300 bg-blue-950/60 border border-blue-800 px-1.5 py-0.2 rounded mt-0.5">{call.primary_topic}</span>
                        </div>
                      </div>

                      <button
                        onClick={() => triggerIncomingCountdown(call)}
                        disabled={operatorStatus === 'busy' || !!activeCall}
                        className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white font-bold text-xs flex items-center gap-1 transition active:scale-95 shadow-xs"
                      >
                        <Play className="w-3 h-3 fill-current" />
                        <span>Qabul qilish</span>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-[#1E3A5F] text-[11px] text-slate-400 flex items-center justify-between">
              <span>Navbat tartibi: <strong>FIFO (First-In, First-Out)</strong></span>
              <span className="text-blue-400">Avto-ulanish faol</span>
            </div>
          </div>

          <div className="lg:col-span-7 rounded-2xl border shadow-sm p-6 flex flex-col justify-between transition-colors min-h-[500px]" style={{ backgroundColor: '#0F172A', borderColor: '#1E293B' }}>
            {!activeCall ? (
              <div className="my-auto text-center py-16 text-slate-400">
                <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 mx-auto flex items-center justify-center text-slate-300 mb-4">
                  <UserCheck className="w-8 h-8 text-blue-400" />
                </div>
                <h3 className="text-lg font-bold text-white mb-1">Jonli Qo&apos;ng&apos;iroq Boshqaruvi</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto">
                  Operator holatini &quot;Bo&apos;sh&quot; qilib belgilang yoki navbatdan qo&apos;ng&apos;iroqni qabul qiling.
                </p>
              </div>
            ) : (
              <div className="flex flex-col h-full justify-between space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-[#1E3A5F]">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 rounded-full bg-blue-400 animate-pulse" />
                    <div>
                      <div className="font-extrabold text-sm text-white">{activeCall.citizen_name} ({activeCall.citizen_phone})</div>
                      <div className="text-[11px] text-blue-300 font-mono">Jonli Muloqot Rejimi • Mavzu: {activeCall.primary_topic}</div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-slate-200">⏱️ {formatTime(callDuration)}</div>
                    <button
                      onClick={() => setIsMuted(!isMuted)}
                      className={`p-2 rounded-lg border transition ${isMuted ? 'bg-slate-800 border-slate-700 text-slate-400' : 'bg-blue-900/60 border-blue-500 text-white'}`}
                      title={isMuted ? "Mikrofonni yoqish" : "Mikrofonni o'chirish"}
                    >
                      {isMuted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 flex items-center justify-center gap-1.5 h-16">
                  {[40, 70, 30, 85, 60, 95, 45, 80, 55, 90, 35, 65, 75, 40, 80, 60, 90, 45].map((h, i) => (
                    <div
                      key={i}
                      className="w-1.5 bg-blue-500 rounded-full transition-all duration-300 animate-pulse"
                      style={{
                        height: `${isMuted ? 10 : Math.max(15, (h + Math.sin(Date.now() / 200 + i) * 30))}%`,
                        opacity: isMuted ? 0.3 : 0.9,
                      }}
                    />
                  ))}
                </div>

                <div className="flex-1 min-h-[220px] max-h-[280px] overflow-y-auto bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3 font-sans text-xs">
                  {messages.length === 0 ? (
                    <div className="text-center py-8 text-slate-500 italic">Transkripsiya stream jarayoni kutilmoqda...</div>
                  ) : (
                    messages.map((m) => (
                      <div
                        key={m.id}
                        className={`flex flex-col gap-1 p-2.5 rounded-lg border ${
                          m.role === 'citizen' ? 'bg-slate-900/90 border-slate-800 text-slate-100' : m.role === 'operator' ? 'bg-blue-950/60 border-blue-800/80 text-blue-100 ml-4' : 'bg-slate-950 border-slate-800 text-slate-300'
                        }`}
                      >
                        <div className="flex items-center justify-between text-[10px]">
                          <span className="font-bold uppercase tracking-wider text-blue-300">
                            {m.role === 'citizen' ? activeCall.citizen_name : m.role === 'operator' ? operatorName : 'SözLab AI'}
                          </span>
                          <span className="text-slate-500 font-mono">{new Date(m.timestamp).toLocaleTimeString('uz-UZ')}</span>
                        </div>
                        <p className="text-xs leading-relaxed">{m.text}</p>
                      </div>
                    ))
                  )}
                  <div ref={messagesEndRef} />
                </div>

                <div className="space-y-3 pt-2">
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={customText}
                      onChange={(e) => setCustomText(e.target.value)}
                      onKeyDown={(e) => { if (e.key === 'Enter') handleSendMessage(); }}
                      placeholder="Fuqaroga matnli xabar yoki javob yo'llash..."
                      className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                    />
                    <button onClick={handleSendMessage} className="px-3.5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition active:scale-95">
                      <Send className="w-4 h-4" />
                    </button>
                  </div>

                  <button
                    onClick={handleEndCall}
                    className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-extrabold text-xs flex items-center justify-center gap-2 shadow-lg transition active:scale-98"
                  >
                    <PhoneOff className="w-4 h-4" />
                    <span>Qo&apos;ng&apos;iroqni Yakunlash</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {countdown !== null && incomingCall && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in">
            <div className="w-full max-w-md bg-slate-950 border-2 border-blue-500 rounded-3xl p-7 shadow-2xl text-center text-white space-y-5 animate-in zoom-in-95 duration-200">
              <div className="relative w-24 h-24 mx-auto flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="48" cy="48" r="40" stroke="#1E293B" strokeWidth="6" fill="transparent" />
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="#2563EB"
                    strokeWidth="6"
                    fill="transparent"
                    strokeDasharray={251.2}
                    strokeDashoffset={(251.2 * (3 - countdown)) / 3}
                    className="transition-all duration-1000 ease-linear"
                  />
                </svg>
                <span className="absolute font-extrabold text-3xl font-mono text-blue-400">{countdown}</span>
              </div>

              <div>
                <span className="text-[10px] font-extrabold uppercase tracking-widest px-3 py-1 rounded-full bg-blue-950 border border-blue-800 text-blue-300">
                  Kiruvchi Murojaat
                </span>
                <h3 className="text-xl font-extrabold mt-3 text-white">{incomingCall.citizen_name}</h3>
                <p className="text-xs text-slate-400 font-mono mt-0.5">{incomingCall.citizen_phone}</p>
                <p className="text-xs font-semibold text-blue-300 mt-2">Mavzu: {incomingCall.primary_topic}</p>
              </div>

              <div className="p-3 bg-blue-950/60 border border-blue-800/80 rounded-xl text-xs text-blue-200 font-bold font-mono">
                Daqiqalar: {countdown}... Qo&apos;ng&apos;iroqga ulanmoqda!
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => { setIncomingCall(null); setCountdown(null); }}
                  className="flex-1 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold transition"
                >
                  Rad Etish
                </button>
                <button
                  onClick={() => { connectToCall(incomingCall); setIncomingCall(null); setCountdown(null); }}
                  className="flex-1 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition active:scale-95 shadow-md"
                >
                  Darhol Ulanish
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </RoleProtectedPage>
  );
}
