"""
SözLab WebSocket Manager:
1. /ws/call/{call_id}: Real-time voice session between citizen and SözLab AI
2. /ws/admin: Invisible supervisor ghost listener & teleprompter
"""

import asyncio
import json
import uuid
from typing import Dict, Set, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.models.schemas import SpeakerRole, MessageSchema
from app.services.call_manager import call_manager
from app.services.ai_dialog import dialog_manager
from app.services.tts_service import tts_service

router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    def __init__(self):
        # call_id -> set of active citizen WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # admin broad WebSockets
        self.admin_connections: Set[WebSocket] = set()
        # call_id -> set of admin WebSockets (100% invisible ghost mode)
        self.admin_listeners: Dict[str, Set[WebSocket]] = {}

    async def connect_call(self, call_id: str, websocket: WebSocket):
        await websocket.accept()
        if call_id not in self.active_connections:
            self.active_connections[call_id] = set()
        self.active_connections[call_id].add(websocket)

    def disconnect_call(self, call_id: str, websocket: WebSocket):
        if call_id in self.active_connections:
            self.active_connections[call_id].discard(websocket)
            if not self.active_connections[call_id]:
                del self.active_connections[call_id]

    async def connect_admin(self, websocket: WebSocket):
        await websocket.accept()
        self.admin_connections.add(websocket)

    def disconnect_admin(self, websocket: WebSocket):
        self.admin_connections.discard(websocket)
        for call_id, listeners in list(self.admin_listeners.items()):
            listeners.discard(websocket)
            if not listeners:
                del self.admin_listeners[call_id]

    def subscribe_admin(self, websocket: WebSocket, call_id: str):
        if call_id not in self.admin_listeners:
            self.admin_listeners[call_id] = set()
        self.admin_listeners[call_id].add(websocket)

    def unsubscribe_admin(self, websocket: WebSocket, call_id: str):
        if call_id in self.admin_listeners:
            self.admin_listeners[call_id].discard(websocket)
            if not self.admin_listeners[call_id]:
                del self.admin_listeners[call_id]

    async def broadcast_to_admin_listeners(self, call_id: str, data: dict):
        """Sends data ONLY to admin listeners for that call (100% silent & invisible to citizen)."""
        if call_id in self.admin_listeners:
            for connection in list(self.admin_listeners[call_id]):
                try:
                    await connection.send_json(data)
                except Exception:
                    pass

    async def broadcast_to_admins(self, data: dict):
        for connection in list(self.admin_connections):
            try:
                await connection.send_json(data)
            except Exception:
                pass

    async def broadcast_to_call(self, call_id: str, data: dict, exclude: Optional[WebSocket] = None):
        if call_id in self.active_connections:
            for connection in list(self.active_connections[call_id]):
                if exclude and connection == exclude:
                    continue
                try:
                    await connection.send_json(data)
                except Exception:
                    pass

    # Compatibility stubs
    async def broadcast_to_operators(self, data: dict):
        pass

    async def broadcast_queue_updates(self):
        pass


ws_manager = ConnectionManager()

