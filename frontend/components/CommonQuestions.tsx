'use client';

import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, BookOpen, ExternalLink, Sparkles, Volume2, ShieldCheck } from 'lucide-react';
import Link from 'next/link';

interface FAQCategory {
  id: string;
  name: string;
  items: Array<{
    q: string;
    a: string;
    regulation: string;
    link?: string;
  }>;
}

export const FAQ_DATA: FAQCategory[] = [
  {
    id: 'maktab',
    name: 'Maktab Ta\'limi & Pul Yig\'ish',
    items: [
      {
        q: 'Maktabda o\'quvchilardan yoki ota-onalardan pul yig\'ish (fond, ta\'mirlash, bayramlar) qonuniymi?',
        a: 'Mutlaqo noqonuniy va qat\'iyan taqiqlangan! Konstitutsiyaning 50-moddasiga ko\'ra davlat umumiy o\'rta ta\'lim olishni bepul kafolatlaydi. Maktablarni ta\'mirlash va jihozlash to\'liq davlat budjetidan moliyalashtiriladi. Pul yig\'gan maktab rahbarlari va xodimlari ma\'muriy (MJtK 61) hamda jinoiy (JK 165, 205) javobgarlikka tortiladi.',
        regulation: 'Konstitutsiya 50-moddasi; "Ta\'lim to\'g\'risida"gi Qonun 4-moddasi; JK 165, 205-moddalari.',
        link: 'https://lex.uz',
      },
      {
        q: 'Bolani 1-sinfga qabul qilish tartibi va yoshi qanday belgilangan?',
        a: 'Bola 7 yoshga to\'ladigan yilda umumta\'lim maktabining 1-sinfiga qabul qilinadi (masalan, 2026-yilda 2019-yilda tug\'ilganlar). Qabul my.maktab.uz portali orqali 2 bosqichda: 1-bosqich mikrohudud bo\'yicha bepul va sinovsiz, 2-bosqich mikrohududdan tashqari bo\'sh o\'rinlar bo\'yicha amalga oshiriladi.',
        regulation: '"Ta\'lim to\'g\'risida"gi Qonun 9-moddasi; VMQ-376.',
        link: 'https://my.maktab.uz',
      },
      {
        q: 'Yagona maktab formasi majburiymi? Ro\'mol va do\'ppi kiyishga ruxsat bormi?',
        a: 'Yagona maktab formasi majburiy talab emas, balki tavsiyaviy hisoblanadi. O\'quvchi qizlarning oq yoki och rangli milliy ro\'mol o\'rab, o\'g\'il bolalarning do\'ppi kiyib kelishiga to\'sqinlik qilish qat\'iyan man etiladi. Forma yo\'qligi uchun o\'quvchini darsdan chetlatish noqonuniydir.',
        regulation: 'Vazirlar Mahkamasining 666 va 271-son qarorlari.',
      },
    ],
  },
  {
    id: 'pedagog',
    name: 'Pedagoglar Huquqlari (O\'RQ-901)',
    items: [
      {
        q: 'O\'qituvchilarni darsdan tashqari ishlarga (obodonlashtirish, hashar, obuna) jalb qilish mumkinmi?',
        a: 'Qat\'iyan taqiqlanadi! Konstitutsiyaning 52-moddasiga ko\'ra o\'qituvchining sha\'ni va qadr-qimmati davlat himoyasidadir. O\'RQ-901 qonuniga binoan pedagoglarni obodonlashtirish, ko\'cha tozalash, majburiy obuna va hisobotlar yig\'ishga majburlash man etiladi. Buni buzgan mansabdorlarga BHMning 100 dan 150 baravarigacha jarima solinadi.',
        regulation: 'Konstitutsiya 52-moddasi; Qonun O\'RQ-901; MJtK 51-moddasi 2-qismi.',
        link: 'https://lex.uz',
      },
      {
        q: 'Pedagog xodimlar uchun yillik mehnat ta\'tili necha kun?',
        a: 'Umumta\'lim muassasalari pedagog xodimlariga davomiyligi 56 kalendar kuni bo\'lgan haq to\'lanadigan yillik uzaytirilgan asosiy mehnat ta\'tili beriladi.',
        regulation: 'Mehnat kodeksi 501-moddasi; O\'RQ-901 12-moddasi.',
      },
      {
        q: 'Maktab o\'qituvchilari uchun 1 stavka dars soati necha soat?',
        a: 'Umumta\'lim muassasalarida 1-11-sinf o\'qituvchilari uchun haftalik bir stavka ish yuklamasi 16 akademik soat qilib belgilangan. Maksimal 1.5 stavkagacha (24 soat) dars berilishi mumkin.',
        regulation: 'Vazirlar Mahkamasining 275-son qarori.',
      },
    ],
  },
  {
    id: 'grantlar',
    name: 'OTM Qabuli va Grantlar (PF-81)',
    items: [
      {
        q: '2024–2026-yillarda davlat grantlari har yili qanday qayta taqsimlanadi?',
        a: 'PF-81-son Farmonga muvofiq, davlat grantlari talabaga butun o\'qish davri (4 yil) uchun kafolatlanmaydi. 1-kursda kirish ballariga ko\'ra beriladi, 2-kursdan boshlab esa HEMIS tizimidagi GPA natijalariga asosan a\'lochi talabalar o\'rtasida har yili qayta taqsimlanadi.',
        regulation: 'Prezidentning 2024-yil 24-maydagi PF-81-son Farmoni.',
        link: 'https://lex.uz',
      },
      {
        q: 'Davlat OTMlari magistraturasida o\'qiyotgan xotin-qizlar kontrakti qanday qoplanadi?',
        a: 'Barcha davlat OTMlarining magistratura mutaxassisliklariga to\'lov-kontrakt asosida qabul qilingan xotin-qizlarning to\'lov-kontrakti davlat budjeti mablag\'lari hisobidan 100% qaytarish shartisiz to\'lab beriladi.',
        regulation: 'Vazirlar Mahkamasining 2022-yil 15-avgustdagi 447-son qarori.',
        link: 'https://my.gov.uz',
      },
      {
        q: 'Ijara xonadonida yashaydigan talabalarga 50 foiz ijara kompensatsiyasi to\'lanadimi?',
        a: 'Ha! Davlat OTMlarining kunduzgi bo\'limida ijarada turuvchi talabalarga oylik ijara to\'lovining 50 foizi: Toshkent shahrida BHMning 1 baravarigacha, viloyatlarda esa 0.5 baravarigacha budjetdan to\'lab beriladi.',
        regulation: 'Vazirlar Mahkamasining 2021-yil 24-sentyabrdagi 605-son qarori.',
      },
    ],
  },
  {
    id: 'kredit',
    name: 'Ta\'lim Krediti & Ijtimoiy Kafolatlar',
    items: [
      {
        q: 'Xotin-qizlar uchun ta\'lim krediti haqiqatan ham foizsizmi?',
        a: 'Ha! Kunduzgi ta\'limda o\'qiyotgan xotin-qizlarning ta\'lim krediti foizlari to\'liq Moliya vazirligi Jamg\'armasi hisobidan qoplanadi (talabaga 0%). Asosiy qarz esa o\'qish tugagach 7-oydan boshlab 7 yil davomida qaytariladi.',
        regulation: 'Vazirlar Mahkamasining 2021-yil 18-avgustdagi 527-son qarori.',
      },
      {
        q: 'Inklyuziv ta\'lim nima va nogironligi bo\'lgan bolalar oddiy maktabda o\'qiy oladimi?',
        a: 'Ha! Qonun bo\'yicha barcha umumta\'lim maktablarida alohida ta\'lim ehtiyojlari bo\'lgan bolalar uchun inklyuziv sinflar ochilishi shart. Nogironligi bo\'lgan bolalarni oddiy maktabga qabul qilishdan bosh tortish qat\'iyan taqiqlanadi.',
        regulation: 'Konstitutsiya 50-moddasi; "Ta\'lim to\'g\'risida"gi Qonun 20-moddasi; PQ-4860.',
      },
    ],
  },
];

