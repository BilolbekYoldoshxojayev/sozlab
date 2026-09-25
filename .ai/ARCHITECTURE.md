# Architecture: Vazir Chat

## Stack
- **Frontend**: Next.js 14+ (App Router), React 18, Tailwind CSS, Lucide React, HTML5 Web Audio API / Canvas Visualizer.
- **Backend**: Python 3.12+ / 3.14 with FastAPI, Uvicorn, WebSockets, Pydantic v2.
- **AI & Speech Engine**:
  - LLM Dialog Manager: Google Gemini 1.5 / 2.0 Flash (`google-genai` / REST) with specialized Uzbek system prompt and structured JSON intent extraction.
  - Speech-to-Text: Gemini Multimodal Audio transcription + fallback text input.
  - Text-to-Speech: `edge-tts` utilizing neural voices (`uz-UZ-MadinaNeural` ayol ovozi, `uz-UZ-SardorNeural` erkak ovozi), caching in memory/disk.
- **Database / State**:
  - In-memory async state store + Supabase / PostgreSQL schema compatibility for call logs, transcriptions, queue events.
- **Inter-service Communication**:
  - WebSocket (`/ws/call/{call_id}`) for bidirectional voice & transcript streaming.
  - REST endpoints (`/api/calls`, `/api/analytics`, `/api/knowledge`) for dashboard queries.

## Application Structure
```
vazir-chat/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── calls.py         # REST: Qo'ng'iroqlar ro'yxati, qidiruv, operator amallari
│   │   │   │   ├── analytics.py     # REST: KPI, statistika va grafik ma'lumotlari
│   │   │   │   ├── knowledge.py     # REST: Vazirlik bilimlar bazasi qidiruvi
│   │   │   │   └── ws.py            # WebSocket: Real-vaqtda audio va transkript almashish
│   │   ├── core/
│   │   │   ├── config.py            # Sozlamalar va .env o'zgaruvchilari
│   │   │   └── logger.py            # Log yozish tizimi
│   │   ├── services/
│   │   │   ├── ai_dialog.py         # Gemini Dialog Manager, niyat (intent) va sentiment tahlili
│   │   │   ├── knowledge_base.py    # Vazirlik nizomlari, FAQ, semantik qidiruv
│   │   │   ├── tts_service.py       # edge-tts bilan audio yaratish va kesh
│   │   │   └── call_manager.py      # Qo'ng'iroqlar holatini boshqarish (in-memory + db)
│   │   ├── models/
│   │   │   └── schemas.py           # Pydantic v2 ma'lumotlar modellari
│   │   └── main.py                  # FastAPI ilovasi va CORS sozlamalari
│   ├── tests/                       # Pytest testlari
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx               # Asosiy layout, davlat ramzlari va navigatsiya
│   │   ├── page.tsx                 # Bosh sahifa (Landing)
│   │   ├── call/
│   │   │   └── page.tsx             # Fuqaro ovozli qo'ng'iroq simulyatori
│   │   ├── operator/
│   │   │   └── page.tsx             # Operator boshqaruv paneli
│   │   ├── analytics/
│   │   │   └── page.tsx             # Analitika va diagrammalar
│   │   └── history/
│   │       └── page.tsx             # Qo'ng'iroqlar arxivi va transkripsiyalar
│   ├── components/
│   │   ├── Navbar.tsx               # Hukumat uslubidagi yuqori menyu
│   │   ├── AudioWaveform.tsx        # Canvas Web Audio to'lqin visualizatori
│   │   ├── CallSimulator.tsx        # Mikrofon, qo'ng'iroq boshqaruvi va audio pleyer
│   │   ├── OperatorQueue.tsx        # Jonli navbat va transkript monitori
│   │   └── AnalyticsCharts.tsx      # SVG/Tailwind asosidagi ko'rkam diagrammalar
│   ├── lib/
│   │   ├── api.ts                   # Backend REST va WebSocket mijozlari
│   │   └── types.ts                 # TypeScript interfeyslari
│   ├── package.json
│   └── tailwind.config.js
```

## Data Flow
1. **Fuqaro gapiradi** -> Web Audio API mikrofon audio oqimini yozadi -> Base64/Binary bo'lib WebSocket orqali Backendga uzatiladi.
2. **Backend**:
   - `ai_dialog.py`: Audioni/matnni tahlil qiladi, niyatni (masalan: `qabul_sanasi`, `kontrakt_narxi`, `ttj_ariza`) aniqlaydi.
   - `knowledge_base.py`: Eng mos vazirlik reglamentini chiqaradi.
   - `Gemini`: Aniq, xushmuomala o'zbek tilida rasmiy javob tuzadi va sentimentni baholaydi (`Ijobiy`, `Neytral`, `Salbiy`).
   - `tts_service.py`: Javob matnini o'zbek ayol ovozida (`uz-UZ-MadinaNeural`) MP3/WAV ga o'giradi.
3. **Frontend**:
   - WebSocket orqali transkript va audio URL / Base64 keladi.
   - Audio darhol ijro etiladi, suhbat oynasida matn ko'rinadi.
   - Operator paneliga real-vaqtda yangilangan ma'lumot uzatiladi.