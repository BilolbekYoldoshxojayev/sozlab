'use client';

import Link from 'next/link';
import {
  PhoneCall, Shield, Sparkles, BookOpen, Clock, Bot,
  ArrowRight, ShieldCheck, CheckCircle2, FileText, Scale
} from 'lucide-react';
import CommonQuestions from '@/components/CommonQuestions';
import { useRole } from '@/lib/useRole';

export default function HomePage() {
  const { setRole } = useRole();

  const coreFeatures = [
    {
      title: 'VoiceLab Gulnoza Ovoz Modeli',
      desc: 'VoiceLab Studio SDK orqali tabiiy, ravon va professional o\'zbek adabiy tilidagi ovoz sintezi va tezkor transkripsiya.',
      icon: Sparkles,
    },
    {
      title: '50 ta Rasmiy FAQ va Ensiklopediya',
      desc: 'Maktab, bog\'cha, OTM qabuli, davlat grantlari, pedagoglar huquqlari va ta\'lim standartlari bo\'yicha to\'liq normativ baza.',
      icon: BookOpen,
    },
    {
      title: 'Qat\'iy Huquqiy Cheklov (Guardrail)',
      desc: 'AI faqat ta\'lim qonunchiligi (Konstitutsiya, O\'RQ-637, O\'RQ-901, VMQ) asosida aniq javob beradi; sohadan tashqari mavzularga to\'qima javob bermaydi.',
      icon: Scale,
    },
  ];

  const workflowStages = [
    {
      num: '01',
      title: 'Ovozli Savol',
      desc: 'Fuqaro mikrofonga erkin va tabiiy o\'zbek tilida savol beradi.',
    },
    {
      num: '02',
      title: 'VoiceLab STT',
      desc: 'VoiceLab rasmiy nutq modeli orqali ovoz aniq matnga o\'giriladi.',
    },
    {
      num: '03',
      title: 'Yuridik RAG Tahlili',
      desc: '50 ta rasmiy FAQ va normativ ensiklopediyadan qonuniy asoslar topiladi.',
    },
    {
      num: '04',
      title: 'Ovozli Javob & Subtitr',
      desc: 'VoiceLab Gulnoza ovozida rasmiy moddalar keltirilib, javob qaytadi.',
    },
  ];

  return (
    <div className="flex flex-col gap-10 py-4 sm:py-8 text-zinc-100 max-w-6xl mx-auto px-4">
      {/* Hero Section: Minimalist Obsidian Enterprise */}
      <div className="relative overflow-hidden rounded-2xl bg-zinc-900 border border-zinc-800 p-8 sm:p-12 lg:p-14 shadow-2xl">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-800 border border-zinc-700 text-xs font-medium text-zinc-300 mb-6">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>1006 / 1007 Yagona Avtonom Ovozli Markaz</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-bold tracking-tight text-white leading-tight mb-5">
            O&apos;zbekiston Respublikasi Ta&apos;lim Vazirliklari uchun{' '}
            <span className="text-zinc-200">
              100% Avtonom AI Ovozli Call-Markazi
            </span>
          </h1>

          <p className="text-sm sm:text-base text-zinc-400 leading-relaxed mb-8 max-w-2xl font-normal">
            Maktabgacha ta&apos;lim, maktablar, oliy ta&apos;lim qabuli, davlat grantlari va pedagoglar huquqiy himoyasi bo&apos;yicha barcha savollarga 24/7 rejimida tabiiy o&apos;zbek tilida rasmiy qonuniy asoslangan ovozli maslahat.
          </p>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              href="/call"
              onClick={() => setRole('citizen')}
              className="flex items-center gap-2 px-6 py-3 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 font-semibold text-xs transition active:scale-95 shadow-md"
            >
              <PhoneCall className="w-4 h-4" />
              <span>Ovozli Qo&apos;ng&apos;iroqni Boshlash</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Link>

            <Link
              href="/history"
              className="flex items-center gap-2 px-5 py-3 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 font-medium text-xs transition active:scale-95"
            >
              <FileText className="w-4 h-4 text-zinc-400" />
              <span>50 ta Rasmiy FAQ Bazasini O&apos;qish</span>
            </Link>

            <Link
              href="/admin"
              onClick={() => setRole('admin')}
              className="flex items-center gap-2 px-5 py-3 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 font-medium text-xs transition active:scale-95"
            >
              <Shield className="w-4 h-4 text-zinc-400" />
              <span>Admin Nazorati</span>
            </Link>
          </div>
        </div>

        {/* Quick Metrics Bar */}
        <div className="mt-10 pt-6 border-t border-zinc-800 grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <div className="text-xl font-bold text-white font-mono">100%</div>
            <div className="text-xs text-zinc-400 mt-0.5">Avtonom AI Yechim</div>
          </div>
          <div>
            <div className="text-xl font-bold text-white font-mono">&lt; 1.2s</div>
            <div className="text-xs text-zinc-400 mt-0.5">VoiceLab Ovoz Sintezi</div>
          </div>
          <div>
            <div className="text-xl font-bold text-white font-mono">50 FAQ</div>
            <div className="text-xs text-zinc-400 mt-0.5">8 ta Asosiy Bo&apos;lim</div>
          </div>
          <div>
            <div className="text-xl font-bold text-white font-mono">24 / 7</div>
            <div className="text-xs text-zinc-400 mt-0.5">Uzluksiz Xizmat</div>
          </div>
        </div>
      </div>

      {/* Core Advantages */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {coreFeatures.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div
              key={idx}
              className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 flex flex-col justify-between hover:border-zinc-700 transition"
            >
              <div>
                <div className="w-10 h-10 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center text-zinc-200 mb-4">
                  <Icon className="w-5 h-5 text-zinc-300" />
                </div>
                <h3 className="font-semibold text-sm text-white mb-2">{item.title}</h3>
                <p className="text-xs text-zinc-400 leading-relaxed">{item.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* 50 FAQ Interactive Knowledge Base Preview */}
      <CommonQuestions />

      {/* Workflow: How It Works */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 sm:p-10">
        <div className="max-w-xl mb-8">
          <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider bg-zinc-800 px-2.5 py-1 rounded border border-zinc-700">
            Avtonom Jarayon
          </span>
          <h2 className="text-xl sm:text-2xl font-bold text-white mt-3 mb-1.5">
            SözLab Qanday Ishlaydi?
          </h2>
          <p className="text-xs text-zinc-400">
            Fuqaro mikrofoni orqali yuborilgan ovozli murojaatdan to rasmiy huquqiy javobgacha bo&apos;lgan 4 bosqichli zanjir.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {workflowStages.map((st, i) => (
            <div key={i} className="p-5 bg-zinc-950/70 rounded-xl border border-zinc-800/80">
              <span className="text-2xl font-bold text-zinc-500 font-mono block mb-2">{st.num}</span>
              <h4 className="font-semibold text-xs text-white mb-1.5">{st.title}</h4>
              <p className="text-xs text-zinc-400 leading-relaxed">{st.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
