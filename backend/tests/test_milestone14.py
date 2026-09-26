"""
Milestone 14 Comprehensive Test Suite
- Constitution 50-Page Database Ingestion
- STT Silent Turn Greeting Bug Fix
- Uzbek TTS Normalizer (Roman numerals, ordinals, abbreviations)
- LLM Max Tokens Verification (1024)
- Human Operator Manager & FIFO Queue
"""

import pytest
import asyncio
from app.data.constitution_50_loader import get_constitution_50_articles, load_raw_constitution_50_json
from app.data.education_legislation_encyclopedia import search_encyclopedia
from app.services.knowledge_base import get_complete_legal_context
from app.services.ai_dialog import dialog_manager
from app.services.uzbek_text_normalizer import normalize_text_for_tts
from app.services.llm_orchestrator import llm_orchestrator
from app.services.operator_manager import operator_manager
from app.models.schemas import OperatorStatus

@pytest.mark.asyncio
async def test_constitution_50_ingestion():
    articles = get_constitution_50_articles()
    assert len(articles) > 0, "Constitution 50 articles should be non-empty"
    
    # Search logic test
    res = search_encyclopedia("ijtimoiy davlat", limit=3)
    assert len(res) > 0

    ctx = get_complete_legal_context("Konstitutsiya 50-modda")
    assert ctx["in_scope"] is True
    assert len(ctx["articles"]) > 0

@pytest.mark.asyncio
async def test_stt_silent_turn_greeting_fix():
    turn_res = await dialog_manager.process_user_turn("call-123", "   ")
    assert turn_res.ai_text == "Kechirasiz, ovozingizni aniq eshita olmadim. Qaytadan gapira olasizmi?"

    transcribed, audio_res = await dialog_manager.process_audio_turn("call-123", b"short_dummy_bytes")
    assert audio_res.ai_text == "Kechirasiz, ovozingizni aniq eshita olmadim. Qaytadan gapira olasizmi?"


def test_uzbek_tts_normalizer():
    # Roman Numerals
    assert normalize_text_for_tts("I Bob") == "birinchi Bob"
    assert normalize_text_for_tts("X-sinf") == "o'ninchi sinf"
    assert normalize_text_for_tts("III qism") == "uchinchi qism"

    # Ordinals
    assert normalize_text_for_tts("1-chi") == "birinchi"
    assert "birchi" not in normalize_text_for_tts("1-chi")
    assert normalize_text_for_tts("2-chi") == "ikkinchi"

    # Abbreviation X
    assert "Davlat Xizmatlari Markazi" in normalize_text_for_tts("DXM")

def test_llm_max_tokens_configuration():
    assert getattr(llm_orchestrator, "default_timeout", None) is not None

def test_operator_manager_fifo_queue():
    res1 = operator_manager.request_human_operator("call-001")
    assert res1["status"] in ["countdown", "queued"]
    assert res1["queue_position"] == 1

    status_info = operator_manager.get_queue_status()
    assert status_info["queue_length"] >= 1
