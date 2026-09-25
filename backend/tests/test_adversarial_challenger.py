import io
import json
import pytest
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.services.call_manager import CallManager, call_manager
from app.services.ai_dialog import AIDialogManager, dialog_manager
from app.models.schemas import OperatorStatus, CallStatus, SpeakerRole, TopicCategory

client = TestClient(app)

# ============================================================================
# VECTOR 1: AUDIO-TURN ENDPOINT FLEXIBILITY & 422 ERADICATION
# ============================================================================

def test_audio_turn_flexibility_audio_and_voice_name():
    """Assert audio-turn works with 'audio' + 'voice_name' (standard frontend payload)."""
    c = call_manager.create_call("Audio Flex Caller 1")
    dummy_wav = b"RIFF" + b"\x00" * 400
    files = {"audio": ("sample.wav", io.BytesIO(dummy_wav), "audio/wav")}
    data = {"voice_name": "uz-UZ-MadinaNeural", "voice_enabled": "true"}

    res = client.post(f"/api/calls/{c.id}/audio-turn", files=files, data=data)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    body = res.json()
    assert body["call_id"] == c.id
    assert "transcribed_text" in body
    assert "ai_text" in body
    assert "user_text" in body
    assert "bot_text" in body
    assert body["user_text"] == body["transcribed_text"]
    assert body["bot_text"] == body["ai_text"]
    assert "status" in body

def test_audio_turn_flexibility_file_and_voice():
    """Assert audio-turn works with legacy 'file' + 'voice' parameter names."""
    c = call_manager.create_call("Audio Flex Caller 2")
    dummy_wav = b"RIFF" + b"\x00" * 400
    files = {"file": ("legacy.wav", io.BytesIO(dummy_wav), "audio/wav")}
    data = {"voice": "uz-UZ-SardorNeural", "voice_enabled": "true"}

    res = client.post(f"/api/calls/{c.id}/audio-turn", files=files, data=data)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    body = res.json()
    assert body["call_id"] == c.id
    assert len(body["ai_text"]) > 0

def test_audio_turn_missing_audio_returns_400_never_422():
    """Assert audio-turn with missing audio returns HTTP 400 Bad Request, NEVER 422 Unprocessable Entity."""
    c = call_manager.create_call("Missing Audio Caller")
    
    # 1. No files at all
    res = client.post(f"/api/calls/{c.id}/audio-turn", data={"voice_name": "uz-UZ-MadinaNeural"})
    assert res.status_code == 400, f"Expected 400 on missing audio, got {res.status_code}: {res.text}"
    assert res.status_code != 422, "Must NEVER return 422 Unprocessable Entity for missing audio"
    assert "audio fayl yuborilmadi" in res.json().get("detail", "").lower()

    # 2. Empty payload
    res_empty = client.post(f"/api/calls/{c.id}/audio-turn")
    assert res_empty.status_code == 400, f"Expected 400 on empty request, got {res_empty.status_code}"

def test_audio_turn_mime_type_variations():
    """Assert audio-turn handles various browser audio MIME types without error."""
    c = call_manager.create_call("Mime Variety Caller")
    dummy_audio = b"\x00" * 300

    mime_types = [
        "audio/webm",
        "audio/webm;codecs=opus",
        "audio/mp4",
        "audio/wav",
        "audio/ogg; codecs=opus"
    ]

    for mime in mime_types:
        files = {"audio": ("audio_sample", io.BytesIO(dummy_audio), mime)}
        res = client.post(f"/api/calls/{c.id}/audio-turn", files=files, data={"voice_name": "uz-UZ-MadinaNeural"})
        assert res.status_code == 200, f"Failed on mime {mime}: {res.status_code} - {res.text}"

def test_audio_turn_nonexistent_call_id():
    """Assert audio-turn with nonexistent call returns 404."""
    dummy_wav = b"RIFF" + b"\x00" * 300
    files = {"audio": ("sample.wav", io.BytesIO(dummy_wav), "audio/wav")}
    res = client.post("/api/calls/non-existent-call-99999/audio-turn", files=files)
    assert res.status_code == 404


# ============================================================================
# VECTOR 2: ZERO-MOCK BEHAVIOR ON SILENT / UNCLEAR AUDIO
# ============================================================================