export default function CommonQuestions() {
  const [activeCategory, setActiveCategory] = useState<string>('maktab');
  const [openItems, setOpenItems] = useState<Record<string, boolean>>({});

  const toggleItem = (key: string) => {
    setOpenItems((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const selectedCategory = FAQ_DATA.find((c) => c.id === activeCategory) || FAQ_DATA[0];

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 sm:p-8 text-zinc-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-zinc-800 pb-5 mb-6">
        <div>
          <div className="flex items-center space-x-2 text-zinc-400 mb-1">
            <BookOpen className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-semibold uppercase tracking-wider text-zinc-300">
              Rasmiy Yuridik Bilimlar Bazasi
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            TOP-50 Rasmiy Savol-Javob To&apos;plami
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Konstitutsiya, Qonunlar va Hukumat qarorlariga asoslangan rasmiy javoblar
          </p>
        </div>

        <Link
          href="/call"
          className="inline-flex items-center justify-center space-x-2 px-4 py-2 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 font-semibold text-xs transition active:scale-95 shrink-0"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Ovozli Muloqotda So&apos;rash</span>
        </Link>
      </div>

      {/* Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 mb-5 scrollbar-none">
        {FAQ_DATA.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition ${
              activeCategory === cat.id
                ? 'bg-zinc-800 text-white border border-zinc-700'
                : 'bg-zinc-950/60 text-zinc-400 hover:text-zinc-200 border border-zinc-800/80'
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* Accordion Questions */}
      <div className="space-y-2.5">
        {selectedCategory.items.map((item, idx) => {
          const itemKey = `${selectedCategory.id}-${idx}`;
          const isOpen = !!openItems[itemKey];

          return (
            <div
              key={itemKey}
              className={`rounded-xl border transition ${
                isOpen ? 'border-zinc-700 bg-zinc-950/80' : 'border-zinc-800/80 bg-zinc-950/40 hover:border-zinc-700'
              }`}
            >
              <button
                onClick={() => toggleItem(itemKey)}
                className="w-full text-left p-4 flex items-start justify-between gap-4 cursor-pointer"
              >
                <div className="flex items-start space-x-3">
                  <div className="p-1 rounded bg-zinc-800 text-zinc-300 shrink-0 mt-0.5">
                    <HelpCircle className="w-3.5 h-3.5" />
                  </div>
                  <span className="font-semibold text-xs sm:text-sm text-zinc-100 leading-snug">
                    {item.q}
                  </span>
                </div>
                <div className="text-zinc-500 p-0.5">
                  {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </div>
              </button>

              {isOpen && (
                <div className="px-4 pb-4 pt-1 text-xs text-zinc-300 leading-relaxed border-t border-zinc-800/80 animate-fade-in">
                  <p className="mb-3">{item.a}</p>

                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2.5 pt-2.5 border-t border-zinc-800/80 bg-zinc-900/60 p-2.5 rounded-lg">
                    <div className="text-[11px] text-zinc-400">
                      <strong className="text-zinc-300">Qonuniy Asos:</strong> {item.regulation}
                    </div>

                    <div className="flex items-center space-x-2">
                      {item.link && (
                        <a
                          href={item.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center space-x-1 text-zinc-400 hover:text-white text-[11px] font-medium"
                        >
                          <span>lex.uz</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                      <Link
                        href="/call"
                        className="inline-flex items-center space-x-1 text-zinc-200 hover:text-white text-[11px] font-semibold bg-zinc-800 px-2.5 py-1 rounded border border-zinc-700"
                      >
                        <Volume2 className="w-3 h-3 text-blue-400" />
                        <span>Ovozli Tinglash</span>
                      </Link>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
