# Project: SözLab

## Name
**SözLab (Oliy Ta'lim, Fan va Innovatsiyalar Vazirligi AI Ovozli Call Markazi)**


## Goal
Ta'lim va Innovatsiyalar Vazirligi (Ministry of Higher Education, Science and Innovations of the Republic of Uzbekistan) uchun sun'iy intellektga asoslangan ovozli va matnli qo'ng'iroq markazi (AI Call Center & Voice Assistant) platformasini yaratish.

## Problem
1. **Yuklama yuqoriligi**: Oliy ta'lim, qabul mavsumi, grantlar, stipendiyalar va diplom nostrifikatsiyasi bo'yicha fuqarolar (abituriyentlar, talabalar, ota-onalar) call-markazga kuniga o'n minglab bir xil savollar bilan murojaat qiladi.
2. **Kutish vaqti**: Operatorlar yetishmasligi tufayli kutish vaqti uzayadi va fuqarolar noroziligi oshadi.
3. **Analitika yetishmasligi**: Qo'ng'iroqlar mazmuni bo'yicha markazlashgan tizimli tahlil va real-vaqt hisoboti yo'q.
4. **O'zbek tili cheklovlari**: O'zbek tilidagi ovozli muloqot va intonatsiyani tabiiy tushunuvchi ixtisoslashgan yechimlar kam.

## Target Users
1. **Fuqarolar (Abituriyentlar, Talabalar, Ota-onalar)**: Vazirlikka telefon/web orqali qo'ng'iroq qilib, tezkor va aniq ma'lumot oluvchilar.
2. **Call Markaz Operatorlari**: Murakkab holatlarda qo'ng'iroqni qabul qilib, AI transkripsiyasi va tayyor maslahat takliflari bilan ishlovchilar.
3. **Vazirlik Rahbariyati va Tahlilchilari**: Qo'ng'iroqlar dinamikasi, ijobiy/salbiy kayfiyat, eng ko'p so'ralayotgan muammolar statistikasi orqali qaror qabul qiluvchilar.

## Team Roster (Umummilliy AI Xakaton, Namangan 2026)
1. **Bilolbek** — Lead Developer / AI & System Integrator
2. **Fayzulloh** — Product Manager & Lead Pitcher
3. **Iskandar** — Domain Expert & Legal/Data Researcher
4. **Temurmalik** — Business Analyst & Financial/Impact Strategist
5. **Ziyovuddin** — UI/UX Designer & Media Lead

## Current Status
- **Phase**: Implementation & Engineering Lifecycle in progress.
- **Approved Architecture**: Monorepo (`/frontend` Next.js 14 App Router, `/backend` FastAPI Python).
- **Core AI**: Gemini Dialog Manager (multimodal/dialog) + edge-tts (`uz-UZ-MadinaNeural`, `uz-UZ-SardorNeural`) + Higher Education Ministry Knowledge Base + WebSocket real-time audio pipeline.


## Current Objective
To'liq ishlovchi, ko'rgazmali va taqdimotga 100% tayyor monorepo ilovasini yaratish, barcha avtotestlarni o'tkazish, xavfsizlik auditini bajarish va xakaton g'oliblik MVP talablariga moslash.

## Constraints
- Hackathon deadline: 2-4 kunlik qat'iy vaqt (Namangan AI Xakaton, Ta'lim treki).
- Real-time demo barqarorligi: oflayn/onlayn rejimlar uchun chidamli fallback va avtomatik mock tizimi.
- To'liq o'zbek tilidagi interfeys va tabiiy nutq.

## Non-Goals
- Haqiqiy telekom GSM provayderlari bilan jismoniy SIP/E1 ulanish (Web Audio Call Simulator orqali to'liq emulyatsiya qilinadi).