def test_zero_mock_silent_audio_returns_polite_uzbek_clarification():
    """
    Assert that empty or silent audio produces polite Uzbek clarification
    and NEVER contains artificial mock questions about OTM admissions.
    """
    c = call_manager.create_call("Zero Mock Audio Test")
    
    # Send empty/silent audio bytes (100 zero bytes)
    silent_audio = b"\x00" * 100
    files = {"audio": ("silent.webm", io.BytesIO(silent_audio), "audio/webm")}
    res = client.post(f"/api/calls/{c.id}/audio-turn", files=files, data={"voice_name": "uz-UZ-MadinaNeural"})
    
    assert res.status_code == 200
    data = res.json()
    
    # 1. Polite Uzbek clarification verification
    expected_phrase = "Kechirasiz, ovozingizni aniq eshita olmadim. Qaytadan gapira olasizmi?"
    assert expected_phrase.lower() in data["ai_text"].lower(), (
        f"Expected clarification phrase '{expected_phrase}', got: '{data['ai_text']}'"
    )
    
    # 2. Strict Zero-Mock check: NEVER contain the old mock admission question
    forbidden_substrings = [
        "otmlarga qabul qachon boshlanadi",
        "nechta yo'nalish tanlash mumkin",
        "mock question"
    ]
    for forbidden in forbidden_substrings:
        assert forbidden not in data["ai_text"].lower(), (
            f"Zero-mock violation! Found forbidden mock text '{forbidden}' in response: {data['ai_text']}"
        )
    
    # 3. Intent must reflect unclear audio
    assert data["intent"] == "Tushunarsiz_Ovoz"

@pytest.mark.asyncio
async def test_zero_mock_unclear_audio_direct_service():
    """Directly test AIDialogManager.process_audio_turn with empty and zero bytes."""
    mgr = AIDialogManager()
    
    # Empty bytes
    transcribed, turn_res = await mgr.process_audio_turn("test-call", b"", "audio/webm")
    assert turn_res.intent == "Tushunarsiz_Ovoz"
    assert "aniq eshita olmadim" in turn_res.ai_text
    assert "otmlarga qabul qachon boshlanadi" not in turn_res.ai_text.lower()
    
    # 10 bytes noise
    transcribed_short, turn_res_short = await mgr.process_audio_turn("test-call", b"dummy12345", "audio/webm")
    assert turn_res_short.intent == "Tushunarsiz_Ovoz"
    assert "aniq eshita olmadim" in turn_res_short.ai_text
    assert "otmlarga qabul qachon boshlanadi" not in turn_res_short.ai_text.lower()


# ============================================================================
# VECTOR 3: FAREWELL AUTO-COMPLETION
# ============================================================================

@pytest.mark.parametrize("farewell_phrase", [
    "rahmat",
    "katta rahmat",
    "xayr",
    "xayir",
    "sog' bo'ling",
    "sog boling",
    "salomat bo'ling",
    "tushundim",
    "bye",
    "end",
    "tushunarli",
    "minnatdorman"
])
def test_farewell_auto_completion_keywords(farewell_phrase):
    """
    Assert that every recognized farewell phrase triggers:
    1. Intent: 'Xayrlashuv'
    2. Response status: 'completed'
    3. CallRecord in call_manager transitions to CallStatus.COMPLETED
    """
    c = call_manager.create_call(f"Farewell Caller ({farewell_phrase})")
    call_id = c.id

    turn_res = client.post(f"/api/calls/{call_id}/turn", json={
        "call_id": call_id,
        "user_text": f"Savolim yo'q, {farewell_phrase}!",
        "voice_enabled": False
    })
    assert turn_res.status_code == 200
    data = turn_res.json()

    assert data["intent"] == "Xayrlashuv", f"Expected intent 'Xayrlashuv' for phrase '{farewell_phrase}', got '{data['intent']}'"
    assert data["status"] == "completed", f"Expected status 'completed' for phrase '{farewell_phrase}', got '{data['status']}'"

    # Verify persisted call state in call_manager
    persisted = call_manager.get_call(call_id)
    assert persisted is not None
    assert persisted.status == CallStatus.COMPLETED
    assert persisted.ended_at is not None
    assert persisted.resolution_summary is not None

def test_farewell_via_audio_turn_simulated():
    """Assert farewell detected during audio-turn transitions status to completed."""
    c = call_manager.create_call("Audio Farewell Caller")
    call_id = c.id

    # We mock or pass a turn that transcribes farewell or test farewell handler directly
    # Even if audio transcription falls back to unclear, if transcribed is farewell:
    is_farewell = dialog_manager.is_farewell("Rahmat, sog' bo'ling")
    assert is_farewell is True

    # Test via turn endpoint first
    res = client.post(f"/api/calls/{call_id}/turn", json={
        "call_id": call_id,
        "user_text": "Katta rahmat, sog' bo'ling",
        "voice_enabled": False
    })
    assert res.json()["status"] == "completed"

    # Now verify subsequent audio-turn on completed call stays completed
    dummy_wav = b"RIFF" + b"\x00" * 300
    files = {"audio": ("sample.wav", io.BytesIO(dummy_wav), "audio/wav")}
    audio_res = client.post(f"/api/calls/{call_id}/audio-turn", files=files)
    assert audio_res.status_code == 200
    assert audio_res.json()["status"] == "completed"


