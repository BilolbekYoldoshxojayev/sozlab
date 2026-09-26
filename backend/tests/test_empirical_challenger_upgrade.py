"""
Empirical & Adversarial Challenger Verification Suite
Author: challenger_upgrade
Tests:
1. R1: Silence padding function byte counts, frequencies, channels, corrupt inputs; Lola configuration.
2. R2: Uzbek text normalizer with extreme numbers, all law citations, percentages, educational abbreviations, and markdown.
3. R4: CallConcatenator multi-turn concatenation and strict timeline beat marker monotonicity.
4. R5: CallManager disk persistence, atomic writes, and cold-start reload across fresh instances.
"""

import io
import json
import math
import os
import shutil
import tempfile
import wave
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Ensure backend root is on sys.path
import sys
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.services.voicelab_service import append_trailing_silence_wav, voicelab_service
from app.services.uzbek_text_normalizer import (
    normalize_text_for_tts,
    number_to_uzbek_cardinal,
    number_to_uzbek_ordinal,
    normalize_law_citations,
    normalize_percentages,
    normalize_abbreviations,
    strip_markdown_symbols,
)
from app.services.call_concatenator import CallConcatenator
from app.services.call_manager import CallManager
from app.models.schemas import CallRecord, CallStatus, SpeakerRole, MessageSchema, TopicCategory, SentimentType


# ============================================================================
# HELPER: Generate synthetic WAV in memory
# ============================================================================
def create_synthetic_wav(
    duration_sec: float,
    framerate: int = 24000,
    nchannels: int = 1,
    sampwidth: int = 2,
    freq: float = 440.0,
) -> bytes:
    """Creates a mathematically valid PCM WAV buffer in memory."""
    buf = io.BytesIO()
    nframes = int(framerate * duration_sec)
    with wave.open(buf, "wb") as w:
        w.setnchannels(nchannels)
        w.setsampwidth(sampwidth)
        w.setframerate(framerate)

        # Generate simple sine wave or nonzero PCM samples
        pcm_chunks = bytearray()
        for i in range(nframes):
            val = int(32767.0 * 0.3 * math.sin(2.0 * math.pi * freq * (i / framerate)))
            if sampwidth == 2:
                sample_bytes = int(val).to_bytes(2, byteorder="little", signed=True)
            elif sampwidth == 1:
                uval = max(0, min(255, int(128 + 50 * math.sin(2.0 * math.pi * freq * (i / framerate)))))
                sample_bytes = bytes([uval])
            elif sampwidth == 3:
                sample_bytes = int(val * 256).to_bytes(3, byteorder="little", signed=True)
            else:
                sample_bytes = b"\x00" * sampwidth

            pcm_chunks.extend(sample_bytes * nchannels)

        w.writeframes(bytes(pcm_chunks))

    return buf.getvalue()


# ============================================================================
# SECTION 1: R1 SILENCE PADDING & LOLA CONFIG EMPIRICAL STRESS TESTS
# ============================================================================

