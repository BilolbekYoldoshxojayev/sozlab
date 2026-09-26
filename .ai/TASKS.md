## IN PROGRESS
### Milestone 15: Initial Greeting Fix, Hands-Free VAD, Cyrillic STT Converter, Plain Text TTS Normalizer, CapCut Beat Markers for Admin, and Operator Elimination
- [ ] **Task 15.1 [Initial Greeting Fix]**: Remove auto-greeting on call creation in `call_manager.py`, `calls.py`, `CallSimulator.tsx`, and `chat/page.tsx` so system waits for user input.
- [ ] **Task 15.2 [Cyrillic STT Converter]**: Implement `cyrillic_to_latin_uzbek` in `uzbek_text_normalizer.py` and apply in `stt_service.py` & `ai_dialog.py` so Cyrillic speech matches legal keywords.
- [ ] **Task 15.3 [Number & Modda Normalizer + Symbol Stripping]**: Convert `44-modda` -> `qirq to'rtinchi modda` and strip all asterisks (`*`) and symbols from LLM outputs for TTS.
- [ ] **Task 15.4 [Hands-Free VAD Audio Recording]**: Implement auto-silence detection in `CallSimulator.tsx` using Web Audio AnalyserNode (1.2s quiet audio triggers send).
- [ ] **Task 15.5 [Operator Elimination & Access Control]**: Delete `/operator` routes, remove operator from `useRole.tsx`, `Navbar.tsx`, `RoleGateModal.tsx`, `RoleProtectedPage.tsx`, and enforce strict 403 route protection.
- [ ] **Task 15.6 [Admin CapCut Timeline Beat Markers & Audio Player]**: Implement interactive question timeline beat markers and live transcript viewer in `app/admin/page.tsx`.
- [ ] **Task 15.7 [Testing & Build Verification]**: Run `pytest` backend tests and `npm run build` frontend build.


## REVIEW

## DONE
- [x] Task 14.1 [Database & Knowledge Base]: Ingest 50-page Constitution Legal Encyclopedia (`Ozbekiston_Konstitutsiyasi_Talim_Moddalari_50_Sahifa.json`) into backend knowledge search index (`backend/app/data/constitution_50_loader.py` & `knowledge_base.py`).
- [x] Task 14.2 [STT & Turn Logic]: Fix empty audio / silent turn greeting bug in `calls.py` and `ai_dialog.py` so system never auto-greets with "Va alaykum assalom" on silence.
- [x] Task 14.3 [Uzbek TTS Normalizer]: Implement `uzbek_text_normalizer.py` for Roman numerals (`I`, `II`, `III` -> `birinchi`, `ikkinchi`), ordinal fix (`1-chi` -> `birinchi`), and `X` sound pronunciation in `tts_service.py` & `voicelab_service.py`.
- [x] Task 14.4 [LLM Orchestrator & Complete Text]: Increase `max_tokens` to 1024 across Groq, Gemini, Cloudflare, Mistral, and Cerebras in `llm_orchestrator.py` to prevent response cutoffs.
- [x] Task 14.5 [Human Operator System]: Implement `operator_manager.py` with FIFO queue, operator online status, WebSocket queue position alerts, 3-second pre-call countdown warning, and live human-to-human audio/text stream in `calls.py` and `ws.py`.
- [x] Task 14.6 [Frontend Operator Page & UI Cleanup]: Re-create `/operator` console with 3-second countdown alert & queue dashboard; simplify site navbar and pages to focus on core features (`/call`, `/chat`, `/history`, `/operator`).
- [x] Task 14.7 [Verification & Testing]: Run backend unit tests (`pytest`), frontend production build (`npm run build`), and verify zero errors.

