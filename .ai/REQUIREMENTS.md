# Requirements: Vazir Chat

## Functional Requirements

### 1. Citizen Voice Call Simulator (Fuqaro Qo'ng'iroq Interfeysi)
- **FR-1.1**: Web Audio API orqali brauzer mikrofonidan audio yozish va real-vaqtda audio waveform animatsiyasini ko'rsatish.
- **FR-1.2**: Foydalanuvchi ovozini backendga WebSocket yoki REST orqali uzatish, Gemini AI / STT orqali o'zbekcha matnga aylantirish.
- **FR-1.3**: Foydalanuvchiga tabiiy o'zbek tilida (edge-tts `uz-UZ-MadinaNeural` yoki `uz-UZ-SardorNeural`) ovozli javob qaytarish va brauzerda avtomatik o'ynash.
- **FR-1.4**: Suhbat tarixini (chat dialog stream) xabarlar ko'rinishida chiqarish.
- **FR-1.5**: "Operatorga ulash" (Handover to Human Agent) funksiyasi — AI hal qila olmagan yoki fuqaro talab qilgan holatda qo'ng'iroqni operator navbatiga o'tkazish.

### 2. Ministry Knowledge Base (Vazirlik Bilimlar Bazasi)
- **FR-2.1**: Ta'lim va Innovatsiyalar Vazirligiga oid rasmiy bilimlar bazasi (Knowledge Base):
  - Qabul jarayoni va my.uzbmb.uz orqali ro'yxatdan o'tish
  - Davlat grantlari va tabaqalashtirilgan kontrakt (super-kontrakt)
  - Talabalar turar joylari (TTJ) va ijara kompensatsiyasi
  - Xorijiy diplomlarni nostrifikatsiya qilish (tan olish)
  - Stipendiyalar va imtiyozli ta'lim kreditlari
  - O'qishni ko'chirish (Perevod) qoidalari
- **FR-2.2**: Semantik/kalit so'z bo'yicha qidiruv (Hybrid Search) va Gemini context injection (RAG) imkoniyati.

### 3. Operator Dashboard (Operator Paneli)
- **FR-3.1**: Faol qo'ng'iroqlar ro'yxati (Active Calls Queue) — AI xizmat ko'rsatayotgan, kutayotgan yoki operatorga o'tgan statuslar.
- **FR-3.2**: Real-time transkripsiya ko'rinishi (Live conversation feed).
- **FR-3.3**: Sentiment / Kayfiyat tahlili (Ijobiy, Neytral, Salbiy / Shikoyat) nishonlari bilan ko'rsatish.
- **FR-3.4**: Operator tomonidan qo'ng'iroqni o'ziga olish ("Qabul qilish") va AI tavsiya etgan tayyor javoblar (Smart Suggestions) orqali muloqot qilish.

### 4. Analytics & Call History (Tahlil va Tarix)
- **FR-4.1**: Umumiy statistika kartalari (Bugungi qo'ng'iroqlar, AI tomonidan mustaqil hal etilgan ulushi %, O'rtacha suhbat vaqti, Operator yuklamasi kamayishi).
- **FR-4.2**: Mavzular bo'yicha taqsimot grafiklari (Qabul, Grant, TTJ, Nostrifikatsiya, Kontrakt).
- **FR-4.3**: Barcha qo'ng'iroqlar arxivi, qidiruv, audio tinglash va AI tomonidan yaratilgan qisqa xulosa (Executive Summary).

### 5. Dual-AI Voice Processing (Aisha AI Primary + Gemini/Edge Fallback)
- **FR-5.1**: O'zbek tili uchun Aisha AI API (`https://back.aisha.group`, `Gulnoza` modeli) asosiy ustuvor ovoz generatori (TTS) va transkriptori (STT) sifatida ishlashi.
- **FR-5.2**: Agar Aisha AI tarmoq, limit yoki format xatoligi bersa, qo'ng'iroq uzilmasdan avtomatik ravishda Edge-TTS (`uz-UZ-MadinaNeural`) va Gemini dialog qatlamiga zaxira o'tishi (Zero downtime fallback).

### 6. Role-Based Access Isolation & Concise UX
- **FR-6.1**: Sahifalar qat'iy cheklovga ega bo'lishi: Fuqaro (`/call`), Operator (`/operator`), Admin (`/admin`). Boshqa foydalanuvchi roli boshqa oynaga to'g'ridan-to'g'ri o'tganda "Kirish Cheklangan" ekrani chiqishi va ruxsat berilmasligi.
- **FR-6.2**: Navbar menyusida faqat amaldagi rolga ruxsat etilgan bo'limlar ko'rinishi.
- **FR-6.3**: Saytdagi ortiqcha uzun byurokratik matnlar va xakaton yozuvlarini qisqartirish, zamonaviy, ixcham va aniq (less wordy) SaaS ko'rinishiga keltirish.

## Non-Functional Requirements
- **NFR-1 (Latency)**: Ovozli javob kechikishi 1.5 - 2.5 soniyadan oshmasligi kerak.
- **NFR-2 (Design)**: O'zbekiston Respublikasi davlat standartlariga mos, zamonaviy, ishonchli vizual dizayn (Gerb/Bayroq elementlari, ko'k-zumrad hukumat tuslari, toza tipografika).
- **NFR-3 (Offline/Fallback Resilience)**: Hackathon sahnasida internet sekinlashganda ham demo 100% to'xtab qolmasligi uchun avtomatik zaxira tizimi (local speech synthesis & knowledge fallback).
- **NFR-4 (Security)**: Xavfsiz WebSocket ulanish, maxfiy kalitlarni `.env` da saqlash, foydalanuvchi ma'lumotlarini tozalash (input sanitization), rolga asoslangan sahifa izolyatsiyasi.

## Acceptance Criteria
- Hakamlar oldida fuqaro sifatida savol berilganda: audio to'lqin ko'rinishi, o'zbekcha transkripsiya, aniq hukumat nizomiga asoslangan javob va o'zbekcha ovoz yangrashi.
- Operator panelida qo'ng'iroq o'z vaqtida paydo bo'lishi va tahlil qilinishi.
- Fuqaro operator yoki admin sahifasini ocha olmasligi, operator ham fuqaro yoki admin sahifasiga aralashmasligi.
- Barcha sahifalar xatosiz ishlashi va testlardan o'tishi.