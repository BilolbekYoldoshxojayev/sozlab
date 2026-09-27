import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.voicelab_service import voicelab_service
from app.services.stt_service import stt_service
from app.services.ai_dialog import dialog_manager

def test_voicelab_container_detection_magic_bytes_and_mimes():
    """Verify voicelab _sync_transcribe does not mislabel non-WAV bytes as WAV."""
    mock_client = MagicMock()
    mock_job = MagicMock()
    mock_job.id = "test-job-123"
    mock_job.status = "completed"
    mock_job.transcript = "Assalomu alaykum"
    mock_client.stt.transcribe.return_value = mock_job

    with patch.object(voicelab_service, "get_client", return_value=mock_client):
        # 1. Real RIFF WAV
        wav_bytes = b"RIFF" + b"\x00" * 40
        voicelab_service._sync_transcribe(wav_bytes, filename="voice.wav", language="uz")
        call_kwargs = mock_client.stt.transcribe.call_args.kwargs
        assert call_kwargs["content_type"] == "audio/wav"
        assert call_kwargs["filename"] == "speech.wav"

        # 2. WebM with EBML header
        webm_bytes = b"\x1aE\xdf\xa3" + b"\x00" * 40
        voicelab_service._sync_transcribe(webm_bytes, filename="user_call.wav", language="uz")
        call_kwargs = mock_client.stt.transcribe.call_args.kwargs
        assert call_kwargs["content_type"] == "audio/webm"
        assert call_kwargs["filename"] == "speech.webm"

        # 3. WebM bytes without EBML header but with audio/webm mime_type
        arbitrary_webm_bytes = b"\x00\x00\x00\x1f" + b"some_opus_packet" * 5
        voicelab_service._sync_transcribe(arbitrary_webm_bytes, filename="user_call.wav", language="uz", mime_type="audio/webm;codecs=opus")
        call_kwargs = mock_client.stt.transcribe.call_args.kwargs
        assert call_kwargs["content_type"] == "audio/webm"
        assert call_kwargs["filename"] == "speech.webm"

        # 4. MP4 / AAC container (e.g. from iOS/Safari)
        mp4_bytes = b"\x00\x00\x00\x20ftypM4A " + b"\x00" * 40
        voicelab_service._sync_transcribe(mp4_bytes, filename="user_call.wav", language="uz", mime_type="audio/mp4")
        call_kwargs = mock_client.stt.transcribe.call_args.kwargs
        assert call_kwargs["content_type"] == "audio/mp4"
        assert call_kwargs["filename"] == "speech.mp4"

        # 5. OGG container
        ogg_bytes = b"OggS\x00\x02" + b"\x00" * 40
        voicelab_service._sync_transcribe(ogg_bytes, filename="user_call.wav", language="uz", mime_type="audio/ogg")
        call_kwargs = mock_client.stt.transcribe.call_args.kwargs
        assert call_kwargs["content_type"] == "audio/ogg"
        assert call_kwargs["filename"] == "speech.ogg"

@pytest.mark.asyncio
async def test_stt_service_fallback_whisper_container_resolution():
    """Verify Groq Whisper fallback aligns container filenames when voicelab fails."""
    fake_audio = b"\x1aE\xdf\xa3" + b"\x00" * 250

    with patch.object(voicelab_service, "transcribe_audio", side_effect=Exception("VoiceLab failed")):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"text": "Salom ta'lim"}
            mock_post.return_value = mock_resp

            text = await stt_service.transcribe(
                audio_bytes=fake_audio,
                mime_type="audio/webm;codecs=opus",
                filename="user_call.wav",
                language="uz"
            )
            assert text == "Salom ta'lim"
            files_arg = mock_post.call_args.kwargs["files"]
            # File tuple is (filename, bytes, content_type)
            fn, b_content, mime = files_arg["file"]
            assert fn == "speech.webm"
            assert mime == "audio/webm"

@pytest.mark.asyncio
async def test_ai_dialog_process_audio_turn_passes_filename():
    """Verify process_audio_turn preserves custom filename and mime_type."""
    fake_wav = b"RIFF" + b"\x00" * 250
    with patch.object(stt_service, "transcribe", new_callable=AsyncMock) as mock_stt:
        mock_stt.return_value = "Assalomu alaykum"
        with patch.object(dialog_manager, "process_user_turn", new_callable=AsyncMock) as mock_turn:
            mock_turn.return_value = MagicMock(ai_text="Va alaykum assalom")
            txt, res = await dialog_manager.process_audio_turn(
                call_id="call-test-1",
                audio_bytes=fake_wav,
                mime_type="audio/wav",
                filename="call_turn_0.wav"
            )
            assert txt == "Assalomu alaykum"
            assert mock_stt.call_args.kwargs["filename"] == "call_turn_0.wav"
            assert mock_stt.call_args.kwargs["mime_type"] == "audio/wav"
