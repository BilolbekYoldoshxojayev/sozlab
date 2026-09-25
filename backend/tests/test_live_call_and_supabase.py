import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
import json
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.call_manager import call_manager
from app.services.supabase_service import supabase_service
from app.models.schemas import CallRecord, CallStatus, SpeakerRole, MessageSchema, utc_now

client = TestClient(app)

@pytest.mark.asyncio
async def test_supabase_service_graceful_fallback(tmp_path):
    # Test that unconfigured or offline Supabase safely saves to offline archive
    test_call = call_manager.create_call(citizen_name="Sinov Fuqaro", citizen_phone="+998 90 123-45-67")
    call_manager.add_live_transcript_turn(test_call.id, SpeakerRole.CITIZEN, "Sinov Fuqaro", "Assalomu alaykum")
    call_manager.add_live_transcript_turn(test_call.id, SpeakerRole.AI, "SözLab AI", "Vaalaykum assalom, qanday yordam bera olaman?")
    
    # Mock offline file to tmp_path
    original_offline = supabase_service.offline_file
    try:
        supabase_service.offline_file = tmp_path / "offline_archive.jsonl"
        with patch.object(supabase_service, "is_configured", return_value=False):
            success = await supabase_service.archive_call_record(test_call)
            assert success is False
            assert supabase_service.offline_file.exists()
            content = supabase_service.offline_file.read_text(encoding="utf-8")
            assert test_call.id in content
            assert "Sinov Fuqaro" in content
    finally:
        supabase_service.offline_file = original_offline

@pytest.mark.asyncio
async def test_supabase_service_online_mock():
    test_call = call_manager.create_call(citizen_name="Abbosbek", citizen_phone="+998 93 111-22-33")
    
    mock_response = AsyncMock()
    mock_response.status_code = 201
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        with patch.object(supabase_service, "is_configured", return_value=True):
            success = await supabase_service.archive_call_record(test_call)
            assert success is True

def test_live_citizen_ai_websocket_interaction():
    test_call = call_manager.create_call(citizen_name="WS Test Caller", citizen_phone="+998 99 000-11-22")
    call_id = test_call.id

    with client.websocket_connect(f"/ws/call/{call_id}") as citizen_ws:
        # Initial call_connected
        init_citizen = citizen_ws.receive_json()
        assert init_citizen["type"] == "call_connected"

        # Send ping
        citizen_ws.send_json({"type": "ping"})
        pong = citizen_ws.receive_json()
        assert pong["type"] == "pong"

        # End call
        citizen_ws.send_json({"type": "end_call", "summary": "WS call completed"})
        end_event = citizen_ws.receive_json()
        assert end_event["type"] == "call_completed"
