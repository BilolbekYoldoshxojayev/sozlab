"""
Deterministic Unit Tests for Aisha AI Speech Service and Dual-AI Fallback Engine
Milestone M4: Automated Testing & Verification
Covers:
1. test_aisha_tts_success: Mock Aisha 201 Created + audio download, audio saved to cache and URL returned
2. test_aisha_tts_caching: Verify repeated turns hit disk cache with was_cached=True without network call
3. test_aisha_tts_fallback_on_http_error: Mock Aisha 403/500 HTTP error, seamless fallback to Edge-TTS
4. test_aisha_tts_fallback_on_timeout: Mock Aisha timeout, graceful fallback to Edge-TTS
5. test_aisha_tts_circuit_breaker_open_and_recovery: CLOSED -> OPEN on 3 failures, bypass while OPEN, recovery on cooldown
6. test_aisha_stt_transcription_success: Mock Aisha STT returning transcript, verify transcribed text
7. test_aisha_stt_fallback_on_error: Mock Aisha STT error, verify fallback to Gemini Multimodal STT
8. test_dual_ai_tts_service_integration: Verify tts_service.generate_speech integration with Aisha and Edge-TTS
"""
import asyncio
import io
import time
from pathlib import Path
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.services.aisha_service import (
    AishaAPIException,
    AishaService,
    aisha_service,
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


@pytest.mark.asyncio
async def test_aisha_tts_success(tmp_path):
    """
    1. test_aisha_tts_success:
    Mocks httpx returning 201 with audio_path, verifies audio saved to cache and URL returned.
    """
    test_text = "Vazirlik qabul komissiyasi test muloqoti"
    mock_audio_bytes = b"RIFF" + b"\x00" * 400

    # Mock responses for Aisha synthesis POST and subsequent audio file GET
    mock_post_resp = httpx.Response(
        status_code=201,
        json={"audio_path": "/media/tts_audios/sample_test.wav"},
        request=httpx.Request("POST", f"{aisha_service.base_url}/api/v1/tts/post/"),
    )
    mock_get_resp = httpx.Response(
        status_code=200,
        content=mock_audio_bytes,
        request=httpx.Request("GET", f"{aisha_service.base_url}/media/tts_audios/sample_test.wav"),
    )

    # 1. Direct AishaService verification
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_post.return_value = mock_post_resp
        mock_get.return_value = mock_get_resp

        raw_audio = await aisha_service.tts_synthesize(test_text)
        assert raw_audio == mock_audio_bytes
        assert mock_post.called
        assert mock_get.called

    # 2. TTSService integration verification with fresh cache
    tts_service.breaker.reset()
    aisha_filename = tts_service._get_cache_filename(
        test_text, "aisha", settings.AISHA_TTS_MODEL, str(settings.AISHA_TTS_SPEED), pitch="+0Hz"
    )
    cached_file = tts_service.cache_dir / aisha_filename
    if cached_file.exists():
        cached_file.unlink()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_post.return_value = mock_post_resp
        mock_get.return_value = mock_get_resp

        url, duration, was_cached = await tts_service.generate_speech(test_text, prefer_aisha=True)
        assert url == f"/api/audio/{aisha_filename}"
        assert url.endswith(".wav")
        assert duration > 0
        assert was_cached is False
        assert cached_file.exists()
        assert cached_file.stat().st_size == len(mock_audio_bytes)


@pytest.mark.asyncio
async def test_aisha_tts_caching():
    """
    2. test_aisha_tts_caching:
    Verifies repeated calls hit disk cache with was_cached=True without network call.
    """
    test_text = "Kesh sinovi uchun takroriy matn"
    mock_audio_bytes = b"RIFF" + b"\x00" * 450
    tts_service.breaker.reset()

    # Clear cache file if existing
    aisha_filename = tts_service._get_cache_filename(
        test_text, "aisha", settings.AISHA_TTS_MODEL, str(settings.AISHA_TTS_SPEED), pitch="+0Hz"
    )
    cached_file = tts_service.cache_dir / aisha_filename
    if cached_file.exists():
        cached_file.unlink()

    mock_post_resp = httpx.Response(
        status_code=201,
        json={"audio_path": "/media/tts_audios/cache_test.wav"},
        request=httpx.Request("POST", f"{aisha_service.base_url}/api/v1/tts/post/"),
    )
    mock_get_resp = httpx.Response(
        status_code=200,
        content=mock_audio_bytes,
        request=httpx.Request("GET", f"{aisha_service.base_url}/media/tts_audios/cache_test.wav"),
    )

    # First call: synthesis via network
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_post.return_value = mock_post_resp
        mock_get.return_value = mock_get_resp

        url1, duration1, was_cached1 = await tts_service.generate_speech(test_text, prefer_aisha=True)
        assert mock_post.call_count == 1
        assert mock_get.call_count == 1
        assert was_cached1 is False
        assert url1.endswith(".wav")

    # Second call: must hit disk cache with ZERO network requests
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post2, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get2:
        url2, duration2, was_cached2 = await tts_service.generate_speech(test_text, prefer_aisha=True)
        assert url2 == url1
        assert was_cached2 is True
        assert mock_post2.call_count == 0
        assert mock_get2.call_count == 0


@pytest.mark.asyncio
async def test_aisha_tts_fallback_on_http_error():
    """
    3. test_aisha_tts_fallback_on_http_error:
    Mocks Aisha API HTTP error (403/500), verifies seamless fallback to Edge-TTS (uz-UZ-MadinaNeural).
    """
    test_text = "HTTP 500 xatolik zaxira sinovi"
    tts_service.breaker.reset()

    # Clear cache files
    edge_filename = tts_service._get_cache_filename(test_text, "edge", "uz-UZ-MadinaNeural", "+0%", "+0Hz")
    edge_file = tts_service.cache_dir / edge_filename
    if edge_file.exists():
        edge_file.unlink()

    aisha_filename = tts_service._get_cache_filename(
        test_text, "aisha", settings.AISHA_TTS_MODEL, str(settings.AISHA_TTS_SPEED), pitch="+0Hz"
    )
    aisha_file = tts_service.cache_dir / aisha_filename
    if aisha_file.exists():
        aisha_file.unlink()

    # Aisha returns HTTP 500 error
    mock_err_resp = httpx.Response(
        status_code=500,
        json={"detail": "Aisha GPU cluster out of memory", "error_key": "gpu_oom"},
        request=httpx.Request("POST", f"{aisha_service.base_url}/api/v1/tts/post/"),
    )

    async def fake_edge_save(save_path):
        Path(save_path).write_bytes(b"ID3" + b"\x00" * 350)

    mock_communicate = MagicMock()
    mock_communicate.save = AsyncMock(side_effect=fake_edge_save)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("edge_tts.Communicate", return_value=mock_communicate):
        mock_post.return_value = mock_err_resp

        url, duration, was_cached = await tts_service.generate_speech(
            test_text, voice="uz-UZ-MadinaNeural", prefer_aisha=True
        )

        # Verified seamless fallback to Edge-TTS without raising an unhandled exception
        assert url == f"/api/audio/{edge_filename}"
        assert url.endswith(".mp3")
        assert duration > 0
        assert was_cached is False
        assert edge_file.exists()
        assert tts_service.breaker.failure_count == 1


@pytest.mark.asyncio
async def test_aisha_tts_fallback_on_timeout():
    """
    4. test_aisha_tts_fallback_on_timeout:
    Mocks Aisha timeout, verifies graceful fallback to Edge-TTS.
    """
    test_text = "Tarmoq kechikishi va timeout sinovi"
    tts_service.breaker.reset()

    edge_filename = tts_service._get_cache_filename(test_text, "edge", "uz-UZ-MadinaNeural", "+0%", "+0Hz")
    edge_file = tts_service.cache_dir / edge_filename
    if edge_file.exists():
        edge_file.unlink()

    aisha_filename = tts_service._get_cache_filename(
        test_text, "aisha", settings.AISHA_TTS_MODEL, str(settings.AISHA_TTS_SPEED), pitch="+0Hz"
    )
    aisha_file = tts_service.cache_dir / aisha_filename
    if aisha_file.exists():
        aisha_file.unlink()

    async def fake_edge_save(save_path):
        Path(save_path).write_bytes(b"ID3" + b"\x00" * 320)

    mock_communicate = MagicMock()
    mock_communicate.save = AsyncMock(side_effect=fake_edge_save)

    # Aisha times out with httpx.TimeoutException
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Read timeout after 6.0s")), \
         patch("edge_tts.Communicate", return_value=mock_communicate):

        url, duration, was_cached = await tts_service.generate_speech(
            test_text, voice="uz-UZ-MadinaNeural", prefer_aisha=True
        )

        assert url == f"/api/audio/{edge_filename}"
        assert url.endswith(".mp3")
        assert duration > 0
        assert was_cached is False
        assert tts_service.breaker.failure_count == 1


@pytest.mark.asyncio
async def test_aisha_tts_circuit_breaker_open_and_recovery():
    """
    5. test_aisha_tts_circuit_breaker_open_and_recovery:
    Verifies CLOSED -> OPEN on 3 consecutive failures, bypassing Aisha while OPEN,
    and recovery when cooldown expires.
    """
    cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=0.15)
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.can_attempt() is True

    # 1. First failure -> state remains CLOSED
    cb.record_failure()
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.failure_count == 1
    assert cb.can_attempt() is True

    # 2. Second failure -> state remains CLOSED
    cb.record_failure()
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.failure_count == 2
    assert cb.can_attempt() is True

    # 3. Third failure -> threshold reached, transitions to OPEN
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    assert cb.failure_count == 3

    # 4. Immediate attempt while OPEN and cooldown not expired -> bypass (can_attempt is False)
    assert cb.can_attempt() is False

    # 5. Wait for cooldown to expire
    await asyncio.sleep(0.18)

    # 6. First call after cooldown -> transitions to HALF_OPEN (allows probe)
    assert cb.can_attempt() is True
    assert cb.state == CircuitBreakerState.HALF_OPEN

    # 7. Successful probe resets circuit to CLOSED
    cb.record_success()
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.failure_count == 0

    # 8. Test HALF_OPEN failure returns to OPEN
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    await asyncio.sleep(0.18)
    assert cb.can_attempt() is True
    assert cb.state == CircuitBreakerState.HALF_OPEN
    cb.record_failure()  # probe failed
    assert cb.state == CircuitBreakerState.OPEN


