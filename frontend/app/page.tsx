'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import {
  PhoneCall, Headset, BarChart3, ShieldCheck, Sparkles,
  BookOpen, Clock, Bot, ArrowRight, Zap, CheckCircle2,
  Users, User, Shield, PhoneForwarded
} from 'lucide-react';
import CommonQuestions from '@/components/CommonQuestions';
import { useRole } from '@/lib/useRole';

export default function HomePage() {
  const router = useRouter();
  const { session, isReady, hasSelectedRole, setRole } = useRole();

  useEffect(() => {
    if (isReady && hasSelectedRole) {
      if (session.role === 'operator') {
        router.replace('/operator');
      } else if (session.role === 'admin') {
        router.replace('/admin');
      }
    }
  }, [isReady, hasSelectedRole, session.role, router]);

  const highlights = [
    {
      title: 'Dual-AI Ovozli Muloqot',
      desc: 'Aisha AI va Edge-TTS orqali uzluksiz, tabiiy o\'zbek tilida ovozli muloqot va real vaqtli transkripsiya (< 1.2s javob tezligi).',
      icon: Sparkles,
      color: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
    {
      title: 'Rasmiy Bilimlar Bazasi',
      desc: 'Qabul, grant, super-kontrakt, TTJ va nostrifikatsiya bo\'yicha vazirlikning tasdiqlangan rasmiy me\'yorlari (100% rasmiy manba).',
      icon: BookOpen,
      color: 'bg-blue-50 text-blue-700 border-blue-200',
    },
    {
      title: 'Aqlli FIFO Navbat',
      desc: 'Murakkab murojaatlarni navbatchi operatorlar flotiga avtomatik va kechikishsiz yo\'naltirish (Zero-drop dispatch).',
      icon: Headset,
      color: 'bg-amber-50 text-amber-700 border-amber-200',
    },
  ];

  const steps = [
    {
      step: '01',
      title: 'Ovozli Murojaat',
      desc: 'Mikrofon orqali savolingizni tabiiy o\'zbek tilida bering.',
    },
    {
      step: '02',
      title: 'Tezkor Tahlil',
      desc: 'Gemini va me\'yoriy baza asosida rasmiy javob topiladi.',
    },
    {
      step: '03',
      title: 'Ovozli Javob',
      desc: 'Tabiiy ovozda javob beriladi va jonli subtitr aks etadi.',
    },
    {
      step: '04',
      title: 'Operator Yordami',
      desc: 'Zarur hollarda qo\'ng\'iroq navbatchi operatorga uzatiladi.',
    },
  ];

  return (
    <div className="flex flex-col gap-12 py-4 sm:py-8">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#081e38] via-[#0b2b50] to-[#1e6091] text-white p-8 sm:p-12 lg:p-16 shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-emerald-400/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 backdrop-blur border border-white/20 text-xs font-semibold text-amber-300 mb-6">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Oliy Ta&apos;lim Ovozli AI Platformasi</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight mb-6">
            Ta&apos;lim va Innovatsiyalar Vazirligi uchun{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-emerald-300 to-sky-200">
              Sun&apos;iy Intellektli Ovozli Call Markaz
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-200 leading-relaxed mb-8 max-w-2xl font-normal">
            Oliy ta&apos;lim bo&apos;yicha barcha savollarga 24/7 rejimida tabiiy o&apos;zbek tilida tezkor ovozli javob beruvchi intellektual call-markaz.
          </p>

          <div className="flex flex-wrap items-center gap-4">
            <Link
              href="/call"
              onClick={() => setRole('citizen')}
              className="flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-sm shadow-lg shadow-emerald-900/30 transition-all hover:scale-105 active:scale-95"
            >
              <PhoneCall className="w-4 h-4 animate-bounce" />
              <span>Ovozli Qo&apos;ng&apos;iroqni Boshlash</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/operator"
              onClick={() => setRole('operator', 'op-1', 'Nargiza Qodirova')}
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-semibold text-sm backdrop-blur transition-all"
            >
              <Headset className="w-4 h-4 text-amber-300" />
              <span>Operator Paneliga O&apos;tish</span>
            </Link>

            <Link
              href="/admin"
              onClick={() => setRole('admin')}
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-semibold text-sm backdrop-blur transition-all"
            >
              <Shield className="w-4 h-4 text-purple-300" />
              <span>Admin Boshqaruvi</span>
            </Link>
          </div>
        </div>

        {/* Floating Quick Stats Badge */}
        <div className="mt-10 pt-8 border-t border-white/10 grid grid-cols-2 sm:grid-cols-4 gap-4 text-center sm:text-left">
          <div>
            <div className="text-2xl font-extrabold text-amber-300 font-mono">85.4%</div>
            <div className="text-xs text-slate-300 font-medium">AI orqali avtomatik hal etish</div>
          </div>
          <div>
            <div className="text-2xl font-extrabold text-emerald-300 font-mono">&lt; 1.2s</div>
            <div className="text-xs text-slate-300 font-medium">Ovozli javob tezligi</div>
          </div>
          <div>
            <div className="text-2xl font-extrabold text-sky-300 font-mono">3 Operator</div>
            <div className="text-xs text-slate-300 font-medium">Smart navbat & dispatch</div>
          </div>
          <div>
            <div className="text-2xl font-extrabold text-indigo-300 font-mono">24 / 7</div>
            <div className="text-xs text-slate-300 font-medium">To&apos;xtovsiz xizmat</div>
          </div>
        </div>
      </div>

      {/* 3 Distinct User Roles Section */}
      <div className="bg-white rounded-3xl border border-slate-200 p-8 sm:p-10 shadow-sm">
        <div className="text-center max-w-2xl mx-auto mb-8">
          <span className="text-xs font-bold text-emerald-700 uppercase tracking-wider bg-emerald-50 px-3 py-1 rounded-full border border-emerald-100">
            Foydalanuvchi Tajribasi
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-3 mb-2">
            3 Ta Alohida Rol Orqali Tizimga Kiring
          </h2>
          <p className="text-xs sm:text-sm text-slate-500">
            Tizimdan fuqaro, operator yoki vazirlik ma&apos;muri sifatida foydalaning.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Role 1: Citizen */}
          <div className="p-6 rounded-2xl border border-emerald-200 bg-gradient-to-b from-emerald-50/40 to-white flex flex-col justify-between hover:shadow-md transition">
            <div>
              <div className="w-12 h-12 rounded-xl bg-emerald-500 text-white flex items-center justify-center font-bold mb-4 shadow-md shadow-emerald-500/20">
                <User className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 mb-1">1. Fuqaro (Citizen)</h3>
              <p className="text-xs text-slate-600 mb-4 leading-relaxed">
                Vazirlik AI yordamchisiga mikrofon orqali gapirib savol beradi, rasmiy javobni ovozli tinglaydi, kerak bo&apos;lsa navbatga turadi.
              </p>
            </div>
            <Link
              href="/call"
              onClick={() => setRole('citizen')}
              className="w-full text-center py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition"
            >
              Fuqaro Sifatida Kirish →
            </Link>
          </div>

          {/* Role 2: Operator */}
          <div className="p-6 rounded-2xl border border-blue-200 bg-gradient-to-b from-blue-50/40 to-white flex flex-col justify-between hover:shadow-md transition">
            <div>
              <div className="w-12 h-12 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold mb-4 shadow-md shadow-blue-600/20">
                <Headset className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 mb-1">2. Inson-Operator</h3>
              <p className="text-xs text-slate-600 mb-4 leading-relaxed">
                AI yo&apos;naltirgan yoki navbatdagi fuqarolarni qabul qiladi, real-vaqtda chat yozishadi va qo&apos;ng&apos;iroqni yakunlaydi.
              </p>
            </div>
            <Link
              href="/operator"
              onClick={() => setRole('operator', 'op-1', 'Nargiza Qodirova')}
              className="w-full text-center py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-sm transition"
            >
              Operator Sifatida Kirish →
            </Link>
          </div>

          {/* Role 3: Admin */}
          <div className="p-6 rounded-2xl border border-purple-200 bg-gradient-to-b from-purple-50/40 to-white flex flex-col justify-between hover:shadow-md transition">
            <div>
              <div className="w-12 h-12 rounded-xl bg-purple-600 text-white flex items-center justify-center font-bold mb-4 shadow-md shadow-purple-600/20">
                <Shield className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 mb-1">3. Vazirlik Ma&apos;muri (Admin)</h3>
              <p className="text-xs text-slate-600 mb-4 leading-relaxed">
                Barcha 3 operator holati, jonli FIFO navbat oqimi, RAG bilimlar bazasi va umumiy tizim yuklamasini nazorat qiladi.
              </p>
            </div>
            <Link
              href="/admin"
              onClick={() => setRole('admin')}
              className="w-full text-center py-2.5 px-4 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs shadow-sm transition"
            >
              Admin Sifatida Kirish →
            </Link>
          </div>
        </div>
      </div>

      {/* Interactive Official FAQ Section */}
      <CommonQuestions />

      {/* Core Advantages */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {highlights.map((h, i) => {
          const Icon = h.icon;
          return (
            <div
              key={i}
              className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow"
            >
              <div>
                <div className={`w-11 h-11 rounded-xl border flex items-center justify-center mb-4 ${h.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base text-slate-900 mb-2">{h.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed">{h.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* How it Works Section */}
      <div className="bg-white rounded-3xl border border-slate-200 p-8 sm:p-12 shadow-sm">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <span className="text-xs font-bold text-blue-700 uppercase tracking-wider bg-blue-50 px-3 py-1 rounded-full border border-blue-100">
            Tizim Mexanizmi
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-3 mb-2">
            SözLab Qanday Ishlaydi?
          </h2>

          <p className="text-xs sm:text-sm text-slate-500">
            Fuqaro murojaatidan to rasmiy ovozli javobgacha bo&apos;lgan to&apos;liq jarayon.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((st, i) => (
            <div key={i} className="relative flex flex-col p-5 bg-slate-50 rounded-2xl border border-slate-200">
              <span className="text-3xl font-black text-slate-300 font-mono mb-2">{st.step}</span>
              <h4 className="font-bold text-sm text-slate-900 mb-1.5">{st.title}</h4>
              <p className="text-xs text-slate-600 leading-relaxed">{st.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
