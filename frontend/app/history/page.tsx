'use client';

import React, { useEffect, useState, useRef } from 'react';
import {
  History, Search, Volume2, CheckCircle2, AlertCircle, Clock,
  Filter, FileText, ChevronRight, Play, Pause
} from 'lucide-react';
import { CallRecord } from '@/lib/types';
import { fetchCalls, getAudioFullUrl } from '@/lib/api';
import { fetchSupabaseCalls } from '@/lib/supabaseClient';
import RoleProtectedPage from '@/components/RoleProtectedPage';
import TranscriptHighlightedText, { HighlightLegend } from '@/components/TranscriptHighlightedText';

export default function HistoryPage() {
  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [search, setSearch] = useState('');
  const [selectedCall, setSelectedCall] = useState<CallRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTurnAudioId, setActiveTurnAudioId] = useState<string | null>(null);

  const turnAudioRef = useRef<HTMLAudioElement | null>(null);

  const loadCalls = async (query?: string) => {
    try {
      setLoading(true);
      const data = await fetchCalls(undefined, query);
      setCalls(data);
      if (data.length > 0 && !selectedCall) {
        setSelectedCall(data[0]);
      }
    } catch (e) {
      console.warn('Primary backend fetchCalls failed, attempting Supabase fallback:', e);
      try {
        const supaData = await fetchSupabaseCalls(50);
        const mapped: CallRecord[] = supaData.map((sc) => ({
          id: sc.id,
          citizen_name: sc.citizen_name || 'Fuqaro',
          citizen_phone: sc.citizen_phone || '+998 90 000-00-00',
          status: (sc.status as any) || 'completed',
          started_at: sc.started_at || sc.created_at,
          ended_at: sc.ended_at,
          duration_seconds: sc.duration_seconds || 60,
          assigned_operator: sc.operator_name,
          messages: [],
          primary_topic: (sc.primary_topic as any) || 'Umumiy Murojaat',
          overall_sentiment: (sc.sentiment as any) || 'Neytral',
          resolution_summary: sc.ai_summary,
          resolved_by_ai: true,
        }));
        setCalls(mapped);
        if (mapped.length > 0 && !selectedCall) {
          setSelectedCall(mapped[0]);
        }
      } catch (fallbackErr) {
        console.error('Failed to load history from Supabase fallback:', fallbackErr);
      }
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

  const playTurnAudio = (msgId: string, audioUrl: string) => {
    if (!turnAudioRef.current) return;

    if (activeTurnAudioId === msgId) {
      turnAudioRef.current.pause();
      setActiveTurnAudioId(null);
      return;
    }

    const fullUrl = getAudioFullUrl(audioUrl);
    turnAudioRef.current.src = fullUrl;
    turnAudioRef.current.play().then(() => {
      setActiveTurnAudioId(msgId);
    }).catch((err) => {
      console.warn('[Turn Audio playback warning]:', err);
      setActiveTurnAudioId(null);
    });
  };

  // Find master audio url: either call-level audio_url, recording_url, or first message audio_url
  const masterAudioSrc = selectedCall?.audio_url
    ? getAudioFullUrl(selectedCall.audio_url)
    : selectedCall?.recording_url
    ? getAudioFullUrl(selectedCall.recording_url)
    : selectedCall?.messages.find((m) => m.audio_url)
    ? getAudioFullUrl(selectedCall.messages.find((m) => m.audio_url)!.audio_url!)
    : null;

  return (
    <RoleProtectedPage allowedRoles={['citizen', 'admin']}>
      {/* Hidden audio element for turn playback */}
      <audio
        ref={turnAudioRef}
        onEnded={() => setActiveTurnAudioId(null)}
        onError={() => setActiveTurnAudioId(null)}
        className="hidden"
      />

      <div className="flex flex-col gap-6">
        {/* Header */}
        <div
          className="rounded-2xl border p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-colors"
          style={{
            backgroundColor: 'var(--bg-card)',
            borderColor: 'var(--border-card)',
            color: 'var(--text-primary)',
          }}
        >
          <div>
            <div className="flex items-center gap-2">
              <span
                className="p-1.5 rounded-lg"
                style={{
                  backgroundColor: 'var(--bg-subtle)',
                  color: 'var(--accent-tab)',
                }}
              >
                <History className="w-5 h-5" />
              </span>
              <h1 className="text-xl sm:text-2xl font-extrabold tracking-tight" style={{ color: 'var(--text-primary)' }}>
                Murojaatlar va Qo&apos;ng&apos;iroqlar Arxivi
              </h1>
            </div>
            <p className="text-xs mt-1 max-w-2xl" style={{ color: 'var(--text-muted)' }}>
              Barcha suhbatlar audiosi, AI transkripsiya protokoli va tahliliy xulosalari bilan tanishish.
            </p>
          </div>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5" style={{ color: 'var(--text-muted)' }} />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Ism, telefon yoki mavzu..."
                className="pl-9 pr-4 py-2 rounded-xl text-xs focus:outline-none transition w-64 border"
                style={{
                  backgroundColor: 'var(--bg-subtle)',
                  borderColor: 'var(--border-card)',
                  color: 'var(--text-primary)',
                }}
              />
            </div>
            <button
              type="submit"
              className="px-3.5 py-2 font-bold text-xs rounded-xl shadow-xs transition"
              style={{
                backgroundColor: 'var(--accent-cta)',
                color: '#ffffff',
              }}
            >
              Qidirish
            </button>
          </form>
        </div>

        {/* Main Master-Detail Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Calls List Table (5 cols) */}
          <div
            className="lg:col-span-5 rounded-2xl border shadow-sm overflow-hidden min-h-[500px] h-[calc(100vh-16rem)] flex flex-col transition-colors"
            style={{
              backgroundColor: 'var(--bg-card)',
              borderColor: 'var(--border-card)',
            }}
          >
            <div
              className="p-4 border-b text-xs font-bold flex justify-between items-center transition-colors"
              style={{
                backgroundColor: 'var(--bg-subtle)',
                borderColor: 'var(--border-subtle)',
                color: 'var(--text-primary)',
              }}
            >
              <span>Barcha Qo&apos;ng&apos;iroqlar ({calls.length})</span>
              <span className="text-[11px] font-normal" style={{ color: 'var(--text-muted)' }}>
                Tarix tartibida
              </span>
            </div>

            <div className="flex-1 overflow-y-auto divide-y" style={{ borderColor: 'var(--border-subtle)' }}>
              {calls.length === 0 ? (
                <div className="p-8 text-center text-xs" style={{ color: 'var(--text-muted)' }}>
                  {loading ? 'Yuklanmoqda...' : 'Hech qanday murojaat topilmadi.'}
                </div>
              ) : (
                calls.map((call) => {
                  const isSelected = selectedCall?.id === call.id;
                  const hasAudio = Boolean(
                    call.audio_url || call.recording_url || call.messages.some((m) => m.audio_url)
                  );
                  return (
                    <div
                      key={call.id}
                      onClick={() => setSelectedCall(call)}
                      className={`p-4 cursor-pointer transition-all flex items-center justify-between ${
                        isSelected ? 'border-l-4' : 'hover:opacity-90'
                      }`}
                      style={{
                        backgroundColor: isSelected ? 'var(--bg-subtle)' : 'transparent',
                        borderColor: isSelected ? 'var(--accent-tab)' : 'var(--border-subtle)',
                      }}
                    >
                      <div className="min-w-0 pr-2">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-bold text-xs truncate" style={{ color: 'var(--text-primary)' }}>
                            {call.citizen_name}
                          </span>
                          <span
                            className={`text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0 border ${
                              call.overall_sentiment === 'Ijobiy'
                                ? 'bg-blue-950/60 text-blue-300 border-blue-800/60'
                                : call.overall_sentiment === 'Salbiy'
                                ? 'bg-slate-800 text-slate-300 border-slate-700'
                                : 'bg-slate-900 text-slate-400 border-slate-800'
                            }`}
                          >
                            {call.overall_sentiment}
                          </span>
                          {hasAudio && (
                            <span
                              title="Audio yozuv mavjud"
                              className="text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0 border bg-blue-900/30 text-blue-300 border-blue-800/50"
                            >
                              🔊 Audio
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] font-medium truncate max-w-[220px]" style={{ color: 'var(--text-secondary)' }}>
                          {call.primary_topic}
                        </p>
                        <span className="text-[10px] mt-1 block" style={{ color: 'var(--text-muted)' }}>
                          {new Date(call.started_at).toLocaleDateString('uz-UZ')}{' '}
                          {new Date(call.started_at).toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' })} •{' '}
                          {call.duration_seconds}s
                        </span>
                      </div>

                      <ChevronRight className="w-4 h-4 shrink-0" style={{ color: 'var(--text-muted)' }} />
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Selected Call Detail Protocol (7 cols) */}
          <div
            className="lg:col-span-7 rounded-2xl border shadow-sm overflow-hidden min-h-[500px] h-[calc(100vh-16rem)] flex flex-col transition-colors"
            style={{
              backgroundColor: 'var(--bg-card)',
              borderColor: 'var(--border-card)',
            }}
          >
            {selectedCall ? (
              <>
                {/* Header Details */}
                <div
                  className="p-5 border-b space-y-3 transition-colors"
                  style={{
                    backgroundColor: 'var(--bg-subtle)',
                    borderColor: 'var(--border-subtle)',
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-bold text-base" style={{ color: 'var(--text-primary)' }}>
                        {selectedCall.citizen_name}
                      </h3>
                      <p className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
                        {selectedCall.citizen_phone}
                      </p>
                    </div>
                    <div className="text-right">
                      <span
                        className="text-[10px] font-bold px-2.5 py-1 rounded-full border bg-blue-950/60 text-blue-300 border-blue-800/60"
                      >
                        {selectedCall.resolved_by_ai ? 'AI tomonidan hal etilgan' : 'Operator ishtirokida'}
                      </span>
                    </div>
                  </div>

                  {/* Master Call Audio Player Card */}
                  <div
                    className="p-3.5 rounded-xl border shadow-xs transition-colors"
                    style={{
                      backgroundColor: 'var(--bg-card)',
                      borderColor: 'var(--border-card)',
                    }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
                          style={{
                            backgroundColor: 'var(--accent-cta)',
                            color: '#ffffff',
                          }}
                        >
                          <Volume2 className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <h4 className="font-bold text-xs" style={{ color: 'var(--text-primary)' }}>
                            Qo&apos;ng&apos;iroq Audio Yozuvi
                          </h4>
                          <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
                            Davomiyligi: {selectedCall.duration_seconds} soniya • So&apos;zLab AI va Fuqaro suhbati
                          </span>
                        </div>
                      </div>
                      <span
                        className="text-[10px] font-mono px-2 py-0.5 rounded border bg-blue-950/60 text-blue-300 border-blue-800/60"
                      >
                        {masterAudioSrc ? '100% Yozilgan' : 'Matnli Protokol'}
                      </span>
                    </div>

                    {masterAudioSrc ? (
                      <audio
                        controls
                        className="w-full h-8 rounded-lg focus:outline-none mt-1"
                        src={masterAudioSrc}
                      />
                    ) : (
                      <p className="text-[11px] mt-1 italic" style={{ color: 'var(--text-muted)' }}>
                        Ushbu qo&apos;ng&apos;iroq uchun yaxlit audio fayl saqlanmagan. Quyidagi transkripsiyada mavjud bo&apos;lsa, alohida turn audiosini tinglashingiz mumkin.
                      </p>
                    )}
                  </div>

                  {/* AI Executive Summary Card */}
                  {selectedCall.resolution_summary && (
                    <div
                      className="p-3 rounded-xl border"
                      style={{
                        backgroundColor: 'var(--bg-card)',
                        borderColor: 'var(--border-card)',
                      }}
                    >
                      <div className="flex items-center gap-1.5 font-bold text-xs mb-1" style={{ color: 'var(--accent-tab)' }}>
                        <FileText className="w-3.5 h-3.5" />
                        <span>AI Tahliliy Xulosasi:</span>
                      </div>
                      <p className="text-xs leading-relaxed font-medium" style={{ color: 'var(--text-primary)' }}>
                        {selectedCall.resolution_summary}
                      </p>
                    </div>
                  )}
                </div>

                {/* Full Transcript History */}
                <div
                  className="flex-1 overflow-y-auto p-5 space-y-3.5"
                  style={{ backgroundColor: 'var(--bg-app)' }}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-wider block" style={{ color: 'var(--text-muted)' }}>
                      To&apos;liq Transkripsiya Protokoli ({selectedCall.messages.length} ta xabar)
                    </span>
                  </div>

                  {/* Visual Legend for 4 Soft Color Badges */}
                  <HighlightLegend />

                  {selectedCall.messages.length === 0 ? (
                    <div className="py-12 text-center text-xs" style={{ color: 'var(--text-muted)' }}>
                      Transkripsiya yozuvlari mavjud emas.
                    </div>
                  ) : (
                    selectedCall.messages.map((m, idx) => (
                      <div
                        key={m.id || idx}
                        className={`flex flex-col ${
                          m.role === 'citizen' ? 'items-start' : 'items-start pl-4 border-l-2'
                        }`}
                        style={{
                          borderColor: m.role !== 'citizen' ? 'var(--accent-tab)' : 'transparent',
                        }}
                      >
                        <div className="flex items-center gap-1.5 text-[10px] mb-1" style={{ color: 'var(--text-muted)' }}>
                          <strong style={{ color: 'var(--text-secondary)' }}>
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
                        <div
                          className="p-3 rounded-xl text-xs max-w-[95%] shadow-xs leading-relaxed border transition-colors"
                          style={{
                            backgroundColor: 'var(--bg-card)',
                            borderColor: 'var(--border-card)',
                            color: 'var(--text-primary)',
                          }}
                        >
                          <TranscriptHighlightedText text={m.text} />

                          {m.audio_url && (
                            <div
                              className="mt-2.5 pt-2 border-t flex items-center gap-2"
                              style={{ borderColor: 'var(--border-subtle)' }}
                            >
                              <button
                                type="button"
                                onClick={() => playTurnAudio(m.id || String(idx), m.audio_url!)}
                                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-bold transition shadow-xs"
                                style={{
                                  backgroundColor:
                                    activeTurnAudioId === (m.id || String(idx))
                                      ? 'var(--accent-cta)'
                                      : 'var(--bg-subtle)',
                                  color:
                                    activeTurnAudioId === (m.id || String(idx))
                                      ? '#ffffff'
                                      : 'var(--text-secondary)',
                                  border: '1px solid var(--border-card)',
                                }}
                              >
                                {activeTurnAudioId === (m.id || String(idx)) ? (
                                  <>
                                    <Pause className="w-3 h-3" />
                                    <span>To&apos;xtatish</span>
                                  </>
                                ) : (
                                  <>
                                    <Volume2 className="w-3 h-3" />
                                    <span>Turn Ovozini Tinglash</span>
                                  </>
                                )}
                              </button>
                              <span className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>
                                Audio Turn
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-xs" style={{ color: 'var(--text-muted)' }}>
                Ko&apos;rish uchun qo&apos;ng&apos;iroqni tanlang.
              </div>
            )}
          </div>
        </div>
      </div>
    </RoleProtectedPage>
  );
}
