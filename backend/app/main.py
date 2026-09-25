from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.core.config import settings
from app.api.routes import calls, analytics, knowledge, ws
from app.services.tts_service import tts_service

app = FastAPI(
    title="SözLab API",
    description="SözLab — O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligi AI Call Markazi",
    version="1.0.0"
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
app.include_router(analytics.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")
app.include_router(ws.router)

# Direct audio file streaming from cache
@app.get("/api/audio/{filename}", tags=["Audio"])
async def serve_audio_file(filename: str):
    path = tts_service.get_audio_filepath(filename)
    if not path:
        raise HTTPException(status_code=404, detail="Audio fayl topilmadi")
    return FileResponse(
        path=path,
        media_type="audio/mpeg",
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
