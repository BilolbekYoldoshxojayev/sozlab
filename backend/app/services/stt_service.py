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
            logger.warning(f"[VoiceLab STT Warning]: {e}. Attempting Aisha fallback.")

        # 2. Secondary Fallback: Aisha STT API
        try:
            transcript = await aisha_service.transcribe_audio(
                audio_bytes=audio_bytes,
                filename=filename,
                language=language,
            )
            if transcript and transcript.strip():
                return transcript.strip()
        except Exception as ex:
            logger.error(f"[Aisha STT Fallback Error]: {ex}")

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
