"""
Speech-to-Text (STT) Service with Dual-AI Fallback:
Primary: Aisha AI STT (/api/v1/stt/post/)
Fallback: Google Gemini 2.5 Flash Multimodal Audio Recognition
"""
import logging
from typing import Optional
from app.core.config import settings
from app.services.aisha_service import aisha_service

logger = logging.getLogger(__name__)


class STTService:
    """Unified STT Service prioritizing Aisha AI with fallback to Gemini Multimodal."""

    async def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        filename: str = "voice.wav",
        language: str = "uz",
    ) -> str:
        """
        Transcribes audio with dual-AI strategy:
        1. Prioritize Aisha AI STT.
        2. Gracefully fall back to Gemini 2.5 Flash Multimodal STT on error or empty transcript.
        """
        if not audio_bytes or len(audio_bytes) < 200:
            return ""

        # 1. Primary: Aisha AI STT
        try:
            transcript = await aisha_service.transcribe_audio(
                audio_bytes=audio_bytes,
                filename=filename,
                language=language,
            )
            if transcript and transcript.strip():
                return transcript.strip()
        except Exception as e:
            logger.warning(f"[Dual-AI STT Fallback] Aisha STT unavailable ({e}). Falling back to Gemini Multimodal.")

        # 2. Resilient Fallback: Google Gemini Multimodal STT
        try:
            if settings.GEMINI_API_KEY:
                from google.genai import types
                from app.services.ai_dialog import dialog_manager

                client = dialog_manager._get_client()
                if client:
                    clean_mime = mime_type.split(";")[0].strip().lower() if mime_type else "audio/webm"
                    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=clean_mime)
                    prompt = (
                        "Quyidagi o'zbek tilidagi audio yozuvni eshiting va fuqaro nima deganini "
                        "faqat o'zbek adabiy tilidagi matn sifatida yozib bering (boshqa hech narsa qo'shmang)."
                    )
                    res = client.models.generate_content(
                        model=dialog_manager.PRIMARY_MODEL,
                        contents=[audio_part, prompt],
                    )
                    if res and res.text:
                        return res.text.strip().replace('"', '').replace("'", "")
        except Exception as ex:
            logger.error(f"[Gemini Multimodal STT Error]: {ex}")

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
