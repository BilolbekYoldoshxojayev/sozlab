'use client';

import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, BookOpen, ExternalLink, Sparkles, Send, Volume2 } from 'lucide-react';
import Link from 'next/link';

interface FAQCategory {
  id: string;
  name: string;
  icon?: string;
  items: Array<{
    q: string;
    a: string;
    regulation: string;
    link?: string;
  }>;
}

export const FAQ_DATA: FAQCategory[] = [
  {
    id: 'qabul',
    name: 'Qabul va Hujjatlar (my.uzbmb.uz)',
    items: [
      {
        q: 'OTMlarga bakalavriatga qabul qachon boshlanadi va nechta yo\'nalish tanlash mumkin?',
        a: 'Oliy ta\'lim muassasalariga qabul har yili 5-iyundan 25-iyungacha my.uzbmb.uz hamda my.gov.uz portallari orqali onlayn amalga oshiriladi. Abituriyentlar bitta ta\'lim shakli (kunduzgi, sirtqi, kechki yoki masofaviy) doirasida fanlar majmuasi bir xil bo\'lgan 5 tagacha bakalavriat ta\'lim yo\'nalishini tanlash huquqiga ega.',
        regulation: 'Vazirlar Mahkamasining 2019-yil 7-iyundagi 468-son qarori.',
        link: 'https://my.uzbmb.uz',
      },
      {
        q: 'Abituriyent ro\'yxatdan o\'tishi uchun qanday hujjatlar talab etiladi?',
        a: 'Fuqarolik pasporti yoki ID-karta ma\'lumotlari (JSHSHIR), umumiy o\'rta (11-sinf) yoki o\'rta maxsus ta\'lim muassasasini tugatganligi haqidagi attestat/diplom, shuningdek agar mavjud bo\'lsa, xorijiy til yoki umumta\'lim fanlari bo\'yicha milliy/xalqaro sertifikat.',
        regulation: 'Vazirlar Mahkamasining 2024-yil 24-maydagi 304-son qarori.',
      },
    ],
  },
  {
    id: 'grantlar',
    name: 'Davlat Grantlari va GPA Tizimi',
    items: [
      {
        q: 'Davlat granti 1-kursdan keyin qayta taqsimlanadimi?',
        a: 'Ha, O\'zbekiston Respublikasi Prezidentining 2024-yil 24-maydagi PF-81-son Farmoniga muvofiq, 2024/2025-o\'quv yilidan boshlab davlat grantlari talabaning reyting ko\'rsatkichlari (GPA) asosida har o\'quv yili yakunida qayta taqsimlanadi. Yuqori o\'zlashtirgan talabalarga grant saqlanadi yoki shartnomada o\'qiyotgan iqtidorli talabalarga grant ajratiladi.',
        regulation: 'Prezidentning 2024-yil 24-maydagi PF-81-son Farmoni.',
      },
      {
        q: 'Ijtimoiy-rag\'batlantiruvchi grantlar qayta taqsimlanadimi?',
        a: 'Yo\'q, ehtiyojmand oilalar xotin-qizlari, nogironligi bo\'lgan shaxslar, Mehribonlik uyi tarbiyalanuvchilari uchun ajratilgan maqsadli va ijtimoiy grantlar 4 yil davomida to\'liq saqlanib qoladi.',
        regulation: 'Vazirlar Mahkamasining 2021-yil 17-sentabrdagi 576-son qarori.',
      },
    ],
  },
  {
    id: 'kontrakt',
    name: 'Kontrakt va Tabaqalashtirilgan Shartnoma',
    items: [
      {
        q: 'Super-kontrakt arizasini topshirish va to\'lash tartibi qanday?',
        a: 'Kirish imtihonlarida to\'plash mumkin bo\'lgan eng yuqori ballning kamida 30% ini (56,7 ball) to\'plagan va qabul chegarasiga 4,05 balldan ortiq yetmagan abituriyentlar tabaqalashtirilgan to\'lov-shartnoma (super-kontrakt) asosida o\'qishga qabul qilinadi. Ariza OTM rektori nomiga yoziladi yoki my.uzbmb.uz orqali shakllantiriladi.',
        regulation: 'Davlat komissiyasining har yillik 1-son bayoni.',
      },
      {
        q: 'Bazaviy kontrakt to\'lovini bo\'lib-bo\'lib to\'lash mumkinmi?',
        a: 'Ha, talabalar to\'lov-shartnoma mablag\'larini o\'quv yili davomida teng 4 qismga bo\'lib to\'lashlari mumkin: kamida 25% — 15-sentabrgacha, 50% — 1-yanvargacha, 75% — 1-aprelgacha va 100% — 1-iyulgacha.',
        regulation: 'Oliy va o\'rta maxsus ta\'lim vazirligi Nizomi.',
      },
    ],
  },
  {
    id: 'ttj',
    name: 'Talabalar Turar Joyi (TTJ) va Ijara',
    items: [
      {
        q: 'Yotoqxonaga ariza qayerdan topshiriladi va kimlarga imtiyoz beriladi?',
        a: 'Talabalar turar joyiga joylashish uchun arizalar har yili 1-avgustdan boshlab my.gov.uz portali orqali elektron qabul qilinadi. Temir daftar, Ayollar daftari yoki Yoshlar daftarida turgan, nogironligi bo\'lgan hamda 1-kurs talabalariga ustuvor navbat beriladi.',
        regulation: 'Vazirlar Mahkamasining 2023-yil 8-avgustdagi 345-son qarori.',
        link: 'https://my.gov.uz',
      },
      {
        q: 'Ijara to\'lovining 50 foizi qanday qoplab beriladi?',
        a: 'Davlat OTMlarida kunduzgi ta\'limda tahsil olib, ijarada yashaydigan talabalarga oylik ijara to\'lovining 50 foizi (Toshkent shahrida BHMning 1 baravari, viloyatlarda BHMning 0,5 baravari miqdorida) davlat byudjeti hisobidan qoplab beriladi.',
        regulation: 'Prezidentning 2021-yil 13-apreldagi PQ-5071-son qarori.',
      },
    ],
  },
  {
    id: 'nostrifikatsiya',
    name: 'Diplom Tan Olish (Nostrifikatsiya)',
    items: [
      {
        q: 'Xorijiy diplomni tan olish tartibi qanday? TOP-1000 universitetlar imtihonsiz o\'tadimi?',
        a: 'Ha, xalqaro e\'tirof etilgan Quacquarelli Symonds (QS), Times Higher Education (THE) yoki ARWU reytingida birinchi 1000 talikka kirgan oliygohlar diplomlari to\'g\'ridan-to\'g\'ri (maxsus sinov imtihonlarisiz) my.gov.uz orqali tan olinadi va guvohnoma beriladi.',
        regulation: 'Vazirlar Mahkamasining 2019-yil 24-iyuldagi 620-son qarori.',
      },
      {
        q: 'Nostrifikatsiya qilish uchun ariza qancha muddatda ko\'rib chiqiladi?',
        a: 'To\'g\'ridan-to\'g\'ri tan olinadigan diplomlar 10 ish kunida, maxsus sinov talab etiladigan diplomlar esa tegishli imtihon o\'tkazilgandan so\'ng 15 ish kunida rasmiylashtiriladi.',
        regulation: 'Ta\'lim sifatini nazorat qilish davlat inspeksiyasi reglamenti.',
      },
    ],
  },
  {
    id: 'kredit',
    name: 'Ta\'lim Krediti va Imtiyozlar',
    items: [
      {
        q: 'Xotin-qizlar uchun foizsiz ta\'lim krediti qanday ajratiladi?',
        a: 'Barcha davlat va nodavlat OTMlarda to\'lov-shartnoma asosida tahsil olayotgan xotin-qizlar uchun tijorat banklari tomonidan Markaziy bankning amaldagi stavkasida ta\'lim krediti ajratiladi, biroq foiz to\'lovlari to\'liq Ta\'lim kreditini moliyalashtirish jamg\'armasi hisobidan qoplanadi. Talaba faqat asosiy qarzni o\'qishni tugatgandan so\'ng 7-oydan boshlab 7 yil davomida qaytaradi.',
        regulation: 'Prezidentning 2022-yil 18-iyuldagi PQ-323-son qarori.',
      },
      {
        q: 'Ta\'lim kreditini olish uchun qaysi hujjatlar kerak?',
        a: 'Tijorat bankiga: 1) Ariza, 2) Shaxsni tasdiqlovchi hujjat, 3) To\'lov-shartnoma (kontrakt), 4) Kafil yoki garov ta\'minoti (xotin-qizlar va "Ijtimoiy himoya yagona reyestri" dagilarga kafil talab etilmaydi).',
        regulation: 'Vazirlar Mahkamasining 2021-yil 18-avgustdagi 527-son qarori.',
      },
    ],
  },
];

