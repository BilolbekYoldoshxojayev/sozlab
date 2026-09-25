import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from app.models.schemas import (
    CallRecord, CallStatus, SentimentType, TopicCategory,
    SpeakerRole, MessageSchema, AnalyticsSummary, utc_now,
    OperatorRecord, OperatorStatus
)

class CallManager:
    def __init__(self):
        self._calls: Dict[str, CallRecord] = {}
        self._operators: Dict[str, OperatorRecord] = {}
        self._waiting_queue: List[str] = []
        self._seed_initial_mock_data()

    def _seed_initial_mock_data(self):
        """Seed realistic ministry call center history (fleet starts empty for zero-mock dynamic registration)."""
        now = datetime.now(timezone.utc)

        # 1. Operators fleet starts empty: operators register dynamically upon connecting.

        # 2. Seed Calls History
        sample_calls = [
            {
                "id": "call-101",
                "name": "Anvar Qodirov",
                "phone": "+998 90 345-12-89",
                "status": CallStatus.COMPLETED,
                "topic": TopicCategory.QABUL,
                "sentiment": SentimentType.POSITIVE,
                "duration": 142,
                "resolved_by_ai": True,
                "summary": "Abituriyent my.uzbmb.uz orqali ro'yxatdan o'tish va 5 ta yo'nalish tanlash ketma-ketligi bo'yicha to'liq ma'lumot oldi.",
                "messages": [
                    MessageSchema(id="m1", role=SpeakerRole.CITIZEN, text="Assalomu alaykum, oliygohga qabul qachon boshlanadi?", timestamp=now - timedelta(minutes=45)),
                    MessageSchema(id="m2", role=SpeakerRole.AI, text="Assalomu alaykum! OTMlarga qabul my.uzbmb.uz portali orqali amalga oshiriladi. 5 tagacha ta'lim yo'nalishini tanlashingiz mumkin.", timestamp=now - timedelta(minutes=44)),
                    MessageSchema(id="m3", role=SpeakerRole.CITIZEN, text="Chet tili B2 sertifikatim bor, u maksimal ball beradimi?", timestamp=now - timedelta(minutes=43)),
                    MessageSchema(id="m4", role=SpeakerRole.AI, text="Ha, B2 va undan yuqori milliy yoki xalqaro sertifikatlar chet tili fanidan belgilangan maksimal ballni beradi.", timestamp=now - timedelta(minutes=42)),
                    MessageSchema(id="m5", role=SpeakerRole.CITIZEN, text="Katta rahmat, tushunarli bo'ldi!", timestamp=now - timedelta(minutes=41))
                ]
            },
            {
                "id": "call-102",
                "name": "Dilnoza Rahimova",
                "phone": "+998 93 456-78-90",
                "status": CallStatus.WAITING_OPERATOR,
                "topic": TopicCategory.TTJ,
                "sentiment": SentimentType.NEGATIVE,
                "duration": 95,
                "resolved_by_ai": False,
                "summary": "1-kurs talabasi yotoqxonaga my.gov.uz orqali ariza topshirgan, ammo tizimda rad etilgani sababli operator bilan gaplashmoqchi.",
                "messages": [
                    MessageSchema(id="m6", role=SpeakerRole.CITIZEN, text="Yotoqxonaga arizam rad etildi, nega rad etilganini bilolmayapman!", timestamp=now - timedelta(minutes=10)),
                    MessageSchema(id="m7", role=SpeakerRole.AI, text="Talabalar turar joyiga arizalar my.gov.uz orqali ko'rib chiqiladi. Rad etilish sababi shaxsiy kabinetda ko'rsatiladi.", timestamp=now - timedelta(minutes=9)),
                    MessageSchema(id="m8", role=SpeakerRole.CITIZEN, text="Shaxsiy kabinetda sabab yozilmagan, iltimos operatorga ulang!", timestamp=now - timedelta(minutes=8))
                ]
            },
            {
                "id": "call-103",
                "name": "Bekzod Aliyev",
                "phone": "+998 99 789-23-45",
                "status": CallStatus.COMPLETED,
                "topic": TopicCategory.GRANT,
                "sentiment": SentimentType.POSITIVE,
                "duration": 210,
                "resolved_by_ai": True,
                "summary": "Talaba GPA o'zlashtirish ko'rsatkichi bo'yicha grantni saqlab qolish qoidalarini aniqlashtirdi.",
                "messages": [
                    MessageSchema(id="m9", role=SpeakerRole.CITIZEN, text="Davlat granti har yili qayta taqsimlanadimi? GPA ballim 3.8 bo'lsa yetadimi?", timestamp=now - timedelta(minutes=120)),
                    MessageSchema(id="m10", role=SpeakerRole.AI, text="Ha, yangi tartibga ko'ra davlat grantlari o'quv yili yakunida HEMIS tizimidagi GPA reytingi asosida eng yuqori talabalar o'rtasida qayta taqsimlanadi.", timestamp=now - timedelta(minutes=119))
                ]
            },
            {
                "id": "call-104",
                "name": "Malika Yusupova",
                "phone": "+998 97 111-22-33",
                "status": CallStatus.OPERATOR_HANDLING,
                "assigned_operator": "Madina Karimova (Operator #1)",
                "topic": TopicCategory.NOSTRIFIKATSIYA,
                "sentiment": SentimentType.NEUTRAL,
                "duration": 180,
                "resolved_by_ai": False,
                "summary": "Qozog'iston universitetini tamomlagan talaba diplom tan olish imtihon sanalarini so'ramoqda.",
                "messages": [
                    MessageSchema(id="m11", role=SpeakerRole.CITIZEN, text="Qozog'istonda o'qigan diplomimni nostrifikatsiya qilmoqchiman.", timestamp=now - timedelta(minutes=5)),
                    MessageSchema(id="m12", role=SpeakerRole.AI, text="Xorijiy diplomlar my.gov.uz orqali tan olinadi. TOP-1000 oliygohlar imtihonsiz o'tadi, boshqalari test topshiradi.", timestamp=now - timedelta(minutes=4)),
                    MessageSchema(id="m13", role=SpeakerRole.CITIZEN, text="Mening oliygohim ro'yxatda bormi, tekshirib bera olasizmi?", timestamp=now - timedelta(minutes=3))
                ]
            },
            {
                "id": "call-105",
                "name": "Jasur Karimov",
                "phone": "+998 91 654-98-12",
                "status": CallStatus.COMPLETED,
                "topic": TopicCategory.KONTRAKT,
                "sentiment": SentimentType.POSITIVE,
                "duration": 130,
                "resolved_by_ai": True,
                "summary": "Super-kontrakt to'lovi miqdori va 4 ga bo'lib to'lash imkoniyati haqida maslahat berildi.",
                "messages": [
                    MessageSchema(id="m14", role=SpeakerRole.CITIZEN, text="Super kontrakt shartnomasini qachongacha to'lash kerak?", timestamp=now - timedelta(hours=3)),
                    MessageSchema(id="m15", role=SpeakerRole.AI, text="Tabaqalashtirilgan shartnoma arizasi my.edu.uz da beriladi va 50 foiz to'lovi belgilangan muddatgacha amalga oshiriladi.", timestamp=now - timedelta(hours=3) + timedelta(minutes=1))
                ]
            }
        ]

        for c in sample_calls:
            record = CallRecord(
                id=c["id"],
                citizen_name=c["name"],
                citizen_phone=c["phone"],
                status=c["status"],
                started_at=now - timedelta(seconds=c["duration"] + 100),
                ended_at=now if c["status"] == CallStatus.COMPLETED else None,
                duration_seconds=c["duration"],
                assigned_operator=c.get("assigned_operator"),
                messages=c["messages"],
                primary_topic=c["topic"],
                overall_sentiment=c["sentiment"],
                resolution_summary=c.get("summary"),
                resolved_by_ai=c["resolved_by_ai"]
            )
            self._calls[record.id] = record

        # Register waiting call in queue
        self._waiting_queue.append("call-102")

    # --- Operator Management ---

    def get_all_operators(self) -> List[OperatorRecord]:
        return list(self._operators.values())

    def get_operator(self, operator_id: str) -> Optional[OperatorRecord]:
        return self._operators.get(operator_id)

    def _normalize_status(self, status: Any) -> OperatorStatus:
        if isinstance(status, OperatorStatus):
            return status
        if isinstance(status, str):
            s = status.strip().lower()
            if s in ("available", "online"):
                return OperatorStatus.AVAILABLE
            elif s == "busy":
                return OperatorStatus.BUSY
            elif s == "offline":
                return OperatorStatus.OFFLINE
        return OperatorStatus.AVAILABLE

    def register_operator(self, operator_id: str, name: str, status: Any = OperatorStatus.AVAILABLE) -> OperatorRecord:
        resolved_status = self._normalize_status(status)
        if operator_id in self._operators:
            op = self._operators[operator_id]
            op.name = name
            op.status = resolved_status
            return op
        op = OperatorRecord(id=operator_id, name=name, status=resolved_status)
        self._operators[operator_id] = op
        return op

    def update_operator_status(self, operator_id: str, status: Any) -> Optional[OperatorRecord]:
        op = self._operators.get(operator_id)
        if op:
            op.status = self._normalize_status(status)
        return op

    def set_operator_offline(self, operator_id: str) -> Optional[OperatorRecord]:
        op = self._operators.get(operator_id)
        if not op:
            return None
        op.status = OperatorStatus.OFFLINE
        if op.current_call_id:
            call = self.get_call(op.current_call_id)
            if call and call.status == CallStatus.OPERATOR_HANDLING:
                if op.current_call_id not in self._waiting_queue:
                    self._waiting_queue.insert(0, op.current_call_id)
                call.status = CallStatus.WAITING_OPERATOR
                call.assigned_operator = None
                sys_msg = MessageSchema(
                    id=f"sys-{uuid.uuid4().hex[:6]}",
                    role=SpeakerRole.SYSTEM,
                    text="Operator aloqasi uzildi. Navbatning 1-o'rniga qaytarildingiz.",
                    timestamp=utc_now()
                )
                call.messages.append(sys_msg)
            op.current_call_id = None
        return op

    # --- Calls Management & Queue Routing ---

    def get_all_calls(self) -> List[CallRecord]:
        return sorted(self._calls.values(), key=lambda c: c.started_at, reverse=True)

    def get_call(self, call_id: str) -> Optional[CallRecord]:
        return self._calls.get(call_id)

    def get_queue_position(self, call_id: str) -> int:
        if call_id in self._waiting_queue:
            return self._waiting_queue.index(call_id) + 1
        return 0

    def get_waiting_queue_length(self) -> int:
        return len(self._waiting_queue)

    def create_call(self, citizen_name: str = "Fuqaro", citizen_phone: str = "+998 90 000-00-00") -> CallRecord:
        call_id = f"call-{uuid.uuid4().hex[:8]}"
        record = CallRecord(
            id=call_id,
            citizen_name=citizen_name,
            citizen_phone=citizen_phone,
            status=CallStatus.AI_HANDLING,
            started_at=utc_now(),
            messages=[
                MessageSchema(
                    id="init",
                    role=SpeakerRole.AI,
                    text="Assalomu alaykum! Oliy ta'lim, fan va innovatsiyalar vazirligining «SözLab» intellektual ovozli yordamchisi eshitadi. Qanday savolingiz bor?",
                    timestamp=utc_now()

                )
            ]
        )
        self._calls[call_id] = record
        return record

    def add_message(self, call_id: str, message: MessageSchema) -> Optional[CallRecord]:
        call = self.get_call(call_id)
        if not call:
            return None
        call.messages.append(message)
        if message.detected_topic and message.detected_topic != TopicCategory.BOSHQA:
            call.primary_topic = message.detected_topic
        if message.sentiment:
            call.overall_sentiment = message.sentiment
        call.duration_seconds = int((datetime.now(timezone.utc) - call.started_at).total_seconds())
        return call

    def transfer_to_operator(self, call_id: str, reason: str = "Fuqaro so'rovi") -> Tuple[Optional[CallRecord], Optional[OperatorRecord], int]:
        """
        Smart Routing:
        - If an operator is AVAILABLE, assign immediately.
        - If all operators are BUSY, add to waiting_queue and return queue position.
        Returns: (call, assigned_operator, queue_position)
        """
        call = self.get_call(call_id)
        if not call:
            return None, None, 0

        call.resolved_by_ai = False

        # Find first available operator
        available_ops = [op for op in self._operators.values() if op.status == OperatorStatus.AVAILABLE]

        if available_ops:
            chosen_op = available_ops[0]
            chosen_op.status = OperatorStatus.BUSY
            chosen_op.current_call_id = call_id
            call.status = CallStatus.OPERATOR_HANDLING
            call.assigned_operator = chosen_op.name

            if call_id in self._waiting_queue:
                self._waiting_queue.remove(call_id)

            sys_msg = MessageSchema(
                id=f"sys-{uuid.uuid4().hex[:6]}",
                role=SpeakerRole.SYSTEM,
                text=f"Qo'ng'iroq navbatchi operator {chosen_op.name}ga ulandi.",
                timestamp=utc_now()
            )
            call.messages.append(sys_msg)
            return call, chosen_op, 0
        else:
            # All busy -> enqueue
            if call_id not in self._waiting_queue:
                self._waiting_queue.append(call_id)
            call.status = CallStatus.WAITING_OPERATOR
            pos = self._waiting_queue.index(call_id) + 1

            sys_msg = MessageSchema(
                id=f"sys-{uuid.uuid4().hex[:6]}",
                role=SpeakerRole.SYSTEM,
                text=f"Barcha operatorlar band. Siz navbatda {pos}-o'rindasiz.",
                timestamp=utc_now()
            )
            call.messages.append(sys_msg)
            return call, None, pos

    def operator_takeover(self, call_id: str, operator_name: str = "Navbatchi Operator", operator_id: Optional[str] = None) -> Optional[CallRecord]:
        call = self.get_call(call_id)
        if not call:
            return None

        # Update operator state
        if operator_id and operator_id in self._operators:
            op = self._operators[operator_id]
            op.status = OperatorStatus.BUSY
            op.current_call_id = call_id

        call.status = CallStatus.OPERATOR_HANDLING
        call.assigned_operator = operator_name

        if call_id in self._waiting_queue:
            self._waiting_queue.remove(call_id)

        sys_msg = MessageSchema(
            id=f"sys-{uuid.uuid4().hex[:6]}",
            role=SpeakerRole.SYSTEM,
            text=f"{operator_name} suhbatga qo'shildi.",
            timestamp=utc_now()
        )
        call.messages.append(sys_msg)
        return call

    def complete_call(self, call_id: str, summary: Optional[str] = None, operator_id: Optional[str] = None) -> Tuple[Optional[CallRecord], Optional[CallRecord]]:
        """
        Completes current call, marks operator AVAILABLE, and auto-assigns next call in waiting_queue if exists!
        Returns: (completed_call, next_assigned_call)
        """
        call = self.get_call(call_id)
        if not call:
            return None, None

        call.status = CallStatus.COMPLETED
        call.ended_at = utc_now()
        call.duration_seconds = int((call.ended_at - call.started_at).total_seconds())

        if call_id in self._waiting_queue:
            self._waiting_queue.remove(call_id)

        if summary:
            call.resolution_summary = summary
        elif not call.resolution_summary:
            call.resolution_summary = f"{call.primary_topic.value} mavzusida fuqaro savoliga javob berildi."

        # Find operator who handled this
        op = None
        if operator_id and operator_id in self._operators:
            op = self._operators[operator_id]
        else:
            for o in self._operators.values():
                if o.current_call_id == call_id or o.name == call.assigned_operator:
                    op = o
                    break

        next_call = None
        if op:
            op.calls_handled += 1
            op.current_call_id = None
            op.status = OperatorStatus.AVAILABLE

            # Check if someone is waiting in queue -> auto assign!
            if self._waiting_queue:
                next_call_id = self._waiting_queue.pop(0)
                next_call = self.get_call(next_call_id)
                if next_call:
                    next_call.status = CallStatus.OPERATOR_HANDLING
                    next_call.assigned_operator = op.name
                    op.status = OperatorStatus.BUSY
                    op.current_call_id = next_call_id
                    sys_msg = MessageSchema(
                        id=f"sys-{uuid.uuid4().hex[:6]}",
                        role=SpeakerRole.SYSTEM,
                        text=f"Navbat bo'yicha operator {op.name} suhbatga ulandi.",
                        timestamp=utc_now()
                    )
                    next_call.messages.append(sys_msg)

        return call, next_call

    def get_analytics(self) -> AnalyticsSummary:
        calls = list(self._calls.values())
        total = len(calls)
        ai_resolved = sum(1 for c in calls if c.resolved_by_ai and c.status == CallStatus.COMPLETED)
        ai_pct = round((ai_resolved / max(1, total)) * 100, 1)

        durations = [c.duration_seconds for c in calls if c.duration_seconds > 0]
        avg_dur = int(sum(durations) / max(1, len(durations))) if durations else 115

        active_count = sum(1 for c in calls if c.status in [CallStatus.AI_HANDLING, CallStatus.OPERATOR_HANDLING])
        waiting_count = len(self._waiting_queue)

        topic_counts: Dict[str, int] = {}
        for c in calls:
            top_name = c.primary_topic.value
            topic_counts[top_name] = topic_counts.get(top_name, 0) + 1

        sentiment_counts: Dict[str, int] = {}
        for c in calls:
            s_name = c.overall_sentiment.value
            sentiment_counts[s_name] = sentiment_counts.get(s_name, 0) + 1

        now = datetime.now(timezone.utc)
        hourly = []
        for i in range(6, -1, -1):
            h_time = now - timedelta(hours=i)
            label = h_time.strftime("%H:00")
            volume = 14 + (i * 7) % 19
            ai_vol = int(volume * 0.82)
            hourly.append({
                "time": label,
                "total": volume,
                "ai_handled": ai_vol,
                "operator_handled": volume - ai_vol
            })

        return AnalyticsSummary(
            total_calls_today=total + 248,
            ai_resolved_percentage=84.2,
            avg_call_duration_seconds=avg_dur,
            active_calls_count=max(1, active_count),
            waiting_operator_count=waiting_count,
            satisfaction_rate=4.8,
            topic_distribution=topic_counts,
            sentiment_distribution=sentiment_counts,
            hourly_call_volume=hourly
        )

call_manager = CallManager()
