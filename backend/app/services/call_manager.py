"""
SözLab Autonomous Call State Manager
Pure Autonomous AI Voice Center (100% Operator-Free).
Manages calls, live transcript turns, durations, legal citations, and Supabase cloud persistence.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from app.models.schemas import (
    CallRecord, CallStatus, SentimentType, TopicCategory,
    SpeakerRole, MessageSchema, AnalyticsSummary, utc_now
)

logger = logging.getLogger("sozlab.call_manager")

class CallManager:
    def __init__(self):
        import sys
        if "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ or os.environ.get("ENV") == "test":
            self.saved_calls_dir = Path(__file__).resolve().parent.parent.parent / "data" / "test_saved_calls"
        else:
            self.saved_calls_dir = Path(__file__).resolve().parent.parent.parent / "data" / "saved_calls"
        self.saved_calls_dir.mkdir(parents=True, exist_ok=True)
        self._calls: Dict[str, CallRecord] = {}
        
        # Load persisted calls from disk (only in real runtime, never in test mode)
        if "pytest" not in sys.modules and "PYTEST_CURRENT_TEST" not in os.environ and os.environ.get("ENV") != "test":
            self.load_all_calls_from_disk()

    def load_all_calls_from_disk(self) -> int:
        """
        Scans self.saved_calls_dir for all .json files and restores them into self._calls.
        Returns the number of successfully loaded calls.
        """
        if not self.saved_calls_dir.exists():
            return 0
        loaded_count = 0
        for fpath in self.saved_calls_dir.glob("*.json"):
            if fpath.name.endswith(".tmp"):
                continue
            try:
                content = fpath.read_text(encoding="utf-8")
                data = json.loads(content)
                record = CallRecord.model_validate(data)
                record.messages = [
                    m for m in record.messages
                    if not (m.id == "init" or (m.role == SpeakerRole.AI and not m.audio_url and m.text == "Assalomu alaykum, eshitaman."))
                ]
                self._calls[record.id] = record
                loaded_count += 1
            except Exception as e:
                logger.warning(f"Failed to load call file {fpath.name}: {e}")
        if loaded_count > 0:
            logger.info(f"[CallManager] Loaded {loaded_count} persisted call records from {self.saved_calls_dir}")
        return loaded_count

    def save_call_to_disk(self, call_or_id: Union[str, CallRecord]) -> bool:
        """
        Persists call record JSON atomically to self.saved_calls_dir/{call_id}.json.
        Writes to .tmp file first, then atomic os.replace to prevent partial writes.
        """
        try:
            if isinstance(call_or_id, CallRecord):
                record = call_or_id
                c_id = record.id
                self._calls[c_id] = record
            else:
                c_id = str(call_or_id)
                record = self._calls.get(c_id)

            if not record:
                logger.warning(f"save_call_to_disk: Call {c_id} not found in memory.")
                return False

            self.saved_calls_dir.mkdir(parents=True, exist_ok=True)
            target_path = self.saved_calls_dir / f"{c_id}.json"
            tmp_path = self.saved_calls_dir / f"{c_id}.json.tmp"

            payload = record.model_dump(mode="json")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

            os.replace(tmp_path, target_path)
            return True
        except Exception as e:
            logger.warning(f"Failed to persist call {call_or_id} to disk: {e}")
            return False

    def get_all_calls(self) -> List[CallRecord]:
        return sorted(self._calls.values(), key=lambda c: c.started_at, reverse=True)

    def get_call(self, call_id: str) -> Optional[CallRecord]:
        if call_id in self._calls:
            return self._calls[call_id]

        # Fallback disk lookup
        fpath = self.saved_calls_dir / f"{call_id}.json"
        if fpath.exists():
            try:
                content = fpath.read_text(encoding="utf-8")
                data = json.loads(content)
                record = CallRecord.model_validate(data)
                record.messages = [
                    m for m in record.messages
                    if not (m.id == "init" or (m.role == SpeakerRole.AI and not m.audio_url and m.text == "Assalomu alaykum, eshitaman."))
                ]
                self._calls[record.id] = record
                return record
            except Exception as e:
                logger.warning(f"Failed to load call from disk {call_id}: {e}")
        return None

    def create_call(self, citizen_name: str = "Fuqaro", citizen_phone: str = "+998 90 000-00-00") -> CallRecord:
        call_id = f"call-{uuid.uuid4().hex[:8]}"
        record = CallRecord(
            id=call_id,
            citizen_name=citizen_name,
            citizen_phone=citizen_phone,
            status=CallStatus.AI_HANDLING,
            started_at=utc_now(),
            resolved_by_ai=True,
            messages=[]
        )
        self._calls[call_id] = record
        self.save_call_to_disk(record)
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
        if message.llm_provider_used:
            call.llm_provider_used = message.llm_provider_used
            call.last_llm_provider = message.llm_provider_used
        call.duration_seconds = int((datetime.now(timezone.utc) - call.started_at).total_seconds())
        self.save_call_to_disk(call)
        return call

    def complete_call(self, call_id: str, summary: Optional[str] = None) -> Tuple[Optional[CallRecord], None]:
        """
        Completes the AI call and archives to Supabase PostgreSQL.
        """
        call = self.get_call(call_id)
        if not call:
            return None, None

        call.status = CallStatus.COMPLETED
        call.ended_at = utc_now()
        call.duration_seconds = int((call.ended_at - call.started_at).total_seconds())
        call.resolved_by_ai = True

        if summary:
            call.resolution_summary = summary
        elif not call.resolution_summary:
            call.resolution_summary = f"{call.primary_topic.value} mavzusida rasmiy huquqiy tushuntirish berildi."

        # Asynchronously archive to Supabase
        try:
            from app.services.supabase_service import supabase_service
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(supabase_service.archive_call_record(call))
            except RuntimeError:
                pass
        except Exception:
            pass

        self.save_call_to_disk(call)
        return call, None

    def add_live_transcript_turn(self, call_id: str, role: SpeakerRole, speaker_name: str, text: str) -> Optional[MessageSchema]:
        """Record real-time closed caption dialog turn."""
        call = self.get_call(call_id)
        if not call:
            return None
        msg = MessageSchema(
            id=f"live-{uuid.uuid4().hex[:6]}",
            role=role,
            text=text,
            timestamp=utc_now()
        )
        call.messages.append(msg)
        call.duration_seconds = int((datetime.now(timezone.utc) - call.started_at).total_seconds())
        self.save_call_to_disk(call)
        return msg

    def get_analytics(self) -> AnalyticsSummary:
        calls = list(self._calls.values())
        total = len(calls)
        durations = [c.duration_seconds for c in calls if c.duration_seconds > 0]
        avg_dur = int(sum(durations) / len(durations)) if durations else 0
        active_count = sum(1 for c in calls if c.status == CallStatus.AI_HANDLING)

        topic_counts: Dict[str, int] = {}
        for c in calls:
            top_name = c.primary_topic.value if hasattr(c.primary_topic, 'value') else str(c.primary_topic)
            topic_counts[top_name] = topic_counts.get(top_name, 0) + 1

        sentiment_counts: Dict[str, int] = {}
        for c in calls:
            s_name = c.overall_sentiment.value if hasattr(c.overall_sentiment, 'value') else str(c.overall_sentiment)
            sentiment_counts[s_name] = sentiment_counts.get(s_name, 0) + 1

        # Real satisfaction score computed from real calls
        scores = [c.satisfaction_score for c in calls if getattr(c, 'satisfaction_score', None) is not None]
        satisfaction_rate = round(sum(scores) / len(scores), 1) if scores else 5.0

        # Real hourly distribution computed from real calls
        now = datetime.now(timezone.utc)
        hourly = []
        for i in range(6, -1, -1):
            h_time = now - timedelta(hours=i)
            label = h_time.strftime("%H:00")
            hour_calls = sum(
                1 for c in calls
                if getattr(c, 'started_at', None) and c.started_at.hour == h_time.hour and c.started_at.date() == h_time.date()
            )
            hourly.append({
                "time": label,
                "total": hour_calls,
                "ai_handled": hour_calls,
                "operator_handled": 0
            })

        return AnalyticsSummary(
            total_calls_today=total,
            ai_resolved_percentage=100.0 if total > 0 else 0.0,
            avg_call_duration_seconds=avg_dur,
            active_calls_count=active_count,
            waiting_operator_count=0,
            satisfaction_rate=satisfaction_rate,
            topic_distribution=topic_counts,
            sentiment_distribution=sentiment_counts,
            hourly_call_volume=hourly
        )

    # Legacy stubs to prevent any unexpected import or method crash
    def get_all_operators(self) -> list:
        return []

    def get_operator(self, op_id: str):
        return None

    def get_waiting_queue_length(self) -> int:
        return 0

    def purge_all_calls(self) -> int:
        """
        Purges all calls from in-memory cache and deletes persisted files in saved_calls_dir.
        Returns the number of purged calls.
        """
        count = len(self._calls)
        self._calls.clear()
        if self.saved_calls_dir.exists():
            for f in self.saved_calls_dir.glob("*.json"):
                try:
                    f.unlink()
                except Exception:
                    pass
        return count


call_manager = CallManager()