@pytest.mark.asyncio
async def test_aisha_stt_transcription_success():
    """
    6. test_aisha_stt_transcription_success:
    Mocks Aisha STT returning transcript, verifies transcribed text.
    """
    expected_transcript = "Diplom tan olish tartibi qanday?"
    dummy_wav = b"RIFF" + b"\x00" * 400

    mock_resp = httpx.Response(
        status_code=200,
        json={"id": 101, "transcript": expected_transcript},
        request=httpx.Request("POST", f"{aisha_service.base_url}/api/v1/stt/post/"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        # 1. Direct AishaService call
        aisha_result = await aisha_service.transcribe_audio(dummy_wav)
        assert aisha_result == expected_transcript

        # 2. Unified STTService call
        stt_result = await stt_service.transcribe(dummy_wav)
        assert stt_result == expected_transcript


@pytest.mark.asyncio
async def test_aisha_stt_fallback_on_error():
    """
    7. test_aisha_stt_fallback_on_error:
    Mocks Aisha STT error, verifies fallback to Gemini Multimodal STT.
    """
    dummy_wav = b"RIFF" + b"\x00" * 350
    fallback_transcript = "Magistratura kvotalari qachon chiqadi?"

    # 1. Aisha STT fails with HTTP 503 error
    mock_aisha_error = httpx.Response(
        status_code=503,
        json={"detail": "STT service busy"},
        request=httpx.Request("POST", f"{aisha_service.base_url}/api/v1/stt/post/"),
    )

    # Mock Gemini Multimodal response
    mock_gemini_resp = MagicMock()
    mock_gemini_resp.text = f'"{fallback_transcript}"'

    mock_gemini_client = MagicMock()
    mock_gemini_client.models.generate_content.return_value = mock_gemini_resp

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("app.services.ai_dialog.dialog_manager._get_client", return_value=mock_gemini_client):
        mock_post.return_value = mock_aisha_error

        result = await stt_service.transcribe(dummy_wav, mime_type="audio/wav")
        assert result == fallback_transcript
        assert mock_gemini_client.models.generate_content.called

    # 2. Verify empty / silent audio (< 200 bytes) returns empty string without calling external APIs
    empty_result = await stt_service.transcribe(b"RIFF\x00\x00")
    assert empty_result == ""


@pytest.mark.asyncio
async def test_dual_ai_tts_service_integration():
    """
    8. test_dual_ai_tts_service_integration:
    Verifies tts_service.generate_speech integration with Aisha and Edge-TTS.
    """
    tts_service.breaker.reset()
    text_edge = "Integratsiya sinovi: faqat Edge-TTS yo'nalishi"
    text_breaker = "Integratsiya sinovi: ochiq zanjir orqali Edge-TTS"

    # Clean existing caches for these texts
    edge_filename = tts_service._get_cache_filename(text_edge, "edge", "uz-UZ-MadinaNeural", "+0%", "+0Hz")
    (tts_service.cache_dir / edge_filename).unlink(missing_ok=True)

    breaker_filename = tts_service._get_cache_filename(text_breaker, "edge", "uz-UZ-MadinaNeural", "+0%", "+0Hz")
    (tts_service.cache_dir / breaker_filename).unlink(missing_ok=True)

    async def fake_edge_save(save_path):
        Path(save_path).write_bytes(b"ID3" + b"\x00" * 280)

    mock_communicate = MagicMock()
    mock_communicate.save = AsyncMock(side_effect=fake_edge_save)

    # 1. When prefer_aisha=False, routes directly to Edge-TTS without calling Aisha
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("edge_tts.Communicate", return_value=mock_communicate):
        url, duration, _ = await tts_service.generate_speech(text_edge, prefer_aisha=False)
        assert url.endswith(".mp3")
        assert mock_post.call_count == 0

    # 2. When circuit breaker is OPEN, routes directly to Edge-TTS bypassing Aisha
    tts_service.breaker.state = CircuitBreakerState.OPEN
    tts_service.breaker.last_failure_time = time.time()
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post2, \
         patch("edge_tts.Communicate", return_value=mock_communicate):
        url2, _, _ = await tts_service.generate_speech(text_breaker, prefer_aisha=True)
        assert url2.endswith(".mp3")
        assert mock_post2.call_count == 0

    # Reset breaker
    tts_service.breaker.reset()

    # 3. Verify get_audio_filepath helper behavior
    safe_missing = tts_service.get_audio_filepath("test_nonexistent_audio_file.wav")
    assert safe_missing is None
