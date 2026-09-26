'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { PhoneCall, Shield, ArrowRight, X, User, Sparkles, CheckCircle2 } from 'lucide-react';
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-900/60 backdrop-blur-md animate-fade-in overflow-y-auto">
      <div className="relative w-full max-w-2xl bg-white border border-slate-200 rounded-3xl shadow-2xl overflow-hidden my-auto text-slate-900">
        {/* Header */}
        <div className="px-6 pt-6 sm:pt-8 sm:px-8 pb-4 border-b border-slate-100 flex items-start justify-between bg-slate-50/50">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-white p-1 border border-slate-200 shadow-sm flex items-center justify-center shrink-0">
              <img src="/sozlab-logo.png" alt="SözLab Logo" className="w-full h-full object-contain" />
            </div>
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full bg-[#035B60]/10 border border-[#035B60]/20 text-[#035B60] text-xs font-bold mb-2">
                <Sparkles className="w-3.5 h-3.5 text-[#FC6F01]" />
                <span>SÖZ<span className="text-[#FC6F01]">LAB</span> Avtonom Ovozli Markazi</span>
              </div>
              <h2 className="text-xl sm:text-2xl font-black tracking-tight text-slate-900">
                Tizimga kirish rolini tanlang
              </h2>
              <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
                Foydalanuvchi sifatida maslahat oling yoki Admin sifatida yagona monitoringdan foydalaning.
              </p>
            </div>
          </div>

          {hasSelectedRole && (
            <button
              onClick={handleDismiss}
              className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition cursor-pointer"
              title="Yopish"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* 2 Joyful Light Cards */}
        <div className="p-6 sm:p-8 grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Card 1: User (Citizen) */}
          <div className="flex flex-col justify-between rounded-2xl border-2 border-[#035B60]/20 bg-[#035B60]/5 p-6 hover:border-[#035B60] hover:shadow-lg hover:shadow-[#035B60]/10 transition-all group">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-[#035B60] text-white flex items-center justify-center shadow-md shadow-[#035B60]/20">
                  <User className="w-6 h-6" />
                </div>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded-full bg-[#035B60]/10 text-[#035B60]">
                  Foydalanuvchi
                </span>
              </div>

              <h3 className="text-lg font-extrabold text-slate-900 group-hover:text-[#035B60] transition">
                Foydalanuvchi Rejimi
              </h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                Ta&apos;lim qonunchiligi bo&apos;yicha tezkor ovozli muloqot va AI chat maslahatlari.
              </p>

              <div className="mt-4 pt-4 border-t border-[#035B60]/20 space-y-2 text-xs text-slate-700">
                <div className="flex items-center gap-2 text-xs font-medium">
                  <CheckCircle2 className="w-4 h-4 text-[#035B60] shrink-0" />
                  <span>Tabiiy o&apos;zbek ovozi (Hands-Free VAD 1.4s)</span>
                </div>
                <div className="flex items-center gap-2 text-xs font-medium">
                  <CheckCircle2 className="w-4 h-4 text-[#035B60] shrink-0" />
                  <span>AI Ovozli qo&apos;ng&apos;iroq va matnli chat</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleSelectRole('citizen')}
              className="mt-6 w-full py-3 px-4 rounded-xl bg-[#035B60] hover:bg-[#024A4E] text-white font-bold text-xs shadow-md shadow-[#035B60]/20 flex items-center justify-center gap-2 transition active:scale-[0.98] cursor-pointer"
            >
              <span>Foydalanuvchi sifatida kirish</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Card 2: Admin Monitoring */}
          <div className="flex flex-col justify-between rounded-2xl border-2 border-[#FC6F01]/20 bg-[#FC6F01]/5 p-6 hover:border-[#FC6F01] hover:shadow-lg hover:shadow-[#FC6F01]/10 transition-all group">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-[#FC6F01] text-white flex items-center justify-center shadow-md shadow-[#FC6F01]/20">
                  <Shield className="w-6 h-6" />
                </div>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded-full bg-[#FC6F01]/10 text-[#FC6F01]">
                  Admin Monitoring
                </span>
              </div>

              <h3 className="text-lg font-extrabold text-slate-900 group-hover:text-[#FC6F01] transition">
                Yagona Monitoring Markazi
              </h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                Jonli qo&apos;ng&apos;iroqlarni eshitish, bitta yaxlit audio ijrosi va taymlayn markerlari.
              </p>

              <div className="mt-4 pt-4 border-t border-[#FC6F01]/20 space-y-2 text-xs text-slate-700">
                <div className="flex items-center gap-2 text-xs font-medium">
                  <CheckCircle2 className="w-4 h-4 text-[#FC6F01] shrink-0" />
                  <span>Jonli audio va transkript monitoringi</span>
                </div>
                <div className="flex items-center gap-2 text-xs font-medium">
                  <CheckCircle2 className="w-4 h-4 text-[#FC6F01] shrink-0" />
                  <span>Uzluksiz audio va nutq pointerlari</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleSelectRole('admin')}
              className="mt-6 w-full py-3 px-4 rounded-xl bg-[#FC6F01] hover:bg-[#E56300] text-white font-bold text-xs shadow-md shadow-[#FC6F01]/20 flex items-center justify-center gap-2 transition active:scale-[0.98] cursor-pointer"
            >
              <span>Admin Monitoringga kirish</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