class TestR1SilencePaddingAndLolaConfig:

    def test_lola_voice_id_configuration_across_all_layers(self):
        """Verify Lola voice_EvIb9vE6iY_dWgK7OobYdZcX is configured in .env, config, and voicelab_service."""
        expected_voice_id = "voice_EvIb9vE6iY_dWgK7OobYdZcX"

        # 1. Config object
        assert settings.VOICELAB_VOICE_ID == expected_voice_id

        # 2. VoiceLab service instance
        assert voicelab_service.default_voice_id == expected_voice_id

        # 3. Backend .env file directly
        env_file = backend_dir / ".env"
        assert env_file.exists(), ".env file must exist in backend/"
        env_content = env_file.read_text(encoding="utf-8")
        assert f"VOICELAB_VOICE_ID={expected_voice_id}" in env_content

    @pytest.mark.parametrize("corrupt_input", [
        b"",                                      # Empty buffer
        b"RIFF",                                  # Truncated header (4 bytes)
        b"RIFF\x00\x00\x00\x00WAVEfmt ",         # Incomplete header (< 44 bytes)
        b"RIFF" + b"\x00" * 40,                   # 44 bytes of corrupt nulls
        b"\xff\xfb\x90\x44" * 50,                 # Non-WAV MP3 frames
        b"<html><body>502 Bad Gateway</body></html>", # HTML error response
        b'{"error": "rate limit exceeded"}',     # JSON error response
    ])
    def test_silence_padding_corrupt_inputs_graceful_pass_through(self, corrupt_input):
        """Corrupt and non-WAV inputs must be safely returned as-is without raising exceptions."""
        result = append_trailing_silence_wav(corrupt_input, silence_ms=350)
        assert result == corrupt_input, "Must return original bytes unmodified on corrupt/non-WAV input"

    @pytest.mark.parametrize("framerate,nchannels,sampwidth,silence_ms", [
        (24000, 1, 2, 350),  # VoiceLab default: 24kHz mono 16-bit
        (16000, 1, 2, 350),  # Standard telephony/STT: 16kHz mono 16-bit
        (48000, 2, 2, 350),  # High-definition stereo: 48kHz stereo 16-bit
        (8000,  1, 1, 350),  # Narrowband: 8kHz mono 8-bit
        (44100, 2, 2, 350),  # CD-Audio: 44.1kHz stereo 16-bit
        (24000, 1, 2, 500),  # Custom 500ms silence
        (24000, 1, 2, 100),  # Custom 100ms silence
    ])
    def test_silence_padding_exact_byte_formula_verification(
        self, framerate, nchannels, sampwidth, silence_ms
    ):
        """
        Verify exact mathematical byte addition:
        Silence Bytes = floor(framerate * silence_ms / 1000) * nchannels * sampwidth
        """
        duration = 1.0  # 1 second test sound
        original_wav = create_synthetic_wav(
            duration_sec=duration,
            framerate=framerate,
            nchannels=nchannels,
            sampwidth=sampwidth,
        )

        padded_wav = append_trailing_silence_wav(original_wav, silence_ms=silence_ms)

        expected_silence_frames = int(framerate * (silence_ms / 1000.0))
        expected_silence_bytes = expected_silence_frames * nchannels * sampwidth

        # Verify through wave reader
        with wave.open(io.BytesIO(original_wav), "rb") as r_orig:
            orig_frames = r_orig.getnframes()
            orig_pcm = r_orig.readframes(orig_frames)

        with wave.open(io.BytesIO(padded_wav), "rb") as r_padded:
            padded_frames = r_padded.getnframes()
            padded_params = r_padded.getparams()
            padded_pcm = r_padded.readframes(padded_frames)

        # 1. Parameter preservation
        assert padded_params.framerate == framerate
        assert padded_params.nchannels == nchannels
        assert padded_params.sampwidth == sampwidth

        # 2. Frame count increment
        assert padded_frames == orig_frames + expected_silence_frames

        # 3. Byte length delta
        assert len(padded_pcm) == len(orig_pcm) + expected_silence_bytes

        # 4. Content verification: original audio preserved at start
        assert padded_pcm[:len(orig_pcm)] == orig_pcm

        # 5. Trailing bytes must be 100% zero-valued PCM silence
        trailing_pcm = padded_pcm[len(orig_pcm):]
        assert len(trailing_pcm) == expected_silence_bytes
        assert trailing_pcm == b"\x00" * expected_silence_bytes


# ============================================================================
# SECTION 2: R2 NORMALIZER ADVERSARIAL STRESS TESTS
# ============================================================================

