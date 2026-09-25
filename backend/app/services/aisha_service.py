"""
Aisha AI Speech Service (TTS & STT)
Official integration with https://back.aisha.group
Provides Uzbek speech synthesis (Gulnoza model) and speech-to-text transcription.
"""
import io
import logging
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class AishaAPIException(Exception):
    """Exception raised for errors during Aisha AI API requests."""

    def __init__(self, message: str, status_code: int = 500, error_key: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_key = error_key


class AishaService:
    """Client for Aisha AI Speech APIs (TTS & STT)."""

    def __init__(self):
        self.base_url: str = settings.AISHA_BASE_URL.rstrip("/")
        self.api_key: str = settings.AISHA_API_KEY
        self.default_model: str = settings.AISHA_TTS_MODEL  # Gulnoza
        self.default_mood: str = settings.AISHA_TTS_MOOD    # Neutral
        self.default_speed: float = settings.AISHA_TTS_SPEED  # 1.0
        self.timeout: float = settings.AISHA_TIMEOUT_SECONDS  # 6.0s

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-Api-Key": self.api_key,
            "Accept-Language": "uz",
            "User-Agent": "VazirChat/1.0 (AishaClient)",
        }

    async def tts_synthesize(
        self,
        transcript: str,
        model: Optional[str] = None,
        mood: Optional[str] = None,
        speed: Optional[float] = None,
        timeout: Optional[float] = None,
    ) -> bytes:
        """
        Synthesizes speech using Aisha AI Gulnoza model.
        Endpoint: POST /api/v1/tts/post/ (multipart/form-data)
        Downloads synthesized audio from returned audio_path with X-Api-Key header.
        Returns: raw audio bytes (WAV).
        """
        clean_transcript = transcript.strip() if transcript else ""
        if not clean_transcript:
            clean_transcript = "Eshitaman, savolingizni bering."
        if len(clean_transcript) > 1000:
            clean_transcript = clean_transcript[:1000]

        target_model = model or self.default_model
        target_mood = mood or self.default_mood
        target_speed = str(speed if speed is not None else self.default_speed)
        request_timeout = timeout or self.timeout

        data = {
            "transcript": clean_transcript,
            "language": "uz",
            "model": target_model,
            "mood": target_mood,
            "speed": target_speed,
        }

        url = f"{self.base_url}/api/v1/tts/post/"
        async with httpx.AsyncClient(timeout=request_timeout) as client:
            try:
                res = await client.post(url, data=data, headers=self._get_headers())
            except Exception as exc:
                raise AishaAPIException(f"Network error connecting to Aisha TTS: {exc}", status_code=503)

            if res.status_code != 201:
                try:
                    err_json = res.json()
                    detail = err_json.get("detail", res.text)
                    error_key = err_json.get("error_key", "unknown_error")
                except Exception:
                    detail = res.text
                    error_key = "unknown_error"
                raise AishaAPIException(
                    f"Aisha TTS failed ({res.status_code}): {detail}",
                    status_code=res.status_code,
                    error_key=error_key,
                )

            res_data = res.json()
            audio_path = res_data.get("audio_path") or res_data.get("audio_url")
            if not audio_path:
                raise AishaAPIException("No audio_path returned by Aisha TTS", status_code=500)

            # Download audio file with required X-Api-Key header
            full_audio_url = audio_path if audio_path.startswith("http") else f"{self.base_url}{audio_path}"
            try:
                audio_res = await client.get(full_audio_url, headers=self._get_headers())
            except Exception as exc:
                raise AishaAPIException(f"Network error downloading audio from Aisha: {exc}", status_code=503)

            if audio_res.status_code != 200:
                raise AishaAPIException(
                    f"Failed to download audio from Aisha: HTTP {audio_res.status_code}",
                    status_code=audio_res.status_code,
                )

            return audio_res.content

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "voice.wav",
        language: str = "uz",
        timeout: Optional[float] = None,
    ) -> str:
        """
        Transcribes short audio using Aisha STT.
        Endpoint: POST /api/v1/stt/post/ (multipart/form-data)
        Returns: transcribed text string.
        """
        if not audio_bytes or len(audio_bytes) < 200:
            return ""

        request_timeout = timeout or (self.timeout + 4.0)
        url = f"{self.base_url}/api/v1/stt/post/"

        files = {
            "audio": (filename, audio_bytes, "audio/wav")
        }
        data = {
            "language": language,
            "has_diarization": "false",
        }

        async with httpx.AsyncClient(timeout=request_timeout) as client:
            try:
                res = await client.post(url, data=data, files=files, headers=self._get_headers())
            except Exception as exc:
                raise AishaAPIException(f"Network error connecting to Aisha STT: {exc}", status_code=503)

            if res.status_code != 200:
                try:
                    err_json = res.json()
                    detail = err_json.get("detail", res.text)
                    error_key = err_json.get("error_key", "unknown_error")
                except Exception:
                    detail = res.text
                    error_key = "unknown_error"
                raise AishaAPIException(
                    f"Aisha STT failed ({res.status_code}): {detail}",
                    status_code=res.status_code,
                    error_key=error_key,
                )

            res_data = res.json()
            return res_data.get("transcript", "").strip()


aisha_service = AishaService()
