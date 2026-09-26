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
    
    # Gemini API (Rank 2 Multi-LLM)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    # Cerebras API (Ultra-Fast Hardware Inference)
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    CEREBRAS_API_URL: str = os.getenv("CEREBRAS_API_URL", "https://api.cerebras.ai/v1/chat/completions")
    CEREBRAS_PRIMARY_MODEL: str = os.getenv("CEREBRAS_PRIMARY_MODEL", "qwen-3.8-27b")
    CEREBRAS_FALLBACK_MODEL: str = os.getenv("CEREBRAS_FALLBACK_MODEL", "gpt-oss-120b")

    # Groq API (Rank 2 Multi-LLM, ultra-fast 0.35s)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_URL: str = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    GROQ_PRIMARY_MODEL: str = os.getenv("GROQ_PRIMARY_MODEL", "qwen/qwen3.8-27b")
    GROQ_FALLBACK_MODEL: str = os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-120b")

    # Cloudflare Workers AI (Rank 3 Multi-LLM)
    CLOUDFLARE_ACCOUNT_ID: str = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
    CLOUDFLARE_API_TOKEN: str = os.getenv("CLOUDFLARE_API_TOKEN", "")
    CLOUDFLARE_MODEL: str = os.getenv("CLOUDFLARE_MODEL", "@cf/meta/llama-3.1-8b-instruct")
    CLOUDFLARE_API_URL: str = os.getenv(
        "CLOUDFLARE_API_URL",
        f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/{CLOUDFLARE_MODEL}" if CLOUDFLARE_ACCOUNT_ID else ""
    )

    # Mistral AI (Rank 4 Multi-LLM)
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_API_URL: str = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1/chat/completions")
    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

    # Multi-LLM Orchestrator Config
    LLM_TIMEOUT_SECONDS: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "6.0"))
    
    # Edge-TTS
    DEFAULT_TTS_VOICE: str = os.getenv("DEFAULT_TTS_VOICE", "uz-UZ-MadinaNeural")
    AUDIO_CACHE_DIR: Path = Path(os.getenv("AUDIO_CACHE_DIR", "./cache/audio")).resolve()
    
    # VoiceLab Official SDK Integration (Noble Lynx)
    VOICELAB_API_KEY: str = os.getenv("VOICELAB_API_KEY", "")
    VOICELAB_VOICE_ID: str = os.getenv("VOICELAB_VOICE_ID", "voice_EvIb9vE6iY_dWgK7OobYdZcX")
    VOICELAB_SPEED: float = float(os.getenv("VOICELAB_SPEED", "1.32"))
    VOICELAB_TIMEOUT_SECONDS: float = float(os.getenv("VOICELAB_TIMEOUT_SECONDS", "15.0"))

    # Aisha AI Speech Integration (Secondary Fallback)
    AISHA_BASE_URL: str = os.getenv("AISHA_BASE_URL", "https://back.aisha.group")
    AISHA_API_KEY: str = os.getenv("AISHA_API_KEY", "")
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
