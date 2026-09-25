'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import {
  ShieldAlert, ArrowRight, Shield, PhoneCall, Headset,
  AlertOctagon, RefreshCw
} from 'lucide-react';
import { useRole, UserRole } from '@/lib/useRole';

export interface RoleProtectedPageProps {
  allowedRoles: UserRole[];
  children: React.ReactNode;
  fallbackPath?: string;
}

interface RoleMeta {
  name: string;
  primaryPath: string;
  primaryLabel: string;
  icon: React.ElementType;
  badgeClass: string;
  buttonClass: string;
}

const ROLE_METAS: Record<UserRole, RoleMeta> = {
  citizen: {
    name: 'Fuqaro (Abituriyent)',
    primaryPath: '/call',
    primaryLabel: "Fuqaro Ovozli Xonasiga O'tish",
    icon: PhoneCall,
    badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    buttonClass: 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/30',
  },
  operator: {
    name: 'Call-Markaz Operatori',
    primaryPath: '/operator',
    primaryLabel: 'Operator Paneliga Qaytish',
    icon: Headset,
    badgeClass: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    buttonClass: 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/30',
  },
  admin: {
    name: "Vazirlik Ma'muri (Admin)",
    primaryPath: '/admin',
    primaryLabel: 'Admin Boshqaruviga Qaytish',
    icon: Shield,
    badgeClass: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    buttonClass: 'bg-purple-600 hover:bg-purple-500 text-white shadow-purple-900/30',
  },
};

export default function RoleProtectedPage({
  allowedRoles,
  children,
  fallbackPath,
}: RoleProtectedPageProps) {
  const router = useRouter();
  const { session, isReady, hasSelectedRole, openRoleGate } = useRole();

  // 1. Prevent Flash of Unauthorized Content (FOUC) while reading localStorage
  if (!isReady) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center p-6 text-center animate-fade-in">
        <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center shadow-xl mb-3">
          <Shield className="w-6 h-6 text-blue-400 animate-pulse" />
        </div>
        <p className="text-xs font-semibold text-slate-400 tracking-wide">
          Xavfsizlik &amp; Ruxsat tekshiruvi...
        </p>
      </div>
    );
  }

  // 2. If user hasn't selected a role yet, RoleGateModal is open
  if (!hasSelectedRole) {
    return null;
  }

  // 3. Authorization check
  const isAuthorized = allowedRoles.includes(session.role);

  if (isAuthorized) {
    return <>{children}</>;
  }

  // 4. Unauthorized "Kirish Cheklangan" (Access Restricted) Screen
  const currentRoleMeta = ROLE_METAS[session.role] || ROLE_METAS.citizen;
  const targetPath = fallbackPath || currentRoleMeta.primaryPath;
  const allowedNames = allowedRoles.map((r) => ROLE_METAS[r]?.name || r).join(', ');

  return (
    <div className="min-h-[70vh] flex items-center justify-center p-4 sm:p-6 animate-fade-in">
      <div className="relative w-full max-w-xl bg-slate-900/95 backdrop-blur-xl border border-rose-500/30 rounded-3xl shadow-2xl overflow-hidden p-6 sm:p-10 text-center text-white">
        {/* Ambient background glows */}
        <div className="absolute -top-20 -left-20 w-64 h-64 bg-rose-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 -right-20 w-64 h-64 bg-amber-600/10 rounded-full blur-3xl pointer-events-none" />

        {/* Top Security Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold mb-5">
          <AlertOctagon className="w-3.5 h-3.5 text-rose-400" />
          <span>Oyna Izolyatsiyasi: Kirish Cheklangan (403)</span>
        </div>

        {/* Warning Icon Badge */}
        <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-rose-500/20 to-rose-950/40 border border-rose-500/40 text-rose-400 flex items-center justify-center shadow-lg shadow-rose-950/50 mb-4">
          <ShieldAlert className="w-8 h-8 text-rose-400 animate-pulse" />
        </div>

        {/* Heading & Subtitle */}
        <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white mb-2">
          Kirish Cheklangan
        </h2>
        <p className="text-xs sm:text-sm text-slate-300 mb-6 leading-relaxed">
          Ushbu xizmat oynasidan foydalanish uchun sizda yetarli huquq mavjud emas. 3 ta noutbukli tizim arxitekturasida har bir rol faqat o&apos;ziga biriktirilgan xonada ishlashi belgilangan.
        </p>

        {/* Role Comparison Details Box */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-2xl p-4 mb-6 text-left space-y-2.5 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Sizning joriy rolingiz:</span>
            <span className={`px-2 py-0.5 rounded-full border text-[11px] font-bold ${currentRoleMeta.badgeClass}`}>
              {currentRoleMeta.name}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Talab etiladigan rol:</span>
            <span className="px-2 py-0.5 rounded-full border border-slate-700 bg-slate-800 text-amber-300 font-semibold text-[11px]">
              {allowedNames}
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={() => router.push(targetPath)}
            className={`w-full py-3.5 px-5 rounded-xl font-bold text-xs shadow-lg flex items-center justify-center gap-2 transition-all active:scale-95 ${currentRoleMeta.buttonClass}`}
          >
            <span>{currentRoleMeta.primaryLabel}</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <button
            onClick={openRoleGate}
            className="w-full py-2.5 px-4 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white font-medium text-xs transition"
          >
            Rolni almashtirish (Shlyuz)
          </button>
        </div>
      </div>
    </div>
  );
}
