'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  PhoneCall, Headset, Shield, Sparkles, Check, ArrowRight,
  User, CheckCircle2, ChevronRight, X
} from 'lucide-react';
import { useRole, UserRole } from '@/lib/useRole';

interface RoleGateModalProps {
  isOpen?: boolean;
  onClose?: () => void;
}

const OPERATORS_LIST = [
  { id: 'op-1', name: 'Nargiza Qodirova (Bosh operator #1)', role: 'Qabul va stipendiyalar bo\'yicha mutaxassis' },
  { id: 'op-2', name: 'Bekzod Aliyev (Katta mutaxassis #2)', role: 'Kontrakt va ta\'lim krediti bo\'yicha mutaxassis' },
  { id: 'op-3', name: 'Dilnoza Karimova (Konsultant #3)', role: 'Yotoqxona (TTJ) va nostrifikatsiya masalalari' },
];

export default function RoleGateModal({ isOpen, onClose }: RoleGateModalProps) {
  const router = useRouter();
  const { session, setRole, isRoleGateOpen, closeRoleGate, hasSelectedRole, isReady } = useRole();

  const [selectedOp, setSelectedOp] = useState(OPERATORS_LIST[0]);
  const [citizenName, setCitizenName] = useState('Rustam Usmonov');
  const [citizenPhone, setCitizenPhone] = useState('+998 (90) 777-88-99');

  // Determine whether modal is shown
  const showModal = isOpen !== undefined ? isOpen : (isReady && isRoleGateOpen);

  if (!showModal) return null;

  const handleSelectRole = (role: UserRole) => {
    if (role === 'citizen') {
      setRole('citizen');
      if (onClose) onClose();
      else closeRoleGate();
      router.push('/call');
    } else if (role === 'operator') {
      setRole('operator', selectedOp.id, selectedOp.name);
      if (onClose) onClose();
      else closeRoleGate();
      router.push('/operator');
    } else if (role === 'admin') {
      setRole('admin');
      if (onClose) onClose();
      else closeRoleGate();
      router.push('/admin');
    }
  };

  const handleDismiss = () => {
    if (onClose) {
      onClose();
    } else {
      closeRoleGate();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/85 backdrop-blur-xl animate-fade-in overflow-y-auto">
      <div className="relative w-full max-w-5xl bg-slate-900 border border-slate-700/80 rounded-3xl shadow-2xl overflow-hidden my-auto text-white">
        {/* Glow ambient effects */}
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-emerald-600/20 rounded-full blur-3xl pointer-events-none" />

        {/* Modal Header */}
        <div className="relative px-6 pt-6 sm:pt-8 sm:px-10 pb-4 border-b border-slate-800 flex items-start justify-between">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold mb-3">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Oliy ta&apos;lim, fan va innovatsiyalar vazirligi — SözLab AI</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              Tizimdan foydalanish uchun rolingizni tanlang
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 mt-1.5 max-w-2xl">
              Har bir noutbuk yoki qurilma o&apos;zining maxsus interfeysida mustaqil ishlaydi. 
              Rolingizga mos kartani tanlang:
            </p>
          </div>

          {hasSelectedRole && (
            <button
              onClick={handleDismiss}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
              title="Yopish"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* 3 Interactive Role Cards */}
        <div className="relative p-6 sm:p-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: Fuqaro (Citizen) */}
          <div className="flex flex-col justify-between rounded-2xl border border-emerald-500/30 bg-gradient-to-b from-emerald-950/40 to-slate-900/90 p-5 sm:p-6 hover:border-emerald-500 hover:shadow-xl hover:shadow-emerald-900/30 transition-all group">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform">
                  <PhoneCall className="w-6 h-6 text-emerald-400" />
                </div>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  Fuqaro
                </span>
              </div>

              <h3 className="text-lg font-bold text-white group-hover:text-emerald-300 transition-colors">
                🏛️ Fuqaro (Abituriyent)
              </h3>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                Oliy ta&apos;lim bo&apos;yicha ovozli AI yordamchisiga qo&apos;ng&apos;iroq qilish, tabiiy o&apos;zbek tilida savol berish va tezkor rasmiy javob olish.
              </p>

              <div className="mt-4 pt-4 border-t border-emerald-500/20 space-y-2 text-xs text-slate-300">
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>100vh iOS/Telegram ovozli aloqa</span>
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>Dinamik Voice Orb & Jonli Subtitr</span>
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>Zaruratda operator navbatiga ulanish</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleSelectRole('citizen')}
              className="mt-6 w-full py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-700/30 flex items-center justify-center gap-2 transition-all active:scale-95 group-hover:translate-y-[-1px]"
            >
              <span>Fuqaro sifatida kirish</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Card 2: Operator (Call-Center) */}
          <div className="flex flex-col justify-between rounded-2xl border border-blue-500/30 bg-gradient-to-b from-blue-950/40 to-slate-900/90 p-5 sm:p-6 hover:border-blue-500 hover:shadow-xl hover:shadow-blue-900/30 transition-all group">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-blue-500/20 border border-blue-500/40 text-blue-400 flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform">
                  <Headset className="w-6 h-6 text-blue-400" />
                </div>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40">
                  Operator
                </span>
              </div>

              <h3 className="text-lg font-bold text-white group-hover:text-blue-300 transition-colors">
                🎧 Call-Markaz Operatori
              </h3>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                AI yo&apos;naltirgan fuqarolar qo&apos;ng&apos;iroqlarini qabul qilish, FIFO navbati va jonli muloqot o&apos;tkazish.
              </p>

              {/* Operator Selector */}
              <div className="mt-4 pt-3 border-t border-blue-500/20">
                <label className="text-[11px] font-semibold text-slate-300 block mb-1.5">
                  Operator shaxsi va litsenziyasi:
                </label>
                <select
                  value={selectedOp.id}
                  onChange={(e) => {
                    const found = OPERATORS_LIST.find((o) => o.id === e.target.value);
                    if (found) setSelectedOp(found);
                  }}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-2.5 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {OPERATORS_LIST.map((op) => (
                    <option key={op.id} value={op.id} className="bg-slate-900 text-white">
                      {op.name}
                    </option>
                  ))}
                </select>
                <p className="text-[10px] text-blue-300 mt-1 line-clamp-1">
                  {selectedOp.role}
                </p>
              </div>

              <div className="mt-3 space-y-1.5 text-xs text-slate-300">
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                  <span>Real-vaqtli FIFO navbat taqsimoti</span>
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                  <span>3 soniyalik avtomatik navbatga ulanish</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleSelectRole('operator')}
              className="mt-6 w-full py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-700/30 flex items-center justify-center gap-2 transition-all active:scale-95 group-hover:translate-y-[-1px]"
            >
              <span>Operator sifatida kirish</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Card 3: Vazirlik Ma'muri (Admin) */}
          <div className="flex flex-col justify-between rounded-2xl border border-purple-500/30 bg-gradient-to-b from-purple-950/40 to-slate-900/90 p-5 sm:p-6 hover:border-purple-500 hover:shadow-xl hover:shadow-purple-900/30 transition-all group">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-purple-500/20 border border-purple-500/40 text-purple-400 flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform">
                  <Shield className="w-6 h-6 text-purple-400" />
                </div>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40">
                  Admin
                </span>
              </div>

              <h3 className="text-lg font-bold text-white group-hover:text-purple-300 transition-colors">
                🛡️ Vazirlik Ma&apos;muri (Admin)
              </h3>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                Tizim monitoringi, operatorlar floti nazorati, bilimlar bazasi va jonli suhbatlarni yashirin tinglash (Ghost Mode).
              </p>

              <div className="mt-4 pt-4 border-t border-purple-500/20 space-y-2 text-xs text-slate-300">
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                  <span>🎧 Ghost Mode — Yashirin ovozli eshitish</span>
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                  <span>Jonli transkripsiya teleprompteri</span>
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                  <span>100% ko&apos;rinmas kuzatuv (nol bildirishnoma)</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleSelectRole('admin')}
              className="mt-6 w-full py-3 px-4 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-700/30 flex items-center justify-center gap-2 transition-all active:scale-95 group-hover:translate-y-[-1px]"
            >
              <span>Admin sifatida kirish</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Footer info note */}
        <div className="px-6 sm:px-10 py-4 bg-slate-950/60 border-t border-slate-800 text-center text-xs text-slate-400 flex items-center justify-between">
          <span>Namangan Hakaton — Oliy ta&apos;lim, fan va innovatsiyalar vazirligi treki</span>
          <span className="text-slate-500">Istalgan vaqt Navbar orqali rolni almashtirish mumkin</span>
        </div>
      </div>
    </div>
  );
}
