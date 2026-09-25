'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { PhoneCall, Shield, ArrowRight, X, Sparkles, CheckCircle2 } from 'lucide-react';
import { useRole, UserRole } from '@/lib/useRole';

interface RoleGateModalProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export default function RoleGateModal({ isOpen, onClose }: RoleGateModalProps) {
  const router = useRouter();
  const { setRole, isRoleGateOpen, closeRoleGate, hasSelectedRole, isReady } = useRole();

  const showModal = isOpen !== undefined ? isOpen : (isReady && isRoleGateOpen);
  if (!showModal) return null;

  const handleSelectRole = (role: UserRole) => {
    if (role === 'citizen') {
      setRole('citizen');
      if (onClose) onClose();
      else closeRoleGate();
      router.push('/call');
    } else if (role === 'admin') {
      setRole('admin');
      if (onClose) onClose();
      else closeRoleGate();
      router.push('/admin');
    }
  };

  const handleDismiss = () => {
    if (onClose) onClose();
    else closeRoleGate();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-md animate-fade-in overflow-y-auto">
      <div className="relative w-full max-w-3xl bg-zinc-950 border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden my-auto text-zinc-100">
        {/* Header */}
        <div className="px-6 pt-6 sm:pt-8 sm:px-8 pb-4 border-b border-zinc-800/80 flex items-start justify-between">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-300 text-xs font-medium mb-3">
              <Sparkles className="w-3.5 h-3.5 text-zinc-400" />
              <span>SözLab — 100% Avtonom AI Ovozli Markazi (1006 / 1007)</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
              Tizimga kirish turini tanlang
            </h2>
            <p className="text-xs sm:text-sm text-zinc-400 mt-1 max-w-xl">
              Rasmiy ta&apos;lim qonunchiligi (50 ta rasmiy FAQ va normativ ensiklopediya) asosida ishlovchi avtonom sun&apos;iy intellekt markazi.
            </p>
          </div>

          {hasSelectedRole && (
            <button
              onClick={handleDismiss}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-900 transition"
              title="Yopish"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* 2 Clean Monochrome Cards */}
        <div className="p-6 sm:p-8 grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Card 1: Fuqaro (Citizen) */}
          <div className="flex flex-col justify-between rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 hover:border-zinc-600 transition-all group">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-xl bg-zinc-800 border border-zinc-700 text-zinc-200 flex items-center justify-center">
                  <PhoneCall className="w-5 h-5" />
                </div>
                <span className="text-[10px] uppercase font-semibold tracking-wider px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
                  Fuqaro
                </span>
              </div>

              <h3 className="text-base font-semibold text-white group-hover:text-zinc-200">
                Ovozli Qo&apos;ng&apos;iroq (1006 / 1007)
              </h3>
              <p className="text-xs text-zinc-400 mt-2 leading-relaxed">
                Ta&apos;lim qonunchiligi, maktab, bog&apos;cha, OTM qabuli, grant va pedagoglar huquqlari bo&apos;yicha jonli ovozli maslahat.
              </p>

              <div className="mt-4 pt-4 border-t border-zinc-800/80 space-y-2 text-xs text-zinc-300">
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                  <span>VoiceLab Gulnoza tabiiy o&apos;zbek ovozi</span>
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                  <span>50 ta rasmiy FAQ va Qonun moddalari havolasi</span>
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                  <span>100% Avtonom AI — navbatsiz tezkor javob</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleSelectRole('citizen')}
              className="mt-6 w-full py-2.5 px-4 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 font-semibold text-xs flex items-center justify-center gap-2 transition active:scale-[0.98]"
            >
              <span>Qo&apos;ng&apos;iroqni boshlash</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Card 2: Vazirlik Ma'muri (Admin) */}
          <div className="flex flex-col justify-between rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 hover:border-zinc-600 transition-all group">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-xl bg-zinc-800 border border-zinc-700 text-zinc-200 flex items-center justify-center">
                  <Shield className="w-5 h-5" />
                </div>
                <span className="text-[10px] uppercase font-semibold tracking-wider px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
                  Nazorat
                </span>
              </div>

              <h3 className="text-base font-semibold text-white group-hover:text-zinc-200">
                Vazirlik Boshqaruv Paneli
              </h3>
              <p className="text-xs text-zinc-400 mt-2 leading-relaxed">
                Qo&apos;ng&apos;iroqlar monitoringi, 50 ta FAQ tahlili, Supabase arxivi va jonli suhbatlarni kuzatish.
              </p>

              <div className="mt-4 pt-4 border-t border-zinc-800/80 space-y-2 text-xs text-zinc-300">
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                  <span>Jonli transkripsiya teleprompteri</span>
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                  <span>Yuridik moddalar kesimida analitika</span>
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                  <span>100% Avtonom yechim darajasi nazorati</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleSelectRole('admin')}
              className="mt-6 w-full py-2.5 px-4 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-white font-semibold text-xs border border-zinc-700 flex items-center justify-center gap-2 transition active:scale-[0.98]"
            >
              <span>Admin paneliga o&apos;tish</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 sm:px-8 py-3.5 bg-zinc-950 border-t border-zinc-800/80 flex items-center justify-between text-xs text-zinc-500">
          <span>O&apos;zbekiston Respublikasi Ta&apos;lim Vazirliklari Yagona Axborot Tizimi</span>
          <span>SözLab Production v2.0</span>
        </div>
      </div>
    </div>
  );
}
