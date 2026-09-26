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

### 7. Human Operator Connection & FIFO Queue
- **FR-7.1**: Real human operator request mechanism: Citizens can request human operator via UI button or voice query ("Operator bilan bog'lanish").
- **FR-7.2**: FIFO Queue Management: When all human operators are busy or unavailable, citizens are placed in a first-in-first-out (FIFO) queue with live position tracking ("Siz navbatdasiz: 1-o'rin").
- **FR-7.3**: Operator Pre-Call 3-Second Countdown: Before an available operator receives an incoming citizen call, the operator console presents an active 3-second animated & audible countdown warning ("Daqiqalar: 3... 2... 1...").
- **FR-7.4**: Flawless Human-to-Human Audio & Chat Bridge: Real-time web audio and text chat connection between citizen and operator via WebSocket room.

### 8. Constitution 50-Page Encyclopedia Database Integration
- **FR-8.1**: Full ingestion of `Ozbekiston_Konstitutsiyasi_Talim_Moddalari_50_Sahifa.json` (18 Articles, 9 Chapters, 50 Pages) into backend knowledge base for 100% legal grounding.

### 9. Uzbek TTS Text Normalization & Complete Answers
- **FR-9.1**: Roman numerals (`I`, `II`, `III`, `IV`, `V`, `VI`, `VII`, `VIII`, `IX`, `X`) normalized to Uzbek numbers (`birinchi`, `ikkinchi`, etc.) for TTS synthesis.
- **FR-9.2**: Ordinals `1-chi`, `2-chi` normalized to `birinchi`, `ikkinchi` (never `birchi`).
- **FR-9.3**: English `X` in abbreviations (like `DXM`) normalized to Uzbek `X` / `Davlat Xizmatlari Markazi`.
- **FR-9.4**: LLM max_tokens increased to 1024 to prevent cutoffs mid-sentence or mid-citation.
- **FR-9.5**: Silent turn / STT non-speech bug resolved so system never auto-greets with "Va alaykum assalom" on silent audio.

### 10. UI Simplification (Core Features Only)
- **FR-10.1**: Simplify navbar and site navigation to focus strictly on core features: `Ovozli Qo'ng'iroq`, `AI Chat`, `Qo'ng'iroqlar & FAQ`, `Operator Paneli`.

## Non-Functional Requirements
- **NFR-1 (Latency)**: Ovozli javob kechikishi 1.5 - 2.5 soniyadan oshmasligi kerak.
- **NFR-2 (Design)**: Strict 3-color dark executive palette (Slate Black, Royal Navy Blue, Ice White).
- **NFR-3 (Offline/Fallback Resilience)**: Automatic multi-tier LLM failover (Groq -> Cloudflare -> Gemini -> Mistral -> Local Rule Engine).
- **NFR-4 (Security)**: Secure WebSocket connection, role isolation, input sanitization.


## Acceptance Criteria
- Hakamlar oldida fuqaro sifatida savol berilganda: audio to'lqin ko'rinishi, o'zbekcha transkripsiya, aniq hukumat nizomiga asoslangan javob va o'zbekcha ovoz yangrashi.
- Operator panelida qo'ng'iroq o'z vaqtida paydo bo'lishi va tahlil qilinishi.
- Fuqaro operator yoki admin sahifasini ocha olmasligi, operator ham fuqaro yoki admin sahifasiga aralashmasligi.
- Barcha sahifalar xatosiz ishlashi va testlardan o'tishi.