import time
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm_orchestrator import llm_orchestrator
from app.services.knowledge_base import get_complete_legal_context

router = APIRouter(prefix="/chat", tags=["AI Chat"])

class ChatMessageRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = None

class ChatMessageResponse(BaseModel):
    response: str
    provider: str
    latency_ms: float
    citations: List[Dict[str, Any]]
    in_scope: bool

@router.post("", response_model=ChatMessageResponse)
async def send_chat_message(request: ChatMessageRequest):
    """
    Direct, ultra-fast AI text chat grounded in official education laws.
    Prioritizes fastest LLM: Cerebras -> Groq (0.35s) -> Cloudflare -> Gemini.
    """
    clean_text = request.message.strip() if request.message else ""
    if not clean_text:
        raise HTTPException(status_code=400, detail="Savol matni bo'sh bo'lishi mumkin emas")

    t0 = time.perf_counter()
    legal_ctx = get_complete_legal_context(clean_text, max_faqs=3, max_articles=2)
    response_text, provider = await llm_orchestrator.generate_response(
        user_text=clean_text,
        conversation_history=request.history,
        legal_context=legal_ctx,
        prioritize_fastest=True
    )
    t1 = time.perf_counter()

    citations = []
    for faq in legal_ctx.get("faqs", []):
        citations.append({
            "title": faq.get("question"),
            "legal_basis": faq.get("legal_basis"),
            "chapter": faq.get("chapter_title")
        })
    for art in legal_ctx.get("articles", []):
        citations.append({
            "title": art.get("title"),
            "legal_basis": art.get("doc_title"),
            "chapter": "Normativ-huquqiy baza"
        })

    return ChatMessageResponse(
        response=response_text,
        provider=provider,
        latency_ms=round((t1 - t0) * 1000, 1),
        citations=citations[:3],
        in_scope=legal_ctx.get("in_scope", True)
    )