@router.websocket("/ws/call/{call_id}")
async def call_websocket_endpoint(websocket: WebSocket, call_id: str):
    await ws_manager.connect_call(call_id, websocket)
    call = call_manager.get_call(call_id)
    if not call:
        call = call_manager.create_call(citizen_name="Fuqaro (Jonli)", citizen_phone="+998 90 999-00-11")
        call_id = call.id

    try:
        # Send initial call status and greeting
        await websocket.send_json({
            "type": "call_connected",
            "call_id": call_id,
            "status": call.status.value,
            "messages": [m.model_dump(mode="json") for m in call.messages]
        })

        while True:
            raw_text = await websocket.receive_text()
            try:
                payload = json.loads(raw_text)
            except Exception:
                payload = {"type": "user_speech", "text": raw_text}

            msg_type = payload.get("type", "user_speech")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            if msg_type == "user_speech":
                user_text = payload.get("text", "").strip()
                voice_name = payload.get("voice", "Gulnoza")
                
                if not user_text:
                    continue

                # 1. Record citizen message
                citizen_msg = MessageSchema(
                    id=f"msg-{uuid.uuid4().hex[:6]}",
                    role=SpeakerRole.CITIZEN,
                    text=user_text
                )
                call_manager.add_message(call_id, citizen_msg)

                # Send citizen message confirmation
                update_event = {
                    "type": "new_message",
                    "call_id": call_id,
                    "message": citizen_msg.model_dump(mode="json")
                }
                await ws_manager.broadcast_to_call(call_id, update_event)
                await ws_manager.broadcast_to_admin_listeners(call_id, {
                    "type": "ghost_message",
                    "call_id": call_id,
                    "role": "citizen",
                    "text": user_text,
                    "timestamp": citizen_msg.timestamp.isoformat() if hasattr(citizen_msg.timestamp, "isoformat") else str(citizen_msg.timestamp)
                })

                # Indicate AI thinking
                await ws_manager.broadcast_to_call(call_id, {
                    "type": "ai_thinking",
                    "call_id": call_id
                })

                # 2. Process through AI Dialog Manager (50 FAQ & Legal Encyclopedia)
                dialog_res = await dialog_manager.process_user_turn(call_id, user_text)

                # 3. Generate Speech via VoiceLab
                audio_url = None
                try:
                    url, _, _ = await tts_service.generate_speech(dialog_res.ai_text, voice=voice_name)
                    audio_url = url
                except Exception as e:
                    print(f"[WebSocket TTS Warning]: {e}")

                # 4. Save AI response
                ai_msg = MessageSchema(
                    id=f"ai-{uuid.uuid4().hex[:6]}",
                    role=SpeakerRole.AI,
                    text=dialog_res.ai_text,
                    audio_url=audio_url,
                    sentiment=dialog_res.sentiment,
                    detected_topic=dialog_res.topic
                )
                call_manager.add_message(call_id, ai_msg)

                # Mirror AI response to admin listeners
                await ws_manager.broadcast_to_admin_listeners(call_id, {
                    "type": "ghost_message",
                    "call_id": call_id,
                    "role": "bot",
                    "text": dialog_res.ai_text,
                    "audio_url": audio_url,
                    "timestamp": ai_msg.timestamp.isoformat() if hasattr(ai_msg.timestamp, "isoformat") else str(ai_msg.timestamp)
                })

                # Send AI response with audio URL & legal references
                await ws_manager.broadcast_to_call(call_id, {
                    "type": "ai_response",
                    "call_id": call_id,
                    "message": ai_msg.model_dump(mode="json"),
                    "topic": dialog_res.topic.value,
                    "sentiment": dialog_res.sentiment.value,
                    "knowledge_references": dialog_res.knowledge_references,
                    "smart_suggestions": dialog_res.smart_suggestions
                })

            elif msg_type == "live_caption":
                caption_text = payload.get("text", "").strip()
                if caption_text:
                    call_manager.add_live_transcript_turn(call_id, SpeakerRole.CITIZEN, "Fuqaro", caption_text)
                    await ws_manager.broadcast_to_call(call_id, {
                        "type": "live_caption",
                        "call_id": call_id,
                        "speaker_role": "citizen",
                        "speaker_name": "Fuqaro",
                        "text": caption_text
                    })
                    await ws_manager.broadcast_to_admin_listeners(call_id, {
                        "type": "ghost_message",
                        "call_id": call_id,
                        "role": "citizen",
                        "text": caption_text,
                        "timestamp": str(call_manager.get_call(call_id).duration_seconds if call_manager.get_call(call_id) else 0)
                    })

            elif msg_type == "end_call":
                summary = payload.get("summary", "Ovozli muloqot yakunlandi.")
                call_manager.complete_call(call_id, summary=summary)
                await ws_manager.broadcast_to_call(call_id, {
                    "type": "call_completed",
                    "summary": summary
                })
                await ws_manager.broadcast_to_admin_listeners(call_id, {
                    "type": "ghost_call_status",
                    "call_id": call_id,
                    "status": "completed",
                    "summary": summary
                })
                await ws_manager.broadcast_to_admins({
                    "type": "call_completed",
                    "call_id": call_id,
                    "calls": [c.model_dump(mode="json") for c in call_manager.get_all_calls()]
                })

    except WebSocketDisconnect:
        ws_manager.disconnect_call(call_id, websocket)

@router.websocket("/ws/admin")
async def admin_websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect_admin(websocket)
    try:
        calls = call_manager.get_all_calls()
        await websocket.send_json({
            "type": "admin_initial_state",
            "calls": [c.model_dump(mode="json") for c in calls]
        })
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            call_id = data.get("call_id")

            if action == "silent_listen" and call_id:
                ws_manager.subscribe_admin(websocket, call_id)
                call = call_manager.get_call(call_id)
                await websocket.send_json({
                    "type": "subscribed",
                    "call_id": call_id,
                    "call": call.model_dump(mode="json") if call else None
                })
            elif action in ("unlisten", "stop_listen") and call_id:
                ws_manager.unsubscribe_admin(websocket, call_id)
                await websocket.send_json({
                    "type": "unsubscribed",
                    "call_id": call_id
                })
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect_admin(websocket)
    except Exception:
        ws_manager.disconnect_admin(websocket)
