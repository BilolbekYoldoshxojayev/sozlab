import hashlib
import os
import asyncio
from pathlib import Path
from typing import Optional, Tuple
import edge_tts
from app.core.config import settings

class TTSService:
    def __init__(self):
        self.cache_dir: Path = settings.AUDIO_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_voice: str = settings.DEFAULT_TTS_VOICE

    def _get_cache_filename(self, text: str, voice: str, rate: str, pitch: str) -> str:
        key = f"{text}_{voice}_{rate}_{pitch}"
        file_hash = hashlib.md5(key.encode("utf-8")).hexdigest()
        return f"{file_hash}.mp3"

    async def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> Tuple[str, float, bool]:
        """
        Synthesizes Uzbek text using edge-tts.
        Returns: (audio_url_path, duration_estimate_seconds, was_cached)
        """
        clean_text = text.strip()
        if not clean_text:
            clean_text = "Eshitaman, savolingizni bering."

        selected_voice = voice or self.default_voice
        if selected_voice not in ["uz-UZ-MadinaNeural", "uz-UZ-SardorNeural"]:
            selected_voice = "uz-UZ-MadinaNeural"

        filename = self._get_cache_filename(clean_text, selected_voice, rate, pitch)
        file_path = self.cache_dir / filename

        # Estimated duration in seconds (average ~13-15 chars per second for Uzbek speech)
        duration_estimate = max(1.0, round(len(clean_text) / 14.0, 2))

        # Check cache
        if file_path.exists() and file_path.stat().st_size > 1024:
            return f"/api/audio/{filename}", duration_estimate, True

        # Synthesize with edge-tts
        try:
            communicate = edge_tts.Communicate(
                clean_text,
                selected_voice,
                rate=rate,
                pitch=pitch
            )
            
            # Write to temporary file then atomically replace to avoid half-written reads
            tmp_path = self.cache_dir / f"tmp_{filename}"
            await communicate.save(str(tmp_path))
            
            if tmp_path.exists() and tmp_path.stat().st_size > 0:
                tmp_path.replace(file_path)
            
            return f"/api/audio/{filename}", duration_estimate, False
            
        except Exception as e:
            print(f"[TTS Error] Generation failed for '{clean_text[:30]}...': {e}")
            # If network error or failure occurs, check if file exists anyway or return empty fallback
            if file_path.exists():
                return f"/api/audio/{filename}", duration_estimate, True
            raise e

    def get_audio_filepath(self, filename: str) -> Optional[Path]:
        """Returns safe path to audio file if exists within cache directory."""
        # Prevent directory traversal
        safe_name = os.path.basename(filename)
        path = self.cache_dir / safe_name
        if path.exists() and path.is_file():
            return path
        return None

tts_service = TTSService()
