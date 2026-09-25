import io
import pytest
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.services.knowledge_base import search_knowledge_base, TopicCategory
from app.services.tts_service import tts_service
from app.services.ai_dialog import dialog_manager
from app.services.call_manager import call_manager
from app.models.schemas import OperatorStatus, CallStatus

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "vazirligi" in data["ministry"].lower()

def test_knowledge_base_search():
    results = search_knowledge_base("OTMga qabul va hujjat topshirish qachon")
    assert len(results) > 0
    assert results[0].topic == TopicCategory.QABUL

    ttj_results = search_knowledge_base("yotoqxona va talabalar turar joyi ijara")
    assert len(ttj_results) > 0
    assert ttj_results[0].topic == TopicCategory.TTJ

    nostr_results = search_knowledge_base("diplom tan olish va nostrifikatsiya")
    assert len(nostr_results) > 0
    assert nostr_results[0].topic == TopicCategory.NOSTRIFIKATSIYA

def test_calls_api_crud():
    res = client.get("/api/calls")
    assert res.status_code == 200
    calls = res.json()
    assert len(calls) >= 5

    # Start new call
    new_res = client.post("/api/calls", json={"name": "Rustam Alimov", "phone": "+998 90 555-12-34"})
    assert new_res.status_code == 200
    new_call = new_res.json()
    call_id = new_call["id"]
    assert new_call["citizen_name"] == "Rustam Alimov"

    # Turn
    turn_res = client.post(f"/api/calls/{call_id}/turn", json={
        "call_id": call_id,
        "user_text": "Men oliygohga qabul qachon boshlanishini bilmoqchi edim",
        "voice_enabled": False
    })
    assert turn_res.status_code == 200
    turn_data = turn_res.json()
    assert turn_data["topic"] == TopicCategory.QABUL.value
    assert len(turn_data["ai_text"]) > 10

    # Transfer call (smart routing)
    trans_res = client.post(f"/api/calls/{call_id}/transfer", json={"reason": "Operator yordami kerak"})
    assert trans_res.status_code == 200
    data = trans_res.json()
    assert "call" in data

    # Operator takeover
    take_res = client.post(f"/api/calls/{call_id}/takeover", json={"operator_name": "Madina Karimova"})
    assert take_res.status_code == 200
    assert take_res.json()["status"] == "operator_handling"

    # Complete call
    comp_res = client.post(f"/api/calls/{call_id}/complete", json={"summary": "Qabul sanalari tushuntirildi"})
    assert comp_res.status_code == 200
    assert comp_res.json()["completed_call"]["status"] == "completed"

def test_audio_turn_endpoint():
    new_res = client.post("/api/calls", json={"name": "Audio Test", "phone": "+998 90 111-22-33"})
    call_id = new_res.json()["id"]

    # Create dummy audio payload (1000 bytes)
    dummy_wav = b"RIFF" + b"\x00" * 996
    files = {"file": ("test.wav", io.BytesIO(dummy_wav), "audio/wav")}

    res = client.post(f"/api/calls/{call_id}/audio-turn", files=files, data={"voice": "uz-UZ-MadinaNeural"})
    assert res.status_code == 200
    data = res.json()
    assert data["call_id"] == call_id
    assert len(data["transcribed_text"]) > 0
    assert len(data["ai_text"]) > 0

def test_multi_operator_queue():
    # Register 3 dynamic operators (for zero-mock production fleet)
    call_manager.register_operator("op-1", "Madina Karimova (Operator #1)")
    call_manager.register_operator("op-2", "Jasur Aliyev (Operator #2)")
    call_manager.register_operator("op-3", "Dilnoza Shokirova (Operator #3)")

    # Fetch operators
    op_res = client.get("/api/calls/operators")
    assert op_res.status_code == 200
    ops = op_res.json()
    assert len(ops) >= 3

    # Clear queue to ensure isolated test environment
    call_manager._waiting_queue.clear()

    # Mark all operators busy to test queueing
    for op in call_manager._operators.values():
        op.status = OperatorStatus.BUSY

    # Start 2 calls that ask for operator
    c1 = call_manager.create_call("Fuqaro 1")
    c2 = call_manager.create_call("Fuqaro 2")

    _, _, pos1 = call_manager.transfer_to_operator(c1.id)
    _, _, pos2 = call_manager.transfer_to_operator(c2.id)

    assert pos1 > 0
    assert pos2 > pos1

    # Now release an operator -> c1 should be automatically assigned!
    comp_call, next_call = call_manager.complete_call("call-101", operator_id="op-1")
    assert next_call is not None
    assert next_call.id == c1.id
    assert next_call.status.value == "operator_handling"

    # Reset operators to available
    for op in call_manager._operators.values():
        op.status = OperatorStatus.AVAILABLE

def test_analytics_endpoint():
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["total_calls_today"] > 0
    assert data["ai_resolved_percentage"] > 0
    assert "Qabul va Hujjatlar" in data["topic_distribution"]
    assert len(data["hourly_call_volume"]) > 0

@pytest.mark.asyncio
async def test_tts_generation():
    text = "Assalomu alaykum, vazirlik qabul komissiyasi."
    url, duration, cached = await tts_service.generate_speech(text, voice="uz-UZ-MadinaNeural")
    assert url.startswith("/api/audio/")
    assert duration > 0.5
    url2, _, cached2 = await tts_service.generate_speech(text, voice="uz-UZ-MadinaNeural")
    assert url2 == url
    assert cached2 is True

