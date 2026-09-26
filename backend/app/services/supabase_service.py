import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx

from app.core.config import settings
from app.models.schemas import CallRecord, SpeakerRole

logger = logging.getLogger("sozlab.supabase")

class SupabaseService:
    def __init__(self):
        self.url = settings.SUPABASE_URL.rstrip("/") if settings.SUPABASE_URL else ""
        self.key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY or ""
        self.cache_dir = settings.AUDIO_CACHE_DIR.parent
        self.offline_file = self.cache_dir / "supabase_offline_archive.jsonl"
        self._ensure_cache()

    def _ensure_cache(self):
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create cache dir for Supabase offline storage: {e}")

    def is_configured(self) -> bool:
        return bool(self.url and self.key and "supabase.co" in self.url)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }

    def _save_offline(self, call_data: Dict[str, Any], transcripts: List[Dict[str, Any]]):
        """Graceful degradation: save call locally if Supabase is unreachable or unconfigured."""
        try:
            payload = {
                "archived_locally_at": datetime.now(timezone.utc).isoformat(),
                "call": call_data,
                "transcripts": transcripts
            }
            with open(self.offline_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
            logger.info(f"Saved call {call_data.get('id')} to local offline archive: {self.offline_file}")
        except Exception as e:
            logger.error(f"Failed to write to local offline archive: {e}")

    async def archive_call(self, call_data: Dict[str, Any], transcripts: List[Dict[str, Any]]) -> bool:
        """
        Archives call record and associated transcript entries to Supabase.
        Falls back gracefully to local offline storage if unconfigured or error.
        """
        if not self.is_configured():
            logger.info("Supabase credentials not configured, falling back to offline archive.")
            self._save_offline(call_data, transcripts)
            return False

        headers = self._get_headers()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. Upsert into calls table
                calls_endpoint = f"{self.url}/rest/v1/calls"
                res_call = await client.post(calls_endpoint, headers=headers, json=[call_data])
                
                if res_call.status_code not in (200, 201, 204):
                    logger.warning(
                        f"Supabase calls insert failed (status {res_call.status_code}): {res_call.text}. Saving offline."
                    )
                    self._save_offline(call_data, transcripts)
                    return False

                # 2. Insert transcripts if present
                if transcripts:
                    transcripts_endpoint = f"{self.url}/rest/v1/call_transcripts"
                    res_trans = await client.post(transcripts_endpoint, headers=headers, json=transcripts)
                    if res_trans.status_code not in (200, 201, 204):
                        logger.warning(
                            f"Supabase call_transcripts insert failed (status {res_trans.status_code}): {res_trans.text}"
                        )

            logger.info(f"Successfully archived call {call_data.get('id')} to Supabase.")
            return True

        except Exception as e:
            logger.warning(f"Network error archiving to Supabase ({e}), falling back to offline cache.")
            self._save_offline(call_data, transcripts)
            return False

    async def archive_call_record(self, call: CallRecord) -> bool:
        """High-level helper to archive a CallRecord object."""
        started_iso = call.started_at.isoformat() if hasattr(call.started_at, "isoformat") else str(call.started_at)
        ended_iso = call.ended_at.isoformat() if call.ended_at and hasattr(call.ended_at, "isoformat") else None

        topic_val = call.primary_topic.value if hasattr(call.primary_topic, "value") else str(call.primary_topic or "BOSHQA")
        sentiment_val = call.overall_sentiment.value if hasattr(call.overall_sentiment, "value") else str(call.overall_sentiment or "NEUTRAL")

        call_data = {
            "id": call.id,
            "citizen_name": call.citizen_name or "Fuqaro",
            "citizen_phone": call.citizen_phone or "+998 90 000-00-00",
            "operator_name": call.assigned_operator,
            "status": call.status.value if hasattr(call.status, "value") else str(call.status),
            "primary_topic": topic_val,
            "sentiment": sentiment_val,
            "duration_seconds": call.duration_seconds,
            "ai_summary": call.resolution_summary,
            "resolved_by_ai": call.resolved_by_ai,
            "started_at": started_iso,
            "ended_at": ended_iso
        }

        transcripts = []
        for msg in call.messages:
            msg_role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            speaker_role = "CITIZEN" if msg_role == "citizen" else ("OPERATOR" if msg_role == "operator" else ("AI" if msg_role == "ai" else "SYSTEM"))
            speaker_name = call.citizen_name if speaker_role == "CITIZEN" else (call.assigned_operator if speaker_role == "OPERATOR" else "SözLab AI")

            transcripts.append({
                "call_id": call.id,
                "speaker_role": speaker_role,
                "speaker_name": speaker_name,
                "text": msg.text,
                "timestamp_offset_seconds": 0.0
            })

        return await self.archive_call(call_data, transcripts)

    async def get_recent_calls(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent calls from Supabase if configured."""
        if not self.is_configured():
            return []
        try:
            headers = self._get_headers()
            url = f"{self.url}/rest/v1/calls?order=started_at.desc&limit={limit}"
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    return res.json()
        except Exception as e:
            logger.warning(f"Error fetching calls from Supabase: {e}")
    async def purge_all_records(self) -> Dict[str, Any]:
        """
        Purges all call records and transcripts from Supabase PostgreSQL tables and local offline cache.
        """
        result = {"supabase_purged": False, "offline_cache_purged": False, "detail": ""}

        # Clear local offline file
        try:
            if self.offline_file.exists():
                self.offline_file.unlink()
                result["offline_cache_purged"] = True
                logger.info(f"Purged local offline archive: {self.offline_file}")
        except Exception as e:
            logger.error(f"Failed to purge offline file: {e}")

        if not self.is_configured():
            result["detail"] = "Supabase unconfigured; offline cache cleared."
            return result

        headers = self._get_headers()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. Try RPC procedure first if configured
                rpc_endpoint = f"{self.url}/rest/v1/rpc/purge_all_call_records"
                try:
                    res_rpc = await client.post(rpc_endpoint, headers=headers, json={})
                    if res_rpc.status_code in (200, 204):
                        result["supabase_purged"] = True
                        result["detail"] = "Successfully purged via RPC procedure."
                        return result
                except Exception:
                    pass

                # 2. Direct PostgREST delete
                # Delete transcripts first (child)
                transcripts_url = f"{self.url}/rest/v1/call_transcripts?id=not.is.null"
                await client.delete(transcripts_url, headers=headers)

                # Delete calls (parent)
                calls_url = f"{self.url}/rest/v1/calls?id=not.is.null"
                res_calls = await client.delete(calls_url, headers=headers)
                if res_calls.status_code in (200, 204):
                    result["supabase_purged"] = True
                    result["detail"] = "Successfully purged via REST delete."
                else:
                    result["detail"] = f"REST delete status: {res_calls.status_code}"
        except Exception as e:
            logger.warning(f"Error purging Supabase records: {e}")
            result["detail"] = str(e)

        return result

supabase_service = SupabaseService()

