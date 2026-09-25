# 🏛️ Vazir Chat — Ta'lim va Innovatsiyalar Vazirligi AI Call Markazi

> **Umummilliy AI Xakaton, Namangan (24–27 Sentabr 2026)**  
> **Treki:** Ta'lim (Education)  
> **Loyiha nomi:** Vazir Chat (Vazir Ovozli Muloqot Markazi)

---

## 📌 Loyiha Haqida

**Vazir Chat** — O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligi uchun ishlab chiqilgan sun'iy intellektga asoslangan milliy ovozli call markaz tizimi.

U abituriyentlar, talabalar va ota-onalarning OTMlarga qabul, davlat grantlari, kontrakt/super-kontrakt, talabalar turar joyi (TTJ), xorijiy diplomlarni nostrifikatsiya qilish va stipendiyalar bo'yicha beradigan savollariga **tabiiy o'zbek tilida ovozli javob beradi**, suhbatni real-vaqtda transkripsiya qiladi, murakkab arizalarni avtomatik navbatchi operatorga yo'naltiradi va vazirlik rahbariyatiga to'liq tahliliy dashboard taqdim etadi.

---

## 🚀 Asosiy Imkoniyatlar

1. 🎙️ **O'zbek Tili Ovozli AI (STT & TTS)**:
   - Microsoft `edge-tts` neyron modellari (`uz-UZ-MadinaNeural` ayol ovozi va `uz-UZ-SardorNeural` erkak ovozi).
   - Smart audio keshlash (MD5 hash) — takroriy savollarga 0.1 soniyada javob.
   - HTML5 Web Audio API Canvas orqali interaktiv audio to'lqin vizualizatsiyasi.
2. 📚 **Vazirlik Rasmiy Bilimlar Bazasi (RAG & Knowledge Base)**:
   - Vazirlar Mahkamasi va Oliy ta'lim vazirligining rasmiy nizomlari, qabul parametrlari, me'yoriy aktlar bilan integratsiya.
   - Gemini Dialog Manager orqali vazirlik adabiy tilida aniq va xushmuomala javob qaytarish.
3. 🔄 **Smart Operator Handover (Inson va AI Hamkorligi)**:
   - Fuqaroning noroziligi yoki shikoyati sezilganda (Sentiment Analysis: `Salbiy`), qo'ng'iroq zudlik bilan navbatchi operator ekraniga uzatiladi.
   - Operator bir klik bilan qo'ng'iroqni qabul qiladi va AI tomonidan tavsiya etilgan tayyor javoblardan foydalanadi.
4. 📊 **Tahliliy Boshqaruv Paneli (KPI & Analytics)**:
   - Bugungi qo'ng'iroqlar soni, AI tomonidan mustaqil hal etilgan ulush (84.2%), o'rtacha muloqot vaqti va fuqarolar qoniqish reytingi.
   - Mavzular bo'yicha taqsimot va soatlik qo'ng'iroqlar dinamikasi.
5. 📜 **Murojaatlar Arxivi va Transkripsiyalar**:
   - Har bir suhbatning to'liq matnli protokoli, audio yozuvi va AI tomonidan shakllantirilgan tahliliy xulosasi.

---

## 🏗️ Arxitektura va Texnologiyalar

| Qatlam | Texnologiya | Sabab va Afzallik |
|---|---|---|
| **Frontend** | Next.js 14 (App Router), Tailwind CSS, Lucide React, TypeScript | Zamonaviy hukumat uslubidagi interfeys, tezkor yuklanish |
| **Backend** | Python 3.12+ / 3.14, FastAPI, Uvicorn, WebSockets, Pydantic v2 | Yuqori tezlik, asinxron audio oqimlar, ML integratsiyasi |
| **Ovozli Model (TTS)** | `edge-tts` (`uz-UZ-MadinaNeural`, `uz-UZ-SardorNeural`) | To'liq bepul, litsenziyalangan tabiiy o'zbek neyron ovozlari |
| **Dialog Manager** | Google Gemini API (Multimodal / Dialog) + Resilient Rule-based Engine | Xakaton taqdimotida 100% oflayn/onlayn ishonchlilik kafolati |
| **Protokol** | WebSocket (`/ws/call/{id}`, `/ws/operator`) + REST API | Jonli audio va transkripsiya sinxronizatsiyasi |

---

## ⚡ Tezkor Ishga Tushirish

### 1. Avtomatik Ishga Tushirish (Tavsiya etiladi)
PowerShell terminalida bitta buyruq orqali:
```powershell
.\start_dev.ps1
```

### 2. Qo'lda Ishga Tushirish

**Backend:**
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Brauzerda oching:
- 🌐 **Fuqaro va Asosiy Sahifa:** [http://localhost:3000](http://localhost:3000)
- 📞 **Qo'ng'iroq Simulyatori:** [http://localhost:3000/call](http://localhost:3000/call)
- 🎧 **Operator Paneli:** [http://localhost:3000/operator](http://localhost:3000/operator)
- 📊 **Tahliliy Dashboard:** [http://localhost:3000/analytics](http://localhost:3000/analytics)
- 📜 **Qo'ng'iroqlar Arxivi:** [http://localhost:3000/history](http://localhost:3000/history)
- 🛠️ **FastAPI Swagger Hujjatlari:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Avtomatlashtirilgan Testlar

Backend testlarini ishga tushirish:
```bash
python -m pytest backend/tests/test_backend.py -v
```
Frontend build tekshiruvi:
```bash
cd frontend
npm run build
```

---

## 🏆 Hakamlar Oldida 2 Daqiqalik Jonli Taqdimot Ssenariysi

1. **Kirish (15 sek):** Bosh sahifani ko'rsating — Ta'lim va Innovatsiyalar Vazirligi call markazidagi muammo (kuniga minglab takroriy savollar).
2. **Jonli Qo'ng'iroq (40 sek):** `/call` sahifasida "Qo'ng'iroq Qilish" tugmasini bosing. O'zbek tilida savol bering: *"OTMlarga qabul qachon boshlanadi va nechta yo'nalish tanlash mumkin?"*. Audio to'lqin harakati, real-vaqt transkripsiya va Madina ovozida o'zbekcha javobni eshittiring.
3. **Smart Operatorga O'tish (25 sek):** Shikoyat yoki operator talab qiling: *"Mening arizamda muammo bor, operatorga ulang"*. AI darhol qo'ng'iroqni uzatadi.
4. **Operator Paneli (25 sek):** `/operator` sahifasiga o'ting — kutayotgan qo'ng'iroq, transkripsiya, ijobiy/salbiy sentiment va operator tomonidan 1-klikda tayyor javob yuborilishini namoyish eting.
5. **Analitika va Xulosa (15 sek):** `/analytics` sahifasida 84.2% AI avtomatlashtirish, qoniqish darajasi va soatlik yuklama grafiklarini ko'rsatib, loyihani yakunlang.
