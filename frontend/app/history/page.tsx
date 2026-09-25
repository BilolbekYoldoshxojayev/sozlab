'use client';

import React, { useEffect, useState } from 'react';
import {
  History, Search, Volume2, CheckCircle2, AlertCircle, Clock,
  Filter, FileText, ChevronRight
} from 'lucide-react';
import { CallRecord } from '@/lib/types';
import { fetchCalls, getAudioFullUrl } from '@/lib/api';
import RoleProtectedPage from '@/components/RoleProtectedPage';

export default function HistoryPage() {
  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [search, setSearch] = useState('');
  const [selectedCall, setSelectedCall] = useState<CallRecord | null>(null);
  const [loading, setLoading] = useState(true);

  const loadCalls = async (query?: string) => {
    try {
      setLoading(true);
      const data = await fetchCalls(undefined, query);
      setCalls(data);
      if (data.length > 0 && !selectedCall) {
        setSelectedCall(data[0]);
      }
    } catch (e) {
      console.error('Failed to load history:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCalls();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadCalls(search);
  };

  return (
    <RoleProtectedPage allowedRoles={['operator', 'admin']}>
      <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-slate-100 text-slate-800">
              <History className="w-5 h-5 text-[#0b2b50]" />
            </span>
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
              Murojaatlar va Qo&apos;ng&apos;iroqlar Arxivi
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1 max-w-2xl">
            Barcha suhbatlar audiosi, AI transkripsiya protokoli va tahliliy xulosalari bilan tanishish.
          </p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Ism, telefon yoki mavzu..."
              className="pl-9 pr-4 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0b2b50] w-64"
            />
          </div>
          <button
            type="submit"
            className="px-3.5 py-2 bg-[#0b2b50] hover:bg-blue-950 text-white font-bold text-xs rounded-xl shadow-xs"
          >
            Qidirish
          </button>
        </form>
      </div>

      {/* Main Master-Detail Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Calls List Table (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden h-[680px] flex flex-col">
          <div className="p-4 border-b border-slate-200 bg-slate-50 text-xs font-bold text-slate-700 flex justify-between items-center">
            <span>Barcha Qo&apos;ng&apos;iroqlar ({calls.length})</span>
            <span className="text-[11px] text-slate-400 font-normal">Tarix tartibida</span>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
            {calls.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">Hech qanday murojaat topilmadi.</div>
            ) : (
              calls.map((call) => {
                const isSelected = selectedCall?.id === call.id;
                return (
                  <div
                    key={call.id}
                    onClick={() => setSelectedCall(call)}
                    className={`p-4 cursor-pointer transition-all flex items-center justify-between ${
                      isSelected ? 'bg-blue-50/80 border-l-4 border-[#0b2b50]' : 'hover:bg-slate-50'
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold text-xs text-slate-900">{call.citizen_name}</span>
                        <span
                          className={`text-[9px] font-bold px-1.5 py-0.2 rounded ${
                            call.overall_sentiment === 'Ijobiy'
                              ? 'bg-emerald-100 text-emerald-800'
                              : call.overall_sentiment === 'Salbiy'
                              ? 'bg-rose-100 text-rose-800'
                              : 'bg-slate-100 text-slate-700'
                          }`}
                        >
                          {call.overall_sentiment}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-600 font-medium truncate max-w-[220px]">
                        {call.primary_topic}
                      </p>
                      <span className="text-[10px] text-slate-400 mt-1 block">
                        {new Date(call.started_at).toLocaleDateString('uz-UZ')}{' '}
                        {new Date(call.started_at).toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' })} •{' '}
                        {call.duration_seconds}s
                      </span>
                    </div>

                    <ChevronRight className="w-4 h-4 text-slate-300" />
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Selected Call Detail Protocol (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden h-[680px] flex flex-col">
          {selectedCall ? (
            <>
              {/* Header Details */}
              <div className="p-5 border-b border-slate-200 bg-slate-50">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="font-bold text-base text-slate-900">{selectedCall.citizen_name}</h3>
                    <p className="text-xs text-slate-500 font-mono">{selectedCall.citizen_phone}</p>
                  </div>
                  <div className="text-right">
                    <span
                      className={`text-[10px] font-bold px-2.5 py-1 rounded-full ${
                        selectedCall.resolved_by_ai
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                          : 'bg-blue-100 text-blue-800 border border-blue-200'
                      }`}
                    >
                      {selectedCall.resolved_by_ai ? 'AI tomonidan hal etilgan' : 'Operator ishtirokida'}
                    </span>
                  </div>
                </div>

                {/* AI Executive Summary Card */}
                {selectedCall.resolution_summary && (
                  <div className="mt-3 p-3 bg-blue-50/70 border border-blue-200/80 rounded-xl">
                    <div className="flex items-center gap-1.5 text-blue-900 font-bold text-xs mb-1">
                      <FileText className="w-3.5 h-3.5" />
                      <span>AI Tahliliy Xulosasi:</span>
                    </div>
                    <p className="text-xs text-blue-950 leading-relaxed font-medium">
                      {selectedCall.resolution_summary}
                    </p>
                  </div>
                )}
              </div>

              {/* Full Transcript History */}
              <div className="flex-1 overflow-y-auto p-5 space-y-3.5 bg-slate-50/30">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                  To&apos;liq Transkripsiya Protokoli ({selectedCall.messages.length} ta xabar)
                </span>

                {selectedCall.messages.map((m, idx) => (
                  <div
                    key={m.id || idx}
                    className={`flex flex-col ${
                      m.role === 'citizen' ? 'items-start' : 'items-start pl-4 border-l-2 border-blue-400'
                    }`}
                  >
                    <div className="flex items-center gap-1.5 text-[10px] text-slate-400 mb-1">
                      <strong className="text-slate-700">
                        {m.role === 'citizen' ? 'Fuqaro' : m.role === 'ai' ? 'Vazir AI' : 'Operator'}
                      </strong>
                      <span>•</span>
                      <span>
                        {new Date(m.timestamp).toLocaleTimeString('uz-UZ', {
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit',
                        })}
                      </span>
                    </div>
                    <div className="p-3 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 max-w-[95%] shadow-xs leading-relaxed">
                      {m.text}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-slate-400 text-xs">
              Ko&apos;rish uchun qo&apos;ng&apos;iroqni tanlang.
            </div>
          )}
        </div>
      </div>
    </div>
  </RoleProtectedPage>
  );
}
