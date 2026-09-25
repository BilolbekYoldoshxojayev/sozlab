from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query
from app.models.schemas import KnowledgeItem
from app.services.knowledge_base import MINISTRY_KNOWLEDGE_BASE, search_knowledge_base
from app.data.education_faq_50 import FAQ_50_ITEMS, search_faq_items
from app.data.education_legislation_encyclopedia import LEGAL_ENCYCLOPEDIA_ARTICLES, search_encyclopedia

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

@router.get("", response_model=List[KnowledgeItem])
def list_knowledge_items():
    return MINISTRY_KNOWLEDGE_BASE

@router.get("/search", response_model=List[KnowledgeItem])
def search_items(q: str = Query(..., min_length=1, description="Qidiruv so'zi")):
    return search_knowledge_base(q, limit=5)

@router.get("/faqs-50")
def get_50_faqs(q: Optional[str] = Query(None, description="Filter 50 FAQs by search query")):
    if q and q.strip():
        return search_faq_items(q.strip(), limit=50)
    return FAQ_50_ITEMS

@router.get("/encyclopedia")
def get_encyclopedia(q: Optional[str] = Query(None, description="Filter legal articles")):
    if q and q.strip():
        return search_encyclopedia(q.strip(), limit=20)
    return LEGAL_ENCYCLOPEDIA_ARTICLES
