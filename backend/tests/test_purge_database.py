import io
import base64
import pytest
from pathlib import Path
import sys

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.services.call_manager import call_manager
from app.services.supabase_service import supabase_service
from app.models.schemas import CallStatus

client = TestClient(app)

def test_call_manager_purge_unit():
    """Verify call_manager.purge_all_calls() empties in-memory storage and returns count."""
    # Ensure at least one call exists
    call_manager.create_call(citizen_name="Sinov Fuqaro", citizen_phone="+998 90 999-00-11")
    assert len(call_manager.get_all_calls()) > 0

    count = call_manager.purge_all_calls()
    assert count > 0
    assert len(call_manager.get_all_calls()) == 0


@pytest.mark.asyncio
async def test_supabase_service_purge_unit():
    """Verify supabase_service.purge_all_records() runs gracefully without unhandled exceptions."""
    res = await supabase_service.purge_all_records()
    assert isinstance(res, dict)
    assert "offline_cache_purged" in res
    assert "supabase_purged" in res


def test_api_purge_database_endpoint_removed():
    """Verify DELETE /api/calls/purge-database returns 405 Method Not Allowed after web-app database removal."""
    purge_res = client.delete("/api/calls/purge-database")
    assert purge_res.status_code in [404, 405]


def test_audio_turn_base64_persistence():
    """Verify that uploading citizen audio stores a genuine Base64 data URI on message and call."""
    # 1. Start a call
    create_res = client.post("/api/calls", json={"name": "Nigora Karimova", "phone": "+998 91 222-33-44"})
    assert create_res.status_code == 200
    call_id = create_res.json()["id"]

    # 2. Send synthetic audio turn
    sample_wav_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    files = {"audio": ("sample.wav", io.BytesIO(sample_wav_bytes), "audio/wav")}
    data = {"voice_enabled": "false"}

    turn_res = client.post(f"/api/calls/{call_id}/audio-turn", files=files, data=data)
    assert turn_res.status_code == 200
    turn_data = turn_res.json()
    assert turn_data["call_id"] == call_id

    # 3. Retrieve call details and inspect audio_url
    detail_res = client.get(f"/api/calls/{call_id}")
    assert detail_res.status_code == 200
    call_record = detail_res.json()

    # Verify call.audio_url has data URI
    assert call_record.get("audio_url") is not None
    assert call_record["audio_url"].startswith("data:audio/wav;base64,")

    # Verify citizen message audio_url
    citizen_msg = next((m for m in call_record["messages"] if m["role"] == "citizen"), None)
    assert citizen_msg is not None
    assert citizen_msg.get("audio_url") is not None
    assert citizen_msg["audio_url"].startswith("data:audio/wav;base64,")

    # 4. Verify base64 decode reproduces the exact bytes sent
    b64_content = citizen_msg["audio_url"].split("base64,")[1]
    decoded_bytes = base64.b64decode(b64_content)
    assert decoded_bytes == sample_wav_bytes
