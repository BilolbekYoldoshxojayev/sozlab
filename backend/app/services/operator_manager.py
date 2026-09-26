"""
SözLab Human Operator Manager & FIFO Queue Service
Manages:
1. operator_fifo_queue (FIFO queue of citizen call IDs)
2. Operator state transitions: AVAILABLE, BUSY, COUNTDOWN, OFFLINE
3. 3-second pre-call countdown events for operators
"""

import asyncio
import collections
import logging
from typing import Dict, Any, List, Optional
from app.models.schemas import OperatorStatus, OperatorRecord

logger = logging.getLogger(__name__)

class OperatorManager:
    def __init__(self):
        self.operator_fifo_queue: collections.deque = collections.deque()
        self.operators: Dict[str, OperatorRecord] = {
            "op-1": OperatorRecord(id="op-1", name="Operator Dilshod", status=OperatorStatus.AVAILABLE),
            "op-2": OperatorRecord(id="op-2", name="Operator Malika", status=OperatorStatus.AVAILABLE),
            "op-3": OperatorRecord(id="op-3", name="Operator Shahnoza", status=OperatorStatus.OFFLINE),
        }

    def request_human_operator(self, call_id: str) -> Dict[str, Any]:
        """
        Adds call_id to FIFO queue and assigns available operator if present.
        """
        if call_id not in self.operator_fifo_queue:
            self.operator_fifo_queue.append(call_id)

        queue_position = list(self.operator_fifo_queue).index(call_id) + 1

        # Check for AVAILABLE operator
        available_op = next((op for op in self.operators.values() if op.status == OperatorStatus.AVAILABLE), None)

        if available_op:
            # Transition operator to COUNTDOWN
            available_op.status = OperatorStatus.COUNTDOWN
            available_op.current_call_id = call_id

            return {
                "status": "countdown",
                "call_id": call_id,
                "operator_id": available_op.id,
                "operator_name": available_op.name,
                "queue_position": 1,
                "countdown_seconds": 3,
                "message": f"{available_op.name} bilan bog'lanmoqda... 3 soniya tayyorgarlik."
            }

        return {
            "status": "queued",
            "call_id": call_id,
            "queue_position": queue_position,
            "message": f"Barcha operatorlar band. Siz navbatda {queue_position}-o'rindasiz."
        }

    def set_operator_status(self, operator_id: str, status: OperatorStatus) -> Optional[OperatorRecord]:
        op = self.operators.get(operator_id)
        if not op:
            return None
        op.status = status
        if status == OperatorStatus.AVAILABLE:
            op.current_call_id = None
        return op

    def get_all_operators(self) -> List[OperatorRecord]:
        return list(self.operators.values())

    def get_queue_status(self) -> Dict[str, Any]:
        return {
            "queue_length": len(self.operator_fifo_queue),
            "queued_call_ids": list(self.operator_fifo_queue),
            "available_operators_count": sum(1 for op in self.operators.values() if op.status == OperatorStatus.AVAILABLE)
        }

operator_manager = OperatorManager()
