"""
SözLab Autonomous AI Calls API Router
Handles AI voice calls, turns, audio synthesis, and admin ghost listeners.
Zero operator queues or handovers.
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Body, UploadFile, File, Form
from app.models.schemas import (
    CallRecord, DialogTurnRequest, DialogTurnResponse, AudioTurnResponse,
    MessageSchema, SpeakerRole, CallStatus
)
from app.services.call_manager import call_manager
from app.services.ai_dialog import dialog_manager
from app.services.tts_service import tts_service
from app.api.routes.ws import ws_manager

router = APIRouter(prefix="/calls", tags=["Calls"])

@router.get("", response_model=List[CallRecord])
def get_calls(
    status: Optional[str] = Query(None, description="Filter by call status"),
    search: Optional[str] = Query(None, description="Search by name, phone or topic")
):
    calls = call_manager.get_all_calls()
    if status:
        calls = [c for c in calls if c.status.value == status]
    if search:
        s_low = search.lower()
        calls = [
            c for c in calls
            if s_low in c.citizen_name.lower()
            or s_low in c.citizen_phone
            or s_low in c.primary_topic.value.lower()
            or any(s_low in m.text.lower() for m in c.messages)
        ]
    return calls

@router.post("", response_model=CallRecord)
def start_call(
    name: str = Body("Fuqaro", embed=True),
    phone: str = Body("+998 90 000-00-00", embed=True)
):
    return call_manager.create_call(citizen_name=name, citizen_phone=phone)

@router.get("/{call_id}", response_model=CallRecord)
def get_call_details(call_id: str):
    call = call_manager.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Qo'ng'iroq topilmadi")
    return call

@router.post("/{call_id}/turn", response_model=DialogTurnResponse)
async def process_call_turn(call_id: str, request: DialogTurnRequest):
    call = call_manager.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Qo'ng'iroq topilmadi")

    # Record citizen message
    user_msg_id = f"msg-{uuid.uuid4().hex[:6]}"
    user_msg = MessageSchema(
        id=user_msg_id,
        role=SpeakerRole.CITIZEN,
        text=request.user_text
    )
    call_manager.add_message(call_id, user_msg)

    # Process AI turn strictly grounded in legal context
    dialog_res = await dialog_manager.process_user_turn(call_id, request.user_text)

    # Voice synthesis via VoiceLab Gulnoza
    audio_url = None
    if request.voice_enabled:
        try:
            url, _, _ = await tts_service.generate_speech(
                dialog_res.ai_text,
                voice=request.voice_name
            )
            audio_url = url
            dialog_res.audio_url = url
        except Exception as e:
            print(f"[TTS Error in Turn]: {e}")

    # Record AI response message
    ai_msg_id = f"ai-{uuid.uuid4().hex[:6]}"
    ai_msg = MessageSchema(
        id=ai_msg_id,
        role=SpeakerRole.AI,
        text=dialog_res.ai_text,
        audio_url=audio_url,
        sentiment=dialog_res.sentiment,
        detected_topic=dialog_res.topic
    )
    call_manager.add_message(call_id, ai_msg)

    # Check farewell
    if dialog_res.intent == "Xayrlashuv" or dialog_manager.is_farewell(request.user_text):
        call_manager.complete_call(call_id, summary="Fuqaro minnatdorchilik bildirib suhbatni yakunladi.")
        dialog_res.status = "completed"
    else:
        current_call = call_manager.get_call(call_id)
        dialog_res.status = current_call.status.value if current_call else call.status.value

    # Bridge to WebSocket subscribers and Admin Listeners
    citizen_ts = user_msg.timestamp.isoformat() if hasattr(user_msg.timestamp, "isoformat") else str(user_msg.timestamp)
    bot_ts = ai_msg.timestamp.isoformat() if hasattr(ai_msg.timestamp, "isoformat") else str(ai_msg.timestamp)

    await ws_manager.broadcast_to_call(call_id, {
        "type": "new_message",
        "call_id": call_id,
        "message": user_msg.model_dump(mode="json")
    })
    await ws_manager.broadcast_to_call(call_id, {
        "type": "ai_response",
        "call_id": call_id,
        "message": ai_msg.model_dump(mode="json"),
        "audio_url": audio_url
    })
    await ws_manager.broadcast_to_admin_listeners(call_id, {
        "type": "ghost_message",
        "call_id": call_id,
        "role": "citizen",
        "text": request.user_text,
        "timestamp": citizen_ts
    })
    await ws_manager.broadcast_to_admin_listeners(call_id, {
        "type": "ghost_message",
        "call_id": call_id,
        "role": "bot",
        "text": dialog_res.ai_text,
        "audio_url": audio_url,
        "timestamp": bot_ts
    })

    return dialog_res

@router.post("/{call_id}/audio-turn", response_model=AudioTurnResponse)
async def process_call_audio_turn(
    call_id: str,
    audio: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None),
    voice_name: Optional[str] = Form(None),
    voice: Optional[str] = Form(None),
    voice_enabled: Optional[str] = Form("true")
):
    """
    Accepts real audio recording from browser, transcribes via VoiceLab Studio SDK,
    generates strictly grounded legal response and VoiceLab synthesized audio.
    """
    call = call_manager.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Qo'ng'iroq topilmadi")

    upload_file = audio or file
    if not upload_file:
        raise HTTPException(status_code=400, detail="Audio fayl yuborilmadi")

    selected_voice = voice_name or voice
    is_voice_enabled = str(voice_enabled).lower() not in ("false", "0", "no", "none")

    audio_bytes = await upload_file.read()
    mime_type = upload_file.content_type or "audio/wav"

    # Transcribe via VoiceLab & evaluate through dialog manager
    transcribed_text, dialog_res = await dialog_manager.process_audio_turn(
        call_id=call_id,
        audio_bytes=audio_bytes,
        mime_type=mime_type,
        voice_name=selected_voice or "Gulnoza"
    )

    # Record citizen message with transcribed text
    user_msg_id = f"msg-{uuid.uuid4().hex[:6]}"
    user_msg = MessageSchema(
        id=user_msg_id,
        role=SpeakerRole.CITIZEN,
        text=transcribed_text
    )
    call_manager.add_message(call_id, user_msg)

    # Synthesize AI speech with VoiceLab
    audio_url = None
    if is_voice_enabled:
        try:
            url, _, _ = await tts_service.generate_speech(dialog_res.ai_text, voice=selected_voice)
            audio_url = url
        except Exception as e:
            print(f"[Audio Turn TTS Warning]: {e}")

    # Record AI message
    ai_msg_id = f"ai-{uuid.uuid4().hex[:6]}"
    ai_msg = MessageSchema(
        id=ai_msg_id,
        role=SpeakerRole.AI,
        text=dialog_res.ai_text,
        audio_url=audio_url,
        sentiment=dialog_res.sentiment,
        detected_topic=dialog_res.topic
    )
    call_manager.add_message(call_id, ai_msg)

    # Check farewell
    if dialog_res.intent == "Xayrlashuv" or call.status == CallStatus.COMPLETED or dialog_manager.is_farewell(transcribed_text):
        call_manager.complete_call(call_id, summary="Fuqaro minnatdorchilik bildirib suhbatni yakunladi.")
        current_status = "completed"
    else:
        current_call = call_manager.get_call(call_id)
        current_status = current_call.status.value if current_call else call.status.value

    # Bridge to WebSockets & Admin Ghost Listeners
    citizen_ts = user_msg.timestamp.isoformat() if hasattr(user_msg.timestamp, "isoformat") else str(user_msg.timestamp)
    bot_ts = ai_msg.timestamp.isoformat() if hasattr(ai_msg.timestamp, "isoformat") else str(ai_msg.timestamp)

    await ws_manager.broadcast_to_call(call_id, {
        "type": "transcription",
        "call_id": call_id,
        "text": transcribed_text,
        "role": "citizen"
    })
    await ws_manager.broadcast_to_call(call_id, {
        "type": "new_message",
        "call_id": call_id,
        "message": user_msg.model_dump(mode="json")
    })
    await ws_manager.broadcast_to_call(call_id, {
        "type": "ai_response",
        "call_id": call_id,
        "message": ai_msg.model_dump(mode="json"),
        "audio_url": audio_url
    })

    # Admin ghost listener mirroring
    await ws_manager.broadcast_to_admin_listeners(call_id, {
        "type": "ghost_message",
        "call_id": call_id,
        "role": "citizen",
        "text": transcribed_text,
        "timestamp": citizen_ts
    })
    await ws_manager.broadcast_to_admin_listeners(call_id, {
        "type": "ghost_message",
        "call_id": call_id,
        "role": "bot",
        "text": dialog_res.ai_text,
        "audio_url": audio_url,
        "timestamp": bot_ts
    })

    return AudioTurnResponse(
        call_id=call_id,
        transcribed_text=transcribed_text,
        ai_text=dialog_res.ai_text,
        user_text=transcribed_text,
        bot_text=dialog_res.ai_text,
        status=current_status,
        audio_url=audio_url,
        sentiment=dialog_res.sentiment,
        intent=dialog_res.intent,
        topic=dialog_res.topic,
        requires_operator=False
    )

@router.post("/{call_id}/complete")
async def complete_call(
    call_id: str,
    summary: Optional[str] = Body(None, embed=True)
):
    call, _ = call_manager.complete_call(call_id, summary=summary)
    if not call:
        raise HTTPException(status_code=404, detail="Qo'ng'iroq topilmadi")
    
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

    # Await Supabase archiving
    try:
        from app.services.supabase_service import supabase_service
        await supabase_service.archive_call_record(call)
    except Exception:
        pass

    return {"completed_call": call}
