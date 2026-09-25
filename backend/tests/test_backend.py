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
from app.services.knowledge_base import (
    search_knowledge_base,
    get_complete_legal_context,
    is_in_educational_scope,
    OUT_OF_SCOPE_REFUSAL,
    TopicCategory
)
from app.data.education_faq_50 import FAQ_50_ITEMS, search_faq_items
from app.data.education_legislation_encyclopedia import LEGAL_ENCYCLOPEDIA_ARTICLES, search_encyclopedia
from app.services.tts_service import tts_service
from app.services.ai_dialog import dialog_manager
from app.services.call_manager import call_manager
from app.models.schemas import CallStatus

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "vazirligi" in data["ministry"].lower()

def test_knowledge_base_50_faqs_structure():
    assert len(FAQ_50_ITEMS) == 50
    # Verify all 8 chapters exist
    chapters = {item["chapter"] for item in FAQ_50_ITEMS}
    assert chapters == {1, 2, 3, 4, 5, 6, 7, 8}

    # Verify Savol 2 (Maktab pul yig'ish)
    q2 = next(f for f in FAQ_50_ITEMS if f["id"] == 2)
    assert "pul yig'ish" in q2["question"].lower()
    assert "noqonuniy" in q2["short_answer"].lower()
    assert "50-modda" in q2["legal_basis"]

    # Verify Savol 9 (Pedagog majburiy mehnati)
    q9 = next(f for f in FAQ_50_ITEMS if f["id"] == 9)
    assert "majburiy" in q9["legal_basis"].lower() or "51-modda" in q9["legal_basis"].lower() or "52-modda" in q9["legal_basis"]

def test_legal_encyclopedia_structure():
    assert len(LEGAL_ENCYCLOPEDIA_ARTICLES) >= 10
    codes = {item["code"] for item in LEGAL_ENCYCLOPEDIA_ARTICLES}
    assert "CONST-50" in codes
    assert "CONST-52" in codes
    assert "ORQ-637" in codes
    assert "ORQ-901" in codes
    assert "PF-81" in codes
    assert "VMQ-447" in codes

def test_calls_api_crud():
    res = client.get("/api/calls")
    assert res.status_code == 200
    calls = res.json()
    assert len(calls) >= 3

    # Start new call
    new_res = client.post("/api/calls", json={"name": "Rustam Alimov", "phone": "+998 90 555-12-34"})
    assert new_res.status_code == 200
    new_call = new_res.json()
    call_id = new_call["id"]
    assert new_call["citizen_name"] == "Rustam Alimov"

    # Turn with legal question
    turn_res = client.post(f"/api/calls/{call_id}/turn", json={
        "call_id": call_id,
        "user_text": "Maktabda ota-onalardan pul yig'ish qonuniymi?",
        "voice_enabled": False
    })
    assert turn_res.status_code == 200
    turn_data = turn_res.json()
    assert len(turn_data["ai_text"]) > 10
    assert "pul" in turn_data["ai_text"].lower() or "taqiq" in turn_data["ai_text"].lower() or "qonun" in turn_data["ai_text"].lower()

    # Complete call
    comp_res = client.post(f"/api/calls/{call_id}/complete", json={"summary": "Qonuniy asoslar tushuntirildi"})
    assert comp_res.status_code == 200
    assert comp_res.json()["completed_call"]["status"] == "completed"

def test_audio_turn_endpoint():
    new_res = client.post("/api/calls", json={"name": "Audio Test", "phone": "+998 90 111-22-33"})
    call_id = new_res.json()["id"]

    dummy_wav = b"RIFF" + b"\x00" * 996
    files = {"file": ("test.wav", io.BytesIO(dummy_wav), "audio/wav")}

    res = client.post(f"/api/calls/{call_id}/audio-turn", files=files, data={"voice": "Gulnoza"})
    assert res.status_code == 200
    data = res.json()
    assert data["call_id"] == call_id
    assert len(data["ai_text"]) > 0

def test_analytics_endpoint():
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["ai_resolved_percentage"] == 100.0
    assert data["waiting_operator_count"] == 0
    assert data["total_calls_today"] > 0

@pytest.mark.asyncio
async def test_tts_generation():
    audio_path, duration, cached = await tts_service.generate_speech(
        "Assalomu alaykum, vazirlikka xush kelibsiz.",
        voice="uz-UZ-MadinaNeural"
    )
    assert audio_path.startswith("/api/audio/")
    assert duration > 0

def test_admin_websocket_silent_listen_and_ghost():
    with client.websocket_connect("/ws/admin") as admin_ws:
        init_data = admin_ws.receive_json()
        assert init_data["type"] == "admin_initial_state"
        assert "calls" in init_data

        admin_ws.send_json({
            "action": "silent_listen",
            "call_id": "call-101"
        })
        sub_resp = admin_ws.receive_json()
        assert sub_resp["type"] == "subscribed"
        assert sub_resp["call_id"] == "call-101"
