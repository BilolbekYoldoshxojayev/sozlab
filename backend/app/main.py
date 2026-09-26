from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.core.config import settings
from app.api.routes import calls, analytics, knowledge, chat, ws
from app.services.tts_service import tts_service
from app.services.call_manager import call_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    loaded = call_manager.load_all_calls_from_disk()
    print(f"[STARTUP] Loaded {loaded} call records from disk into CallManager.")
    yield


app = FastAPI(
    title="SözLab API",
    description="SözLab — O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligi AI Call Markazi",
    version="1.0.0",
    lifespan=lifespan
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Open for local dev & hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(calls.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")
app.include_router(ws.router)

# Direct audio file streaming from cache
@app.get("/api/audio/{filename}", tags=["Audio"])
async def serve_audio_file(filename: str):
    path = tts_service.get_audio_filepath(filename)
    if not path:
        raise HTTPException(status_code=404, detail="Audio fayl topilmadi")
    media_type = "audio/wav" if filename.lower().endswith(".wav") else "audio/mpeg"
    return FileResponse(
        path=path,
        media_type=media_type,
        filename=filename
    )

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "ministry": settings.MINISTRY_NAME,
        "hotline": settings.HOTLINE_NUMBER,
        "default_voice": settings.DEFAULT_TTS_VOICE,
        "gemini_active": bool(settings.GEMINI_API_KEY)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
