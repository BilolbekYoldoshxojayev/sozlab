import asyncio
import json
import uuid
from typing import Dict, Set, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.models.schemas import SpeakerRole, MessageSchema
from app.services.call_manager import call_manager
from app.services.ai_dialog import dialog_manager
from app.services.tts_service import tts_service

router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    def __init__(self):
        # call_id -> set of active WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # operator broad WebSockets for dashboard
        self.operator_connections: Set[WebSocket] = set()
        # websocket -> operator_id
        self.operator_map: Dict[WebSocket, str] = {}
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

    async def connect_operator(self, websocket: WebSocket, operator_id: Optional[str] = None):
        await websocket.accept()
        self.operator_connections.add(websocket)
        if operator_id:
            self.operator_map[websocket] = operator_id

    async def disconnect_operator(self, websocket: WebSocket):
        self.operator_connections.discard(websocket)
        operator_id = self.operator_map.pop(websocket, None)
        if operator_id:
            call_manager.set_operator_offline(operator_id)
            await self.broadcast_to_operators({
                "type": "operators_updated",
                "operators": [o.model_dump(mode="json") for o in call_manager.get_all_operators()]
            })
            await self.broadcast_to_admins({
                "type": "operators_updated",
                "operators": [o.model_dump(mode="json") for o in call_manager.get_all_operators()]
            })
            await self.broadcast_queue_updates()

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
        """Sends data ONLY to admin listeners for that call. Must be 100% silent and invisible to citizen and operator sockets!"""
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

    async def broadcast_to_call(self, call_id: str, data: dict):
        if call_id in self.active_connections:
            for connection in list(self.active_connections[call_id]):
                try:
                    await connection.send_json(data)
                except Exception:
                    pass

    async def broadcast_to_operators(self, data: dict):
        for connection in list(self.operator_connections):
            try:
                await connection.send_json(data)
            except Exception:
                pass

    async def broadcast_queue_updates(self):
        """Broadcast updated positions to all citizens currently in the waiting queue."""
        for call_id in list(call_manager._waiting_queue):
            pos = call_manager.get_queue_position(call_id)
            await self.broadcast_to_call(call_id, {
                "type": "queue_update",
                "position": pos,
                "message": f"Siz navbatda {pos}-o'rindasiz."
            })

ws_manager = ConnectionManager()

