from typing import List, Optional
from fastapi import APIRouter, Query
from app.models.schemas import KnowledgeItem
from app.services.knowledge_base import MINISTRY_KNOWLEDGE_BASE, search_knowledge_base

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

@router.get("", response_model=List[KnowledgeItem])
def list_knowledge_items():
    return MINISTRY_KNOWLEDGE_BASE

@router.get("/search", response_model=List[KnowledgeItem])
def search_items(q: str = Query(..., min_length=1, description="Qidiruv so'zi")):
    return search_knowledge_base(q, limit=5)
