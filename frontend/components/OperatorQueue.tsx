'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Headset, PhoneIncoming, AlertTriangle, CheckCircle, Clock,
  Send, User, Sparkles, Filter, RefreshCw, MessageSquare, ShieldCheck,
  Check, PhoneForwarded, Zap, Pause
} from 'lucide-react';
import { CallRecord, Message, OperatorRecord } from '@/lib/types';
import {
  fetchCalls, fetchOperators, operatorTakeover, operatorSendMessage, completeCall,
  getOperatorWebSocketUrl
} from '@/lib/api';
import { useRole } from '@/lib/useRole';
import OperatorLiveCall from '@/components/OperatorLiveCall';

interface AutoConnectState {
  active: boolean;
  nextCallId: string;
  citizenName: string;
  topic?: string;
  remainingSeconds: number;
  progressPercent: number;
}

export default function OperatorQueue() {
  const { session } = useRole();
  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [operators, setOperators] = useState<OperatorRecord[]>([]);
  const [selectedCallId, setSelectedCallId] = useState<string | null>(null);
  const [activeLiveCall, setActiveLiveCall] = useState<CallRecord | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  // 3-second auto-connect countdown state
  const [autoConnect, setAutoConnect] = useState<AutoConnectState>({
    active: false,
    nextCallId: '',
    citizenName: '',
    topic: '',
    remainingSeconds: 3,
    progressPercent: 100,
  });

  const activeOperatorName = session.operatorName || 'Nargiza Qodirova (Operator #1)';

  const wsRef = useRef<WebSocket | null>(null);
  const selectedCall = calls.find((c) => c.id === selectedCallId) || calls[0] || null;

  const startCountdown = (nextCallId: string, citizenName: string, topic?: string) => {
    setAutoConnect({
      active: true,
      nextCallId,
      citizenName,
      topic: topic || 'Umumiy Murojaat',
      remainingSeconds: 3,
      progressPercent: 100,
    });
  };

  const cancelCountdown = () => {
    setAutoConnect((prev) => ({ ...prev, active: false }));
  };

  const instantConnect = async (callIdToConnect?: string) => {
    const targetCallId = callIdToConnect || autoConnect.nextCallId;
    cancelCountdown();
    if (targetCallId) {
      await handleTakeover(targetCallId);
      setSelectedCallId(targetCallId);
    }
  };

  // Countdown timer effect
  useEffect(() => {
    if (!autoConnect.active) return;

    const startTime = Date.now();
    const durationMs = 3000;

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const remainingMs = Math.max(0, durationMs - elapsed);
      const remainingSecs = Math.ceil(remainingMs / 1000);
      const progress = (remainingMs / durationMs) * 100;

      setAutoConnect((prev) => ({
        ...prev,
        remainingSeconds: remainingSecs,
        progressPercent: progress,
      }));

      if (remainingMs <= 0) {
        clearInterval(interval);
        instantConnect(autoConnect.nextCallId);
      }
    }, 50);

    return () => clearInterval(interval);
  }, [autoConnect.active, autoConnect.nextCallId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [callsData, opsData] = await Promise.all([
        fetchCalls(),
        fetchOperators().catch(() => []),
      ]);
      setCalls(callsData);
      setOperators(opsData);
      if (callsData.length > 0 && !selectedCallId) {
        setSelectedCallId(callsData[0].id);
      }
    } catch (e) {
      console.error('Failed to load operator queue data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    // Connect to operator WebSocket
    try {
      const wsUrl = getOperatorWebSocketUrl();
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'initial_state') {
            setCalls(data.calls);
            if (data.calls.length > 0 && !selectedCallId) {
              setSelectedCallId(data.calls[0].id);
            }
          } else if (data.type === 'call_updated') {
            const updated: CallRecord = data.call;
            setCalls((prev) => {
              const idx = prev.findIndex((c) => c.id === updated.id);
              if (idx >= 0) {
                const next = [...prev];
                next[idx] = updated;
                return next;
              }
              return [updated, ...prev];
            });
            fetchOperators().then(setOperators).catch(() => {});
          } else if (data.type === 'queue_update' || data.type === 'operator_assigned') {
            fetchCalls().then(setCalls).catch(() => {});
            fetchOperators().then(setOperators).catch(() => {});
          } else if (data.type === 'next_call_countdown') {
            startCountdown(data.next_call_id, data.caller_name || 'Fuqaro', data.topic);
          }
        } catch (e) {
          console.error('[Operator WS Parse Error]:', e);
        }
      };

      wsRef.current = ws;

      return () => {
        ws.close();
      };
    } catch (e) {
      console.error('[Operator WS Connect Error]:', e);
    }
  }, []);

  const handleTakeover = async (callId: string) => {
    try {
      const updated = await operatorTakeover(callId, activeOperatorName);
      setCalls((prev) => prev.map((c) => (c.id === callId ? updated : c)));
      setSelectedCallId(callId);
      setActiveLiveCall(updated);
      fetchOperators().then(setOperators).catch(() => {});
    } catch (e) {
      console.error('Takeover failed:', e);
      const fallbackCall = calls.find((c) => c.id === callId);
      if (fallbackCall) {
        setActiveLiveCall(fallbackCall);
      }
    }
  };

  const handleCompleteCall = async (callId: string) => {
    try {
      const updated = await completeCall(callId, 'Operator tomonidan muammo to\'liq hal etildi.');
      setCalls((prev) => prev.map((c) => (c.id === callId ? updated : c)));
      const [freshCalls, freshOps] = await Promise.all([fetchCalls(), fetchOperators()]);
      setCalls(freshCalls);
      setOperators(freshOps);

      // Check for queued callers to auto-connect in 3 seconds
      const nextQueued = freshCalls.find((c) => c.status === 'waiting_operator');
      if (nextQueued) {
        startCountdown(nextQueued.id, nextQueued.citizen_name, nextQueued.primary_topic);
      }
    } catch (e) {
      console.error('Complete failed:', e);
    }
  };

  const filteredCalls = calls.filter((c) => {
    if (statusFilter === 'all') return true;
    if (statusFilter === 'my_calls') return c.assigned_operator === activeOperatorName;
    return c.status === statusFilter;
  });

  const waitingCount = calls.filter((c) => c.status === 'waiting_operator').length;
  const myActiveCallsCount = calls.filter((c) => c.status === 'operator_handling' && c.assigned_operator === activeOperatorName).length;

  // 100vh Full-Screen Live Call Mode
  if (activeLiveCall) {
    return (
      <OperatorLiveCall
        callId={activeLiveCall.id}
        citizenName={activeLiveCall.citizen_name || 'Fuqaro'}
        citizenPhone={activeLiveCall.citizen_phone || '+998 (90) 000-00-00'}
        topic={activeLiveCall.primary_topic || 'Umumiy Murojaat'}
        operatorName={activeOperatorName}
        onEndCall={() => {
          setActiveLiveCall(null);
          loadData();
        }}
      />
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Active Operator Status & Multi-Operator Fleet Bar */}
      <div className="bg-slate-900 border border-slate-800 text-white rounded-2xl p-4 sm:p-5 shadow-lg">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center space-x-3.5">
            <div className="w-12 h-12 rounded-xl bg-blue-500/20 border border-blue-500/30 text-blue-400 flex items-center justify-center font-bold text-lg">
              <Headset className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-bold text-base text-white">{activeOperatorName}</h3>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1 animate-pulse" />
                  Onlayn (Ishchi o&apos;rin)
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Ta&apos;lim va Innovatsiyalar Vazirligi Call-Markazi • Faol muloqotlar: <strong className="text-white">{myActiveCallsCount}</strong> ta
              </p>
            </div>
          </div>

          {/* Fleet Status Avatars */}
          <div className="flex items-center gap-3 bg-slate-950/60 p-2.5 rounded-xl border border-slate-800 overflow-x-auto">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider shrink-0">
              Operatorlar Holati:
            </span>
            {operators.length > 0 ? (
              operators.map((op) => (
                <div
                  key={op.id}
                  className={`flex items-center space-x-2 px-2.5 py-1 rounded-lg border text-xs shrink-0 ${
                    op.status === 'busy'
                      ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                      : op.status === 'online'
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                      : 'bg-slate-800 border-slate-700 text-slate-400'
                  }`}
                >
                  <span
                    className={`w-2 h-2 rounded-full ${
                      op.status === 'busy'
                        ? 'bg-amber-400 animate-pulse'
                        : op.status === 'online'
                        ? 'bg-emerald-400'
                        : 'bg-slate-500'
                    }`}
                  />
                  <span className="font-medium">{op.name.split(' ')[0]}</span>
                  <span className="text-[10px] opacity-70">({op.status === 'busy' ? 'Band' : 'Bo\'sh'})</span>
                </div>
              ))
            ) : (
              <span className="text-xs text-slate-500">Operatorlar yuklanmoqda...</span>
            )}
          </div>
        </div>
      </div>

      {/* 3-Second Auto-Connect Countdown Bar */}
      {autoConnect.active && (
        <div className="bg-gradient-to-r from-blue-950 via-slate-900 to-[#081e38] border-2 border-amber-400 rounded-2xl p-4 sm:p-5 shadow-2xl text-white animate-in slide-in-from-top duration-300">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <div className="w-12 h-12 rounded-xl bg-amber-500/20 border border-amber-400 text-amber-300 flex items-center justify-center font-extrabold text-xl font-mono animate-pulse">
                {autoConnect.remainingSeconds}s
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm sm:text-base font-extrabold text-white">
                    Navbatdagi fuqaro 3 soniyada ulanadi ({autoConnect.remainingSeconds}.. {autoConnect.remainingSeconds > 1 ? autoConnect.remainingSeconds - 1 + '.. ' : ''}1..)
                  </span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-400 text-slate-950">
                    FIFO Avto-Ulanish
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-0.5">
                  Fuqaro: <strong className="text-amber-300">{autoConnect.citizenName}</strong>
                  {autoConnect.topic && (
                    <> • Mavzu: <strong className="text-emerald-300">{autoConnect.topic}</strong></>
                  )}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2.5 shrink-0">
              <button
                onClick={() => instantConnect(autoConnect.nextCallId)}
                className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 transition-all active:scale-95"
              >
                <Zap className="w-4 h-4" />
                <span>Zudlik bilan boshlash</span>
              </button>

              <button
                onClick={cancelCountdown}
                className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 font-semibold text-xs transition-all active:scale-95"
              >
                <Pause className="w-3.5 h-3.5" />
                <span>Tanaffus / Bekor</span>
              </button>
            </div>
          </div>

          {/* Animated Progress Bar */}
          <div className="mt-3.5 w-full bg-slate-800/80 rounded-full h-2.5 overflow-hidden border border-white/10">
            <div
              className="bg-gradient-to-r from-amber-400 via-emerald-400 to-emerald-500 h-full rounded-full transition-all duration-75 ease-linear"
              style={{ width: `${autoConnect.progressPercent}%` }}
            />
          </div>
        </div>
      )}

      {/* Top Banner Alert if calls are waiting */}
      {waitingCount > 0 && (
        <div className="bg-amber-50 border border-amber-300 rounded-2xl p-4 flex items-center justify-between shadow-sm animate-pulse">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-amber-500 text-white flex items-center justify-center font-bold">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-sm text-amber-900">
                Operator Diqqatiga: {waitingCount} ta fuqaro jonli navbatda kutmoqda!
              </h4>
              <p className="text-xs text-amber-700">
                AI murakkab yoki shikoyat arizalarini zudlik bilan inson-operator ko&apos;rigiga yo&apos;naltirdi.
              </p>
            </div>
          </div>
          <button
            onClick={() => setStatusFilter('waiting_operator')}
            className="px-3.5 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold transition-all shadow-sm"
          >
            Navbatni Ko&apos;rish
          </button>
        </div>
      )}

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Queue List (5 cols) */}
        <div className="lg:col-span-5 flex flex-col bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden h-[720px]">
          {/* Queue Header & Filters */}
          <div className="p-4 border-b border-slate-200 bg-slate-50/70">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Headset className="w-5 h-5 text-[#0b2b50]" />
                <h3 className="font-bold text-sm text-slate-800">Jonli Qo&apos;ng&apos;iroqlar Navbati</h3>
              </div>
              <button
                onClick={loadData}
                className="p-1.5 rounded-lg hover:bg-slate-200 text-slate-500 transition-colors"
                title="Yangilash"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            {/* Filter Tabs */}
            <div className="grid grid-cols-4 gap-1 p-1 bg-slate-200/70 rounded-xl text-[11px] font-semibold">
              <button
                onClick={() => setStatusFilter('all')}
                className={`py-1.5 rounded-lg transition-all ${
                  statusFilter === 'all'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Barchasi ({calls.length})
              </button>
              <button
                onClick={() => setStatusFilter('waiting_operator')}
                className={`py-1.5 rounded-lg transition-all ${
                  statusFilter === 'waiting_operator'
                    ? 'bg-amber-500 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Kutayotgan ({waitingCount})
              </button>
              <button
                onClick={() => setStatusFilter('my_calls')}
                className={`py-1.5 rounded-lg transition-all ${
                  statusFilter === 'my_calls'
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Mening ({myActiveCallsCount})
              </button>
              <button
                onClick={() => setStatusFilter('completed')}
                className={`py-1.5 rounded-lg transition-all ${
                  statusFilter === 'completed'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Tugatilgan
              </button>
            </div>
          </div>

          {/* List of Calls */}
          <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
            {filteredCalls.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-xs">
                Ushbu mezon bo&apos;yicha qo&apos;ng&apos;iroq topilmadi.
              </div>
            ) : (
              filteredCalls.map((call) => {
                const isSelected = selectedCall?.id === call.id;
                const isWaiting = call.status === 'waiting_operator';
                const isOperator = call.status === 'operator_handling';

                return (
                  <div
                    key={call.id}
                    onClick={() => setSelectedCallId(call.id)}
                    className={`p-4 cursor-pointer transition-all border-l-4 ${
                      isSelected
                        ? 'bg-blue-50/70 border-[#0b2b50]'
                        : isWaiting
                        ? 'bg-amber-50/50 border-amber-500 hover:bg-amber-50'
                        : 'border-transparent hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xs text-slate-900">{call.citizen_name}</span>
                        <span className="text-[10px] text-slate-400">{call.citizen_phone}</span>
                      </div>
                      <span
                        className={`text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                          isWaiting
                            ? 'bg-amber-100 text-amber-800 animate-pulse'
                            : isOperator
                            ? 'bg-blue-100 text-blue-800'
                            : call.status === 'completed'
                            ? 'bg-slate-100 text-slate-600'
                            : 'bg-emerald-100 text-emerald-800'
                        }`}
                      >
                        {isWaiting
                          ? `Kutmoqda (#${call.queue_position || 1})`
                          : isOperator
                          ? (call.assigned_operator ? call.assigned_operator.split(' ')[0] : 'Operator')
                          : call.status === 'completed'
                          ? 'Tugatildi'
                          : 'AI xizmati'}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-slate-500">
                      <span className="font-medium text-slate-700 truncate max-w-[200px]">
                        {call.primary_topic}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <Clock className="w-3 h-3 text-slate-400" />
                        <span>{call.duration_seconds} soniya</span>
                      </div>
                    </div>

                    {/* Sentiment & Quick Takeover */}
                    <div className="mt-2 flex items-center justify-between">
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                          call.overall_sentiment === 'Ijobiy'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : call.overall_sentiment === 'Salbiy'
                            ? 'bg-rose-50 text-rose-700 border border-rose-200'
                            : 'bg-slate-50 text-slate-600 border border-slate-200'
                        }`}
                      >
                        Kayfiyat: {call.overall_sentiment}
                      </span>

                      {isWaiting && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleTakeover(call.id);
                          }}
                          className="px-2.5 py-1 bg-amber-600 hover:bg-amber-700 text-white text-[10px] font-bold rounded-lg shadow-xs flex items-center gap-1"
                        >
                          <PhoneForwarded className="w-3 h-3" />
                          <span>Qabul qilish</span>
                        </button>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right: Selected Call Detail & Interaction Monitor (7 cols) */}
        <div className="lg:col-span-7 flex flex-col bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden h-[720px]">
          {selectedCall ? (
            <>
              {/* Selected Call Header */}
              <div className="p-4 border-b border-slate-200 bg-slate-50/80 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-sm text-slate-900">{selectedCall.citizen_name}</h3>
                    <span className="text-xs text-slate-500 font-mono">{selectedCall.citizen_phone}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        selectedCall.overall_sentiment === 'Ijobiy'
                          ? 'bg-emerald-100 text-emerald-800'
                          : selectedCall.overall_sentiment === 'Salbiy'
                          ? 'bg-rose-100 text-rose-800'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {selectedCall.overall_sentiment}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Mavzu: <strong className="text-slate-700">{selectedCall.primary_topic}</strong> • Boshlangan:{' '}
                    {new Date(selectedCall.started_at).toLocaleTimeString('uz-UZ')}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  {selectedCall.status !== 'completed' && (
                    <>
                      {selectedCall.status !== 'operator_handling' && (
                        <button
                          onClick={() => handleTakeover(selectedCall.id)}
                          className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0b2b50] hover:bg-blue-900 text-white rounded-xl text-xs font-bold shadow-sm"
                        >
                          <Headset className="w-3.5 h-3.5" />
                          <span>Menga Olish</span>
                        </button>
                      )}
                      <button
                        onClick={() => handleCompleteCall(selectedCall.id)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-sm"
                        title="Yakunlash va navbatdagi fuqaroni avtomatik qabul qilish"
                      >
                        <CheckCircle className="w-3.5 h-3.5" />
                        <span>Yakunlash & Keyingisi</span>
                      </button>
                    </>
                  )}
                </div>
              </div>

              {/* Live Transcript Body */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-slate-50/40">
                {selectedCall.messages.map((m, idx) => (
                  <div
                    key={m.id || idx}
                    className={`flex flex-col ${
                      m.role === 'citizen'
                        ? 'items-start'
                        : m.role === 'operator'
                        ? 'items-end'
                        : 'items-start'
                    }`}
                  >
                    <div className="flex items-center gap-1.5 text-[10px] text-slate-400 mb-1 px-1">
                      <span className="font-bold text-slate-600">
                        {m.role === 'citizen'
                          ? selectedCall.citizen_name
                          : m.role === 'operator'
                          ? `Operator (${selectedCall.assigned_operator || 'Siz'})`
                          : 'SözLab AI'}
                      </span>

                      <span>•</span>
                      <span>{new Date(m.timestamp).toLocaleTimeString('uz-UZ')}</span>
                    </div>
                    <div
                      className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed ${
                        m.role === 'citizen'
                          ? 'bg-white border border-slate-200 text-slate-900 shadow-xs'
                          : m.role === 'operator'
                          ? 'bg-amber-100/90 text-amber-950 border border-amber-300 shadow-xs font-medium'
                          : 'bg-blue-50 text-blue-950 border border-blue-200 shadow-xs'
                      }`}
                    >
                      {m.text}
                    </div>
                  </div>
                ))}
              </div>

              {/* Zero-Chatbot Live Audio Call Action Dock */}
              <div className="p-4 bg-slate-900 text-white border-t border-slate-200 flex items-center justify-between gap-4">
                <div className="flex items-center gap-2 text-xs text-slate-300">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span>
                    <strong>Zero-Chatbot:</strong> Matnli chat olib tashlangan. Barcha muloqot to&apos;liq jonli ovoz (100vh WebRTC) orqali amalga oshiriladi.
                  </span>
                </div>

                {selectedCall.status !== 'completed' ? (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleTakeover(selectedCall.id)}
                      className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg flex items-center gap-2 active:scale-95 transition-all"
                    >
                      <Headset className="w-4 h-4" />
                      <span>Jonli Ovozli Muloqotni Boshlash (100vh)</span>
                    </button>
                    <button
                      onClick={() => handleCompleteCall(selectedCall.id)}
                      className="px-3.5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md active:scale-95 transition-all"
                    >
                      Yakunlash
                    </button>
                  </div>
                ) : (
                  <span className="text-xs text-slate-400 italic">Qo&apos;ng&apos;iroq yakunlangan</span>
                )}
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 text-xs">
              Chap tomondagi navbatdan qo&apos;ng&apos;iroqni tanlang.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
