'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Shield, Users, PhoneCall, Headphones, Clock, CheckCircle2,
  AlertTriangle, RefreshCw, Database, Volume2, Sparkles, Plus,
  Layers, ArrowUpRight, Radio, Square
} from 'lucide-react';
import { CallRecord, OperatorRecord, AnalyticsSummary, KnowledgeItem } from '@/lib/types';
import {
  fetchCalls, fetchOperators, fetchAnalytics, fetchKnowledge,
  startNewCall, getAdminWebSocketUrl, getAudioFullUrl
} from '@/lib/api';

interface GhostTurn {
  id: string;
  role: string;
  speaker: string;
  text: string;
  timestamp: string;
  audio_url?: string;
}

export default function AdminPage() {
  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [operators, setOperators] = useState<OperatorRecord[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [knowledge, setKnowledge] = useState<KnowledgeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSimulating, setIsSimulating] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Ghost Mode State
  const [listeningCallId, setListeningCallId] = useState<string | null>(null);
  const [ghostMessages, setGhostMessages] = useState<GhostTurn[]>([]);
  const [isGhostWsConnected, setIsGhostWsConnected] = useState(false);

  const adminWsRef = useRef<WebSocket | null>(null);
  const adminAudioRef = useRef<HTMLAudioElement | null>(null);
  const teleprompterEndRef = useRef<HTMLDivElement | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [callsData, opsData, analyticsData, kbData] = await Promise.all([
        fetchCalls(),
        fetchOperators().catch(() => []),
        fetchAnalytics().catch(() => null),
        fetchKnowledge().catch(() => []),
      ]);
      setCalls(callsData);
      setOperators(opsData);
      setAnalytics(analyticsData);
      setKnowledge(kbData);
    } catch (e) {
      console.error('Failed to load admin data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // 5s polling for admin monitor
    return () => clearInterval(interval);
  }, []);

  // Teleprompter Auto-scroll
  useEffect(() => {
    teleprompterEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [ghostMessages]);

  // Clean up WebSocket and audio on unmount
  useEffect(() => {
    return () => {
      if (adminWsRef.current) {
        adminWsRef.current.close();
      }
      if (adminAudioRef.current) {
        adminAudioRef.current.pause();
      }
    };
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleSimulateCall = async () => {
    try {
      setIsSimulating(true);
      const names = ['Rustam Usmonov', 'Shahlo Nazarova', 'Akmal Zokirov', 'Nilufar Rahimova'];
      const randomName = names[Math.floor(Math.random() * names.length)];
      const randomPhone = `+998 (9${Math.floor(Math.random() * 9 + 1)}) ${Math.floor(Math.random() * 899 + 100)}-${Math.floor(Math.random() * 89 + 10)}-${Math.floor(Math.random() * 89 + 10)}`;
      await startNewCall(randomName, randomPhone);
      await loadData();
      showToast(`Yangi simulyatsiya qo'ng'irog'i qo'shildi: ${randomName}`);
    } catch (e) {
      console.error('Simulation failed:', e);
    } finally {
      setIsSimulating(false);
    }
  };

  const startListening = (call: CallRecord) => {
    // If already listening to this call, do nothing
    if (listeningCallId === call.id) return;

    // Stop existing audio and disconnect previous WS
    if (adminAudioRef.current) {
      adminAudioRef.current.pause();
      adminAudioRef.current.src = '';
    }
    if (adminWsRef.current) {
      try {
        adminWsRef.current.send(JSON.stringify({ action: 'unlisten', call_id: listeningCallId }));
      } catch {}
      adminWsRef.current.close();
    }

    setListeningCallId(call.id);

    // Seed existing messages
    setGhostMessages(
      (call.messages || []).map((m) => ({
        id: m.id,
        role: m.role,
        speaker:
          m.role === 'citizen'
            ? call.citizen_name
            : m.role === 'operator'
            ? call.assigned_operator || 'Operator'
            : 'SözLab AI',
        text: m.text,
        timestamp: m.timestamp,
        audio_url: m.audio_url,
      }))
    );

    // Connect to /ws/admin
    try {
      const wsUrl = getAdminWebSocketUrl();
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsGhostWsConnected(true);
        ws.send(
          JSON.stringify({
            action: 'silent_listen',
            call_id: call.id,
          })
        );
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (
            data.type === 'ghost_message' ||
            data.type === 'ghost_turn' ||
            data.type === 'new_message'
          ) {
            const role = data.role || data.message?.role || 'ai';
            const speaker =
              data.speaker ||
              (role === 'citizen'
                ? call.citizen_name
                : role === 'operator'
                ? call.assigned_operator || 'Operator'
                : 'SözLab AI');
            const text = data.text || data.message?.text || '';
            const audio_url = data.audio_url || data.message?.audio_url;

            if (text) {
              setGhostMessages((prev) => [
                ...prev,
                {
                  id: `ghost-${Date.now()}-${Math.random()}`,
                  role,
                  speaker,
                  text,
                  timestamp: data.timestamp || new Date().toISOString(),
                  audio_url,
                },
              ]);
            }

            // Play voice cleanly if audio_url is present
            if (audio_url && adminAudioRef.current) {
              adminAudioRef.current.src = getAudioFullUrl(audio_url);
              adminAudioRef.current.play().catch((err) => {
                console.warn('[Admin Ghost Audio autoplay restricted]:', err);
              });
            }
          } else if (data.type === 'call_ended' || data.type === 'call_completed') {
            showToast(`Kuzatilayotgan qo'ng'iroq (#${call.id.slice(0, 8)}) yakunlandi.`);
          }
        } catch (err) {
          console.error('[Ghost WS Parse Error]:', err);
        }
      };

      ws.onclose = () => setIsGhostWsConnected(false);
      ws.onerror = () => setIsGhostWsConnected(false);

      adminWsRef.current = ws;
    } catch (err) {
      console.error('[Ghost WS Connect Error]:', err);
    }
  };

  const stopListening = () => {
    if (adminWsRef.current) {
      try {
        adminWsRef.current.send(JSON.stringify({ action: 'unlisten', call_id: listeningCallId }));
      } catch {}
      adminWsRef.current.close();
    }
    if (adminAudioRef.current) {
      adminAudioRef.current.pause();
      adminAudioRef.current.src = '';
    }
    setListeningCallId(null);
    setIsGhostWsConnected(false);
  };

  const waitingCalls = calls.filter((c) => c.status === 'waiting_operator');
  const activeCalls = calls.filter(
    (c) => c.status === 'ai_handling' || c.status === 'operator_handling'
  );

  return (
    <div className="space-y-8">
      {/* Hidden audio element for Ghost Mode silent eavesdropping */}
      <audio ref={adminAudioRef} autoPlay className="hidden" />

      {/* Toast Alert */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 border border-emerald-500/40 text-white px-4 py-3 rounded-2xl shadow-2xl flex items-center space-x-2 text-xs animate-in fade-in slide-in-from-bottom duration-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 text-white p-6 sm:p-8 rounded-3xl border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div>
          <div className="flex items-center space-x-2.5 text-purple-400 text-xs font-bold uppercase tracking-wider mb-2">
            <Shield className="w-4 h-4" />
            <span>Markaziy Nazorat &amp; Boshqaruv</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Vazirlik Ma&apos;muri Boshqaruv Markazi
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl">
            Sun&apos;iy intellekt agentlari, navbatchi operatorlar xizmati, jonli FIFO navbat va normativ bilimlar bazasini real-vaqtda boshqarish.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={handleSimulateCall}
            disabled={isSimulating}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold shadow-lg shadow-purple-600/30 transition-all active:scale-95 disabled:opacity-50"
          >
            <Plus className="w-4 h-4" />
            <span>{isSimulating ? 'Simulyatsiya...' : 'Test Qo\'ng\'iroq Yaratish'}</span>
          </button>

          <button
            onClick={loadData}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
            title="Yangilash"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 font-medium">Jami Qo&apos;ng&apos;iroqlar</span>
            <div className="text-2xl font-bold text-slate-900 mt-1">{calls.length}</div>
            <span className="text-[10px] text-emerald-600 font-semibold">Bugungi murojaatlar</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center">
            <PhoneCall className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 font-medium">AI Muvaffaqiyat Ulushi</span>
            <div className="text-2xl font-bold text-emerald-600 mt-1">
              {analytics?.ai_resolved_percentage || 85}%
            </div>
            <span className="text-[10px] text-slate-400">Operatorga chiqmasdan hal etildi</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 font-medium">Kutayotgan Fuqarolar (Navbat)</span>
            <div className="text-2xl font-bold text-amber-600 mt-1">{waitingCalls.length}</div>
            <span className="text-[10px] text-amber-700 font-semibold">FIFO oqimida</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 font-medium">Faol Inson-Operatorlar</span>
            <div className="text-2xl font-bold text-purple-700 mt-1">{operators.length}</div>
            <span className="text-[10px] text-purple-600 font-semibold">Navbatchi mutaxassislar</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-purple-50 text-purple-700 flex items-center justify-center">
            <Headphones className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* ACTIVE CALLS LIVE MONITORING & GHOST MODE SECTION */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-100 gap-3">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-xl bg-purple-500/15 border border-purple-500/30 text-purple-700 flex items-center justify-center font-bold">
              <Headphones className="w-5 h-5 text-purple-700" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-base text-slate-900">
                  Jonli Muloqotlar Oqimi (Active Calls Live Table)
                </h3>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800">
                  {activeCalls.length} ta faol
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                AI va operatorlar orqali hozir ayni paytda o&apos;tkazilayotgan barcha jonli suhbatlar
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Real-vaqtli monitoring faol</span>
          </div>
        </div>

        {/* Active Calls Table */}
        {activeCalls.length === 0 ? (
          <div className="py-10 text-center text-slate-400 text-xs">
            <PhoneCall className="w-10 h-10 text-slate-300 mx-auto mb-2 opacity-60" />
            <p className="font-semibold text-slate-700 text-sm">Hozirda jonli davom etayotgan qo&apos;ng&apos;iroq yo&apos;q</p>
            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
              Fuqaro &quot;/call&quot; sahifasidan qo&apos;ng&apos;iroq boshlaganda yoki yuqoridagi &quot;Test Qo&apos;ng&apos;iroq Yaratish&quot; tugmasini bosganingizda ushbu jadvalda paydo bo&apos;ladi.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] border-y border-slate-200">
                <tr>
                  <th className="py-3 px-4">Fuqaro (Murojaatchi)</th>
                  <th className="py-3 px-4">Joriy Holat</th>
                  <th className="py-3 px-4">Asosiy Mavzu</th>
                  <th className="py-3 px-4">Davomiyligi</th>
                  <th className="py-3 px-4 text-right">Ghost Mode (Jonli Eshitish)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {activeCalls.map((call) => {
                  const isListening = listeningCallId === call.id;
                  return (
                    <tr
                      key={call.id}
                      className={`hover:bg-slate-50/80 transition-colors ${
                        isListening ? 'bg-purple-50/60' : ''
                      }`}
                    >
                      <td className="py-3.5 px-4">
                        <div className="font-bold text-slate-900">{call.citizen_name}</div>
                        <div className="text-[11px] text-slate-400 font-mono">{call.citizen_phone}</div>
                      </td>

                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold ${
                            call.status === 'ai_handling'
                              ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                              : 'bg-blue-100 text-blue-800 border border-blue-200'
                          }`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              call.status === 'ai_handling' ? 'bg-emerald-500 animate-pulse' : 'bg-blue-500'
                            }`}
                          />
                          {call.status === 'ai_handling'
                            ? 'AI bilan muloqotda'
                            : `Operator: ${call.assigned_operator || 'Faol'}`}
                        </span>
                      </td>

                      <td className="py-3.5 px-4 text-slate-700 font-medium">
                        {call.primary_topic}
                      </td>

                      <td className="py-3.5 px-4 font-mono text-slate-600">
                        {Math.floor(call.duration_seconds / 60)}:{(call.duration_seconds % 60).toString().padStart(2, '0')}
                      </td>

                      <td className="py-3.5 px-4 text-right">
                        {isListening ? (
                          <button
                            onClick={stopListening}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-md shadow-rose-600/30 transition-all active:scale-95 animate-pulse"
                          >
                            <Square className="w-3.5 h-3.5" />
                            <span>⏹️ Tinglashni To&apos;xtatish</span>
                          </button>
                        ) : (
                          <button
                            onClick={() => startListening(call)}
                            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs shadow-md shadow-purple-600/25 transition-all active:scale-95"
                          >
                            <Headphones className="w-3.5 h-3.5" />
                            <span>🎧 Jonli Tinglash (Ghost Mode)</span>
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Live Teleprompter & Ghost Audio Console */}
        {listeningCallId && (
          <div className="mt-6 p-5 sm:p-6 rounded-2xl bg-gradient-to-b from-slate-950 via-slate-900 to-[#081e38] text-white border-2 border-purple-500/50 shadow-2xl animate-in fade-in slide-in-from-top-2 duration-300">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-white/10 gap-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-400 text-purple-300 flex items-center justify-center font-bold">
                  <Radio className="w-5 h-5 text-purple-300 animate-pulse" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-extrabold text-sm sm:text-base text-white">
                      Jonli Teleprompter &amp; Yashirin Kuzatuv
                    </h4>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                      🔒 100% Invisible • Fuqaro va operatorga bildirilmaydi
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-0.5">
                    Kuzatilayotgan sessiya: <strong className="text-purple-300">#{listeningCallId.slice(0, 12)}</strong>
                    {isGhostWsConnected ? (
                      <span className="text-emerald-400 ml-2 font-mono text-[11px]">• WebSocket Jonli Ulandi</span>
                    ) : (
                      <span className="text-amber-400 ml-2 font-mono text-[11px]">• Kanal Ulanmoqda...</span>
                    )}
                  </p>
                </div>
              </div>

              <button
                onClick={stopListening}
                className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-semibold transition active:scale-95"
              >
                Kuzatuvni yakunlash ✕
              </button>
            </div>

            {/* Real-time Teleprompter Stream Box */}
            <div className="mt-4 max-h-72 overflow-y-auto p-4 rounded-xl bg-slate-950/80 border border-purple-500/20 space-y-3 font-mono text-xs">
              {ghostMessages.length === 0 ? (
                <div className="py-8 text-center text-slate-500">
                  Transkripsiya kutilmoqda... So&apos;zlashuv boshlanishi bilan bu yerda real-vaqtda oqib keladi.
                </div>
              ) : (
                ghostMessages.map((msg, idx) => (
                  <div key={msg.id || idx} className="flex flex-col gap-1 pb-2 border-b border-white/5 last:border-0">
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                          msg.role === 'citizen'
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : msg.role === 'operator'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                        }`}
                      >
                        {msg.speaker}
                      </span>
                      <span className="text-[10px] text-slate-500 font-sans">
                        {new Date(msg.timestamp).toLocaleTimeString('uz-UZ')}
                      </span>
                      {msg.audio_url && (
                        <span className="text-[10px] text-purple-400 flex items-center gap-1 font-sans">
                          <Volume2 className="w-3 h-3" />
                          <span>Ovoz eshittirilmoqda</span>
                        </span>
                      )}
                    </div>
                    <p className="text-slate-100 font-sans text-xs leading-relaxed pl-1">
                      {msg.text}
                    </p>
                  </div>
                ))
              )}
              <div ref={teleprompterEndRef} />
            </div>

            <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <Volume2 className="w-4 h-4 text-purple-400" />
                <span>Yashirin audio oqimi administrator karnayida avtomatik ijro etilmoqda</span>
              </span>
              <span className="text-[11px] text-slate-500">
                Jami xabarlar: {ghostMessages.length} ta
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Main Grid: Operator Fleet & Live Waiting Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Operator Fleet Table (6 cols) */}
        <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
              <div className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-blue-700" />
                <h3 className="font-bold text-base text-slate-900">Operatorlar Guruhi (Fleet)</h3>
              </div>
              <span className="text-xs text-slate-400 font-medium">Avtomatik Taqsimot</span>
            </div>

            <div className="divide-y divide-slate-100">
              {operators.map((op) => (
                <div key={op.id} className="py-3.5 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-9 h-9 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-xs">
                      {op.name.charAt(0)}
                    </div>
                    <div>
                      <div className="font-semibold text-xs text-slate-900">{op.name}</div>
                      <div className="text-[10px] text-slate-400">{op.role}</div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <div className="text-xs font-bold text-slate-700">{op.handled_today} ta</div>
                      <div className="text-[10px] text-slate-400">ko&apos;rib chiqdi</div>
                    </div>
                    <span
                      className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                        op.status === 'busy'
                          ? 'bg-amber-100 text-amber-800'
                          : op.status === 'online'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {op.status === 'busy' ? 'Band' : op.status === 'online' ? 'Bo\'sh (Kutmoqda)' : 'Oflayn'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-100 text-[11px] text-slate-500 flex items-center justify-between">
            <span>Taqsimot qoidasi: <strong>Band bo&apos;lsa 2-operatorga, keyin 3-ga, barchasi band bo&apos;lsa FIFO navbatga</strong></span>
          </div>
        </div>

        {/* Live Waiting Queue List (6 cols) */}
        <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
              <div className="flex items-center space-x-2">
                <Clock className="w-5 h-5 text-amber-600" />
                <h3 className="font-bold text-base text-slate-900">Jonli Operator Navbati (FIFO)</h3>
              </div>
              <span className="text-xs font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                {waitingCalls.length} ta kutmoqda
              </span>
            </div>

            {waitingCalls.length === 0 ? (
              <div className="py-12 text-center text-slate-400 text-xs">
                <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-2 opacity-60" />
                <p className="font-semibold text-slate-700">Hozirda navbatda kutayotgan fuqaro yo&apos;q</p>
                <p className="text-[11px] text-slate-400">Barcha qo&apos;ng&apos;iroqlar o&apos;z vaqtida qabul qilingan yoki AI tomonidan hal etilgan.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {waitingCalls.map((call, idx) => (
                  <div key={call.id} className="py-3 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-lg bg-amber-500 text-white font-mono font-bold text-xs flex items-center justify-center">
                        #{idx + 1}
                      </div>
                      <div>
                        <div className="font-semibold text-xs text-slate-900">{call.citizen_name}</div>
                        <div className="text-[10px] text-slate-500">{call.primary_topic}</div>
                      </div>
                    </div>

                    <div className="text-right">
                      <span className="text-[10px] font-mono text-slate-500 block">
                        Kutish: {call.duration_seconds}s
                      </span>
                      <span className="text-[9px] font-bold text-amber-800 bg-amber-100 px-1.5 py-0.5 rounded">
                        Kutmoqda
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-slate-100 text-[11px] text-slate-500">
            Operatorlardan biri qo&apos;ng&apos;iroqni yakunlagan zahoti, ushbu navbatdagi 1-o&apos;rindagi fuqaro avtomatik ulanadi.
          </div>
        </div>
      </div>

      {/* Ministry Knowledge Base Status */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
          <div className="flex items-center space-x-2">
            <Database className="w-5 h-5 text-purple-700" />
            <h3 className="font-bold text-base text-slate-900">
              Vazirlik Normativ-Huquqiy Bilimlar Bazasi (RAG Manbalari)
            </h3>
          </div>
          <span className="text-xs text-slate-500">Jami modullar: {knowledge.length} ta</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {knowledge.map((item) => (
            <div key={item.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-purple-800 bg-purple-100 px-2 py-0.5 rounded">
                  {item.topic}
                </span>
              </div>
              <h4 className="font-bold text-xs text-slate-900 line-clamp-1">{item.title}</h4>
              <p className="text-[11px] text-slate-600 line-clamp-2 mt-1">{item.summary}</p>
              <div className="mt-3 pt-2 border-t border-slate-200 text-[10px] text-slate-400 font-mono line-clamp-1">
                {item.official_regulation}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