export default function CommonQuestions() {
  const [activeCategory, setActiveCategory] = useState<string>('qabul');
  const [openItems, setOpenItems] = useState<Record<string, boolean>>({});

  const toggleItem = (key: string) => {
    setOpenItems((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const selectedCategory = FAQ_DATA.find((c) => c.id === activeCategory) || FAQ_DATA[0];

  return (
    <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden p-6 sm:p-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-100 pb-6 mb-6">
        <div>
          <div className="flex items-center space-x-2 text-emerald-600 mb-1">
            <BookOpen className="w-5 h-5" />
            <span className="text-xs font-bold uppercase tracking-wider">Rasmiy Yo&apos;riqnomalar</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Vazirlik Bo&apos;yicha Ko&apos;p So&apos;raladigan Rasmiy Savollar (FAQ)
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Prezident Farmonlari va Vazirlar Mahkamasi qarorlariga asoslangan eng ishonchli javoblar
          </p>
        </div>

        <Link
          href="/call"
          className="inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs shadow-md shadow-emerald-700/20 transition-all active:scale-95 shrink-0"
        >
          <Sparkles className="w-4 h-4" />
          <span>Ovozli Muloqotda So&apos;rash</span>
        </Link>
      </div>

      {/* Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-3 mb-6 scrollbar-none">
        {FAQ_DATA.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              activeCategory === cat.id
                ? 'bg-[#0b2b50] text-white shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900'
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* Accordion Questions */}
      <div className="space-y-3">
        {selectedCategory.items.map((item, idx) => {
          const itemKey = `${selectedCategory.id}-${idx}`;
          const isOpen = !!openItems[itemKey];

          return (
            <div
              key={itemKey}
              className={`rounded-2xl border transition-all ${
                isOpen ? 'border-blue-200 bg-blue-50/20 shadow-xs' : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <button
                onClick={() => toggleItem(itemKey)}
                className="w-full text-left p-4 sm:p-5 flex items-start justify-between gap-4 cursor-pointer"
              >
                <div className="flex items-start space-x-3">
                  <div className="p-1.5 rounded-lg bg-blue-100 text-blue-800 shrink-0 mt-0.5">
                    <HelpCircle className="w-4 h-4" />
                  </div>
                  <span className="font-semibold text-sm text-slate-900 leading-snug">
                    {item.q}
                  </span>
                </div>
                <div className="text-slate-400 p-1">
                  {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </div>
              </button>

              {isOpen && (
                <div className="px-5 pb-5 pt-1 text-xs text-slate-700 leading-relaxed border-t border-slate-100 animate-in fade-in duration-200">
                  <p className="mb-3">{item.a}</p>

                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pt-3 border-t border-slate-200/60 bg-white/70 p-3 rounded-xl">
                    <div className="text-[11px] text-slate-500">
                      <strong>Rasmiy Asos:</strong> {item.regulation}
                    </div>

                    <div className="flex items-center space-x-2">
                      {item.link && (
                        <a
                          href={item.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center space-x-1 text-blue-600 hover:text-blue-800 text-[11px] font-semibold"
                        >
                          <span>Portalga o&apos;tish</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      <Link
                        href={`/call`}
                        className="inline-flex items-center space-x-1 text-emerald-700 hover:text-emerald-900 text-[11px] font-bold bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200"
                      >
                        <Volume2 className="w-3 h-3" />
                        <span>AI bilan muloqot</span>
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
