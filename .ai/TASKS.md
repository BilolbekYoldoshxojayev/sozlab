# Task Board: SözLab Production Overhaul

## READY

## IN PROGRESS

## BLOCKED

## REVIEW

## DONE
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