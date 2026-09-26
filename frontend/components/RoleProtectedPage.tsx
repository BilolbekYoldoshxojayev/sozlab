'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { ShieldAlert, ArrowRight, Shield, PhoneCall, AlertOctagon, Headset } from 'lucide-react';
import { useRole, UserRole } from '@/lib/useRole';

export interface RoleProtectedPageProps {
  allowedRoles?: UserRole[];
  requiredRole?: UserRole;
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
    name: 'Fuqaro (Ovozli AI)',
    primaryPath: '/call',
    primaryLabel: "Fuqaro Ovozli Xonasiga O'tish",
    icon: PhoneCall,
    badgeClass: 'bg-zinc-800 text-zinc-200 border-zinc-700',
    buttonClass: 'bg-zinc-100 hover:bg-white text-zinc-950',
  },
  operator: {
    name: 'Inson Operator',
    primaryPath: '/operator',
    primaryLabel: "Operator Paneliga O'tish",
    icon: Headset,
    badgeClass: 'bg-zinc-800 text-zinc-200 border-zinc-700',
    buttonClass: 'bg-zinc-800 hover:bg-zinc-700 text-white border border-zinc-700',
  },
  admin: {
    name: "Vazirlik Ma'muri (Admin)",
    primaryPath: '/admin',
    primaryLabel: 'Admin Boshqaruviga Qaytish',
    icon: Shield,
    badgeClass: 'bg-zinc-800 text-zinc-200 border-zinc-700',
    buttonClass: 'bg-zinc-800 hover:bg-zinc-700 text-white border border-zinc-700',
  },
};

export default function RoleProtectedPage({
  allowedRoles,
  requiredRole,
  children,
  fallbackPath,
}: RoleProtectedPageProps) {
  const router = useRouter();
  const { session, isReady, hasSelectedRole, openRoleGate } = useRole();

  if (!isReady) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center p-6 text-center animate-fade-in">
        <div className="w-10 h-10 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-3">
          <Shield className="w-5 h-5 text-zinc-400 animate-pulse" />
        </div>
        <p className="text-xs font-medium text-zinc-500 tracking-wide">
          Ruxsat tekshiruvi...
        </p>
      </div>
    );
  }

  if (!hasSelectedRole) return null;

  const effectiveRoles = allowedRoles || (requiredRole ? [requiredRole] : []);
  const isAuthorized = effectiveRoles.includes(session.role);
  if (isAuthorized) return <>{children}</>;

  const currentRoleMeta = ROLE_METAS[session.role] || ROLE_METAS.citizen;
  const targetPath = fallbackPath || currentRoleMeta.primaryPath;
  const allowedNames = effectiveRoles.map((r) => ROLE_METAS[r]?.name || r).join(', ');

  return (
    <div className="min-h-[70vh] flex items-center justify-center p-4 sm:p-6 animate-fade-in">
      <div className="relative w-full max-w-lg bg-zinc-950 border border-zinc-800 rounded-2xl shadow-2xl p-6 sm:p-8 text-center text-zinc-100">
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs font-medium mb-5">
          <AlertOctagon className="w-3.5 h-3.5 text-zinc-400" />
          <span>Kirish Cheklangan (403)</span>
        </div>

        <div className="w-14 h-14 mx-auto rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-300 flex items-center justify-center mb-4">
          <ShieldAlert className="w-7 h-7 text-zinc-300" />
        </div>

        <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white mb-2">
          Ushbu sahifaga kirish cheklangan
        </h2>
        <p className="text-xs text-zinc-400 mb-6 leading-relaxed">
          Ushbu bo&apos;limdan foydalanish uchun tegishli rol huquqi talab etiladi.
        </p>

        <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-4 mb-6 text-left space-y-2.5 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-zinc-500">Sizning joriy rolingiz:</span>
            <span className={`px-2 py-0.5 rounded border text-[11px] font-medium ${currentRoleMeta.badgeClass}`}>
              {currentRoleMeta.name}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-zinc-500">Talab etiladigan rol:</span>
            <span className="px-2 py-0.5 rounded border border-zinc-800 bg-zinc-900 text-zinc-300 font-medium text-[11px]">
              {allowedNames}
            </span>
          </div>
        </div>

        <div className="space-y-2.5">
          <button
            onClick={() => router.push(targetPath)}
            className={`w-full py-2.5 px-4 rounded-lg font-semibold text-xs flex items-center justify-center gap-2 transition active:scale-[0.98] ${currentRoleMeta.buttonClass}`}
          >
            <span>{currentRoleMeta.primaryLabel}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={openRoleGate}
            className="w-full py-2 px-4 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-400 hover:text-white font-medium text-xs transition"
          >
            Rolni almashtirish
          </button>
        </div>
      </div>
    </div>
  );
}