- [x] Task 9.1: Frontend - Completely delete `app/operator/page.tsx`, `OperatorQueue.tsx`, `OperatorLiveCall.tsx`; clean `Navbar.tsx`, `useRole.tsx`, `RoleGateModal.tsx`, `RoleProtectedPage.tsx`
- [x] Task 9.2: Backend - Remove operator fleet, queues, and handover logic from `call_manager.py`, `ws.py`, `calls.py`
- [x] Task 9.3: Backend - Ingest all 50 FAQs and official legal encyclopedia from the 2 PDFs into `app/data/education_faq_50.py` and `app/data/education_legislation_encyclopedia.py`
- [x] Task 9.4: Backend - Integrate official VoiceLab Studio SDK (Noble Lynx) in `voicelab_service.py`, `tts_service.py`, `stt_service.py`
- [x] Task 9.5: Backend - Implement strict guardrail prompt in `ai_dialog.py` (answers exclusively from the 2 PDFs, strictly refuses out-of-scope questions)
- [x] Task 9.6: Frontend - Polish `CallSimulator.tsx` and `app/page.tsx` for pure AI voice assistant with legal citation badges and obsidian monochrome UX
- [x] Task 9.7: Verification - Run full pytest test suite (64/64 passed, 100% green) and frontend verification scripts


## BLOCKED

## REVIEW

## DONE
- [x] Task 7.1: Backend - Integrate Aisha AI service (`aisha_service.py`), configure environment with user API key, and wire prioritized dual-AI TTS fallback in `tts_service.py`
- [x] Task 7.2: Backend - Add unit tests in `tests/test_aisha_service.py` verifying Aisha TTS/STT and edge-tts fallback resilience
- [x] Task 7.3: Frontend - Create `RoleProtectedPage.tsx` route guard and wrap `/operator`, `/admin`, `/call`, `/analytics`, `/history`
- [x] Task 7.4: Frontend - Dynamically filter navigation links in `Navbar.tsx` based on active user role
- [x] Task 7.5: Frontend - Overhaul copy across `app/page.tsx`, `CallSimulator.tsx`, `OperatorQueue.tsx`, and `app/admin/page.tsx` into punchy, concise enterprise copy
- [x] Task 7.6: Verification - Run full pytest suite (51/51 passed) and Next.js production build (`npm run build`)
- [x] Task 1.1: Scaffolding, CORS, schemas, and initial Knowledge Base
- [x] Task 1.2: Uzbek TTS engine (`edge-tts` with Madina/Sardor voices)
- [x] Task 1.3: Gemini Dialog Manager baseline
- [x] Task 1.4: WebSocket baseline & Call state manager
- [x] Task 2.1: Next.js frontend baseline
- [x] Task 3.1: Automated backend testing with pytest
- [x] Task 3.2: Automated frontend verification (`next build`)
- [x] Task 5.1: 7 A4 PDF workflow sheets in `team_guides/`
- [x] Task 5.2: Rebranding to SözLab across all files
- [x] Task 6.1: Backend - Add Gemini API Key to `backend/.env` & configure `gemini-flash-lite-latest` in `ai_dialog.py`
- [x] Task 6.2: Backend - Fix `POST /api/calls/{call_id}/audio-turn` 422 error by accepting both `audio`/`file` and `voice_name`/`voice`
- [x] Task 6.3: Backend - Implement auto-end call intent detection (`rahmat`, `xayr`, `sog' bo'ling`, `tushundim`) and zero-mock error handling
- [x] Task 6.4: Backend - Remove static mock operators from `call_manager.py`; implement real-time operator WebSocket registry (`AVAILABLE`/`BUSY`/`OFFLINE`)
- [x] Task 6.5: Backend - Create `/ws/admin` endpoint with `silent_listen` subscription for invisible eavesdropping & live teleprompter mirroring
- [x] Task 6.6: Backend - Implement 3-second auto-connect countdown event when operator finishes a call with callers in FIFO queue
- [x] Task 6.7: Frontend - Create `RoleGateModal.tsx` upfront role selection gateway & update `useRole.tsx`
- [x] Task 6.8: Frontend - Redesign `CallSimulator.tsx` into a sleek 100vh un-scrollable 1-page voice interface with dynamic Voice Orb & closed captions
- [x] Task 6.9: Frontend - Implement 3-second countdown modal in `OperatorQueue.tsx`
- [x] Task 6.10: Frontend - Implement Admin Ghost Mode (Live Transcript & Silent Audio Player) in `app/admin/page.tsx`
- [x] Task 6.11: Verification - Run `pytest backend/tests/test_backend.py` (38/38 passed) and `npm run build` (0 errors)