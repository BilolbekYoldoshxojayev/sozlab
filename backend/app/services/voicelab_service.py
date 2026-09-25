"""
Official VoiceLab SDK Service (Noble Lynx Subscription)
Provides:
1. VoiceLab TTS: Ultra-natural Uzbek speech synthesis using Gulnoza model
2. VoiceLab STT: High-accuracy Uzbek transcription via VoiceLab Speech-to-Text
"""

import asyncio
import logging
import os
import time
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class VoiceLabAPIException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class VoiceLabService:
    """Official VoiceLab API client wrapper using voicelab-sdk."""

    def __init__(self):
        self.api_key = settings.VOICELAB_API_KEY
        self.default_voice_id = settings.VOICELAB_VOICE_ID
        self.default_speed = settings.VOICELAB_SPEED
        self._client = None
        self._init_client()

    def _init_client(self):
        try:
            from voicelab import VoiceLab
            self._client = VoiceLab(api_key=self.api_key)
            logger.info("[VoiceLab] Official client initialized successfully.")
        except Exception as e:
            logger.error(f"[VoiceLab] Failed to initialize VoiceLab client: {e}")
            self._client = None

    def get_client(self):
        if self._client is None and self.api_key:
            self._init_client()
        return self._client

    def _sync_tts_synthesize(self, text: str, voice_id: str, speed: float) -> bytes:
        client = self.get_client()
        if not client:
            raise VoiceLabAPIException("VoiceLab client is not initialized or API key missing", status_code=500)
        
        try:
            res = client.tts.synthesize(
                text=text,
                language="uz",
                voice_id=voice_id,
                speed=speed
            )
            if hasattr(res, "audio") and res.audio:
                return res.audio
            raise VoiceLabAPIException("VoiceLab TTS returned empty audio payload", status_code=502)
        except Exception as e:
            logger.error(f"[VoiceLab TTS Error]: {e}")
            raise VoiceLabAPIException(f"VoiceLab TTS failed: {str(e)}", status_code=500) from e

    async def tts_synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        speed: Optional[float] = None
    ) -> bytes:
        """Asynchronously synthesizes speech using VoiceLab Gulnoza model."""
        clean_text = text.strip() if text else ""
        if not clean_text:
            clean_text = "Eshitaman, savolingizni bering."

        v_id = voice_id or self.default_voice_id
        spd = speed if speed is not None else self.default_speed

        return await asyncio.to_thread(self._sync_tts_synthesize, clean_text, v_id, spd)

    def _sync_transcribe(self, audio_bytes: bytes, filename: str, language: str) -> str:
        client = self.get_client()
        if not client:
            raise VoiceLabAPIException("VoiceLab client is not initialized", status_code=500)

        try:
            # 1. Dispatch transcription job
            job = client.stt.transcribe(
                audio=audio_bytes,
                language=language,
                filename=filename,
                content_type="audio/wav" if filename.endswith(".wav") else "audio/webm"
            )

            job_id = getattr(job, "id", None)
            if not job_id:
                # Immediate transcript if available
                if getattr(job, "transcript", None):
                    return job.transcript.strip()
                raise VoiceLabAPIException("No job ID or transcript returned by VoiceLab STT", status_code=502)

            # Check if immediately completed
            if getattr(job, "status", None) == "completed" and getattr(job, "transcript", None):
                return job.transcript.strip()

            # 2. Poll for completion (up to 15 attempts, ~6 seconds max)
            for _ in range(15):
                time.sleep(0.4)
                result = client.stt.get_transcription(job_id)
                status = getattr(result, "status", "")
                if status == "completed":
                    transcript = getattr(result, "transcript", "")
                    return (transcript or "").strip()
                elif status in ("failed", "error"):
                    raise VoiceLabAPIException(f"VoiceLab STT transcription job failed: {job_id}", status_code=502)

            # Timeout fallback
            logger.warning(f"[VoiceLab STT Timeout] Job {job_id} did not finish within timeout.")
            return ""
        except Exception as e:
            logger.error(f"[VoiceLab STT Error]: {e}")
            raise VoiceLabAPIException(f"VoiceLab STT failed: {str(e)}", status_code=500) from e

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "voice.wav",
        language: str = "uz"
    ) -> str:
        """Asynchronously transcribes audio using VoiceLab STT."""
        if not audio_bytes or len(audio_bytes) < 200:
            return ""
        return await asyncio.to_thread(self._sync_transcribe, audio_bytes, filename, language)


voicelab_service = VoiceLabService()
