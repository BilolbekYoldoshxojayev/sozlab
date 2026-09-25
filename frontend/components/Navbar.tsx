'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { PhoneCall, Headset, BarChart3, History, Shield, Sparkles, User, Settings } from 'lucide-react';
import { useRole, UserRole } from '@/lib/useRole';
import RoleGateModal from './RoleGateModal';

interface NavItem {
  href: string;
  label: string;
  icon: React.ElementType;
  allowedRoles: UserRole[];
}

const ALL_NAV_LINKS: NavItem[] = [
  { href: '/', label: 'Bosh Sahifa', icon: Sparkles, allowedRoles: ['citizen'] },
  { href: '/call', label: 'Qo\'ng\'iroq Simulyatori', icon: PhoneCall, allowedRoles: ['citizen'] },
  { href: '/operator', label: 'Operator Paneli', icon: Headset, allowedRoles: ['operator'] },
  { href: '/admin', label: 'Admin Boshqaruvi', icon: Shield, allowedRoles: ['admin'] },
  { href: '/analytics', label: 'Analitika', icon: BarChart3, allowedRoles: ['admin'] },
  { href: '/history', label: 'Qo\'ng\'iroqlar Tarixi', icon: History, allowedRoles: ['operator', 'admin'] },
];

export default function Navbar() {
  const pathname = usePathname();
  const { session, openRoleGate, isReady } = useRole();

  const getRoleBadge = () => {
    if (session.role === 'admin') {
      return {
        label: 'Vazirlik Admin',
        color: 'bg-purple-100 text-purple-800 border-purple-200',
        icon: Shield,
        ctaHref: '/admin',
        ctaLabel: 'Boshqaruv Paneli',
        ctaClass: 'bg-purple-700 hover:bg-purple-800 text-white shadow-purple-900/20',
      };
    }
    if (session.role === 'operator') {
      return {
        label: session.operatorName || 'Operator',
        color: 'bg-blue-100 text-blue-800 border-blue-200',
        icon: Headset,
        ctaHref: '/operator',
        ctaLabel: 'Operator Paneli',
        ctaClass: 'bg-blue-600 hover:bg-blue-700 text-white shadow-blue-800/20',
      };
    }
    return {
      label: session.citizenName || 'Fuqaro',
      color: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      icon: User,
      ctaHref: '/call',
      ctaLabel: "Qo'ng'iroq Qilish",
      ctaClass: 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-700/20',
    };
  };

  const badge = getRoleBadge();
  const RoleIcon = badge.icon;

  // Filter links dynamically according to active role
  const visibleLinks = isReady
    ? ALL_NAV_LINKS.filter((link) => link.allowedRoles.includes(session.role))
    : [];

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

          {/* Dynamically Filtered Navigation Links */}
          <nav className="hidden xl:flex items-center gap-1">
            {visibleLinks.map((link) => {
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

          {/* Role Switcher & Dynamic Action CTA */}
          <div className="flex items-center gap-2.5">
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
              href={badge.ctaHref}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold shadow-sm hover:shadow-md transition-all active:scale-95 ${badge.ctaClass}`}
            >
              <RoleIcon className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{badge.ctaLabel}</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Upfront & On-Demand Role Gate Gateway Modal */}
      <RoleGateModal />
    </>
  );
}
