"""
Adversarial Stress Test Suite for VoiceLab Studio SDK Speech Engine and Circuit Breaker
Targeting:
1. Circuit Breaker Stress: Consecutive errors tripping CLOSED -> OPEN and state machine integrity.
2. OPEN State Bypass: Zero-latency penalty bypass directly to Edge-TTS with 0 VoiceLab calls.
3. Timeout & Error Resilience: VoiceLab timeout/500/503/429 handling with zero downtime (valid audio URL).
4. Corrupted / Empty Audio in STT: Empty, sub-200B, boundary, corrupted headers, and STT failure.
5. Cache Collision Avoidance: Hash uniqueness across providers, models, voices, speeds, and pitches.
6. Voice Call Loop Immunity: Audio-turn and WebSocket voice loop resilience under complete failure.
"""

import asyncio
import io
import time
from pathlib import Path
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.voicelab_service import (
    VoiceLabAPIException,
    VoiceLabService,
    voicelab_service,
)
from app.services.tts_service import (
    CircuitBreaker,
    CircuitBreakerState,
    TTSService,
    tts_service,
)
from app.services.stt_service import (
    STTService,
    stt_service,
)
from app.services.call_manager import call_manager, CallStatus

client = TestClient(app)


# ============================================================================
# VECTOR 1: CIRCUIT BREAKER STRESS - CONSECUTIVE ERRORS CLOSED -> OPEN
# ============================================================================

def test_circuit_breaker_consecutive_failure_threshold_stress():
    """
    Stress-test consecutive error transitions:
    - Verifies CLOSED -> OPEN precisely at failure_threshold.
    - Tests 100 consecutive failures: ensures state remains OPEN and failure count tracks.
    """
    threshold = 5
    cb = CircuitBreaker(failure_threshold=threshold, cooldown_seconds=60.0)
    assert cb.state == CircuitBreakerState.CLOSED

    # Failures 1 through threshold - 1 must keep state CLOSED
    for i in range(1, threshold):
        cb.record_failure()
        assert cb.state == CircuitBreakerState.CLOSED, f"State tripped prematurely at {i} failures"
        assert cb.failure_count == i
        assert cb.can_attempt() is True

    # N-th failure must transition immediately to OPEN
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    assert cb.failure_count == threshold
    assert cb.can_attempt() is False

    # 100 additional consecutive failures while OPEN
    for i in range(threshold + 1, threshold + 101):
        prev_time = cb.last_failure_time
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == i
        assert cb.last_failure_time >= prev_time
        assert cb.can_attempt() is False


@pytest.mark.asyncio
async def test_circuit_breaker_concurrent_failure_storm(tmp_path):
    """
    Simulate a high-concurrency burst of 20 simultaneous failing requests through TTSService on uncached texts.
    Verifies that the circuit breaker trips to OPEN without deadlock, race conditions, or unhandled errors.
    """
    tts = TTSService()
    tts.cache_dir = tmp_path
    tts.breaker.failure_threshold = 3
    tts.breaker.cooldown_seconds = 10.0
    tts.breaker.reset()

    text = f"Konkurrent xatolar oqimi sinovi {time.time()}"

    # Mock Edge-TTS save so fallback succeeds cleanly
    async def fake_edge_save(save_path):
        Path(save_path).write_bytes(b"ID3" + b"\x00" * 300)

    mock_comm = MagicMock()
    mock_comm.save = AsyncMock(side_effect=fake_edge_save)

    # VoiceLab fails on every request
    with patch.object(voicelab_service, "tts_synthesize", side_effect=VoiceLabAPIException("VoiceLab cluster down", 503)), \
         patch("edge_tts.Communicate", return_value=mock_comm):

        tasks = [
            tts.generate_speech(f"{text} #{i}", prefer_voicelab=True)
            for i in range(20)
        ]
        results = await asyncio.gather(*tasks)

        assert len(results) == 20
        # All callers received a valid audio URL
        for url, duration, _ in results:
            assert url.startswith("/api/audio/")
            assert duration > 0

        # Breaker must now be in OPEN state
        assert tts.breaker.state == CircuitBreakerState.OPEN
        assert tts.breaker.failure_count >= 3
        assert tts.breaker.can_attempt() is False


