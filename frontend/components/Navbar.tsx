'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { PhoneCall, Headset, BarChart3, History, Shield, Sparkles, User, Settings, Users } from 'lucide-react';
import { useRole } from '@/lib/useRole';
import RoleGateModal from './RoleGateModal';

export default function Navbar() {
  const pathname = usePathname();
  const { session, openRoleGate } = useRole();

  const navLinks = [
    { href: '/', label: 'Bosh Sahifa', icon: Sparkles },
    { href: '/call', label: 'Qo\'ng\'iroq Simulyatori', icon: PhoneCall },
    { href: '/operator', label: 'Operator Paneli', icon: Headset },
    { href: '/admin', label: 'Admin Boshqaruvi', icon: Shield },
    { href: '/analytics', label: 'Analitika', icon: BarChart3 },
    { href: '/history', label: 'Qo\'ng\'iroqlar Tarixi', icon: History },
  ];

  const getRoleBadge = () => {
    if (session.role === 'admin') {
      return {
        label: 'Vazirlik Admin',
        color: 'bg-purple-100 text-purple-800 border-purple-200',
        icon: Shield,
      };
    }
    if (session.role === 'operator') {
      return {
        label: session.operatorName || 'Operator',
        color: 'bg-blue-100 text-blue-800 border-blue-200',
        icon: Headset,
      };
    }
    return {
      label: session.citizenName || 'Fuqaro',
      color: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      icon: User,
    };
  };

  const badge = getRoleBadge();
  const RoleIcon = badge.icon;

  return (
    <>
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
        {/* Top Ministry Ribbon */}
        <div className="bg-[#081e38] text-white text-xs py-1.5 px-4 sm:px-8 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-medium tracking-wide">
              O&apos;ZBEKISTON RESPUBLIKASI OLIY TA&apos;LIM, FAN VA INNOVATSIYALAR VAZIRLIGI
            </span>
          </div>
          <div className="flex items-center gap-4 text-[11px] font-medium text-slate-300">
            <span className="hidden sm:inline">Yagona Ishonch Telefoni: <strong className="text-amber-300">1006</strong></span>
            <span className="hidden md:inline">|</span>
            <span className="hidden md:inline">Tizim: <strong>SözLab AI v1.0</strong></span>
          </div>
        </div>

        {/* Main Navigation Bar */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#0b2b50] to-[#1e6091] flex items-center justify-center text-white shadow-md shadow-blue-950/20 group-hover:scale-105 transition-transform">
              <Shield className="w-5 h-5 text-amber-300" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-lg text-slate-900 tracking-tight">SÖZLAB</span>
                <span className="bg-blue-100 text-[#0b2b50] text-[10px] font-bold px-1.5 py-0.5 rounded-full uppercase tracking-wider">
                  Ovozdosh AI
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium -mt-0.5">
                Oliy Ta&apos;lim AI Ovozli Call-Markazi
              </p>
            </div>
          </Link>


          {/* Navigation Links */}
          <nav className="hidden xl:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-[#0b2b50] text-white shadow-sm shadow-blue-900/20'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-amber-300' : 'text-slate-400'}`} />
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* Role Switcher & Live Call CTA */}
          <div className="flex items-center gap-2.5">
            {/* Role Button */}
            <button
              onClick={openRoleGate}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-semibold shadow-xs transition hover:opacity-90 active:scale-95 ${badge.color}`}
              title="Foydalanuvchi rolini o'zgartirish"
            >
              <RoleIcon className="w-3.5 h-3.5" />
              <span className="truncate max-w-[130px]">{badge.label}</span>
              <Settings className="w-3 h-3 opacity-60 ml-0.5" />
            </button>

            <Link
              href="/call"
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm shadow-emerald-700/20 hover:shadow-md transition-all active:scale-95"
            >
              <PhoneCall className="w-3.5 h-3.5 animate-bounce" />
              <span className="hidden sm:inline">Qo&apos;ng&apos;iroq Qilish</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Upfront & On-Demand Role Gate Gateway Modal */}
      <RoleGateModal />
    </>
  );
}
