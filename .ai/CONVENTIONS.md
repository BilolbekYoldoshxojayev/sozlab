# Conventions: Vazir Chat

## Coding Standards
- **Python**:
  - Python 3.12+ syntax, strict type hints (`typing`, `pydantic v2`).
  - PEP 8 compliance, async-first for I/O and HTTP/WebSocket operations.
  - Exception handling with structured logging.
- **Frontend / TypeScript**:
  - Next.js 14 App Router standards.
  - Strict TypeScript (`noImplicitAny`, type-safe API responses).
  - Tailwind CSS with semantic government theme tokens:
    - Primary: `#0F3A66` (Deep Official Blue)
    - Emerald / Gold accents: `#0F766E` / `#D97706`
    - Neutral: `#0F172A` / `#F8FAFC`
- **Naming Conventions**:
  - Python: `snake_case` for variables, functions, files; `PascalCase` for classes.
  - TypeScript: `camelCase` for variables, functions; `PascalCase` for React components and types.
- **Testing**:
  - Backend: `pytest`, `pytest-asyncio`, `httpx` TestClient.
  - Frontend: clean TypeScript builds (`npm run build`).