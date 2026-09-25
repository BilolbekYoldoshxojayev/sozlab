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