# ============================================================================
# VECTOR 4: AUTONOMOUS AI CALL LIFECYCLE & RESOLUTION
# ============================================================================

def test_autonomous_ai_call_lifecycle_and_zero_operators():
    """Assert pure AI call lifecycle without operator dependency."""
    c = call_manager.create_call("Autonomous AI Citizen")
    assert c.status in (CallStatus.INITIATED, CallStatus.AI_HANDLING)
    assert c.assigned_operator is None

    # Complete call via AI farewell turn
    res = client.post(f"/api/calls/{c.id}/turn", json={
        "call_id": c.id,
        "user_text": "Katta rahmat, barchasi tushunarli bo'ldi, xayr!",
        "voice_enabled": False
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert data["intent"] == "Xayrlashuv"

    persisted = call_manager.get_call(c.id)
    assert persisted.status == CallStatus.COMPLETED
    assert persisted.ended_at is not None
    assert persisted.resolution_summary is not None


# ============================================================================
# VECTOR 5: ADMIN GHOST MODE 100% INVISIBILITY & STREAMING
# ============================================================================

def test_admin_ghost_mode_complete_invisibility():
    """
    Adversarial Test:
    - Citizen connects to /ws/call/{call_id}
    - Admin connects to /ws/admin and subscribes with silent_listen
    - Send speech / turn
    - Admin receives ghost audio turns and text
    - STRICT ASSERTION: Citizen receives ZERO admin events!
    """
    c = call_manager.create_call("Ghost Invisibility Citizen")
    call_id = c.id

    with client.websocket_connect(f"/ws/call/{call_id}") as citizen_ws:
        cit_init = citizen_ws.receive_json()
        assert cit_init["type"] == "call_connected"

        with client.websocket_connect("/ws/admin") as admin_ws:
            admin_init = admin_ws.receive_json()
            assert admin_init["type"] == "admin_initial_state"

            # 1. Admin activates silent_listen
            admin_ws.send_json({"action": "silent_listen", "call_id": call_id})
            sub_res = admin_ws.receive_json()
            assert sub_res["type"] == "subscribed"
            assert sub_res["call_id"] == call_id

            # CITIZEN must NOT receive any message about admin listening!
            # We perform an audio turn on the call
            dummy_wav = b"RIFF" + b"\x00" * 400
            files = {"audio": ("sample.wav", io.BytesIO(dummy_wav), "audio/wav")}
            res = client.post(f"/api/calls/{call_id}/audio-turn", files=files, data={"voice_name": "Gulnoza"})
            assert res.status_code == 200

            # 2. Check Admin receives ghost messages
            ghost_cit = admin_ws.receive_json()
            assert ghost_cit["type"] == "ghost_message"
            assert ghost_cit["call_id"] == call_id
            assert ghost_cit["role"] == "citizen"

            ghost_bot = admin_ws.receive_json()
            assert ghost_bot["type"] == "ghost_message"
            assert ghost_bot["call_id"] == call_id
            assert ghost_bot["role"] == "bot"
            assert "audio_url" in ghost_bot

            # 3. Check Citizen received normal call messages (transcription, new_message, ai_response)
            cit_msg1 = citizen_ws.receive_json()
            assert cit_msg1["type"] in ("transcription", "new_message", "ai_response")
            cit_msg2 = citizen_ws.receive_json()
            assert cit_msg2["type"] in ("transcription", "new_message", "ai_response")
            cit_msg3 = citizen_ws.receive_json()
            assert cit_msg3["type"] in ("transcription", "new_message", "ai_response")

            # Verify NO admin ghost message leaked to citizen!
            for m in [cit_msg1, cit_msg2, cit_msg3]:
                assert m["type"] != "ghost_message"
                assert m["type"] != "subscribed"
                assert "admin" not in m.get("type", "").lower()

            # 4. Admin unlistens
            admin_ws.send_json({"action": "unlisten", "call_id": call_id})
            unsub = admin_ws.receive_json()
            assert unsub["type"] == "unsubscribed"


# ============================================================================
# VECTOR 6: KNOWLEDGE GROUNDING & LEGAL REASONING
# ============================================================================

def test_legal_knowledge_grounding_in_dialog():
    """Assert dialog returns verified legal references for in-scope higher education questions."""
    c = call_manager.create_call("Legal Inquiry Citizen")
    res = client.post(f"/api/calls/{c.id}/turn", json={
        "call_id": c.id,
        "user_text": "Magistraturaga kirishda chet tili sertifikati talab qilinadimi?",
        "voice_enabled": False
    })
    assert res.status_code == 200
    data = res.json()
    assert len(data["knowledge_references"]) > 0
    ref_strs = [str(r).lower() for r in data["knowledge_references"]]
    assert any("magistratura" in t or "til" in t or "sertifikat" in t or "vmq" in t or "qaror" in t for t in ref_strs)

