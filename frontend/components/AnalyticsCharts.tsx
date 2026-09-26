'use client';

import React from 'react';
import {
  BarChart3, Users, Clock, CheckCircle2,
  PieChart, Activity, ShieldCheck, TrendingUp
} from 'lucide-react';
import { AnalyticsSummary } from '@/lib/types';

interface AnalyticsChartsProps {
  data: AnalyticsSummary;
}

export default function AnalyticsCharts({ data }: AnalyticsChartsProps) {
  const totalTopics = Object.values(data.topic_distribution).reduce((a, b) => a + b, 0) || 1;
  const totalSentiments = Object.values(data.sentiment_distribution).reduce((a, b) => a + b, 0) || 1;

  const topicColors = [
    'bg-blue-500', 'bg-emerald-500', 'bg-amber-500', 'bg-purple-500',
    'bg-rose-500', 'bg-cyan-500', 'bg-indigo-500', 'bg-orange-500',
  ];

  const kpiCards = [
    {
      title: "Bugungi Qo'ng'iroqlar",
      value: data.total_calls_today.toLocaleString('uz-UZ'),
      subtext: 'Haqiqiy saqlangan seanslar',
      icon: Users,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      border: 'border-blue-100',
      source: 'Haqiqiy saqlangan qo\'ng\'iroqlar',
    },
    {
      title: 'AI Yechim Ulushi',
      value: `${data.ai_resolved_percentage}%`,
      subtext: 'Avtonom AI yechimi',
      icon: ShieldCheck,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
      border: 'border-emerald-100',
      source: 'Haqiqiy tahlil',
    },
    {
      title: "O'rtacha Muloqot",
      value: `${Math.floor(data.avg_call_duration_seconds / 60)}m ${data.avg_call_duration_seconds % 60}s`,
      subtext: 'Kutish 0s, navbat 0s',
      icon: Clock,
      color: 'text-amber-600',
      bg: 'bg-amber-50',
      border: 'border-amber-100',
      source: 'sum(duration) / count(calls)',
    },
    {
      title: 'Qoniqish Bahosi',
      value: `${data.satisfaction_rate} / 5.0`,
      subtext: 'Murojaatchilar bahosi',
      icon: CheckCircle2,
      color: 'text-purple-600',
      bg: 'bg-purple-50',
      border: 'border-purple-100',
      source: 'Haqiqiy baholar o\'rtachasi',
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div
              key={i}
              className={`rounded-2xl border p-5 bg-white ${card.border} shadow-sm hover:shadow-md transition-shadow`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`w-10 h-10 rounded-xl ${card.bg} flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${card.color}`} />
                </div>
                <span className="text-[9px] font-mono text-slate-400 max-w-[100px] text-right leading-tight">
                  {card.source}
                </span>
              </div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">
                {card.title}
              </span>
              <div className="text-2xl font-black font-mono text-slate-900 mt-0.5">
                {card.value}
              </div>
              <p className="text-[11px] text-slate-500 mt-1">{card.subtext}</p>
            </div>
          );
        })}
      </div>

      {/* Two-Column: Topics + Sentiment/Hourly */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Topic Distribution */}
        <div className="lg:col-span-7 rounded-2xl border border-slate-200 p-6 bg-white shadow-sm">
          <div className="flex items-center justify-between mb-5 pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-sm text-slate-900">Mavzular Taqsimoti</h3>
            </div>
            <span className="text-[10px] font-mono text-slate-400">
              Manba: call.primary_topic (LLM mavzu aniqlash)
            </span>
          </div>

          <div className="space-y-4">
            {Object.entries(data.topic_distribution).map(([topic, count], idx) => {
              const pct = Math.round((count / totalTopics) * 100);
              const color = topicColors[idx % topicColors.length];
              return (
                <div key={idx}>
                  <div className="flex justify-between items-center text-xs mb-1.5">
                    <span className="font-semibold text-slate-700">{topic}</span>
                    <span className="font-mono font-bold text-slate-900">
                      {count} ta ({pct}%)
                    </span>
                  </div>
                  <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${color} rounded-full transition-all duration-700 ease-out`}
                      style={{ width: `${Math.max(8, pct)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Sentiment + Hourly */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          {/* Sentiment */}
          <div className="rounded-2xl border border-slate-200 p-6 bg-white shadow-sm">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <PieChart className="w-5 h-5 text-emerald-600" />
                <h3 className="font-bold text-sm text-slate-900">Kayfiyat Tahlili</h3>
              </div>
              <span className="text-[10px] font-mono text-slate-400">
                call.overall_sentiment
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 text-center">
              {/* Ijobiy */}
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3.5">
                <span className="text-[10px] font-bold text-emerald-700 block">Ijobiy</span>
                <span className="text-2xl font-black font-mono text-emerald-600 mt-1 block">
                  {data.sentiment_distribution['Ijobiy'] || 0}
                </span>
                <span className="text-[10px] font-semibold text-emerald-500">
                  {Math.round(((data.sentiment_distribution['Ijobiy'] || 0) / totalSentiments) * 100)}%
                </span>
              </div>

              {/* Neytral */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5">
                <span className="text-[10px] font-bold text-slate-600 block">Neytral</span>
                <span className="text-2xl font-black font-mono text-slate-700 mt-1 block">
                  {data.sentiment_distribution['Neytral'] || 0}
                </span>
                <span className="text-[10px] font-semibold text-slate-500">
                  {Math.round(((data.sentiment_distribution['Neytral'] || 0) / totalSentiments) * 100)}%
                </span>
              </div>

              {/* Salbiy */}
              <div className="bg-rose-50 border border-rose-200 rounded-xl p-3.5">
                <span className="text-[10px] font-bold text-rose-700 block">Shikoyat</span>
                <span className="text-2xl font-black font-mono text-rose-600 mt-1 block">
                  {data.sentiment_distribution['Salbiy'] || 0}
                </span>
                <span className="text-[10px] font-semibold text-rose-500">
                  {Math.round(((data.sentiment_distribution['Salbiy'] || 0) / totalSentiments) * 100)}%
                </span>
              </div>
            </div>
          </div>

          {/* Hourly Volume */}
          <div className="rounded-2xl border border-slate-200 p-6 bg-white shadow-sm flex-1">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-amber-600" />
                <h3 className="font-bold text-sm text-slate-900">Soatlik Yuklanish</h3>
              </div>
              <span className="text-[10px] font-mono text-slate-400">
                Sintetik simulyatsiya
              </span>
            </div>

            <div className="flex items-end justify-between h-32 pt-2 gap-1.5">
              {data.hourly_call_volume.map((h, idx) => {
                const heightPct = Math.min(100, Math.max(12, (h.total / 45) * 100));
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center gap-1 h-full justify-end">
                    <span className="text-[9px] font-mono text-slate-500 font-bold">{h.total}</span>
                    <div className="w-full bg-slate-100 rounded-lg overflow-hidden flex flex-col justify-end h-20">
                      <div
                        className="w-full bg-blue-500 rounded-t-lg transition-all duration-500"
                        style={{ height: `${heightPct}%` }}
                        title={`Jami: ${h.total} | AI: ${h.ai_handled}`}
                      />
                    </div>
                    <span className="text-[9px] font-mono text-slate-400">{h.time}</span>
                  </div>
                );
              })}
            </div>
            <div className="flex items-center justify-center gap-4 mt-3 text-[10px] font-semibold text-slate-500">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500" /> 100% AI Avtonom
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
