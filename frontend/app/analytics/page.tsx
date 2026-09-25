'use client';

import React, { useEffect, useState } from 'react';
import AnalyticsCharts from '@/components/AnalyticsCharts';
import RoleProtectedPage from '@/components/RoleProtectedPage';
import { BarChart3, RefreshCw } from 'lucide-react';
import { AnalyticsSummary } from '@/lib/types';
import { fetchAnalytics } from '@/lib/api';

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const res = await fetchAnalytics();
      setData(res);
    } catch (e) {
      console.error('Failed to load analytics:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <RoleProtectedPage allowedRoles={['admin']}>
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-indigo-100 text-indigo-800">
                <BarChart3 className="w-5 h-5 text-indigo-700" />
              </span>
              <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
                Tahliliy Tizim &amp; Ish Samaradorligi (KPI)
              </h1>
            </div>
            <p className="text-xs text-slate-500 mt-1 max-w-2xl">
              Ta&apos;lim va Innovatsiyalar Vazirligi call markazining to&apos;liq tahliliy ko&apos;rsatkichlari,
              murojaatlar dinamikasi va AI samaradorligi.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={loadData}
              className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold border border-slate-200 transition-all"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Yangilash</span>
            </button>
          </div>
        </div>

        {loading && !data ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-400 text-xs">
            Tahliliy ma&apos;lumotlar yuklanmoqda...
          </div>
        ) : data ? (
          <AnalyticsCharts data={data} />
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-400 text-xs">
            Ma&apos;lumotlar mavjud emas.
          </div>
        )}
      </div>
    </RoleProtectedPage>
  );
}