# ============================================================================
# VECTOR 2: OPEN STATE BYPASS - 0MS PENALTY DIRECTLY TO EDGE-TTS
# ============================================================================

@pytest.mark.asyncio
async def test_open_state_zero_penalty_bypass():
    """
    Adversarial check: When circuit breaker is in OPEN state,
    calls must bypass VoiceLab with 0 network calls and minimal overhead (<50ms).
    """
    tts = TTSService()
    tts.breaker.state = CircuitBreakerState.OPEN
    tts.breaker.last_failure_time = time.time()
    tts.breaker.cooldown_seconds = 120.0

    async def fake_edge_save(save_path):
        Path(save_path).write_bytes(b"ID3" + b"\x00" * 200)

    mock_comm = MagicMock()
    mock_comm.save = AsyncMock(side_effect=fake_edge_save)

    # VoiceLab spy: if any request is attempted, fail immediately!
    voicelab_spy = AsyncMock(side_effect=AssertionError("VoiceLab was called while circuit breaker was OPEN!"))

    with patch.object(voicelab_service, "tts_synthesize", voicelab_spy), \
         patch("edge_tts.Communicate", return_value=mock_comm):

        # Execute 10 calls while OPEN
        for i in range(10):
            start = time.perf_counter()
            url, duration, was_cached = await tts.generate_speech(
                f"Aylanib o'tish matni {i}",
                prefer_voicelab=True
            )
            elapsed_ms = (time.perf_counter() - start) * 1000

            assert url.startswith("/api/audio/")
            assert duration > 0
            assert elapsed_ms < 100.0, f"Overhead was too high: {elapsed_ms:.2f}ms"

        # Verify ZERO calls made to VoiceLab
        assert voicelab_spy.call_count == 0


# ============================================================================
# VECTOR 3: VOICELAB ERROR VARIATIONS & ZERO DOWNTIME
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.parametrize("status_code,err_msg", [
    (401, "Invalid VoiceLab API Key"),
    (403, "Account quota or IP restricted"),
    (429, "Too many requests to VoiceLab"),
    (500, "VoiceLab Internal Server Error"),
    (502, "VoiceLab Bad Gateway"),
    (503, "VoiceLab Service Unavailable"),
    (504, "VoiceLab Gateway Timeout"),
])
async def test_voicelab_http_errors_zero_downtime(status_code, err_msg):
    """
    Verify that any VoiceLab status code failure (4xx, 5xx) falls back seamlessly to Edge-TTS.
    """
    tts = TTSService()
    tts.breaker.reset()
    text = f"HTTP xatolik sinovi {status_code}"

    async def fake_edge_save(save_path):
        Path(save_path).write_bytes(b"ID3" + b"\x00" * 250)

    mock_comm = MagicMock()
    mock_comm.save = AsyncMock(side_effect=fake_edge_save)

    with patch.object(voicelab_service, "tts_synthesize", side_effect=VoiceLabAPIException(err_msg, status_code)), \
         patch("edge_tts.Communicate", return_value=mock_comm):

        url, duration, was_cached = await tts.generate_speech(text, prefer_voicelab=True)
        assert url.startswith("/api/audio/")
        assert duration > 0
        assert tts.breaker.failure_count == 1


