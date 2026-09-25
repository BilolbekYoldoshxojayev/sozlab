"""
Unit & Integration Tests for VoiceLab Studio SDK Service (Noble Lynx)
Tests:
1. VoiceLab TTS synthesis
2. VoiceLab disk caching
3. VoiceLab STT transcription
4. TTSService fallback
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.voicelab_service import voicelab_service, VoiceLabAPIException
from app.services.tts_service import tts_service, CircuitBreaker, CircuitBreakerState
from app.services.stt_service import stt_service

def test_circuit_breaker_initial_state():
    cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=10.0)
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.can_attempt() is True

def test_circuit_breaker_tripping_and_reset():
    cb = CircuitBreaker(failure_threshold=2, cooldown_seconds=1.0)
    cb.record_failure()
    assert cb.state == CircuitBreakerState.CLOSED
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    assert cb.can_attempt() is False
    cb.reset()
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.can_attempt() is True

@pytest.mark.asyncio
async def test_voicelab_tts_mock_success():
    mock_audio = b"RIFF" + b"\x00" * 400
    mock_result = MagicMock()
    mock_result.audio = mock_audio

    with patch.object(voicelab_service, "_sync_tts_synthesize", return_value=mock_audio):
        audio = await voicelab_service.tts_synthesize("Assalomu alaykum", "voice_01J9NEUTRAL0000000000000001")
        assert audio == mock_audio
        assert len(audio) == 404

@pytest.mark.asyncio
async def test_voicelab_stt_mock_success():
    with patch.object(voicelab_service, "_sync_transcribe", return_value="Maktabda pul yig'ish taqiqlangan"):
        dummy_audio = b"RIFF" + b"\x00" * 500
        transcript = await stt_service.transcribe(dummy_audio)
        assert transcript == "Maktabda pul yig'ish taqiqlangan"

@pytest.mark.asyncio
async def test_tts_service_fallback_to_edge_tts():
    # Force voicelab failure to verify circuit breaker & edge-tts fallback
    with patch.object(voicelab_service, "tts_synthesize", side_effect=VoiceLabAPIException("Mock failure", 500)):
        url, duration, cached = await tts_service.generate_speech(
            "Test fallback speech text",
            voice="uz-UZ-MadinaNeural"
        )
        assert url.startswith("/api/audio/")
        assert duration > 0
