'use client';

import React from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { User, Shield, ArrowRight, CheckCircle2, Headphones, Activity } from 'lucide-react';
import { useRole, UserRole } from '@/lib/useRole';

export default function HomePage() {
  const router = useRouter();
  const { setRole, hasSelectedRole, session, isReady } = useRole();

  // If role already selected, redirect to the appropriate page
  React.useEffect(() => {
    if (isReady && hasSelectedRole) {
      if (session.role === 'admin') {
        router.replace('/admin');
      } else {
        router.replace('/call');
      }
    }
  }, [isReady, hasSelectedRole, session.role, router]);

  const handleSelectRole = (role: UserRole) => {
    setRole(role);
    if (role === 'admin') {
      router.push('/admin');
    } else {
      router.push('/call');
    }
  };

  // Show loading spinner while checking role
  if (!isReady || hasSelectedRole) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="w-12 h-12 rounded-2xl bg-[#035B60]/10 flex items-center justify-center animate-pulse">
          <div className="w-5 h-5 rounded-full border-2 border-[#FC6F01] border-t-transparent animate-spin" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-3xl">
        {/* Brand Header */}
        <div className="text-center mb-10 flex flex-col items-center">
          <div className="mb-4">
            <Image
              src="/sozlab-logo.png"
              alt="SözLab Logo"
              width={220}
              height={55}
              className="h-14 w-auto object-contain mx-auto"
              priority
            />
          </div>
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#035B60]/10 border border-[#035B60]/20 text-[#035B60] text-xs font-bold mb-3">
            <Activity className="w-3.5 h-3.5 text-[#FC6F01]" />
            <span>O&apos;zbekiston Ta&apos;lim Vazirligi AI Ovozli Call-Markazi</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black tracking-tight text-slate-900">
            Tizimga Kirish Rolini Tanlang
          </h1>
          <p className="text-sm text-slate-600 max-w-md mx-auto mt-2 leading-relaxed">
            Fuqaro sifatida ta&apos;lim qonunchiligi bo&apos;yicha ovozli maslahat oling yoki Admin sifatida yagona jonli monitoring stantsiyasini boshqaring.
          </p>
        </div>

        {/* Two Role Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* User / Citizen Card */}
          <button
            onClick={() => handleSelectRole('citizen')}
            className="text-left flex flex-col justify-between rounded-3xl border-2 border-[#035B60]/20 bg-gradient-to-b from-[#035B60]/5 to-transparent p-7 hover:border-[#035B60] hover:shadow-xl hover:shadow-[#035B60]/10 transition-all group cursor-pointer active:scale-[0.98]"
          >
            <div>
              <div className="flex items-center justify-between mb-5">
                <div className="w-14 h-14 rounded-2xl bg-[#035B60] text-white flex items-center justify-center shadow-lg shadow-[#035B60]/30 group-hover:scale-105 transition-transform">
                  <Headphones className="w-7 h-7" />
                </div>
                <span className="text-[10px] uppercase font-black tracking-wider px-3 py-1 rounded-full bg-[#035B60]/15 text-[#035B60] border border-[#035B60]/25">
                  Fuqaro Murojaati
                </span>
              </div>

              <h3 className="text-xl font-black text-slate-900 group-hover:text-[#035B60] transition">
                Fuqaro (Ovozli Muloqot)
              </h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                Ta&apos;lim to&apos;g&apos;risidagi qonunlar, kontraktlar, imtiyozlar va grantlar bo&apos;yicha ovozli AI maslahat.
              </p>

              <div className="mt-5 pt-4 border-t border-[#035B60]/15 space-y-2.5">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
                  <CheckCircle2 className="w-4 h-4 text-[#035B60] shrink-0" />
                  <span>Tabiiy o&apos;zbek ovozi (Hands-Free VAD)</span>
                </div>
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
                  <CheckCircle2 className="w-4 h-4 text-[#035B60] shrink-0" />
                  <span>Jonli moddalar va qonuniy transkriptlar</span>
                </div>
              </div>
            </div>

            <div className="mt-7 w-full py-3.5 px-4 rounded-2xl bg-[#035B60] group-hover:bg-[#02373A] text-white font-bold text-sm shadow-md shadow-[#035B60]/20 flex items-center justify-center gap-2 transition">
              <span>Fuqaro sifatida kirish</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </button>

          {/* Admin Monitoring Card */}
          <button
            onClick={() => handleSelectRole('admin')}
            className="text-left flex flex-col justify-between rounded-3xl border-2 border-[#FC6F01]/30 bg-gradient-to-b from-[#FC6F01]/5 to-transparent p-7 hover:border-[#FC6F01] hover:shadow-xl hover:shadow-[#FC6F01]/15 transition-all group cursor-pointer active:scale-[0.98]"
          >
            <div>
              <div className="flex items-center justify-between mb-5">
                <div className="w-14 h-14 rounded-2xl bg-[#FC6F01] text-white flex items-center justify-center shadow-lg shadow-[#FC6F01]/30 group-hover:scale-105 transition-transform">
                  <Shield className="w-7 h-7" />
                </div>
                <span className="text-[10px] uppercase font-black tracking-wider px-3 py-1 rounded-full bg-[#FC6F01]/15 text-[#FC6F01] border border-[#FC6F01]/25">
                  Yagona Monitoring
                </span>
              </div>

              <h3 className="text-xl font-black text-slate-900 group-hover:text-[#FC6F01] transition">
                Admin (Jonli Monitoring)
              </h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                Yagona interfeys: barcha liniyalarni jonli eshitish, yozuvlarni tekshirish va nutq boshlanish markerlari.
              </p>

              <div className="mt-5 pt-4 border-t border-[#FC6F01]/15 space-y-2.5">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
                  <CheckCircle2 className="w-4 h-4 text-[#FC6F01] shrink-0" />
                  <span>Jonli audio &amp; teleprompter oqimi</span>
                </div>
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
                  <CheckCircle2 className="w-4 h-4 text-[#FC6F01] shrink-0" />
                  <span>Birlashtirilgan to&apos;liq audio &amp; beat markerlar</span>
                </div>
              </div>
            </div>

            <div className="mt-7 w-full py-3.5 px-4 rounded-2xl bg-[#FC6F01] group-hover:bg-[#E56300] text-white font-bold text-sm shadow-md shadow-[#FC6F01]/25 flex items-center justify-center gap-2 transition">
              <span>Admin Monitoringga kirish</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
