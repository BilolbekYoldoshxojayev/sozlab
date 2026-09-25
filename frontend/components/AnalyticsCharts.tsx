'use client';

import React from 'react';
import {
  BarChart3, TrendingUp, Users, Clock, CheckCircle2,
  PieChart, Activity, ShieldCheck
} from 'lucide-react';
import { AnalyticsSummary } from '@/lib/types';

interface AnalyticsChartsProps {
  data: AnalyticsSummary;
}

export default function AnalyticsCharts({ data }: AnalyticsChartsProps) {
  const kpiCards = [
    {
      title: 'Bugungi Qo\'ng\'iroqlar',
      value: data.total_calls_today.toLocaleString('uz-UZ'),
      subtext: 'Barcha tarmoqlardan',
      icon: Users,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      title: 'AI Tomonidan Hal Etilgan',
      value: `${data.ai_resolved_percentage}%`,
      subtext: 'Operator aralashuvisiz',
      icon: ShieldCheck,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
    },
    {
      title: 'O\'rtacha Muloqot Vaqti',
      value: `${Math.floor(data.avg_call_duration_seconds / 60)}m ${data.avg_call_duration_seconds % 60}s`,
      subtext: 'Kutish vaqti 0 soniya',
      icon: Clock,
      color: 'text-amber-600',
      bg: 'bg-amber-50',
    },
    {
      title: 'Fuqarolar Qoniqishi',
      value: `${data.satisfaction_rate} / 5.0`,
      subtext: '96% ijobiy va neytral',
      icon: CheckCircle2,
      color: 'text-indigo-600',
      bg: 'bg-indigo-50',
    },
  ];

  const totalTopics = Object.values(data.topic_distribution).reduce((a, b) => a + b, 0) || 1;
  const totalSentiments = Object.values(data.sentiment_distribution).reduce((a, b) => a + b, 0) || 1;

  return (
    <div className="flex flex-col gap-6">
      {/* 4 KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div
              key={i}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm flex items-center justify-between"
            >
              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  {card.title}
                </span>
                <div className="text-2xl font-bold text-slate-900 mt-1 font-mono">{card.value}</div>
                <p className="text-[11px] text-slate-400 mt-0.5">{card.subtext}</p>
              </div>
              <div className={`w-12 h-12 rounded-xl ${card.bg} flex items-center justify-center ${card.color}`}>
                <Icon className="w-6 h-6" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Two-Column Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Topic Distribution Chart (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-[#0b2b50]" />
              <h3 className="font-bold text-sm text-slate-800">Mavzular Bo&apos;yicha Taqsimot</h3>
            </div>
            <span className="text-xs text-slate-400 font-medium">Oxirgi 24 soat</span>
          </div>

          <div className="space-y-3.5">
            {Object.entries(data.topic_distribution).map(([topic, count], idx) => {
              const pct = Math.round((count / totalTopics) * 100);
              return (
                <div key={idx}>
                  <div className="flex justify-between items-center text-xs mb-1">
                    <span className="font-medium text-slate-700">{topic}</span>
                    <span className="font-mono font-bold text-slate-900">
                      {count} ta ({pct}%)
                    </span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-[#0b2b50] to-[#1e6091] rounded-full transition-all duration-500"
                      style={{ width: `${Math.max(6, pct)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Sentiment & Hourly Volume (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          {/* Sentiment Distribution */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <PieChart className="w-5 h-5 text-emerald-600" />
                <h3 className="font-bold text-sm text-slate-800">Fuqarolar Kayfiyati (Sentiment)</h3>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3">
                <span className="text-[11px] font-bold text-emerald-700 block">Ijobiy</span>
                <span className="text-xl font-bold font-mono text-emerald-900 mt-1 block">
                  {data.sentiment_distribution['Ijobiy'] || 0}
                </span>
                <span className="text-[10px] text-emerald-600">
                  {Math.round(((data.sentiment_distribution['Ijobiy'] || 0) / totalSentiments) * 100)}%
                </span>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-xl p-3">
                <span className="text-[11px] font-bold text-slate-700 block">Neytral</span>
                <span className="text-xl font-bold font-mono text-slate-900 mt-1 block">
                  {data.sentiment_distribution['Neytral'] || 0}
                </span>
                <span className="text-[10px] text-slate-500">
                  {Math.round(((data.sentiment_distribution['Neytral'] || 0) / totalSentiments) * 100)}%
                </span>
              </div>

              <div className="bg-rose-50 border border-rose-200 rounded-xl p-3">
                <span className="text-[11px] font-bold text-rose-700 block">Salbiy / Shikoyat</span>
                <span className="text-xl font-bold font-mono text-rose-900 mt-1 block">
                  {data.sentiment_distribution['Salbiy'] || 0}
                </span>
                <span className="text-[10px] text-rose-600">
                  {Math.round(((data.sentiment_distribution['Salbiy'] || 0) / totalSentiments) * 100)}%
                </span>
              </div>
            </div>
          </div>

          {/* Hourly Call Traffic Volume */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex-1">
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-600" />
                <h3 className="font-bold text-sm text-slate-800">Soatlik Qo&apos;ng&apos;iroqlar Yuklamasi</h3>
              </div>
            </div>

            <div className="flex items-end justify-between h-36 pt-4 gap-2">
              {data.hourly_call_volume.map((h, idx) => {
                const heightPct = Math.min(100, Math.max(15, (h.total / 35) * 100));
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end">
                    <span className="text-[9px] font-mono text-slate-400 font-semibold">{h.total}</span>
                    <div className="w-full bg-slate-100 rounded-lg overflow-hidden flex flex-col justify-end h-24">
                      {/* AI handled slice */}
                      <div
                        className="w-full bg-emerald-600 rounded-t transition-all"
                        style={{ height: `${heightPct}%` }}
                        title={`Jami: ${h.total}, AI: ${h.ai_handled}`}
                      />
                    </div>
                    <span className="text-[10px] font-mono text-slate-500">{h.time}</span>
                  </div>
                );
              })}
            </div>
            <div className="flex items-center justify-center gap-4 mt-3 text-[11px] text-slate-500 font-medium">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-600" /> AI xizmati (84%)
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-slate-300" /> Operator
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