class TestR2NormalizerStressTesting:

    def test_extreme_numbers(self):
        """Stress-test extreme boundary numbers, cardinal functions, and large integers."""
        assert normalize_text_for_tts("0") == "nol"
        assert normalize_text_for_tts("1006") == "bir ming olti"
        assert normalize_text_for_tts("1007") == "bir ming yetti"
        assert normalize_text_for_tts("999999999") == (
            "to'qqiz yuz to'qson to'qqiz million to'qqiz yuz to'qson to'qqiz ming to'qqiz yuz to'qson to'qqiz"
        )
        assert normalize_text_for_tts("4 qismga") == "to'rt qismga"
        # Cardinal function supports negative numbers
        assert number_to_uzbek_cardinal(-5) == "minus besh"
        assert number_to_uzbek_cardinal(-100) == "minus yuz"
        # In normalize_text_for_tts, leading hyphen is preserved as punctuation before cardinal
        assert normalize_text_for_tts("-5") == "-besh"

    def test_all_law_citations(self):
        """Stress-test VMQ, PF, PQ, and O'RQ law citations with various suffixes and spaces."""
        cases = [
            ("VMQ-527", "Vazirlar Mahkamasining besh yuz yigirma yettinchi qarori"),
            ("VMQ-527-son", "Vazirlar Mahkamasining besh yuz yigirma yettinchi qarori"),
            ("VMQ 527", "Vazirlar Mahkamasining besh yuz yigirma yettinchi qarori"),
            ("VMQ-527ga", "Vazirlar Mahkamasining besh yuz yigirma yettinchi qaroriga"),
            ("VMQ-527da", "Vazirlar Mahkamasining besh yuz yigirma yettinchi qarorida"),
            ("PF-81", "Prezidentning sakson birinchi farmoni"),
            ("PF-81-son", "Prezidentning sakson birinchi farmoni"),
            ("PF-81ga", "Prezidentning sakson birinchi farmoniga"),
            ("PQ-123", "Prezidentning yuz yigirma uchinchi qarori"),
            ("O'RQ-637", "O'zbekiston Respublikasining olti yuz o'ttiz yettinchi qonuni"),
            ("O'RQ-901", "O'zbekiston Respublikasining to'qqiz yuz birinchi qonuni"),
            ("ORQ-637", "O'zbekiston Respublikasining olti yuz o'ttiz yettinchi qonuni"),
        ]
        for inp, expected in cases:
            norm = normalize_text_for_tts(inp)
            assert norm == expected, f"Failed on law input '{inp}': got '{norm}', expected '{expected}'"

    def test_percentages(self):
        """Stress-test 0%, 100%, 50%, decimals, and word-form 'foiz'."""
        cases = [
            ("0%", "nol foiz"),
            ("100%", "yuz foiz"),
            ("50%", "ellik foiz"),
            ("0.5%", "nol butun besh foiz"),
            ("50 foiz", "ellik foiz"),
            ("50 foizga", "ellik foizga"),
            ("100% grant", "yuz foiz grant"),
        ]
        for inp, expected in cases:
            norm = normalize_text_for_tts(inp)
            assert norm == expected, f"Failed on percentage '{inp}': got '{norm}', expected '{expected}'"

    def test_educational_abbreviations(self):
        """Stress-test educational abbreviations and their grammatical case inflections."""
        cases = [
            ("GPA", "ji-pi-ey"),
            ("GPAsi", "ji-pi-ey"),
            ("OTM", "oliy ta'lim muassasasi"),
            ("OTMga", "oliy ta'lim muassasasiga"),
            ("OTMda", "oliy ta'lim muassasasida"),
            ("OTMdan", "oliy ta'lim muassasasidan"),
            ("OTMlar", "oliy ta'lim muassasalari"),
            ("OTMlarga", "oliy ta'lim muassasalariga"),
            ("TTJ", "talabalar turar joyi"),
            ("TTJga", "talabalar turar joyiga"),
            ("TTJda", "talabalar turar joyida"),
            ("HEMIS", "xemis"),
            ("my.gov.uz", "may gov uz"),
            ("DXM", "Davlat Xizmatlari Markazi"),
            ("DXMga", "Davlat Xizmatlari Markaziga"),
        ]
        for inp, expected in cases:
            norm = normalize_text_for_tts(inp)
            assert norm == expected, f"Failed on abbreviation '{inp}': got '{norm}', expected '{expected}'"

    def test_markdown_and_punctuation_stripping(self):
        """Ensure TTS text does not contain markdown asterisks, hashes, links, or trailing ellipses."""
        text = "**Muhim xabar:** # Sarlavha [HEMIS portali] orqali 1-moddasi bo'yicha ariza topshiring..."
        normalized = normalize_text_for_tts(text)

        assert "*" not in normalized
        assert "#" not in normalized
        assert "[" not in normalized and "]" not in normalized
        assert "..." not in normalized
        assert "xemis portali" in normalized.lower()
        assert "birinchi moddasi" in normalized.lower()


