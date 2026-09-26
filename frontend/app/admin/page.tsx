'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Shield, PhoneCall, Clock, CheckCircle2,
  RefreshCw, Volume2, Sparkles,
  Radio, Play, Pause, BookmarkCheck,
  TrendingUp, Headphones, Zap, FileText, ChevronRight
} from 'lucide-react';
import { CallRecord, AnalyticsSummary, AudioMarker } from '@/lib/types';
import {
  fetchCalls, fetchAnalytics,
  getAdminWebSocketUrl, getAudioFullUrl
} from '@/lib/api';
import RoleProtectedPage from '@/components/RoleProtectedPage';

interface GhostTurn {
  id: string;
  role: string;
  speaker: string;
  text: string;
  timestamp: string;
  audio_url?: string;
  timestamp_seconds?: number;
}

const formatTime = (secs: number) => {
  if (isNaN(secs) || secs < 0) return '00:00';
  const mins = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${mins.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

export default function AdminPage() {
  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Live Ghost Monitoring State
  const [listeningCallId, setListeningCallId] = useState<string | null>(null);
  const [ghostMessages, setGhostMessages] = useState<GhostTurn[]>([]);
  const [isGhostWsConnected, setIsGhostWsConnected] = useState(false);

  // Audio Playback & Beat Markers State
  const [selectedRecordedCall, setSelectedRecordedCall] = useState<CallRecord | null>(null);
  const [activeTurnIndex, setActiveTurnIndex] = useState<number>(0);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioCurrentTime, setAudioCurrentTime] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);

  const adminWsRef = useRef<WebSocket | null>(null);
  const adminAudioRef = useRef<HTMLAudioElement | null>(null);
  const recordedAudioRef = useRef<HTMLAudioElement | null>(null);
  const teleprompterEndRef = useRef<HTMLDivElement | null>(null);
  const turnRefs = useRef<{ [key: number]: HTMLDivElement | null }>({});

  const loadData = async () => {
    try {
      setLoading(true);
      const [callsData, analyticsData] = await Promise.all([
        fetchCalls(),
        fetchAnalytics().catch(() => null),
      ]);
      setCalls(callsData);
      setAnalytics(analyticsData);
      if (callsData.length > 0 && !selectedRecordedCall) {
        setSelectedRecordedCall(callsData[0]);
        setActiveTurnIndex(0);
      }
    } catch (e) {
      console.error('Failed to load admin data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 4000);
    return () => clearInterval(interval);
  }, []);

  // Teleprompter Auto-scroll
  useEffect(() => {
    teleprompterEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [ghostMessages]);

  // When selected call changes, load continuous full-call audio ONCE and reset playback state
  useEffect(() => {
    if (!recordedAudioRef.current) return;

    if (selectedRecordedCall) {
      const audioSrc = selectedRecordedCall.recording_url || selectedRecordedCall.audio_url;
      if (audioSrc) {
        const fullUrl = getAudioFullUrl(audioSrc);
        if (recordedAudioRef.current.src !== fullUrl) {
          recordedAudioRef.current.pause();
          recordedAudioRef.current.src = fullUrl;
          recordedAudioRef.current.load();
          setIsPlayingAudio(false);
          setAudioCurrentTime(0);
          setAudioDuration(0);
          setActiveTurnIndex(0);
        }
      } else {
        recordedAudioRef.current.pause();
        recordedAudioRef.current.src = '';
        setIsPlayingAudio(false);
        setAudioCurrentTime(0);
        setAudioDuration(0);
        setActiveTurnIndex(0);
      }
    }
  }, [selectedRecordedCall?.id, selectedRecordedCall?.recording_url, selectedRecordedCall?.audio_url]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (adminWsRef.current) adminWsRef.current.close();
      if (adminAudioRef.current) adminAudioRef.current.pause();
      if (recordedAudioRef.current) recordedAudioRef.current.pause();
    };
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const startListening = (call: CallRecord) => {
    if (listeningCallId === call.id) return;

    if (adminAudioRef.current) {
      adminAudioRef.current.pause();
      adminAudioRef.current.src = '';
    }
    if (adminWsRef.current) {
      adminWsRef.current.close();
      adminWsRef.current = null;
    }

    setListeningCallId(call.id);
    const existingGhostTurns: GhostTurn[] = (call.messages || [])
      .filter((m) => m.id !== 'init' && !(m.role === 'ai' && !m.audio_url && m.text?.includes('Assalomu alaykum, eshitaman')))
      .map((m, idx) => {
        const isCitizen = m.role === 'citizen' || (m.role as string) === 'user';
        return {
          id: m.id || `ghost-${idx}`,
          role: isCitizen ? 'citizen' : 'ai',
          speaker: isCitizen ? call.citizen_name : 'SözLab AI',
          text: m.text,
          timestamp: m.timestamp || new Date().toISOString(),
          audio_url: m.audio_url,
          timestamp_seconds: idx * 8,
        };
      });
    setGhostMessages(existingGhostTurns);

    try {
      const wsUrl = getAdminWebSocketUrl();
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsGhostWsConnected(true);
        ws.send(JSON.stringify({ action: 'listen_call', call_id: call.id }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'ghost_message' || data.type === 'ghost_turn' || data.type === 'ai_response' || data.type === 'new_message' || data.type === 'transcription') {
            const m = data.message || data;
            const role = m.role === 'citizen' || (m.role as string) === 'user' ? 'citizen' : 'ai';
            const speaker = role === 'citizen' ? call.citizen_name : 'SözLab AI';
            const text = m.text || '';
            const audio_url = m.audio_url || data.audio_url;

            if (text && text.trim()) {
              setGhostMessages((prev) => {
                if (prev.some((p) => p.text === text && p.role === role)) return prev;
                return [
                  ...prev,
                  {
                    id: `ghost-${Date.now()}-${Math.random()}`,
                    role,
                    speaker,
                    text,
                    timestamp: new Date().toLocaleTimeString('uz-UZ'),
                    audio_url,
                  },
                ];
              });
            }

            if (audio_url && adminAudioRef.current) {
              adminAudioRef.current.src = getAudioFullUrl(audio_url);
              adminAudioRef.current.play().catch(() => {});
            }
          }
        } catch {
          // ignore
        }
      };

      ws.onclose = () => setIsGhostWsConnected(false);
      ws.onerror = () => setIsGhostWsConnected(false);
      adminWsRef.current = ws;
    } catch {
      // ignore
    }
  };

  const stopListening = () => {
    if (adminWsRef.current) {
      try {
        adminWsRef.current.send(JSON.stringify({ action: 'unlisten', call_id: listeningCallId }));
      } catch {}
      adminWsRef.current.close();
      adminWsRef.current = null;
    }
    if (adminAudioRef.current) {
      adminAudioRef.current.pause();
    }
    setListeningCallId(null);
    setIsGhostWsConnected(false);
  };

  // Active Beat Markers from call recording or fallback
  const activeMarkers: AudioMarker[] = React.useMemo(() => {
    if (!selectedRecordedCall) return [];
    if (selectedRecordedCall.audio_markers && selectedRecordedCall.audio_markers.length > 0) {
      return selectedRecordedCall.audio_markers;
    }
    if (selectedRecordedCall.timeline_markers && selectedRecordedCall.timeline_markers.length > 0) {
      return selectedRecordedCall.timeline_markers;
    }
    const msgs = (selectedRecordedCall.messages || []).filter(
      (m) => m.id !== 'init' && !(m.role === 'ai' && !m.audio_url && m.text?.includes('Assalomu alaykum, eshitaman'))
    );
    const totalDuration = audioDuration > 0 ? audioDuration : (selectedRecordedCall.duration_seconds || 10);
    const turnDuration = msgs.length > 0 ? totalDuration / msgs.length : totalDuration;
    return msgs.map((m, idx) => ({
      turn_index: idx,
      role: m.role,
      start_time: Math.round(idx * turnDuration * 100) / 100,
      end_time: Math.round((idx + 1) * turnDuration * 100) / 100,
      duration: Math.round(turnDuration * 100) / 100,
      text: m.text,
    }));
  }, [selectedRecordedCall, audioDuration]);

  // Synchronized message turns with exact 1:1 audio marker mapping
  const selectedCallTurns = React.useMemo(() => {
    if (!selectedRecordedCall) return [];
    const msgs = (selectedRecordedCall.messages || []).filter(
      (m) => m.id !== 'init' && !(m.role === 'ai' && !m.audio_url && m.text?.includes('Assalomu alaykum, eshitaman'))
    );
    if (msgs.length === 0) return [];

    let audioTurnCounter = 0;
    let aiCounter = 0;
    const usedMarkerIndices = new Set<number>();

    return msgs.map((m, idx) => {
      const isCitizen = m.role === 'citizen' || (m.role as string) === 'user';
      if (!isCitizen) {
        aiCounter++;
      }
      const hasAudio = Boolean(m.audio_url);
      let matchedMarkerIndex = -1;

      // 1. Text-based match with role verification
      if (m.text) {
        const cleanMsgText = m.text.trim();
        for (let i = 0; i < activeMarkers.length; i++) {
          if (usedMarkerIndices.has(i)) continue;
          const mk = activeMarkers[i];
          const cleanMkText = (mk.text || '').trim();
          if (
            cleanMkText &&
            (cleanMkText === cleanMsgText ||
              cleanMkText.startsWith(cleanMsgText.slice(0, 25)) ||
              cleanMsgText.startsWith(cleanMkText.slice(0, 25)))
          ) {
            matchedMarkerIndex = i;
            usedMarkerIndices.add(i);
            break;
          }
        }
      }

      // 2. Sequential fallback for audio-bearing turns
      if (matchedMarkerIndex === -1 && hasAudio) {
        for (let i = audioTurnCounter; i < activeMarkers.length; i++) {
          if (!usedMarkerIndices.has(i)) {
            matchedMarkerIndex = i;
            usedMarkerIndices.add(i);
            audioTurnCounter = i + 1;
            break;
          }
        }
      }

      const marker = matchedMarkerIndex >= 0 ? activeMarkers[matchedMarkerIndex] : undefined;

      return {
        id: m.id || `turn-${idx}`,
        role: m.role,
        text: m.text,
        audio_url: m.audio_url,
        timestamp: m.timestamp,
        index: idx,
        aiTurnNumber: !isCitizen ? aiCounter : null,
        markerIndex: matchedMarkerIndex,
        start_time: marker ? marker.start_time : 0,
        end_time: marker ? marker.end_time : 0,
        hasAudio: hasAudio || Boolean(marker),
      };
    });
  }, [selectedRecordedCall, activeMarkers]);

  // Real-time auto-scroll to active turn in transcript pane
  useEffect(() => {
    if (activeTurnIndex !== null) {
      const matchingIdx = selectedCallTurns.findIndex((t) => t.markerIndex === activeTurnIndex);
      const targetIdx = matchingIdx !== -1 ? matchingIdx : activeTurnIndex;
      if (turnRefs.current[targetIdx]) {
        turnRefs.current[targetIdx]?.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
        });
      }
    }
  }, [activeTurnIndex, selectedCallTurns]);

  // Direct seek to specific second and activate turn marker
  const seekToTime = (targetSec: number, turnIdx?: number) => {
    if (!recordedAudioRef.current) return;
    const audio = recordedAudioRef.current;

    const audioSrc = selectedRecordedCall?.recording_url || selectedRecordedCall?.audio_url;
    if (audioSrc) {
      const fullUrl = getAudioFullUrl(audioSrc);
      if (audio.src !== fullUrl) {
        audio.src = fullUrl;
      }
    }

    const maxSec = audio.duration || audioDuration || targetSec;
    const clamped = Math.max(0, Math.min(targetSec, maxSec > 0 ? maxSec : targetSec));

    if (turnIdx !== undefined) {
      setActiveTurnIndex(turnIdx);
    } else if (activeMarkers.length > 0) {
      const foundIdx = activeMarkers.findIndex((m, idx) => {
        const nextStart = activeMarkers[idx + 1]?.start_time ?? (audio.duration || audioDuration || Infinity);
        return clamped >= m.start_time && clamped < nextStart;
      });
      if (foundIdx !== -1) setActiveTurnIndex(foundIdx);
    }

    const applySeek = () => {
      try {
        audio.currentTime = clamped;
        setAudioCurrentTime(clamped);
      } catch (err) {
        console.warn('Seek error:', err);
      }
    };

    applySeek();

    if (audio.paused) {
      audio.play()
        .then(() => {
          setIsPlayingAudio(true);
          // Re-apply seek after playback starts so browser audio decoder jumps to exact frame
          applySeek();
        })
        .catch((err) => console.error('Seek play error:', err));
    }
  };

  // Direct Seek via Turn Row Click or O'tish Button: starts from exact beginning of speech
  const playSpecificTurn = (index: number) => {
    if (!selectedRecordedCall) return;
    const turn = selectedCallTurns[index];
    if (!turn) return;

    const markerIdx = turn.markerIndex >= 0 ? turn.markerIndex : index;
    setActiveTurnIndex(markerIdx);

    const isFullCallAudio = Boolean(
      selectedRecordedCall.recording_url &&
      (selectedRecordedCall.recording_url.includes('_full.wav') || (selectedRecordedCall.audio_markers && selectedRecordedCall.audio_markers.length > 0))
    );

    if (isFullCallAudio && recordedAudioRef.current) {
      // Full concatenated audio: jump directly to speech start timestamp (e.g. 0.0s, 8.2s, 32.21s)
      seekToTime(turn.start_time, markerIdx);
    } else if (turn.audio_url && recordedAudioRef.current) {
      // Individual turn audio: load turn file and play from beginning (0s)
      const fullUrl = getAudioFullUrl(turn.audio_url);
      const audio = recordedAudioRef.current;
      audio.pause();
      audio.src = fullUrl;
      audio.currentTime = 0;
      setAudioCurrentTime(0);
      audio.play()
        .then(() => setIsPlayingAudio(true))
        .catch((err) => console.warn('Turn audio play error:', err));
    } else if (turn.start_time !== undefined) {
      seekToTime(turn.start_time, markerIdx);
    }
  };

  // Toggle Play / Pause for Full Continuous Recorded Call
  const handleTogglePlay = () => {
    if (!recordedAudioRef.current) return;

    if (isPlayingAudio) {
      recordedAudioRef.current.pause();
      setIsPlayingAudio(false);
    } else {
      const audioSrc = selectedRecordedCall?.recording_url || selectedRecordedCall?.audio_url;
      if (!audioSrc) {
        showToast("Audio yozuvi mavjud emas");
        return;
      }
      const fullUrl = getAudioFullUrl(audioSrc);
      if (recordedAudioRef.current.src !== fullUrl) {
        recordedAudioRef.current.src = fullUrl;
      }
      recordedAudioRef.current
        .play()
        .then(() => setIsPlayingAudio(true))
        .catch((err) => {
          console.error('Audio playback error:', err);
          setIsPlayingAudio(false);
        });
    }
  };

  // Audio Playback Ended
  const handleAudioEnded = () => {
    setIsPlayingAudio(false);
    setAudioCurrentTime(0);
    setActiveTurnIndex(0);
  };

  // Synchronized Time Update & Real-Time Active Turn Highlight
  const handleTimeUpdate = () => {
    if (!recordedAudioRef.current) return;
    const cur = recordedAudioRef.current.currentTime;
    setAudioCurrentTime(cur);

    if (activeMarkers.length > 0) {
      const foundIdx = activeMarkers.findIndex((m, idx) => {
        const nextStart = activeMarkers[idx + 1]?.start_time ?? (audioDuration || Infinity);
        return cur >= m.start_time && cur < nextStart;
      });
      if (foundIdx !== -1 && foundIdx !== activeTurnIndex) {
        setActiveTurnIndex(foundIdx);
      }
    }
  };

  // Timeline click seek
  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!recordedAudioRef.current || audioDuration <= 0) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const ratio = Math.max(0, Math.min(1, clickX / rect.width));
    seekToTime(ratio * audioDuration);
  };

  const activeCallsList = calls.filter((c) => c.status !== 'completed');
  const activeListeningCall = calls.find((c) => c.id === listeningCallId);

  return (
    <RoleProtectedPage allowedRoles={['admin']}>
      {/* Light Theme Single Cohesive Monitoring Station with Scroll */}
      <div className="h-full w-full overflow-y-auto scroll-smooth bg-[#F4F8F8] text-slate-900 pb-24 selection:bg-[#FC6F01] selection:text-white scrollbar-thin">
        <audio ref={adminAudioRef} className="hidden" />
        <audio
          ref={recordedAudioRef}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={() => {
            if (recordedAudioRef.current) {
              setAudioDuration(recordedAudioRef.current.duration || 0);
            }
          }}
          onEnded={handleAudioEnded}
          className="hidden"
        />

        {/* Toast Notification */}
        {toastMessage && (
          <div className="fixed top-20 right-6 z-50 px-4 py-2.5 rounded-2xl bg-[#FC6F01] text-white text-xs font-bold shadow-2xl animate-fade-in flex items-center gap-2 border border-orange-400">
            <CheckCircle2 className="w-4 h-4" />
            <span>{toastMessage}</span>
          </div>
        )}

        {/* Top Executive Header with SözLab Brand Logo & Live Status */}
        <header className="bg-white/95 border-b border-[#D2E4E6] px-4 sm:px-8 py-4 shadow-sm sticky top-0 z-30 backdrop-blur-md">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-white p-1 border border-[#CCE1E3] shadow-md shadow-[#035B60]/10 flex items-center justify-center shrink-0">
                <img src="/sozlab-logo.png" alt="SözLab Logo" className="w-full h-full object-contain" />
              </div>
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full bg-[#035B60]/10 border border-[#035B60]/20 text-[#035B60] text-[11px] font-bold mb-1">
                  <span className="w-2 h-2 rounded-full bg-[#FC6F01] animate-ping" />
                  <span>Avtonom Ovozli Monitoring Markazi</span>
                </div>
                <h1 className="text-xl sm:text-2xl font-black text-[#0A2E31] tracking-tight flex items-center gap-2">
                  <span>SÖZ<span className="text-[#FC6F01]">LAB</span></span>
                  <span className="text-slate-300 font-light text-base sm:text-lg">|</span>
                  <span className="text-slate-700 text-sm sm:text-base font-semibold">Qo&apos;ng&apos;iroqlar Nazorati va Auditing</span>
                </h1>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white border border-[#D2E4E6] text-xs font-semibold text-slate-700 shadow-2xs">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>Jonli Oqim: <strong className="text-[#035B60]">24/7 Faol</strong></span>
              </div>

              <button
                onClick={loadData}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#035B60] hover:bg-[#024448] text-white text-xs font-bold transition-all shadow-md shadow-[#035B60]/20 active:scale-95 cursor-pointer"
                title="Ma'lumotlarni yangilash"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                <span>Yangilash</span>
              </button>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
          {/* Key Executive Monitoring KPI Ribbon */}
          <section className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
            {/* Card 1: Jami Qo'ng'iroqlar */}
            <div className="p-5 rounded-2xl bg-white border border-[#D2E4E6] shadow-sm flex items-center justify-between hover:border-[#FC6F01]/50 transition">
              <div>
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Jami Qo&apos;ng&apos;iroqlar</span>
                <div className="text-2xl sm:text-3xl font-black text-[#0A2E31] mt-1 font-mono">{calls.length} ta</div>
                <span className="text-[11px] font-bold text-[#FC6F01]">Barcha Saqlangan Seanslar</span>
              </div>
              <div className="w-12 h-12 rounded-2xl bg-[#FC6F01]/10 text-[#FC6F01] flex items-center justify-center border border-[#FC6F01]/25 shadow-xs">
                <PhoneCall className="w-6 h-6" />
              </div>
            </div>

            {/* Card 2: Faol Jonli Liniyalar */}
            <div className="p-5 rounded-2xl bg-white border border-[#D2E4E6] shadow-sm flex items-center justify-between hover:border-[#035B60]/50 transition">
              <div>
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Jonli Liniyalar</span>
                <div className="text-2xl sm:text-3xl font-black text-[#0A2E31] mt-1 font-mono">
                  {activeCallsList.length} ta
                </div>
                <span className="text-[11px] font-bold text-emerald-600">
                  {activeCallsList.length > 0 ? "Hozir muloqotda" : "Navbatchilikda (Bo'sh)"}
                </span>
              </div>
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center border border-emerald-200 shadow-xs">
                <Radio className={`w-6 h-6 ${activeCallsList.length > 0 ? 'animate-pulse text-[#FC6F01]' : ''}`} />
              </div>
            </div>

            {/* Card 3: AI Yechim Ko'rsatkichi */}
            <div className="p-5 rounded-2xl bg-white border border-[#D2E4E6] shadow-sm flex items-center justify-between hover:border-[#035B60]/50 transition">
              <div>
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">AI Yechim Ulushi</span>
                <div className="text-2xl sm:text-3xl font-black text-[#0A2E31] mt-1 font-mono">
                  {analytics ? analytics.ai_resolved_percentage : 100}%
                </div>
                <span className="text-[11px] font-bold text-[#035B60]">100% Avtonom yechim</span>
              </div>
              <div className="w-12 h-12 rounded-2xl bg-[#035B60]/10 text-[#035B60] flex items-center justify-center border border-[#035B60]/25 shadow-xs">
                <CheckCircle2 className="w-6 h-6" />
              </div>
            </div>

            {/* Card 4: O'rtacha Muloqot Davomiyligi */}
            <div className="p-5 rounded-2xl bg-white border border-[#D2E4E6] shadow-sm flex items-center justify-between hover:border-[#FC6F01]/50 transition">
              <div>
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">O&apos;rtacha Muloqot</span>
                <div className="text-2xl sm:text-3xl font-black text-[#0A2E31] mt-1 font-mono">
                  {analytics ? `${Math.floor(analytics.avg_call_duration_seconds / 60)}m ${analytics.avg_call_duration_seconds % 60}s` : '0m 0s'}
                </div>
                <span className="text-[11px] font-semibold text-slate-500">VAD {analytics ? '1.4s' : '1.4s'} aniqlikda</span>
              </div>
              <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-200 shadow-xs">
                <Clock className="w-6 h-6" />
              </div>
            </div>
          </section>

          {/* Real-Time Live Line Monitoring Box */}
          <section className="p-6 sm:p-7 rounded-3xl bg-white border border-[#D2E4E6] shadow-sm">
            <div className="flex items-center justify-between pb-4 border-b border-[#E2EBF0] mb-5">
              <div className="flex items-center gap-3">
                <span className="w-3 h-3 rounded-full bg-[#FC6F01] animate-ping" />
                <div>
                  <h2 className="text-base sm:text-lg font-black text-[#0A2E31] flex items-center gap-2">
                    <span>Jonli Liniyalar Monitoringi</span>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-bold border border-emerald-200">
                      Real-Time
                    </span>
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Hozirda serverga ulangan va AI bilan suhbatlashayotgan fuqarolar liniyalari
                  </p>
                </div>
              </div>
              <span className="text-xs font-bold px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 border border-slate-200">
                {activeCallsList.length} ta faol liniya
              </span>
            </div>

            {activeCallsList.length === 0 ? (
              <div className="py-8 px-4 text-center rounded-2xl bg-[#F8FAFA] border border-[#E2EBF0]">
                <Radio className="w-8 h-8 text-slate-400 mx-auto mb-2 opacity-60" />
                <p className="text-xs font-bold text-slate-700">
                  Hozirda barcha liniyalar bo&apos;sh — yangi qo&apos;ng&apos;iroqlar kutilmoqda
                </p>
                <p className="text-[11px] text-slate-500 mt-1">
                  Fuqaro ovozli qo&apos;ng&apos;iroq boshlagan zahoti ushbu panelda jonli audio va transkript bilan paydo bo&apos;ladi.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {activeCallsList.map((call) => (
                  <div
                    key={call.id}
                    className="p-4 rounded-2xl border border-[#D2E4E6] bg-[#F8FAFA] flex items-center justify-between shadow-2xs hover:border-[#035B60]/40 transition"
                  >
                    <div>
                      <div className="font-extrabold text-sm text-[#0A2E31] flex items-center gap-2">
                        <span>{call.citizen_name}</span>
                        <span className="w-2 h-2 rounded-full bg-[#FC6F01] animate-ping" />
                      </div>
                      <div className="text-xs text-slate-500 font-mono mt-0.5">{call.citizen_phone}</div>
                    </div>

                    <button
                      onClick={() => startListening(call)}
                      className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer shadow-sm ${
                        listeningCallId === call.id
                          ? 'bg-[#FC6F01] text-white shadow-orange-500/20'
                          : 'bg-[#035B60] hover:bg-[#024448] text-white shadow-[#035B60]/20'
                      }`}
                    >
                      <Radio className="w-3.5 h-3.5 animate-pulse" />
                      <span>{listeningCallId === call.id ? 'Kuzatilmoqda' : 'Jonli Tinglash'}</span>
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Live Ghost Teleprompter for Active Call */}
            {listeningCallId && (
              <div className="mt-6 p-5 sm:p-6 rounded-2xl bg-[#F4F8F8] border border-[#CCE1E3] shadow-inner">
                <div className="flex items-center justify-between pb-3 border-b border-[#D2E4E6] mb-4">
                  <div className="flex items-center gap-2.5 text-xs font-bold text-[#035B60]">
                    <Headphones className="w-4 h-4 animate-bounce text-[#FC6F01]" />
                    <span>Jonli Audio va Transkript Oqimi: <strong className="text-slate-900">{activeListeningCall?.citizen_name}</strong></span>
                  </div>
                  <button
                    onClick={stopListening}
                    className="text-xs font-bold px-3 py-1.5 rounded-lg bg-white hover:bg-slate-100 text-slate-700 border border-[#D2E4E6] transition cursor-pointer shadow-2xs"
                  >
                    Tinglashni Yakunlash ✕
                  </button>
                </div>

                <div className="max-h-64 overflow-y-auto space-y-3 pr-2 text-xs font-mono">
                  {ghostMessages.map((m) => (
                    <div
                      key={m.id}
                      className={`p-3.5 rounded-xl border shadow-2xs ${
                        m.role === 'citizen'
                          ? 'bg-[#FFF6EF] border-[#FCD4BA]'
                          : 'bg-white border-[#CCE1E3]'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className={`font-bold flex items-center gap-1.5 ${
                          m.role === 'citizen' ? 'text-[#FC6F01]' : 'text-[#035B60]'
                        }`}>
                          <span className={`w-2 h-2 rounded-full ${m.role === 'citizen' ? 'bg-[#FC6F01]' : 'bg-[#035B60]'}`} />
                          {m.speaker}
                        </span>
                        <span className="text-[10px] text-slate-400 font-mono">{m.timestamp}</span>
                      </div>
                      <p className="text-slate-800 font-sans text-xs leading-relaxed">{m.text}</p>
                    </div>
                  ))}
                  <div ref={teleprompterEndRef} />
                </div>
              </div>
            )}
          </section>

          {/* Continuous Call Audio & Talk-Start Markers Monitoring Hub */}
          <section className="p-6 sm:p-7 rounded-3xl bg-white border border-[#D2E4E6] shadow-sm">
            <div className="pb-4 border-b border-[#E2EBF0] mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h2 className="text-base sm:text-lg font-black text-[#0A2E31] flex items-center gap-2">
                  <span>Saqlangan Qo&apos;ng&apos;iroqlar Auditi &amp; Yaxlit Audio Ijrochisi</span>
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Har bir qo&apos;ng&apos;iroq bitta uzluksiz audio sifatida tinglanadi. Nutq boshlanish nuqtalarini bosish orqali aniq boshiga o&apos;tish mumkin.
                </p>
              </div>

              {/* Marker Legend */}
              <div className="flex items-center gap-3 text-[11px] font-bold">
                <span className="flex items-center gap-1.5 text-[#FC6F01]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#FC6F01]" />
                  Fuqaro Savoli
                </span>
                <span className="flex items-center gap-1.5 text-[#035B60]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#035B60]" />
                  AI Javobi
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-8">
              {/* Monitored Calls List (5 cols) */}
              <div className="lg:col-span-5 space-y-2.5 max-h-[460px] overflow-y-auto pr-2">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 px-1 mb-1">
                  Mavjud Qo&apos;ng&apos;iroqlar ({calls.length})
                </div>

                {calls.length === 0 ? (
                  <div className="py-12 text-center text-slate-500 text-xs font-medium rounded-2xl bg-[#F8FAFA] border border-[#E2EBF0]">
                    Hozircha saqlangan qo&apos;ng&apos;iroqlar mavjud emas.
                  </div>
                ) : (
                  calls.map((call) => (
                    <div
                      key={call.id}
                      onClick={() => setSelectedRecordedCall(call)}
                      className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                        selectedRecordedCall?.id === call.id
                          ? 'bg-[#035B60]/10 border-2 border-[#035B60] shadow-md shadow-[#035B60]/10'
                          : 'bg-[#F8FAFA] border-[#D2E4E6] hover:border-[#035B60]/40'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-extrabold text-sm text-[#0A2E31]">{call.citizen_name}</span>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white text-[#FC6F01] border border-[#FCD4BA] shadow-2xs">
                          {call.duration_seconds}s
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs text-slate-500">
                        <span className="line-clamp-1">{call.primary_topic || "Ta'lim masalasi"}</span>
                        <ChevronRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Master Audio Review Player & Synchronized Transcript (7 cols) */}
              <div className="lg:col-span-7 p-6 rounded-2xl bg-[#F8FAFA] text-slate-900 border border-[#CCE1E3] flex flex-col justify-between shadow-sm">
                <div>
                  {/* Top Player Details */}
                  <div className="flex items-center justify-between pb-4 border-b border-[#D2E4E6] mb-5">
                    <div>
                      <h3 className="font-extrabold text-base sm:text-lg text-[#0A2E31]">
                        {selectedRecordedCall?.citizen_name || "Qo'ng'iroq Tanlang"}
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {selectedRecordedCall?.citizen_phone} • {selectedCallTurns.length} ta muloqot bosqichi
                      </p>
                    </div>

                    <button
                      onClick={handleTogglePlay}
                      className="w-13 h-13 rounded-2xl bg-[#FC6F01] hover:bg-[#E56300] text-white flex items-center justify-center shadow-lg shadow-[#FC6F01]/25 transition-all active:scale-95 cursor-pointer"
                      title={isPlayingAudio ? "To'xtatish" : "Tinglash"}
                    >
                      {isPlayingAudio ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6 ml-1" />}
                    </button>
                  </div>

                  {/* Interactive Scrubbing Timeline with Beat Markers */}
                  <div className="my-5">
                    <div className="flex items-center justify-between text-xs font-mono text-slate-500 mb-2">
                      <span className="text-[#0A2E31] font-bold">{formatTime(audioCurrentTime)}</span>
                      <span className="text-[#FC6F01] text-[11px] font-bold">Nutq Boshlanish Nuqtalari (Beat Markers)</span>
                      <span>{formatTime(audioDuration)}</span>
                    </div>

                    {/* Timeline Bar with Markers */}
                    <div
                      onClick={handleTimelineClick}
                      className="relative w-full h-5 bg-[#E1EDEF] rounded-full overflow-hidden cursor-pointer flex items-center border border-[#CCE1E3]"
                    >
                      <div
                        className="h-full bg-[#FC6F01] transition-all"
                        style={{ width: `${audioDuration > 0 ? (audioCurrentTime / audioDuration) * 100 : 0}%` }}
                      />

                      {/* Beat Markers for each turn's talk start */}
                      {activeMarkers.map((marker, i) => {
                        const leftPercent = audioDuration > 0
                          ? (marker.start_time / audioDuration) * 100
                          : (i / (activeMarkers.length || 1)) * 100;
                        const clampedPercent = Math.max(0, Math.min(100, leftPercent));
                        const isCurrent = activeTurnIndex === i;
                        const isCitizen = (marker.role as string) === 'citizen' || (marker.role as string) === 'user';
                        return (
                          <div
                            key={`marker-${i}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              seekToTime(marker.start_time, i);
                            }}
                            className={`absolute top-0 bottom-0 w-3 rounded-full transition-transform hover:scale-125 group cursor-pointer z-10 ${
                              isCurrent
                                ? 'bg-white ring-2 ring-[#FC6F01] scale-125 z-20 shadow-md'
                                : isCitizen
                                ? 'bg-[#FC6F01] hover:bg-orange-600'
                                : 'bg-[#035B60] hover:bg-[#024448]'
                            }`}
                            style={{ left: `calc(${clampedPercent}% - 6px)` }}
                            title={`Turn #${i + 1}: ${isCitizen ? 'Fuqaro savoli' : 'AI javobi'} (${formatTime(marker.start_time)})`}
                          >
                            <div className="hidden group-hover:block absolute bottom-8 -translate-x-1/2 left-1/2 px-2.5 py-1 bg-[#062124] text-white font-bold text-[10px] rounded-lg shadow-2xl whitespace-nowrap z-30">
                              <span className={isCitizen ? 'text-[#FC6F01]' : 'text-emerald-400'}>
                                {isCitizen ? '🗣️ Fuqaro savoli' : '🤖 AI javobi'}
                              </span>{' '}
                              • {formatTime(marker.start_time)}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Synchronized Turn-by-Turn Teleprompter List */}
                  <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                    {selectedCallTurns.map((t, idx) => {
                      const isActive = t.markerIndex >= 0 ? activeTurnIndex === t.markerIndex : activeTurnIndex === idx;
                      const isCitizen = (t.role as string) === 'citizen' || (t.role as string) === 'user';
                      return (
                        <div
                          key={t.id || `turn-${idx}`}
                          ref={(el) => { turnRefs.current[idx] = el; }}
                          onClick={() => playSpecificTurn(idx)}
                          className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                            isActive
                              ? 'bg-white border-2 border-[#FC6F01] shadow-md ring-1 ring-[#FC6F01]/30 scale-[1.01]'
                              : isCitizen
                              ? 'bg-[#FFF9F5] border-[#FCD4BA] hover:border-[#FC6F01] text-slate-800'
                              : 'bg-white border-[#D2E4E6] hover:border-[#035B60] text-slate-800'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1 font-mono text-[10px]">
                            <span className={`font-bold flex items-center gap-1.5 ${
                              isCitizen ? 'text-[#FC6F01]' : 'text-[#035B60]'
                            }`}>
                              <span className={`w-2 h-2 rounded-full ${
                                isCitizen ? 'bg-[#FC6F01]' : 'bg-[#035B60]'
                              }`} />
                              {isCitizen ? 'Fuqaro Nutqi' : `AI Javobi #${t.aiTurnNumber || 1}`}
                            </span>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                playSpecificTurn(idx);
                              }}
                              className={`px-2.5 py-1 rounded-lg border font-bold flex items-center gap-1 transition shadow-2xs ${
                                isActive
                                  ? 'bg-[#FC6F01] text-white border-orange-500'
                                  : 'bg-white border-[#D2E4E6] text-[#035B60] hover:text-[#FC6F01] hover:border-[#FC6F01]'
                              }`}
                              title="Nutq boshidan ijro etish"
                            >
                              {isActive && isPlayingAudio && <span className="w-1.5 h-1.5 rounded-full bg-white animate-ping mr-0.5" />}
                              <span>{formatTime(t.start_time)}</span>
                              <span>• ▶ O&apos;tish</span>
                            </button>
                          </div>
                          <p className="font-sans text-slate-800 line-clamp-2 leading-relaxed">{t.text}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </RoleProtectedPage>
  );
}
