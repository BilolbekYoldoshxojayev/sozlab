'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { PhoneCall, BarChart3, History, Shield, Sparkles, User, Settings, BookOpen } from 'lucide-react';
import { useRole, UserRole } from '@/lib/useRole';
import RoleGateModal from './RoleGateModal';

interface NavItem {
  href: string;
  label: string;
  icon: React.ElementType;
  allowedRoles: UserRole[];
}

const ALL_NAV_LINKS: NavItem[] = [
  { href: '/', label: 'Bosh Sahifa', icon: Sparkles, allowedRoles: ['citizen', 'admin'] },
  { href: '/call', label: "Ovozli Qo'ng'iroq (1006 / 1007)", icon: PhoneCall, allowedRoles: ['citizen'] },
  { href: '/history', label: 'Yuridik FAQ Baza (50)', icon: BookOpen, allowedRoles: ['citizen', 'admin'] },
  { href: '/admin', label: 'Admin Boshqaruvi', icon: Shield, allowedRoles: ['admin'] },
  { href: '/analytics', label: 'Analitika', icon: BarChart3, allowedRoles: ['admin'] },
];

export default function Navbar() {
  const pathname = usePathname();
  const { session, openRoleGate, isReady } = useRole();

  const getRoleBadge = () => {
    if (session.role === 'admin') {
      return {
        label: 'Vazirlik Admin',
        color: 'bg-zinc-800 text-zinc-200 border-zinc-700',
        icon: Shield,
        ctaHref: '/admin',
        ctaLabel: 'Admin Paneli',
        ctaClass: 'bg-zinc-800 hover:bg-zinc-700 text-white border border-zinc-700',
      };
    }
    return {
      label: session.citizenName || 'Fuqaro',
      color: 'bg-zinc-800 text-zinc-200 border-zinc-700',
      icon: User,
      ctaHref: '/call',
      ctaLabel: "Ovozli Qo'ng'iroq",
      ctaClass: 'bg-zinc-100 hover:bg-white text-zinc-950 font-semibold',
    };
  };

  const badge = getRoleBadge();
  const RoleIcon = badge.icon;

  const visibleLinks = isReady
    ? ALL_NAV_LINKS.filter((link) => link.allowedRoles.includes(session.role))
    : [];

  return (
    <>
      <header className="sticky top-0 z-50 bg-zinc-950/90 backdrop-blur-md border-b border-zinc-800/80">
        {/* Top Ministry Ribbon */}
        <div className="bg-black/90 text-zinc-400 text-xs py-1.5 px-4 sm:px-8 flex justify-between items-center border-b border-zinc-900">
          <div className="flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span className="font-medium tracking-wide text-zinc-300">
              O&apos;ZBEKISTON RESPUBLIKASI TA&apos;LIM VAZIRLIKLARI YAGONA AXBOROT TIZIMI
            </span>
          </div>
          <div className="flex items-center gap-4 text-[11px] font-medium text-zinc-400">
            <span className="hidden sm:inline">Ishonch Telefonlari: <strong className="text-zinc-200">1006 / 1007</strong></span>
            <span className="hidden md:inline">|</span>
            <span className="hidden md:inline">SözLab: <strong className="text-zinc-200">100% Avtonom AI</strong></span>
          </div>
        </div>

        {/* Main Navigation Bar */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-200 transition-colors group-hover:border-zinc-700">
              <Shield className="w-4 h-4 text-zinc-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base text-zinc-100 tracking-tight">SÖZLAB</span>
                <span className="bg-zinc-800 text-zinc-300 text-[10px] font-semibold px-2 py-0.5 rounded border border-zinc-700">
                  VoiceLab AI
                </span>
              </div>
              <p className="text-[11px] text-zinc-500 font-medium -mt-0.5">
                Avtonom Ta&apos;lim Call-Markazi
              </p>
            </div>
          </Link>

          {/* Dynamically Filtered Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {visibleLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-zinc-800 text-white'
                      : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-zinc-500'}`} />
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* Role Switcher & Action CTA */}
          <div className="flex items-center gap-2.5">
            <button
              onClick={openRoleGate}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition hover:border-zinc-600 active:scale-[0.98] ${badge.color}`}
              title="Rolni o'zgartirish"
            >
              <RoleIcon className="w-3.5 h-3.5 text-zinc-400" />
              <span className="truncate max-w-[120px]">{badge.label}</span>
              <Settings className="w-3 h-3 text-zinc-500 ml-0.5" />
            </button>

            <Link
              href={badge.ctaHref}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs transition active:scale-[0.98] ${badge.ctaClass}`}
            >
              <RoleIcon className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{badge.ctaLabel}</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Upfront & On-Demand Role Gate Modal */}
      <RoleGateModal />
    </>
  );
}
