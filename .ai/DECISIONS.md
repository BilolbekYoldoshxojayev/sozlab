# Architecture Decisions

## [2026-09-24] ADR-001: Monorepo Architecture with Next.js & FastAPI
### Context
Hackathon presentation requires both deep AI/ML capabilities (Python ecosystem, edge-tts, Gemini) and a responsive, high-fidelity government-grade web application (Next.js 14, Tailwind CSS, Web Audio API).
### Decision
Adopt a monorepo structure containing `/frontend` (Next.js) and `/backend` (FastAPI).
### Reason
Enables simultaneous rapid iteration, single-command orchestration, shared types/schemas, and zero deployment friction during the hackathon.

## [2026-09-24] ADR-002: Uzbek TTS Strategy via edge-tts with Smart Audio Caching
### Context
High-quality, natural Uzbek TTS is rare or expensive. `edge-tts` provides high-fidelity neural voices for Uzbek (`uz-UZ-MadinaNeural`, `uz-UZ-SardorNeural`) completely free with no API quota limitations.
### Decision
Use `edge-tts` asynchronously on the FastAPI backend, caching audio by MD5 hash of text to guarantee instant re-play and zero latency for common responses.
### Alternatives Considered
- Google Cloud TTS: Limited free minutes, requires credit card billing.
- Local Piper/Coqui TTS: High CPU/RAM overhead on 4GB VRAM laptops.
- Aisha AI API: Planned as production drop-in adapter once enterprise credentials are provided.

## [2026-09-24] ADR-003: Gemini Multimodal & Resilient Fallback Dialog Manager
### Context
Live hackathon presentations face internet fluctuations or sudden rate limits. The conversational agent must be bulletproof.
### Decision
Implement the Dialog Manager using Gemini 1.5/2.0 Flash with an embedded heuristic/rules fallback layer grounded directly in the Higher Education Ministry Knowledge Base. If API latency spikes or offline demo is required, the system instantly falls back to direct knowledge extraction without failing the call.

## [2026-09-25] ADR-004: Dual-AI Voice Strategy: Aisha AI Primary with Edge-TTS Fallback
### Context
User provided an Aisha AI API key and mandated prioritizing Aisha AI for natural Uzbek speech processing while retaining a secondary AI fallback.
### Decision
Adopt a Dual-AI strategy where `AishaService` acts as the prioritized primary voice engine (utilizing the `Gulnoza` model for Uzbek TTS and Aisha STT). All requests route first to Aisha AI. If network latency, API quota, or format errors occur, the system automatically and silently degrades to Edge-TTS (`uz-UZ-MadinaNeural`) and Gemini reasoning, ensuring zero dropped calls and high reliability.

## [2026-09-25] ADR-005: Client-Side Route Protection & Role Isolation
### Context
Operator and Admin control surfaces must not be visible or accessible to Citizens or unauthorized visitors using the same platform or accessing direct URLs.
### Decision
Implement `RoleProtectedPage.tsx` route guarding with role verification via `useRole` hook, coupled with dynamic role-filtered navigation in `Navbar.tsx`. Any unauthorized URL navigation displays an immediate "Kirish Cheklangan" security gate with a single return button.

## [2026-09-25] ADR-006: WebRTC Handshake State Machine & DOM Audio Binding
### Context
Direct browser-to-browser audio between Citizen and Operator failed due to offer/answer race conditions, detached audio elements blocked by autoplay policies, and unhandled socket signaling.
### Decision
Implement an explicit bidirectional `peer_ready` handshake protocol in `webrtcManager.ts` and `ws.py`. Remote media streams are bound directly to DOM-rendered `<audio>` elements to satisfy browser autoplay policies. Unprocessed early signaling messages are queued until peer connection initialization completes.

## [2026-09-25] ADR-007: Procedural Audio Chimes via Web Audio API
### Context
Call centers and modern voice agents (LiveKit, ElevenLabs, Vapi) provide auditory feedback for critical call transitions (connecting, ringing, operator joined, call end). Relying on external audio assets risks 404s, CORS, or latency.
### Decision
Generate auditory chimes procedurally using the Web Audio API (`AudioContext`, `OscillatorNode`, `GainNode`). This requires zero asset downloads, adds zero network latency, and operates 100% reliably in all environments.

## [2026-09-25] ADR-008: 100% Autonomous AI Voice Architecture & Strict PDF Legal Grounding
### Context
User mandated removing the human operator layer entirely from the codebase ("operator degan narsani butun kodbazadan olib tashla, only ai should be used") and basing all answers strictly on the attached 2 PDFs (50 FAQs & Legal Encyclopedia), refusing anything out-of-scope.
### Decision
1. Eliminate all operator routes (`/operator`), components (`OperatorQueue.tsx`, `OperatorLiveCall.tsx`), queues, and WebRTC peer-to-peer mechanisms. SözLab transitions to a 100% autonomous AI voice assistant.
2. Ingest all 50 FAQs (across 8 chapters) and the complete legal encyclopedia into `education_faq_50.py` and `education_legislation_encyclopedia.py`.
3. Enforce a strict system guardrail: answers are generated exclusively from this legal corpus, citing the exact Constitution/Law/Decree article. Any inquiry outside this scope triggers an official polite refusal explaining the ministry's legal boundaries.