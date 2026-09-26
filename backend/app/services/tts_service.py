"""
Text-to-Speech (TTS) Service with VoiceLab Primary Engine:
Primary: VoiceLab Official Studio SDK (Lola model, WAV format)
Fallback: Microsoft Edge-TTS (uz-UZ-MadinaNeural / uz-UZ-SardorNeural, MP3 format)
Resilience: In-memory Circuit Breaker (CLOSED, OPEN, HALF_OPEN) & MD5 disk cache
"""
import hashlib
import logging
import os
import time
from pathlib import Path
from typing import Optional, Tuple
import edge_tts
from app.core.config import settings
from app.services.voicelab_service import voicelab_service, VoiceLabAPIException

logger = logging.getLogger(__name__)


class CircuitBreakerState:
    CLOSED = "CLOSED"       # Normal: All traffic routes to VoiceLab
    OPEN = "OPEN"           # Failing: Traffic bypasses VoiceLab, routes directly to Edge-TTS
    HALF_OPEN = "HALF_OPEN" # Cooldown passed: One trial probe allowed to test VoiceLab


class CircuitBreaker:
    """In-memory Circuit Breaker to protect against external API failures."""

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = CircuitBreakerState.CLOSED

    def can_attempt(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time >= self.cooldown_seconds:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("[Circuit Breaker] Cooldown elapsed. Transitioned to HALF_OPEN (probing VoiceLab).")
                return True
            return False
        # HALF_OPEN allows probe
        return True

    def record_success(self):
        if self.state != CircuitBreakerState.CLOSED:
            logger.info("[Circuit Breaker] Call succeeded. Resetting state to CLOSED.")
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(
                    f"[Circuit Breaker] Failure threshold reached ({self.failure_count}/{self.failure_threshold}). "
                    f"Tripping to OPEN for {self.cooldown_seconds}s. Bypassing to Edge-TTS fallback."
                )
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            logger.warning("[Circuit Breaker] Half-open probe failed. Returning to OPEN state.")

    def reset(self):
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = CircuitBreakerState.CLOSED


class TTSService:
    """Dual-Engine TTS Service with disk-based MD5 caching and circuit breaker."""

    def __init__(self):
        self.cache_dir: Path = settings.AUDIO_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_edge_voice: str = settings.DEFAULT_TTS_VOICE
        self.breaker = CircuitBreaker(
            failure_threshold=settings.AISHA_CIRCUIT_BREAKER_FAILURES,
            cooldown_seconds=settings.AISHA_CIRCUIT_BREAKER_COOLDOWN,
        )

    def _get_cache_filename(
        self,
        text: str,
        provider: str,
        voice_or_model: str,
        rate_or_speed: str = "1.0",
        pitch: str = "+0Hz",
    ) -> str:
        key = f"{provider}_{voice_or_model}_{text}_{rate_or_speed}_{pitch}"
        file_hash = hashlib.md5(key.encode("utf-8")).hexdigest()
        ext = "wav" if provider in ("voicelab", "aisha") else "mp3"
        return f"{file_hash}.{ext}"

    def _get_legacy_edge_filename(self, text: str, voice: str, rate: str, pitch: str) -> str:
        key = f"{text}_{voice}_{rate}_{pitch}"
        file_hash = hashlib.md5(key.encode("utf-8")).hexdigest()
        return f"{file_hash}.mp3"

    async def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        prefer_voicelab: bool = True,
    ) -> Tuple[str, float, bool]:
        """
        Prioritizes VoiceLab Lola TTS, with seamless fallback to Edge-TTS (uz-UZ-MadinaNeural).
        Returns: (audio_url_path, duration_estimate_seconds, was_cached)
        """
        from app.services.uzbek_text_normalizer import normalize_text_for_tts
        clean_text = normalize_text_for_tts(text) if text else ""
        if not clean_text:
            clean_text = "Eshitaman, savolingizni bering."


        # Duration estimate (~13-15 chars per second for spoken Uzbek + 0.35s silence padding)
        duration_estimate = max(1.0, round(len(clean_text) / 14.0 + 0.35, 2))

        # Target identifiers
        vl_voice_id = settings.VOICELAB_VOICE_ID
        vl_speed = str(settings.VOICELAB_SPEED)
        vl_filename = self._get_cache_filename(clean_text, "voicelab", vl_voice_id, vl_speed, pitch="+0Hz")
        vl_filepath = self.cache_dir / vl_filename

        selected_edge_voice = voice or self.default_edge_voice
        if selected_edge_voice not in ["uz-UZ-MadinaNeural", "uz-UZ-SardorNeural"]:
            selected_edge_voice = "uz-UZ-MadinaNeural"

        edge_filename = self._get_cache_filename(clean_text, "edge", selected_edge_voice, rate, pitch)
        edge_filepath = self.cache_dir / edge_filename
        legacy_edge_filename = self._get_legacy_edge_filename(clean_text, selected_edge_voice, rate, pitch)
        legacy_edge_filepath = self.cache_dir / legacy_edge_filename

        # 1. Check disk cache
        if prefer_voicelab and vl_filepath.exists() and vl_filepath.stat().st_size > 100:
            return f"/api/audio/{vl_filename}", duration_estimate, True

        if edge_filepath.exists() and edge_filepath.stat().st_size > 100:
            if not prefer_voicelab or not self.breaker.can_attempt() or self.breaker.failure_count > 0:
                return f"/api/audio/{edge_filename}", duration_estimate, True

        if legacy_edge_filepath.exists() and legacy_edge_filepath.stat().st_size > 100:
            if not prefer_voicelab or not self.breaker.can_attempt() or self.breaker.failure_count > 0:
                return f"/api/audio/{legacy_edge_filename}", duration_estimate, True

        # 2. Primary: VoiceLab (Gulnoza model)
        if prefer_voicelab and self.breaker.can_attempt():
            try:
                audio_bytes = await voicelab_service.tts_synthesize(
                    text=clean_text,
                    voice_id=vl_voice_id,
                    speed=settings.VOICELAB_SPEED,
                )
                if audio_bytes and len(audio_bytes) > 100:
                    tmp_path = self.cache_dir / f"tmp_{vl_filename}"
                    tmp_path.write_bytes(audio_bytes)
                    tmp_path.replace(vl_filepath)
                    self.breaker.record_success()
                    return f"/api/audio/{vl_filename}", duration_estimate, False
                else:
                    raise VoiceLabAPIException("Empty audio returned by VoiceLab", status_code=502)
            except Exception as e:
                self.breaker.record_failure()
                logger.warning(
                    f"[VoiceLab TTS Fallback] VoiceLab unavailable ({e}). "
                    f"Breaker: {self.breaker.state} (failures={self.breaker.failure_count}). "
                    f"Falling back to Edge-TTS ({selected_edge_voice})."
                )

        # 3. Resilient Fallback: Edge-TTS (uz-UZ-MadinaNeural)
        if edge_filepath.exists() and edge_filepath.stat().st_size > 100:
            return f"/api/audio/{edge_filename}", duration_estimate, True

        try:
            communicate = edge_tts.Communicate(
                clean_text,
                selected_edge_voice,
                rate=rate,
                pitch=pitch,
            )
            tmp_path = self.cache_dir / f"tmp_{edge_filename}"
            await communicate.save(str(tmp_path))
            if tmp_path.exists() and tmp_path.stat().st_size > 0:
                tmp_path.replace(edge_filepath)
            return f"/api/audio/{edge_filename}", duration_estimate, False
        except Exception as e:
            logger.error(f"[TTS Critical Error] Both VoiceLab and Edge-TTS failed: {e}")
            if edge_filepath.exists():
                return f"/api/audio/{edge_filename}", duration_estimate, True
            if legacy_edge_filepath.exists():
                return f"/api/audio/{legacy_edge_filename}", duration_estimate, True
            raise e

    def get_audio_filepath(self, filename: str) -> Optional[Path]:
        """Returns safe path to audio file if exists within cache directory."""
        safe_name = os.path.basename(filename)
        path = self.cache_dir / safe_name
        if path.exists() and path.is_file():
            return path
        return None


tts_service = TTSService()
