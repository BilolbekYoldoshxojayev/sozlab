import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS
    raw_cors = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000")
    CORS_ORIGINS: list[str] = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    
    # Edge-TTS
    DEFAULT_TTS_VOICE: str = os.getenv("DEFAULT_TTS_VOICE", "uz-UZ-MadinaNeural")
    AUDIO_CACHE_DIR: Path = Path(os.getenv("AUDIO_CACHE_DIR", "./cache/audio")).resolve()
    
    # Ministry details
    MINISTRY_NAME: str = "O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligi"
    HOTLINE_NUMBER: str = "1006"

settings = Settings()

# Ensure cache directory exists
settings.AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
