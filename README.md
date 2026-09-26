# 🏛️ SözLab — O'zbekiston Ta'lim Vazirligi AI Ovozli Call Markazi
### *AI-Powered Voice Call Center & Legal Citizen Assistance Platform*

[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014%20App%20Router-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![WebSockets](https://img.shields.io/badge/Real--Time-WebSockets%20Audio%20Stream-010101?logo=socketdotio)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![Multi-LLM](https://img.shields.io/badge/AI%20Core-Multi--LLM%20Orchestrator%20(0.35s)-4285F4?logo=google)](https://ai.google.dev/)
[![VoiceLab](https://img.shields.io/badge/Voice%20AI-VoiceLab%20Lola%20Neural-purple)](https://voicelab.ai/)
[![Database](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E?logo=supabase)](https://supabase.com/)
[![Tests](https://img.shields.io/badge/Tests-142%20Passed-brightgreen)](https://docs.pytest.org/)

> **Umummilliy AI Xakaton (Namangan, 2026)**  
> **Treki:** Ta'lim (Education)  
> **Loyiha nomi:** **SözLab** (O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligi hamda Maktabgacha va maktab ta'limi vazirligi uchun sun'iy intellektga asoslangan milliy ovozli call markazi va fuqarolar maslahat platformasi).

---

## 🌐 Jonli Havolalar (Live Production)

* 🖥️ **Jonli Veb-Ilova (Frontend):** [sozlab.vercel.app](https://sozlab.vercel.app) *(yoki Vercel Production URL)*
* ⚡ **Jonli API & WebSockets (Backend):** [sozlab-backend.onrender.com](https://sozlab-backend.onrender.com)
* 📖 **Interaktiv API Hujjatlari (Swagger):** [sozlab-backend.onrender.com/docs](https://sozlab-backend.onrender.com/docs)
* 🩺 **Salomatlik Tekshiruvi:** [sozlab-backend.onrender.com/health](https://sozlab-backend.onrender.com/health)
* 🗄️ **Ma'lumotlar Bazasi:** Supabase PostgreSQL Cloud

---

## 📌 Mahsulot Haqida (Executive Summary)

**SözLab** — davlat ta'lim tizimidagi eng og'riqli muammolardan birini hal qiluvchi innovatsion tizim:
1. **Call-markazlardagi ulkan yuklama:** Qabul mavsumida, grantlar, stipendiyalar, nostrifikatsiya, maktabga qabul va pedagoglar huquqlari bo'yicha vazirlikning `1006` va `1007` ishonch telefonlariga kuniga o'n minglab bir xil savollar tushadi.
2. **Uzoq kutish vaqti:** Operatorlar soni cheklangani tufayli fuqarolar o'nlab daqiqalar davomida navbatda qolib ketadi.
3. **Standartlashtirilmagan ma'lumot:** Har bir operator turlicha ma'lumot berishi yoki eng so'nggi qonunchilik o'zgarishlaridan bexabar bo'lishi mumkin.
4. **O'zbek tilidagi ovozli AI yetishmasligi:** Fuqarolarning og'zaki nutqini (lahjalar, shevalar, fonetik xatolar) tushunadigan va tabiiy o'zbek tilida qonuniy asoslangan javob beruvchi yechimlar mavjud emas edi.

**SözLab yechimi:**
100% rasmiy ta'lim qonunchiligi (Konstitutsiya, qonunlar, qarorlar) bilan cheklangan (zero-hallucination guardrails), **0.35 soniyali ultra-tezkor Multi-LLM kaskadi** va **VoiceLab Lola neyron ovozi** bilan qurollangan to'liq avtonom ovozli Call Markaz platformasi.

---

## 🚀 Asosiy Imkoniyatlar (Key Features)

### 1. 🎙️ Tabiiy O'zbek Tili Ovozli AI (Ultra-Realistic Speech AI)
* **VoiceLab Lola Neural TTS (Noble Lynx):** O'zbek tilidagi eng tabiiy intonatsiya va pauzalarga ega yuqori sifatli ovoz sintezi.
* **Resilient Audio Fallback:** VoiceLab -> Aisha AI (Gulnoza) -> Microsoft Edge-TTS (`uz-UZ-MadinaNeural`, `uz-UZ-SardorNeural`) kaskadli zaxira mexanizmi.
* **Fonetik & Leksik Normalizatsiya:** Qonun raqamlari (O'RQ-637, VMQ-527, PF-81), sanalar, foizlar (0%, 100%), OTM/TTJ/HEMIS kabi qisqartmalar to'liq adabiy o'zbekcha so'zlarga aylantirib o'qiladi.
* **Sheva va fonetik xatolarga chidamlilik:** Kirillitsa (`Макитапке...`), og'zaki nutq shakllari (`makitapke`, `kontakt`, `byudjet`) avtomatik aniqlanadi.

### 2. 🧠 Ultra-Tezkor Multi-LLM Kaskadli Orkestrator (0.35s)
Yagona provayderga bog'lanib qolmaslik va uzluksiz 100% uptime kafolati uchun 5 pog'onali kaskad arxitekturasi:
1. **Rank 1: Groq LPUs** (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`) — o'rtacha **0.35–0.45s** javob tezligi!
2. **Rank 2: Google Gemini** (`gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-flash`) — chuqur mulohaza va kontekst.
3. **Rank 3: Cloudflare Workers AI** (`@cf/meta/llama-3.1-8b-instruct`) — global edge xizmati.
4. **Rank 4: Mistral AI** (`mistral-small-latest`) — Yevropa bulut zaxirasi.
5. **Rank 5: Deterministic Legal Rule Engine** — hatto barcha sun'iy intellekt API'lari uzilgan taqdirda ham qonunchilik ma'lumotlar bazasidan 0.005 soniyada kafolatlangan javob qaytaradi!

### 3. ⚖️ 100% Qonuniy Asoslangan Bilimlar Bazasi (RAG Engine)
AI hech qachon o'zidan to'qib javob bermaydi (Anti-Hallucination Guardrails). Har bir javob rasmiy huquqiy manbaga tayanadi:
* **Yangi Tahrirdagi O'zbekiston Konstitutsiyasi (50 sahifalik entsiklopediya):** 19-modda (tenglik), 50-modda (bepul umumiy o'rta ta'lim, oliy ta'lim granti), 51-modda (akademik erkinlik), 52-modda (pedagog maqomi va moddiy ta'minoti), 77-modda (ota-onalar mas'uliyati).
* **O'RQ-637:** "Ta'lim to'g'risida"gi O'zbekiston Respublikasi Qonuni.
* **O'RQ-901:** "Pedagogning maqomi to'g'risida"gi Qonun.
* **Vazirlar Mahkamasi Qarorlari:** VMQ-527 (to'lov-kontrakt va ta'lim krediti), VMQ-376 (pedagoglar attestatsiyasi), VMQ-447 (maktabga qabul), VMQ-605 (TTJ qoidalari), PF-81 (Prezident farmoni).
* **Top-50 Rasmiy FAQlar:** Maktabgacha, Maktab, OTM, Diplom nostrifikatsiyasi, Grant va Stipendiyalar.

### 4. 📞 Real-Vaqtli Qo'ng'iroq Simulyatori (1006 Hotline)
* Veb-brauzer orqali haqiqiy telefon qo'ng'irog'i tajribasi (Web Audio API, jonli ovoz to'lqinlari).
* Jonli ikki tomonlama transkripsiya (Citizen Speech vs AI Speech).
* Audio replikalarni millisekundlik aniqlikda birlashtirish (`call_{id}_full.wav`).

### 5. 🎧 Call-Markaz Operatori Ish O'rni (Operator Dashboard)
* Navbatdagi qo'ng'iroqlarni real-vaqtda kuzatish.
* **Smart Co-Pilot:** Operatorga AI tomonidan tavsiya etiladigan tayyor qonuniy javoblar va tezkor havolalar.
* Qo'ng'iroqni o'ziga qabul qilish yoki boshqa mutaxassisga yo'naltirish.

### 6. 📊 Vazirlik Rahbariyati uchun Chuqur Analitika
* **KPI Metrikalari:** Jami qo'ng'iroqlar, AI tomonidan mustaqil yechilgan ulush (85%+), o'rtacha muloqot vaqti, fuqarolar qoniqish darajasi (CSAT).
* **Kayfiyat Tahlili (Sentiment Analysis):** Ijobiy, Neytral, Salbiy va Shikoyat dinamikasi.
* **Top Muammolar Reytingi:** Maktab fondi/remont noqonuniy yig'imlari, OTM kontrakt stavkalari, TTJ yetishmovchiligi, talim krediti foizlari.

### 7. 📜 Murojaatlar Arxivi va Audio Timeline Scrubbing
* Barcha qo'ng'iroqlarning to'liq audiosi, matnli transkripti, hissiy bahosi va qonuniy havolalari.
* Audio pleer orqali har bir replikaga bitta bosishda o'tish (Interactive Scrubbing).

---

## 🏗️ Arxitektura va Texnologiyalar Steki

```
                               ┌────────────────────────────────────────────────────────┐
                               │                    FOYDALANUVCHILAR                    │
                               │   (Abituriyentlar, Talabalar, Ota-onalar, O'qituvchilar)│
                               └───────────────────────────┬────────────────────────────┘
                                                           │ Web Browser / Mobile
                                                           ▼
                               ┌────────────────────────────────────────────────────────┐
                               │             FRONTEND (Next.js 14 App Router)           │
                               │  • TypeScript, Tailwind CSS, Lucide Icons              │
                               │  • Web Audio API Visualizer (HTML5 Canvas)             │
                               │  • Global Vercel Edge Hosting (SSL/HTTPS/WSS)         │
                               └───────────────────────────┬────────────────────────────┘
                                                           │ REST API + WebSockets
                                                           ▼
                               ┌────────────────────────────────────────────────────────┐
                               │              BACKEND API (FastAPI + Python 3.11+)       │
                               │  • Uvicorn Asinxron Server (Render.com)               │
                               │  • WebSocket Manager (/ws/call/{id}, /ws/operator)     │
                               │  • imageio-ffmpeg Audio Transcoding (24kHz Mono WAV)   │
                               └─────────────┬───────────────────────────┬──────────────┘
                                             │                           │
                   ┌─────────────────────────┴────────────┐  ┌───────────┴────────────────────────┐
                   │       MULTI-LLM ORCHESTRATOR         │  │     KNOWLEDGE ENGINE & PERSISTENCE  │
                   │  1. Groq LPU (GPT-OSS / Qwen 0.35s)  │  │  • 50-Sahifalik Konstitutsiya Bazasi│
                   │  2. Google Gemini 2.5 Flash Cascade  │  │  • Top-50 Vazirlik FAQ To'plami     │
                   │  3. Cloudflare Workers AI LLaMA 3.1  │  │  • O'RQ-637, O'RQ-901, VMQ Qarorlari│
                   │  4. Mistral AI Small Latest          │  │  • Supabase PostgreSQL Cloud        │
                   │  5. Deterministic Legal Rule Engine  │  │  • Local JSON Atomic Fallback Store │
                   └──────────────────────────────────────┘  └────────────────────────────────────┘
```

| Qatlam | Tanlangan Texnologiya | Sabab va Xususiyat |
| :--- | :--- | :--- |
| **Frontend** | **Next.js 14 (App Router), React, Tailwind CSS, TypeScript** | Server-Side Rendering (SSR), tezkor yuklanish, zamonaviy davlat portallari dizayni. |
| **Backend** | **Python 3.11+, FastAPI, Uvicorn, WebSockets** | Yuqori o'tkazuvchanlik, asinxron audio streamlar, kuchli ML ekotizimi. |
| **Nutq Sintezi (TTS)** | **VoiceLab Lola Neural + Edge-TTS (Madina/Sardor)** | Yuqori tabiiylikdagi o'zbek tili neyron ovozlari va 100% uzluksiz zaxira. |
| **Nutqni Tanish (STT)**| **VoiceLab STT + Groq Whisper Large v3 Turbo** | 0.4 soniyada o'zbekcha nutqni yuqori aniqlikda matnga aylantirish. |
| **LLM Orkestrator** | **Groq LPU, Gemini 2.5, Cloudflare AI, Mistral** | 0.35 soniyali o'rtacha javob tezligi, avtomatik zaxira kaskadi. |
| **Ma'lumotlar Bazasi**| **Supabase PostgreSQL + Local JSON Store** | Bulutda markazlashgan saqlash, oflayn rejimda lokal diskka atomik yozish. |
| **Audio Qayta Ishlash**| **imageio-ffmpeg & standard wave module** | Brauzerdan kelgan WebM/Opus audio oqimlarini toza 24kHz WAV formatiga o'tkazish. |

---

## 📖 TO'LIQ FOYDALANUVCHI QO'LLANMASI (HANDBOOK)

### 1. Fuqarolar uchun: Ovozli Qo'ng'iroqdan Foydalanish (`/call`)
1. Brauzerda [sozlab.vercel.app/call](https://sozlab.vercel.app/call) sahifasini oching.
2. Ismingiz va telefon raqamingizni kiriting va **"1006 bilan bog'lanish"** tugmasini bosing.
3. Brauzer mikrofon so'raganda **"Ruxsat berish" (Allow)** ni bosing.
4. Go'shak ulanadi va AI Maslahatchi siz bilan salomlashadi.
5. Istalgan ta'lim savolini tabiiy o'zbek tilida gapiring:
   * *"Farzandimni necha yoshdan 1-sinfga bersam bo'ladi?"*
   * *"Maktabda darsliklar va mashq daftarlari uchun pul yig'ish qonuniymi?"*
   * *"Magistraturaga kirishda qaysi sertifikatlar talab qilinadi va kontrakt stavkasi qancha?"*
   * *"O'qituvchiga darsdan tashqari obodonlashtirish ishlarini yuklash mumkinmi?"*
6. AI javobni VoiceLab Lola ovozida darhol eshittiradi va transkripsiyada ko'rsatadi.
7. Suhbat tugagach, qizil go'shakni bosib qo'ng'iroqni yakunlang.

### 2. Fuqarolar uchun: Matnli Chat (`/chat`)
* Ovoz bilan gapirish imkoni bo'lmaganda yoki sokin joylarda fuqaro to'g'ridan-to'g'ri matn orqali savol yozib, bir zumda rasmiy javob va havolalarni olishi mumkin.

### 3. Call-Markaz Operatorlari uchun (`/operator`)
1. [sozlab.vercel.app/operator](https://sozlab.vercel.app/operator) sahifasiga kiring.
2. Jonli navbatda turgan qo'ng'iroqlar holati, fuqaro ma'lumotlari va joriy transkripsiya ko'rinadi.
3. Agar fuqaroning kayfiyati salbiy bo'lsa yoki ariza/shikoyat qoldirayotgan bo'lsa, tizim operatorga ogohlantirish beradi.
4. Operator **"Qo'ng'iroqni Qabul Qilish"** tugmasini bosib muloqotga ulanadi va AI tavsiya etgan qonuniy moddalar asosida tezkor yordam ko'rsatadi.

### 4. Tahlilchilar va Vazirlik Rahbariyati uchun (`/analytics`)
1. [sozlab.vercel.app/analytics](https://sozlab.vercel.app/analytics) sahifasiga o'ting.
2. Real-vaqtdagi tahliliy ko'rsatkichlarni kuzating:
   * **Hal etilganlik ko'rsatkichi:** AI yordamida avtomatlashtirilgan foiz (maqsad: 85%+).
   * **Muammolar reytingi:** Qaysi viloyat yoki sohada eng ko'p shikoyat tushayotgani (maktab formasi, TTJ, kontrakt).
   * **Sentiment dinamikasi:** Fuqarolarning davlat ta'lim xizmatlaridan qoniqish indeksi.

### 5. Qo'ng'iroqlar Arxivi va Tinglash (`/history` va `/admin`)
1. [sozlab.vercel.app/history](https://sozlab.vercel.app/history) yoki `/admin` sahifasiga kiring.
2. Har bir qo'ng'iroq kartasida fuqaroning ismi, sanasi, davomiyligi, mavzusi va xulosasi aks etadi.
3. **"Tafsilotlar"** tugmasini bosib, butun qo'ng'iroq audiosini eshiting yoki replika ustiga bosib, aynan o'sha gap aytilgan sekundga sakrang.

---

## 🛡️ Yuridik Xavfsizlik va Anti-Hallucination Qoidalari

SözLab davlat idorasi mas'uliyatini to'liq his qilgan holda ishlab chiqilgan:
1. **Doiradan tashqari savollar rad etiladi:**  
   Agar fuqaro ta'limga aloqasi bo'lmagan mavzuda (ob-havo, kriptovalyuta, boshqa sohalar) savol bersa, tizim xushmuomala tarzda vazirlik faoliyatiga oid savollarni so'raydi.
2. **Qat'iy manbalar keltiriladi:**  
   "Eshittim", "taxminan" kabi so'zlar ishlatilmaydi. Faqat: *"O'zbekiston Respublikasi Konstitutsiyasi 50-moddasiga binoan..."* yoki *"Vazirlar Mahkamasining 527-son qaroriga asosan..."* shaklida javob beriladi.
3. **Javobgarlik moddalari eslatiladi:**  
   Maktabda noqonuniy pul yig'ish holatlari so'ralganda, Ma'muriy javobgarlik to'g'risidagi kodeksning 197-5-moddasi (pedagog faoliyatiga qonunga xilof ravishda aralashish) va JK 148-2-moddasi bo'yicha jazo choralari aniq ko'rsatiladi.

---

## 💻 Dasturchilar uchun: Lokal Muhitda O'rnatish (Setup Guide)

### Talablar
* Python 3.11 yoki undan yuqori
* Node.js 18.x, 20.x yoki 22.x
* Git

### 1. Repozitoriyani klonlash
```bash
git clone https://github.com/BilolbekYoldoshxojayev/sozlab.git
cd sozlab
```

### 2. Tezkor ishga tushirish (PowerShell)
Loyihada barcha xizmatlarni bitta buyruq bilan yoquvchi skript mavjud:
```powershell
.\start_dev.ps1
```

### 3. Qo'lda alohida ishga tushirish

#### Backend (FastAPI):
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*API hujjatlari:* `http://localhost:8000/docs`

#### Frontend (Next.js):
```bash
cd frontend
npm install
npm run dev
```
*Veb-interfeys:* `http://localhost:3000`

---

## 🔐 Muhit O'zgaruvchilari (Environment Variables)

### Backend (`backend/.env`):
```env
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Multi-LLM API Keys
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
GROQ_API_KEY=your_groq_api_key
GROQ_PRIMARY_MODEL=openai/gpt-oss-120b
GROQ_FALLBACK_MODEL=qwen/qwen3.8-27b
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_id
CLOUDFLARE_API_TOKEN=your_cloudflare_token
MISTRAL_API_KEY=your_mistral_key

# VoiceLab Official Subscription
VOICELAB_API_KEY=your_voicelab_key
VOICELAB_VOICE_ID=voice_EvIb9vE6iY_dWgK7OobYdZcX
VOICELAB_SPEED=1.32

# Fallback Edge-TTS
DEFAULT_TTS_VOICE=uz-UZ-MadinaNeural
AUDIO_CACHE_DIR=./cache/audio

# Supabase PostgreSQL
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

### Frontend (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

---

## 🧪 Avtotestlar va Tekshiruv (Test Suite)

Loyihada **142 ta avtomatlashtirilgan unit, integratsiya, stress va adversarial xavfsizlik testlari** mavjud.

Barcha testlarni ishga tushirish:
```bash
python -m pytest backend/tests -v
```

Frontend buildini tekshirish:
```bash
cd frontend
npm run build
```

---

## 👥 Loyiha Jamoasi (Team SözLab — Namangan AI Xakaton 2026)

| F.I.Sh | Vazifasi va Mas'uliyati |
| :--- | :--- |
| **Bilolbek Yoldoshxojayev** | **Lead Developer & AI System Integrator** — Backend, Frontend, Multi-LLM, WebSocket audio stream va bulut infratuzilmasi. |
| **Fayzulloh** | **Product Manager & Lead Pitcher** — Mahsulot strategiyasi, vazirlik biznes-talablari, xakaton taqdimoti va pitch. |
| **Iskandar** | **Domain Expert & Legal/Data Researcher** — Qonunchilik entsiklopediyasi, 50-sahifalik Konstitutsiya bazasi, Top-50 FAQ tahlili. |
| **Temurmalik** | **Business Analyst & Financial Strategist** — Iqtisodiy samaradorlik, unit economics, xarajatlar optimallashtirish hisoboti. |
| **Ziyovuddin** | **UI/UX Designer & Media Lead** — Foydalanuvchi tajribasi dizayni, brending, vizual taqdimot va media materiallar. |

---

## 📄 Litsenziya

Ushbu loyiha **Umummilliy AI Xakaton (Namangan 2026)** doirasida ishlab chiqilgan. Barcha huquqlar himoyalangan.