@pytest.mark.asyncio
async def test_dialog_manager_fallback():
    turn = await dialog_manager.process_user_turn("call-test", "Assalomu alaykum")
    assert "Assalomu alaykum" in turn.ai_text
    assert turn.sentiment.value == "Neytral"

    turn_neg = await dialog_manager.process_user_turn("call-test", "Mening shikoyatim bor, bu juda yomon!")
    assert turn_neg.sentiment.value == "Salbiy"

def test_admin_websocket_silent_listen_and_ghost():
    # Create a test call
    c = call_manager.create_call("Ghost Test Citizen")
    call_id = c.id

    with client.websocket_connect("/ws/admin") as admin_ws:
        init_data = admin_ws.receive_json()
        assert init_data["type"] == "admin_initial_state"
        assert "calls" in init_data
        assert "operators" in init_data

        # Silent listen subscription
        admin_ws.send_json({"action": "silent_listen", "call_id": call_id})
        sub_resp = admin_ws.receive_json()
        assert sub_resp["type"] == "subscribed"
        assert sub_resp["call_id"] == call_id

        # Trigger a REST turn on the call
        turn_res = client.post(f"/api/calls/{call_id}/turn", json={
            "call_id": call_id,
            "user_text": "Men diplomimni nostrifikatsiya qilmoqchiman",
            "voice_enabled": False
        })
        assert turn_res.status_code == 200

        # Admin socket must silently receive citizen and bot ghost messages
        msg1 = admin_ws.receive_json()
        assert msg1["type"] == "ghost_message"
        assert msg1["call_id"] == call_id
        assert msg1["role"] == "citizen"
        assert "nostrifikatsiya" in msg1["text"].lower()

        msg2 = admin_ws.receive_json()
        assert msg2["type"] == "ghost_message"
        assert msg2["call_id"] == call_id
        assert msg2["role"] == "bot"
        assert len(msg2["text"]) > 0

        # Unsubscribe
        admin_ws.send_json({"action": "unlisten", "call_id": call_id})
        unsub_resp = admin_ws.receive_json()
        assert unsub_resp["type"] == "unsubscribed"
        assert unsub_resp["call_id"] == call_id

def test_audio_turn_ws_bridge_ghost():
    c = call_manager.create_call("Audio Ghost Citizen")
    call_id = c.id

    with client.websocket_connect("/ws/admin") as admin_ws:
        _ = admin_ws.receive_json()  # admin_initial_state
        admin_ws.send_json({"action": "silent_listen", "call_id": call_id})
        _ = admin_ws.receive_json()  # subscribed

        dummy_wav = b"RIFF" + b"\x00" * 996
        files = {"audio": ("test.wav", io.BytesIO(dummy_wav), "audio/wav")}
        res = client.post(f"/api/calls/{call_id}/audio-turn", files=files, data={"voice_name": "uz-UZ-MadinaNeural"})
        assert res.status_code == 200

        msg_cit = admin_ws.receive_json()
        assert msg_cit["type"] == "ghost_message"
        assert msg_cit["call_id"] == call_id
        assert msg_cit["role"] == "citizen"

        msg_bot = admin_ws.receive_json()
        assert msg_bot["type"] == "ghost_message"
        assert msg_bot["call_id"] == call_id
        assert msg_bot["role"] == "bot"

def test_operator_websocket_lifecycle_and_offline():
    op_id = "op-live-test"
    op_name = "Live Test Operator"

    with client.websocket_connect(f"/ws/operator?operator_id={op_id}&operator_name={op_name}") as op_ws:
        init_state = op_ws.receive_json()
        assert init_state["type"] == "initial_state"
        
        # Verify operator is registered and AVAILABLE
        op = call_manager.get_operator(op_id)
        assert op is not None
        assert op.status == OperatorStatus.AVAILABLE

    # After websocket context exits (disconnect), operator must be marked OFFLINE
    op_after = call_manager.get_operator(op_id)
    assert op_after is not None
    assert op_after.status == OperatorStatus.OFFLINE

def test_operator_next_call_countdown():
    # Clear waiting queue for isolation
    call_manager._waiting_queue.clear()

    # Register an operator
    op_id = "op-countdown-test"
    call_manager.register_operator(op_id, "Countdown Operator")

    # Mark all operators busy so new transfer is enqueued
    for op in call_manager._operators.values():
        op.status = OperatorStatus.BUSY

    # Call 1 handled by op-countdown-test
    c1 = call_manager.create_call("Active Caller")
    c1.status = CallStatus.OPERATOR_HANDLING
    c1.assigned_operator = "Countdown Operator"
    call_manager._operators[op_id].current_call_id = c1.id

    # Call 2 queued
    c2 = call_manager.create_call("Queued Caller")
    _, _, pos = call_manager.transfer_to_operator(c2.id)
    assert pos > 0

    with client.websocket_connect("/ws/operator") as op_ws:
        _ = op_ws.receive_json()  # initial_state
        op_ws.send_json({
            "action": "complete",
            "call_id": c1.id,
            "operator_id": op_id,
            "operator_name": "Countdown Operator",
            "summary": "Muvaffaqiyatli yakunlandi"
        })

        countdown_msg = op_ws.receive_json()
        assert countdown_msg["type"] == "next_call_countdown"
        assert countdown_msg["duration"] == 3
        assert countdown_msg["next_call_id"] == c2.id
        assert countdown_msg["caller_name"] == "Queued Caller"