# ============================================================================
# SECTION 3: R4 CALLCONCATENATOR & BEAT MARKERS EMPIRICAL TESTS
# ============================================================================

class TestR4CallConcatenatorAndMarkers:

    @pytest.fixture
    def temp_audio_cache(self):
        """Creates a temporary cache directory for synthetic turns."""
        tmp = tempfile.mkdtemp(prefix="challenger_concat_")
        old_cache = settings.AUDIO_CACHE_DIR
        settings.AUDIO_CACHE_DIR = Path(tmp)
        concatenator = CallConcatenator()
        concatenator.cache_dir = Path(tmp)
        yield concatenator, Path(tmp)
        settings.AUDIO_CACHE_DIR = old_cache
        shutil.rmtree(tmp, ignore_errors=True)

    def test_multi_turn_concatenation_and_strict_monotonicity(self, temp_audio_cache):
        """
        Verify multi-turn concatenation:
        1. All turn audio segments are joined with 400ms inter-turn silence.
        2. Markers start_time and end_time are strictly monotonic:
           start_time[i] >= end_time[i-1] + gap_sec - epsilon
        3. Output WAV header matches 24kHz 16-bit mono.
        4. Total audio duration matches markers[-1]['end_time'].
        """
        concatenator, cache_dir = temp_audio_cache
        call_id = "test-call-monotonicity-99"

        # Create 4 synthetic turn files with known durations
        turn_specs = [
            ("turn0.wav", 1.2, SpeakerRole.AI, "Assalomu alaykum, vazirlik call markazi."),
            ("turn1.wav", 2.0, SpeakerRole.CITIZEN, "Magistratura qabul tartibini so'ramoqchi edim."),
            ("turn2.wav", 2.8, SpeakerRole.AI, "Magistraturaga qabul my.edu.uz orqali amalga oshiriladi."),
            ("turn3.wav", 1.0, SpeakerRole.CITIZEN, "Katta rahmat, tushundim."),
        ]

        messages = []
        for i, (fn, dur, role, text) in enumerate(turn_specs):
            wav_bytes = create_synthetic_wav(duration_sec=dur, framerate=24000, nchannels=1, sampwidth=2)
            fpath = cache_dir / fn
            fpath.write_bytes(wav_bytes)

            msg = MessageSchema(
                id=f"msg-{i}",
                role=role,
                text=text,
                timestamp=datetime.now(timezone.utc),
                audio_url=f"/api/audio/{fn}",
            )
            messages.append(msg)

        # Run concatenation
        audio_url, markers = concatenator.concatenate_call_audio(call_id, messages, gap_ms=400)

        assert audio_url == f"/api/audio/call_{call_id}_full.wav"
        assert len(markers) == 4

        # 1. Monotonicity and gap verification
        for i, marker in enumerate(markers):
            assert marker["turn_index"] == i
            assert marker["start_time"] < marker["end_time"]
            assert marker["duration"] == round(marker["end_time"] - marker["start_time"], 2)

            if i > 0:
                prev_end = markers[i - 1]["end_time"]
                # Must be separated by exactly 400ms (+/- 0.02s float rounding)
                gap = marker["start_time"] - prev_end
                assert gap >= 0.38, f"Turn {i} start {marker['start_time']} overlaps or under-gaps prev {prev_end}"
                assert abs(gap - 0.40) <= 0.02, f"Expected 0.40s gap between turns, got {gap}"

        # 2. Check generated WAV file on disk
        full_wav_path = cache_dir / f"call_{call_id}_full.wav"
        assert full_wav_path.exists()
        assert full_wav_path.stat().st_size > 44

        with wave.open(str(full_wav_path), "rb") as w:
            assert w.getframerate() == 24000
            assert w.getnchannels() == 1
            assert w.getsampwidth() == 2
            total_duration = w.getnframes() / 24000.0

        # Total duration must equal the final marker end_time within 0.02s
        last_marker_end = markers[-1]["end_time"]
        assert abs(total_duration - last_marker_end) <= 0.02, (
            f"WAV total duration ({total_duration:.2f}s) does not match last marker end_time ({last_marker_end:.2f}s)"
        )

    def test_call_concatenator_empty_and_single_turn_boundaries(self, temp_audio_cache):
        """Test boundary conditions: empty messages list and single-turn message."""
        concatenator, cache_dir = temp_audio_cache

        # 1. Empty message list
        url_empty, markers_empty = concatenator.concatenate_call_audio("empty-call", [])
        assert url_empty == ""
        assert markers_empty == []

        # 2. Single turn message
        wav_bytes = create_synthetic_wav(duration_sec=1.5, framerate=24000, nchannels=1, sampwidth=2)
        fpath = cache_dir / "single.wav"
        fpath.write_bytes(wav_bytes)

        single_msg = [
            MessageSchema(
                id="msg-single",
                role=SpeakerRole.AI,
                text="Yagona xabar.",
                timestamp=datetime.now(timezone.utc),
                audio_url="/api/audio/single.wav",
            )
        ]

        url_single, markers_single = concatenator.concatenate_call_audio("single-call", single_msg, gap_ms=400)
        assert url_single == "/api/audio/call_single-call_full.wav"
        assert len(markers_single) == 1
        assert markers_single[0]["start_time"] == 0.0
        assert markers_single[0]["end_time"] == 1.5


