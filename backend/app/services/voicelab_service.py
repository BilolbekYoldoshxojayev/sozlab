"""
Official VoiceLab SDK Service (Noble Lynx Subscription)
Provides:
1. VoiceLab TTS: Ultra-natural Uzbek speech synthesis using Lola model (default) with 350ms trailing silence
2. VoiceLab STT: High-accuracy Uzbek transcription via VoiceLab Speech-to-Text
"""

import asyncio
import io
import logging
import os
import time
import wave
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


def append_trailing_silence_wav(audio_bytes: bytes, silence_ms: int = 350) -> bytes:
    """
    Appends silence_ms (default 350ms) of zero-amplitude PCM samples to a WAV audio buffer.
    Safely preserves channels, sample width, and frame rate.
    If the buffer is not a valid RIFF/WAVE header, returns original audio_bytes without crashing.
    """
    if not audio_bytes or len(audio_bytes) < 44 or not audio_bytes.startswith(b"RIFF"):
        return audio_bytes
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as r:
            params = r.getparams()
            framerate = r.getframerate()
            nchannels = r.getnchannels()
            sampwidth = r.getsampwidth()
            nframes = r.getnframes()
            pcm_data = r.readframes(nframes)

        silence_frames = int(framerate * (silence_ms / 1000.0))
        silence_pcm = b"\x00" * (silence_frames * nchannels * sampwidth)

        out_buf = io.BytesIO()
        with wave.open(out_buf, "wb") as w:
            w.setparams(params)
            w.writeframes(pcm_data + silence_pcm)

        return out_buf.getvalue()
    except Exception as e:
        logger.warning(f"[Audio Padding] Could not append trailing silence: {e}")
        return audio_bytes


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
            t0 = time.perf_counter()
            print(f"\n[VOICELAB-TTS] Synthesizing speech with voice {voice_id} (speed={speed}): '{text}'")
            res = client.tts.synthesize(
                text=text,
                language="uz",
                voice_id=voice_id,
                speed=speed
            )
            if hasattr(res, "audio") and res.audio:
                t1 = time.perf_counter()
                padded_audio = append_trailing_silence_wav(res.audio, silence_ms=350)
                print(f"[VOICELAB-TTS-SUCCESS] Generated {len(res.audio):,} bytes (padded to {len(padded_audio):,} bytes, +350ms silence) in {(t1-t0):.2f}s")
                return padded_audio
            raise VoiceLabAPIException("VoiceLab TTS returned empty audio payload", status_code=502)
        except Exception as e:
            print(f"[VOICELAB-TTS-ERROR]: {e}")
            logger.error(f"[VoiceLab TTS Error]: {e}")
            raise VoiceLabAPIException(f"VoiceLab TTS failed: {str(e)}", status_code=500) from e

    async def tts_synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        speed: Optional[float] = None
    ) -> bytes:
        """Asynchronously synthesizes speech using VoiceLab Lola model."""
        from app.services.uzbek_text_normalizer import normalize_text_for_tts
        clean_text = normalize_text_for_tts(text) if text else ""
        if not clean_text:
            clean_text = "Eshitaman, savolingizni bering."

        v_id = voice_id or self.default_voice_id
        if v_id in ["Lola", "lola", "Gulnoza", "default"]:
            v_id = self.default_voice_id
        spd = speed if speed is not None else self.default_speed

        return await asyncio.to_thread(self._sync_tts_synthesize, clean_text, v_id, spd)

    def _sync_transcribe(self, audio_bytes: bytes, filename: str, language: str) -> str:
        client = self.get_client()
        if not client:
            raise VoiceLabAPIException("VoiceLab client is not initialized", status_code=500)

        # Detect audio container format
        if audio_bytes.startswith(b"RIFF"):
            ct = "audio/wav"
            fn = "speech.wav"
        elif audio_bytes.startswith(b"\x1aE\xdf\xa3"):
            ct = "audio/webm"
            fn = "speech.webm"
        elif audio_bytes.startswith(b"OggS"):
            ct = "audio/ogg"
            fn = "speech.ogg"
        else:
            ct = "audio/wav" if filename.endswith(".wav") else "audio/webm"
            fn = filename

        t0 = time.perf_counter()
        print(f"\n[VOICELAB-STT] Sending {len(audio_bytes):,} bytes ({ct}) to VoiceLab API...")

        try:
            # 1. Dispatch transcription job
            job = client.stt.transcribe(
                audio=audio_bytes,
                language=language,
                filename=fn,
                content_type=ct,
                timeout=30.0
            )

            job_id = getattr(job, "id", None)
            if not job_id:
                # Immediate transcript if available
                if getattr(job, "transcript", None):
                    t1 = time.perf_counter()
                    transcript = job.transcript.strip()
                    print(f"[VOICELAB-STT-SUCCESS] Immediate transcript in {(t1-t0):.2f}s: '{transcript}'")
                    return transcript
                raise VoiceLabAPIException("No job ID or transcript returned by VoiceLab STT", status_code=502)

            # Check if immediately completed
            if getattr(job, "status", None) == "completed" and getattr(job, "transcript", None):
                t1 = time.perf_counter()
                transcript = job.transcript.strip()
                print(f"[VOICELAB-STT-SUCCESS] Immediate completed in {(t1-t0):.2f}s: '{transcript}'")
                return transcript

            # 2. Balanced progressive polling for completion (accommodates short & long audio turns up to ~18s)
            poll_intervals = [
                0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.40, 0.45, 0.45, 0.50,
                0.50, 0.50, 0.50, 0.50, 0.50, 0.60, 0.60, 0.60, 0.60, 0.60,
                0.70, 0.70, 0.70, 0.70, 0.80, 0.80, 0.80, 0.80, 1.00, 1.00
            ]
            for attempt, delay in enumerate(poll_intervals):
                time.sleep(delay)
                result = client.stt.get_transcription(job_id)
                status = getattr(result, "status", "")
                if status == "completed":
                    t1 = time.perf_counter()
                    transcript = (getattr(result, "transcript", "") or "").strip()
                    print(f"[VOICELAB-STT-SUCCESS] Completed at attempt {attempt+1} in {(t1-t0):.2f}s: '{transcript}'")
                    return transcript
                elif status in ("failed", "error"):
                    raise VoiceLabAPIException(f"VoiceLab STT transcription job failed: {job_id}", status_code=502)

            # Timeout fallback
            print(f"[VOICELAB-STT-TIMEOUT] Job {job_id} did not finish within timeout.")
            return ""
        except Exception as e:
            print(f"[VOICELAB-STT-ERROR]: {e}")
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
