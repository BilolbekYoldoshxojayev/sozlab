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
    
    # Aisha AI Speech Integration
    AISHA_BASE_URL: str = os.getenv("AISHA_BASE_URL", "https://back.aisha.group")
    AISHA_API_KEY: str = os.getenv("AISHA_API_KEY", "vlk_Iyeis6LM8pFCI0aMVTbeXUeJqpL_3GMhgAXmMLMAwpI")
    AISHA_TTS_MODEL: str = os.getenv("AISHA_TTS_MODEL", "Gulnoza")
    AISHA_TTS_MOOD: str = os.getenv("AISHA_TTS_MOOD", "Neutral")
    AISHA_TTS_SPEED: float = float(os.getenv("AISHA_TTS_SPEED", "1.0"))
    AISHA_TIMEOUT_SECONDS: float = float(os.getenv("AISHA_TIMEOUT_SECONDS", "6.0"))
    AISHA_CIRCUIT_BREAKER_FAILURES: int = int(os.getenv("AISHA_CIRCUIT_BREAKER_FAILURES", "3"))
    AISHA_CIRCUIT_BREAKER_COOLDOWN: float = float(os.getenv("AISHA_CIRCUIT_BREAKER_COOLDOWN", "60.0"))
    
    # Ministry details
    MINISTRY_NAME: str = "O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligi"
    HOTLINE_NUMBER: str = "1006"

    # Supabase Database
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "") or os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or SUPABASE_KEY

settings = Settings()

# Ensure cache directory exists
settings.AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
