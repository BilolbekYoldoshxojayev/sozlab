"""
Speech-to-Text (STT) Service:
Exclusive Provider: VoiceLab Official Studio SDK (Noble Lynx Subscription)
Fallback: Aisha API (X-Api-Key)
Note: Gemini STT is strictly removed per architectural mandate.
"""
import logging
from typing import Optional
from app.core.config import settings
from app.services.voicelab_service import voicelab_service
from app.services.aisha_service import aisha_service

logger = logging.getLogger(__name__)


class STTService:
    """Unified STT Service utilizing VoiceLab Studio SDK exclusively for speech recognition."""

    async def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        filename: str = "voice.wav",
        language: str = "uz",
    ) -> str:
        """
        Transcribes audio with VoiceLab Studio SDK as primary.
        Zero Gemini audio calls.
        """
        if not audio_bytes or len(audio_bytes) < 200:
            return ""

        # 1. Primary: VoiceLab Studio SDK
        try:
            transcript = await voicelab_service.transcribe_audio(
                audio_bytes=audio_bytes,
                filename=filename,
                language=language,
            )
            if transcript and transcript.strip():
                return transcript.strip()
        except Exception as e:
            print(f"⚠️ [VoiceLab STT Warning]: {e}. Attempting Groq Whisper fallback...")
            logger.warning(f"[VoiceLab STT Warning]: {e}. Attempting Groq Whisper fallback.")

        # 2. Secondary High-Speed Fallback: Groq Whisper Large v3 Turbo (Uzbek)
        if settings.GROQ_API_KEY:
            try:
                import httpx
                import time
                t0 = time.perf_counter()
                print(f"🔄 [STT FALLBACK] Running Groq Whisper Large v3 Turbo ({len(audio_bytes):,} bytes)...")
                headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
                files = {"file": (filename or "speech.wav", audio_bytes, mime_type or "audio/wav")}
                data = {"model": "whisper-large-v3-turbo", "language": "uz"}
                async with httpx.AsyncClient(timeout=25.0) as client:
                    resp = await client.post(
                        "https://api.groq.com/openai/v1/audio/transcriptions",
                        headers=headers,
                        files=files,
                        data=data
                    )
                    if resp.status_code == 200:
                        t1 = time.perf_counter()
                        text = resp.json().get("text", "").strip()
                        if text:
                            print(f"✅ [GROQ WHISPER STT] Fallback transcribed in {(t1-t0):.2f}s: '{text}'")
                            return text
            except Exception as ex:
                print(f"❌ [GROQ WHISPER STT Error]: {ex}")
                logger.error(f"[Groq Whisper STT Error]: {ex}")

        return ""

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "voice.wav",
        language: str = "uz",
        mime_type: str = "audio/wav",
    ) -> str:
        """Alias for transcribe method supporting filename-first argument order."""
        return await self.transcribe(
            audio_bytes=audio_bytes,
            mime_type=mime_type,
            filename=filename,
            language=language,
        )


stt_service = STTService()