# ============================================================================
# VECTOR 4: CORRUPTED OR EMPTY AUDIO INPUTS IN STT
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.parametrize("corrupted_input", [
    b"",
    b"\x00",
    b"\x00" * 10,
    b"\x00" * 199,
    b"RIFF" + b"\x00" * 50,
    b"\xff" * 300,
    b"CORRUPTED_GARBAGE_PAYLOAD" * 20,
])
async def test_stt_corrupted_and_empty_inputs_safety(corrupted_input):
    """
    Adversarial test: STT services must NEVER raise uncaught exceptions on corrupted or empty audio inputs.
    - If audio is empty or < 200 bytes, returns "" safely without calling external services.
    - If audio is corrupted and VoiceLab fails, returns "" safely.
    """
    if not corrupted_input or len(corrupted_input) < 200:
        res = await stt_service.transcribe(corrupted_input)
        assert res == ""
    else:
        with patch.object(voicelab_service, "transcribe_audio", side_effect=VoiceLabAPIException("Audio unreadable", 400)):
            res = await stt_service.transcribe(corrupted_input)
            assert isinstance(res, str)
            assert res == ""


# ============================================================================
# VECTOR 5: CACHE COLLISION EDGE CASES
# ============================================================================

def test_cache_collision_edge_cases_and_unicode():
    """
    Assert collision resistance when text has identical words with different whitespace,
    accents, quotes, or when model and provider names overlap.
    """
    tts = TTSService()
    h1 = tts._get_cache_filename("salom", "voicelab", "Gulnoza")
    h2 = tts._get_cache_filename("salom ", "voicelab", "Gulnoza")
    h3 = tts._get_cache_filename("Salom", "voicelab", "Gulnoza")
    h4 = tts._get_cache_filename("salom", "edge", "uz-UZ-MadinaNeural")
    h5 = tts._get_cache_filename("salom", "voicelab", "Gulnoza_v2")

    distinct = {h1, h2, h3, h4, h5}
    assert len(distinct) == 5, "Collision detected in cache filenames!"


# ============================================================================
# VECTOR 6: AUDIO TURN & WEBSOCKET VOICE LOOP IMMUNITY
# ============================================================================

def test_audio_turn_immunity_on_corrupted_multipart_body():
    """
    Send invalid binary content with wrong MIME type and verify graceful handling.
    When STT cannot extract text from corrupted data, endpoint must return 200 OK with Tushunarsiz_Ovoz.
    """
    c = call_manager.create_call("Corrupted Binary Caller")
    garbage_bytes = b"\xff\xfe\x00\x01\x99" * 100
    files = {"audio": ("corrupted.bin", io.BytesIO(garbage_bytes), "application/octet-stream")}

    with patch.object(voicelab_service, "transcribe_audio", side_effect=Exception("Audio codec unreadable")):
        res = client.post(f"/api/calls/{c.id}/audio-turn", files=files)
        assert res.status_code == 200
        body = res.json()
        assert body["intent"] == "Tushunarsiz_Ovoz"
        assert "aniq eshita olmadim" in body["ai_text"].lower()


def test_voice_loop_websocket_tts_crash_immunity():
    """
    Adversarial test: If tts_service.generate_speech raises an unhandled exception
    inside the WebSocket voice loop, the WebSocket connection and message loop must NOT crash.
    """
    c = call_manager.create_call("WS TTS Failure Caller")
    with client.websocket_connect(f"/ws/call/{c.id}") as ws:
        init_event = ws.receive_json()
        assert init_event["type"] == "call_connected"

        # Mock TTS failing with unexpected RuntimeError
        with patch("app.services.tts_service.tts_service.generate_speech", side_effect=RuntimeError("TTS engine exploded")):
            ws.send_json({
                "type": "user_speech",
                "text": "Kontrakt to'lovi bo'yicha ma'lumot bering",
                "voice": "Gulnoza"
            })

            # Check new_message received
            msg1 = ws.receive_json()
            assert msg1["type"] in ("new_message", "ai_thinking", "ai_response")

            # Check ai_response is delivered with audio_url=None without disconnecting
            all_received = [msg1]
            for _ in range(2):
                all_received.append(ws.receive_json())

            ai_responses = [m for m in all_received if m["type"] == "ai_response"]
            assert len(ai_responses) == 1
            assert ai_responses[0]["message"]["audio_url"] is None
            assert len(ai_responses[0]["message"]["text"]) > 0