# ============================================================================
# SECTION 4: R5 CALLMANAGER PERSISTENCE & RESTORATION EMPIRICAL TESTS
# ============================================================================

class TestR5CallManagerPersistenceAndRestoration:

    @pytest.fixture
    def isolated_saved_calls_dir(self):
        """Creates a completely isolated temporary directory for call persistence."""
        tmp = tempfile.mkdtemp(prefix="challenger_saved_calls_")
        yield Path(tmp)
        shutil.rmtree(tmp, ignore_errors=True)

    def test_call_persistence_atomic_writes_and_cold_restart(self, isolated_saved_calls_dir):
        """
        Verify:
        1. Call creation, message addition, and completion persist atomically to disk ({call_id}.json).
        2. No temporary files (.tmp) are left behind.
        3. A completely fresh CallManager instance pointing to the same folder restores all data.
        """
        tmp_dir = isolated_saved_calls_dir

        # ==========================================
        # PHASE A: Create call on first CallManager
        # ==========================================
        cm1 = CallManager.__new__(CallManager)
        cm1.saved_calls_dir = tmp_dir
        cm1._calls = {}

        call = cm1.create_call(citizen_name="Bobur Mirzo", citizen_phone="+998901112233")
        call_id = call.id

        # Verify disk write immediately after creation
        call_file = tmp_dir / f"{call_id}.json"
        tmp_file = tmp_dir / f"{call_id}.json.tmp"
        assert call_file.exists(), f"Persistence file {call_file} must exist on disk"
        assert not tmp_file.exists(), "Temporary file .tmp must not linger after atomic write"

        # Add citizen turn
        msg_cit = MessageSchema(
            id="msg-cit-1",
            role=SpeakerRole.CITIZEN,
            text="Ikkinchi mutaxassislikka grant bormi?",
            timestamp=datetime.now(timezone.utc),
            detected_topic=TopicCategory.GRANT,
            sentiment=SentimentType.NEUTRAL,
        )
        cm1.add_message(call_id, msg_cit)

        # Add AI turn
        msg_ai = MessageSchema(
            id="msg-ai-1",
            role=SpeakerRole.AI,
            text="O'zbekiston Respublikasi Ta'lim to'g'risidagi qonuniga muvofiq ikkinchi oliy ta'lim faqat shartnoma asosida.",
            timestamp=datetime.now(timezone.utc),
            detected_topic=TopicCategory.GRANT,
            sentiment=SentimentType.POSITIVE,
            llm_provider_used="groq",
            audio_url=f"/api/audio/call_{call_id}_turn1.wav",
        )
        cm1.add_message(call_id, msg_ai)

        # Complete call
        cm1.complete_call(call_id, summary="Ikkinchi mutaxassislik to'lov-shartnoma asosida ekanligi tushuntirildi.")

        # Check completed state on disk
        disk_json = json.loads(call_file.read_text(encoding="utf-8"))
        assert disk_json["id"] == call_id
        assert disk_json["status"] == "completed"
        assert disk_json["resolved_by_ai"] is True
        assert disk_json["citizen_name"] == "Bobur Mirzo"
        assert len(disk_json["messages"]) == 2  # 2 actual turns (citizen + AI, zero phantom init)

        # ==========================================
        # PHASE B: Simulate Server Restart (Fresh Instance)
        # ==========================================
        cm2 = CallManager.__new__(CallManager)
        cm2.saved_calls_dir = tmp_dir
        cm2._calls = {}

        # Invoke startup load method
        loaded_count = cm2.load_all_calls_from_disk()
        assert loaded_count == 1, f"Expected 1 loaded call, got {loaded_count}"

        restored_call = cm2.get_call(call_id)
        assert restored_call is not None, f"Call {call_id} must be restored into memory"
        assert restored_call.id == call_id
        assert restored_call.citizen_name == "Bobur Mirzo"
        assert restored_call.citizen_phone == "+998901112233"
        assert restored_call.status == CallStatus.COMPLETED
        assert restored_call.resolved_by_ai is True
        assert restored_call.primary_topic == TopicCategory.GRANT
        assert restored_call.resolution_summary == "Ikkinchi mutaxassislik to'lov-shartnoma asosida ekanligi tushuntirildi."
        assert len(restored_call.messages) == 2
        assert restored_call.messages[0].text == "Ikkinchi mutaxassislikka grant bormi?"
        assert restored_call.messages[1].role == SpeakerRole.AI
        assert restored_call.messages[1].llm_provider_used == "groq"

    def test_corrupt_persisted_json_tolerance(self, isolated_saved_calls_dir):
        """CallManager must gracefully skip malformed or corrupted JSON files on disk without crashing."""
        tmp_dir = isolated_saved_calls_dir

        # Write corrupt file
        corrupt_file = tmp_dir / "corrupt_call.json"
        corrupt_file.write_text("{ incomplete json payload: ", encoding="utf-8")

        # Write valid file
        valid_call = CallRecord(
            id="call-valid-1",
            citizen_name="Valid Citizen",
            citizen_phone="+998900000000",
            status=CallStatus.COMPLETED,
            started_at=datetime.now(timezone.utc),
            resolved_by_ai=True,
        )
        valid_file = tmp_dir / "call-valid-1.json"
        valid_file.write_text(valid_call.model_dump_json(indent=2), encoding="utf-8")

        # Load fresh manager
        cm = CallManager.__new__(CallManager)
        cm.saved_calls_dir = tmp_dir
        cm._calls = {}

        loaded = cm.load_all_calls_from_disk()
        assert loaded == 1, "Should skip corrupt file and successfully load valid call"
        assert cm.get_call("call-valid-1") is not None
