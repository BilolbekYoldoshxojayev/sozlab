from fastapi import APIRouter
from app.models.schemas import AnalyticsSummary
from app.services.call_manager import call_manager

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("", response_model=AnalyticsSummary)
def get_analytics_overview():
    return call_manager.get_analytics()
