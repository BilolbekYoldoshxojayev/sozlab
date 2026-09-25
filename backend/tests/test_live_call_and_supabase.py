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
    call_manager.add_live_transcript_turn(test_call.id, SpeakerRole.OPERATOR, "Nargiza", "Vaalaykum assalom, qanday yordam bera olaman?")
    
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

def test_webrtc_signaling_exchange():
    test_call = call_manager.create_call(citizen_name="WebRTC Test", citizen_phone="+998 99 000-11-22")
    call_id = test_call.id

    with client.websocket_connect(f"/ws/call/{call_id}") as citizen_ws:
        # Initial call_connected
        init_citizen = citizen_ws.receive_json()
        assert init_citizen["type"] == "call_connected"

        with client.websocket_connect(f"/ws/call/{call_id}") as operator_ws:
            # Initial call_connected for operator
            init_op = operator_ws.receive_json()
            assert init_op["type"] == "call_connected"

            # 1. Operator sends webrtc_offer -> Citizen receives it
            operator_ws.send_json({
                "type": "webrtc_offer",
                "call_id": call_id,
                "sdp": "v=0\r\no=operator 12345 2 IN IP4 127.0.0.1\r\ns=LiveAudioCall",
                "sender_role": "operator"
            })
            offer_event = citizen_ws.receive_json()
            assert offer_event["type"] == "webrtc_offer"
            assert "v=0" in offer_event["sdp"]
            assert offer_event["sender_role"] == "operator"

            # 2. Citizen sends webrtc_answer -> Operator receives it
            citizen_ws.send_json({
                "type": "webrtc_answer",
                "call_id": call_id,
                "sdp": "v=0\r\no=citizen 67890 2 IN IP4 127.0.0.1\r\ns=LiveAudioCallAnswer",
                "sender_role": "citizen"
            })
            answer_event = operator_ws.receive_json()
            assert answer_event["type"] == "webrtc_answer"
            assert "citizen" in answer_event["sdp"]
            assert answer_event["sender_role"] == "citizen"

            # 3. ICE candidate exchange
            operator_ws.send_json({
                "type": "webrtc_ice_candidate",
                "call_id": call_id,
                "candidate": {"candidate": "candidate:1 1 UDP 2130706431 192.168.1.1 50000 typ host"},
                "sender_role": "operator"
            })
            ice_event = citizen_ws.receive_json()
            assert ice_event["type"] == "webrtc_ice_candidate"
            assert "192.168.1.1" in ice_event["candidate"]["candidate"]

def test_websocket_audio_relay_fallback():
    test_call = call_manager.create_call(citizen_name="Audio Relay Test", citizen_phone="+998 90 555-44-33")
    call_id = test_call.id

    with client.websocket_connect(f"/ws/call/{call_id}") as citizen_ws:
        _ = citizen_ws.receive_json()

        with client.websocket_connect(f"/ws/call/{call_id}") as operator_ws:
            _ = operator_ws.receive_json()

            # Citizen sends raw audio chunk
            mock_audio_b64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
            citizen_ws.send_json({
                "type": "peer_audio_chunk",
                "call_id": call_id,
                "audio": mock_audio_b64,
                "sender_role": "citizen"
            })

            # Operator receives relayed audio chunk
            audio_event = operator_ws.receive_json()
            assert audio_event["type"] == "peer_audio_chunk"
            assert audio_event["audio"] == mock_audio_b64
            assert audio_event["sender_role"] == "citizen"

def test_live_captions_subtitles_stream():
    test_call = call_manager.create_call(citizen_name="Caption Test", citizen_phone="+998 90 777-66-55")
    call_id = test_call.id

    with client.websocket_connect(f"/ws/call/{call_id}") as citizen_ws:
        _ = citizen_ws.receive_json()

        with client.websocket_connect(f"/ws/call/{call_id}") as operator_ws:
            _ = operator_ws.receive_json()

            # Operator speaks -> live caption sent
            operator_ws.send_json({
                "type": "live_caption",
                "call_id": call_id,
                "speaker_role": "operator",
                "speaker_name": "Nargiza",
                "text": "Assalomu alaykum, vazirlik call-markazi xizmati!"
            })

            # Both receive live caption event
            cap1 = citizen_ws.receive_json()
            cap2 = operator_ws.receive_json()

            assert cap1["type"] == "live_caption"
            assert cap1["speaker_role"] == "operator"
            assert cap1["text"] == "Assalomu alaykum, vazirlik call-markazi xizmati!"

            assert cap2["type"] == "live_caption"
            assert cap2["text"] == "Assalomu alaykum, vazirlik call-markazi xizmati!"

            # Verify in-memory transcript
            updated_call = call_manager.get_call(call_id)
            assert any("vazirlik call-markazi xizmati" in m.text for m in updated_call.messages)
