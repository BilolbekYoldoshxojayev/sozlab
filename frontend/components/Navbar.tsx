'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { PhoneCall, MessageSquare, Shield, User, Settings, BarChart3 } from 'lucide-react';
import { useRole } from '@/lib/useRole';
import RoleGateModal from './RoleGateModal';

export default function Navbar() {
  const pathname = usePathname();
  const { session, openRoleGate, hasSelectedRole } = useRole();

  const isAdmin = session.role === 'admin';
  const isHomePage = pathname === '/';

  // Hide navbar entirely on home page (role selection screen)
  if (isHomePage) {
    return <RoleGateModal />;
  }

  return (
    <>
      {/* Top Header Navbar */}
      <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-xs backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-14 sm:h-16">
          {/* Logo */}
          <Link href={isAdmin ? "/admin" : "/call"} className="flex items-center gap-3 group">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-white p-1 border border-slate-200 shadow-sm flex items-center justify-center transition-all group-hover:scale-105">
              <img src="/sozlab-logo.png" alt="SözLab Logo" className="w-full h-full object-contain" />
            </div>
            <div className="flex flex-col">
              <span className="font-black text-lg tracking-tight leading-none text-[#035B60] flex items-center">
                SÖZ<span className="text-[#FC6F01]">LAB</span>
              </span>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider leading-none mt-1">
                {isAdmin ? "Monitoring Paneli" : "Ovozli Maslahat"}
              </span>
            </div>
          </Link>

          {/* Top Admin Status Badge if Role is Admin (Single Monitoring Interface) */}
          {isAdmin && (
            <div className="hidden sm:flex items-center gap-2">
              <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold bg-[#035B60]/10 text-[#035B60] border border-[#035B60]/20">
                <span className="w-2 h-2 rounded-full bg-[#FC6F01] animate-ping" />
                <span>Yagona Jonli Monitoring</span>
              </div>
            </div>
          )}

          {/* Right Action: Role Switcher */}
          <div className="flex items-center gap-2">
            <button
              onClick={openRoleGate}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition active:scale-95 shadow-xs cursor-pointer"
              title="Rolni tanlash"
            >
              {isAdmin ? (
                <Shield className="w-4 h-4 text-[#FC6F01]" />
              ) : (
                <User className="w-4 h-4 text-[#035B60]" />
              )}
              <span className="font-bold">{isAdmin ? "Admin" : "Foydalanuvchi"}</span>
              <Settings className="w-3.5 h-3.5 text-slate-400" />
            </button>
          </div>
        </div>
      </header>

      {/* Bottom Floating 2-Button Navbar for User (Citizen) */}
      {!isAdmin && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 w-full max-w-xs px-4">
          <div className="bg-white/95 backdrop-blur-lg border border-slate-200 shadow-xl rounded-2xl p-1.5 flex items-center justify-around gap-2">
            <Link
              href="/call"
              className={`flex-1 flex flex-col items-center justify-center py-2 px-3 rounded-xl transition-all ${
                pathname === '/call'
                  ? 'bg-[#035B60] text-white font-bold shadow-md shadow-[#035B60]/25'
                  : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100 font-medium'
              }`}
            >
              <PhoneCall className="w-5 h-5" />
              <span className="text-[11px] mt-0.5">Qo&apos;ng&apos;iroq</span>
            </Link>

            <Link
              href="/chat"
              className={`flex-1 flex flex-col items-center justify-center py-2 px-3 rounded-xl transition-all ${
                pathname === '/chat'
                  ? 'bg-[#FC6F01] text-white font-bold shadow-md shadow-[#FC6F01]/25'
                  : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100 font-medium'
              }`}
            >
              <MessageSquare className="w-5 h-5" />
              <span className="text-[11px] mt-0.5">AI Chat</span>
            </Link>
          </div>
        </div>
      )}

      {/* Role Gate Modal */}
      <RoleGateModal />
    </>
  );
}