@router.websocket("/ws/call/{call_id}")
async def call_websocket_endpoint(websocket: WebSocket, call_id: str):
    await ws_manager.connect_call(call_id, websocket)
    call = call_manager.get_call(call_id)
    if not call:
        call = call_manager.create_call(citizen_name="Fuqaro (Jonli)", citizen_phone="+998 90 999-00-11")
        call_id = call.id

    try:
        # Check current queue position if in queue
        pos = call_manager.get_queue_position(call_id)

        # Send initial call status and greeting
        await websocket.send_json({
            "type": "call_connected",
            "call_id": call_id,
            "status": call.status.value,
            "queue_position": pos if pos > 0 else None,
            "assigned_operator": call.assigned_operator,
            "messages": [m.model_dump(mode="json") for m in call.messages]
        })

        # Notify operators that a call is live
        await ws_manager.broadcast_to_operators({
            "type": "call_updated",
            "call": call.model_dump(mode="json"),
            "operators": [op.model_dump(mode="json") for op in call_manager.get_all_operators()]
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
                voice_name = payload.get("voice", "uz-UZ-MadinaNeural")
                
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
                await ws_manager.broadcast_to_operators({
                    "type": "call_updated",
                    "call": call_manager.get_call(call_id).model_dump(mode="json")
                })
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

                # 2. Process through AI Dialog Manager
                dialog_res = await dialog_manager.process_user_turn(call_id, user_text)

                # 3. Generate Speech via edge-tts
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

                # Smart operator routing if required
                assigned_op_name = None
                queue_pos = None
                if dialog_res.requires_operator:
                    updated_call, assigned_op, q_pos = call_manager.transfer_to_operator(call_id, reason="AI yo'naltirdi")
                    if assigned_op:
                        assigned_op_name = assigned_op.name
                    else:
                        queue_pos = q_pos

                updated_call = call_manager.get_call(call_id)

                # Send AI response with audio URL & queue info
                await ws_manager.broadcast_to_call(call_id, {
                    "type": "ai_response",
                    "call_id": call_id,
                    "message": ai_msg.model_dump(mode="json"),
                    "requires_operator": dialog_res.requires_operator,
                    "assigned_operator": assigned_op_name,
                    "queue_position": queue_pos,
                    "topic": dialog_res.topic.value,
                    "sentiment": dialog_res.sentiment.value,
                    "smart_suggestions": dialog_res.smart_suggestions
                })

                # Broadcast to Operator Dashboard
                await ws_manager.broadcast_to_operators({
                    "type": "call_updated",
                    "call": updated_call.model_dump(mode="json"),
                    "operators": [op.model_dump(mode="json") for op in call_manager.get_all_operators()]
                })

            elif msg_type == "request_operator":
                reason = payload.get("reason", "Fuqaro operatorni so'radi")
                updated_call, assigned_op, q_pos = call_manager.transfer_to_operator(call_id, reason=reason)
                
                if assigned_op:
                    await ws_manager.broadcast_to_call(call_id, {
                        "type": "operator_assigned",
                        "call_id": call_id,
                        "operator_name": assigned_op.name,
                        "message": f"Siz navbatchi operator {assigned_op.name}ga ulandingiz."
                    })
                else:
                    await ws_manager.broadcast_to_call(call_id, {
                        "type": "queue_update",
                        "call_id": call_id,
                        "position": q_pos,
                        "message": f"Barcha operatorlar band. Siz navbatda {q_pos}-o'rindasiz."
                    })

                await ws_manager.broadcast_to_operators({
                    "type": "call_updated",
                    "call": updated_call.model_dump(mode="json"),
                    "operators": [op.model_dump(mode="json") for op in call_manager.get_all_operators()]
                })

    except WebSocketDisconnect:
        ws_manager.disconnect_call(call_id, websocket)

@router.websocket("/ws/operator")
async def operator_websocket_endpoint(
    websocket: WebSocket,
    operator_id: Optional[str] = Query(None),
    operator_name: Optional[str] = Query(None)
):
    await ws_manager.connect_operator(websocket, operator_id=operator_id)
    try:
        calls = call_manager.get_all_calls()
        operators = call_manager.get_all_operators()
        await websocket.send_json({
            "type": "initial_state",
            "calls": [c.model_dump(mode="json") for c in calls],
            "operators": [op.model_dump(mode="json") for op in operators],
            "waiting_queue_count": call_manager.get_waiting_queue_length()
        })

        if operator_id:
            call_manager.register_operator(operator_id, operator_name or f"Operator ({operator_id})")
            await ws_manager.broadcast_to_operators({
                "type": "operators_updated",
                "operators": [o.model_dump(mode="json") for o in call_manager.get_all_operators()]
            })
            await ws_manager.broadcast_to_admins({
                "type": "operators_updated",
                "operators": [o.model_dump(mode="json") for o in call_manager.get_all_operators()]
            })
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            call_id = data.get("call_id")
            op_id = data.get("operator_id") or operator_id or "op-1"
            op_name = data.get("operator_name") or operator_name or "Operator"
            
            if action == "register":
                ws_manager.operator_map[websocket] = op_id
                op = call_manager.register_operator(op_id, op_name)
                await ws_manager.broadcast_to_operators({
                    "type": "operators_updated",
                    "operators": [o.model_dump(mode="json") for o in call_manager.get_all_operators()]
                })
                await ws_manager.broadcast_to_admins({
                    "type": "operators_updated",
                    "operators": [o.model_dump(mode="json") for o in call_manager.get_all_operators()]
                })

            elif action == "takeover" and call_id:
                call_manager.operator_takeover(call_id, operator_name=op_name, operator_id=op_id)
                updated_call = call_manager.get_call(call_id)
                await ws_manager.broadcast_to_call(call_id, {
                    "type": "operator_joined",
                    "operator_name": op_name
                })
                await ws_manager.broadcast_to_operators({
                    "type": "call_updated",
                    "call": updated_call.model_dump(mode="json"),
                    "operators": [o.model_dump(mode="json") for o in call_manager.get_all_operators()]
                })
                # Re-broadcast queue updates if someone was dequeued
                await ws_manager.broadcast_queue_updates()

            elif action == "complete" and call_id:
                summary = data.get("summary", "Operator tomonidan muammo hal etildi.")
                completed_call, next_call = call_manager.complete_call(call_id, summary=summary, operator_id=op_id)
                
                # Notify citizen that call is completed
                await ws_manager.broadcast_to_call(call_id, {
                    "type": "call_completed",
                    "summary": summary
                })
                # Notify admin ghost listeners that call is completed
                await ws_manager.broadcast_to_admin_listeners(call_id, {
                    "type": "ghost_call_status",
                    "call_id": call_id,
                    "status": "completed",
                    "summary": summary
                })

                # If a waiting citizen was automatically dequeued and assigned to this operator:
                if next_call:
                    topic_str = "Umumiy murojaat"
                    if hasattr(next_call, "primary_topic") and next_call.primary_topic:
                        topic_str = getattr(next_call.primary_topic, "value", str(next_call.primary_topic))
                    elif hasattr(next_call, "topic") and next_call.topic:
                        topic_str = str(next_call.topic)

                    await ws_manager.broadcast_to_call(next_call.id, {
                        "type": "operator_assigned",
                        "operator_name": op_name,
                        "message": f"Navbatingiz keldi. Siz navbatchi operator {op_name}ga ulandingiz."
                    })

                    # Dispatch next_call_countdown to operator socket
                    await websocket.send_json({
                        "type": "next_call_countdown",
                        "duration": 3,
                        "next_call_id": next_call.id,
                        "caller_name": next_call.citizen_name or "Fuqaro",
                        "topic": topic_str,
                        "next_call": next_call.model_dump(mode="json")
                    })

                # Update remaining queue positions
                await ws_manager.broadcast_queue_updates()

                await ws_manager.broadcast_to_operators({
                    "type": "call_completed",
                    "call_id": call_id,
                    "calls": [c.model_dump(mode="json") for c in call_manager.get_all_calls()],
                    "operators": [o.model_dump(mode="json") for o in call_manager.get_all_operators()]
                })
                await ws_manager.broadcast_to_admins({
                    "type": "call_completed",
                    "call_id": call_id,
                    "calls": [c.model_dump(mode="json") for c in call_manager.get_all_calls()],
                    "operators": [o.model_dump(mode="json") for o in call_manager.get_all_operators()]
                })
            
            elif action == "send_message" and call_id:
                text = data.get("text", "")
                msg = MessageSchema(
                    id=f"op-{uuid.uuid4().hex[:6]}",
                    role=SpeakerRole.OPERATOR,
                    text=text
                )
                call_manager.add_message(call_id, msg)
                updated_call = call_manager.get_call(call_id)
                
                await ws_manager.broadcast_to_call(call_id, {
                    "type": "new_message",
                    "call_id": call_id,
                    "message": msg.model_dump(mode="json")
                })
                await ws_manager.broadcast_to_operators({
                    "type": "call_updated",
                    "call": updated_call.model_dump(mode="json")
                })
                # Mirror operator message to admin ghost listeners
                await ws_manager.broadcast_to_admin_listeners(call_id, {
                    "type": "ghost_message",
                    "call_id": call_id,
                    "role": "operator",
                    "text": text,
                    "timestamp": msg.timestamp.isoformat() if hasattr(msg.timestamp, "isoformat") else str(msg.timestamp)
                })

    except WebSocketDisconnect:
        await ws_manager.disconnect_operator(websocket)
    except Exception:
        await ws_manager.disconnect_operator(websocket)

@router.websocket("/ws/admin")
async def admin_websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect_admin(websocket)
    try:
        calls = call_manager.get_all_calls()
        operators = call_manager.get_all_operators()
        await websocket.send_json({
            "type": "admin_initial_state",
            "calls": [c.model_dump(mode="json") for c in calls],
            "operators": [op.model_dump(mode="json") for op in operators],
            "waiting_queue_count": call_manager.get_waiting_queue_length()
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
