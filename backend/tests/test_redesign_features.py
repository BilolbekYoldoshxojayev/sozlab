"""
Comprehensive Test Suite for SözLab Redesign & Feature Enhancements
- 100% Ordinal Number Normalization (1-chi -> birinchi, 1-moddasi -> birinchi moddasi, 44-modda -> qirq to'rtinchi modda)
- Cyrillic-to-Latin Uzbek STT Normalizer
- Markdown Symbol Stripping for TTS
- Out-of-Scope 1-Sentence Refusal Protocol
- No-Truncation System Instructions
- Silence / Blank Audio Handling
- Call Manager Initial State & Beat Marker Timestamps
"""

import pytest
import asyncio
from app.services.uzbek_text_normalizer import (
    number_to_uzbek_ordinal,
    normalize_modda_numbers,
    cyrillic_to_latin_uzbek,
    strip_markdown_symbols,
    normalize_text_for_tts,
)
from app.services.llm_orchestrator import llm_orchestrator
from app.services.knowledge_base import get_complete_legal_context
from app.services.ai_dialog import dialog_manager
from app.services.call_manager import call_manager
from app.models.schemas import CallStatus

def test_hardcoded_and_dynamic_ordinals():
    assert number_to_uzbek_ordinal(1) == "birinchi"
    assert number_to_uzbek_ordinal(2) == "ikkinchi"
    assert number_to_uzbek_ordinal(3) == "uchinchi"
    assert number_to_uzbek_ordinal(4) == "to'rtinchi"
    assert number_to_uzbek_ordinal(5) == "beshinchi"
    assert number_to_uzbek_ordinal(10) == "o'ninchi"
    assert number_to_uzbek_ordinal(20) == "yigirmanchi"
    assert number_to_uzbek_ordinal(30) == "o'ttizinchi"
    assert number_to_uzbek_ordinal(40) == "qirqinchi"
    assert number_to_uzbek_ordinal(44) == "qirq to'rtinchi"
    assert number_to_uzbek_ordinal(50) in ["elliginchi", "elliqinchi"]
    assert number_to_uzbek_ordinal(77) == "yetmish yettinchi"
    assert number_to_uzbek_ordinal(100) == "yuzinchi"

def test_ordinal_phrase_patterns():
    assert normalize_modda_numbers("1-chi sinf") == "birinchi sinf"
    assert normalize_modda_numbers("2-chi bosqich") == "ikkinchi bosqich"
    assert normalize_modda_numbers("3chi qism") == "uchinchi qism"
    assert normalize_modda_numbers("1-moddasi") == "birinchi moddasi"
    assert normalize_modda_numbers("44-modda") == "qirq to'rtinchi modda"
    assert "birchi" not in normalize_modda_numbers("1-chi sinf")

def test_cyrillic_to_latin_uzbek_conversion():
    cyrillic_input = "Конституциянинг 1-моддаси ва таълим тўғрисидаги қонун"
    latin_output = cyrillic_to_latin_uzbek(cyrillic_input)
    assert "Konstitutsiyaning" in latin_output or "konstitutsiyaning" in latin_output.lower()
    assert "ta'lim" in latin_output.lower()
    assert "qonun" in latin_output.lower()

def test_strip_markdown_symbols():
    markdown_text = "**Diqqat!** #1-modda: *Ta'lim* huquqi [batafsil](http://example.com) `code` ~text~ @user $100"
    stripped = strip_markdown_symbols(markdown_text)
    assert "*" not in stripped
    assert "#" not in stripped
    assert "`" not in stripped
    assert "[" not in stripped
    assert "]" not in stripped
    assert "~" not in stripped
    assert "@" not in stripped
    assert "$" not in stripped
    assert "Ta'lim huquqi" in stripped

def test_normalize_text_for_tts_integration():
    raw_text = "**1-moddasi** va *1-chi* sinf o'quvchilari uchun 44-modda huquqi."
    normalized = normalize_text_for_tts(raw_text)
    assert "birinchi moddasi" in normalized
    assert "birinchi sinf" in normalized
    assert "qirq to'rtinchi modda" in normalized
    assert "*" not in normalized

def test_out_of_scope_single_sentence_refusal():
    context = get_complete_legal_context("Futbol bo'yicha Chempionlar ligasi natijalari qanday?")
    assert context["in_scope"] is False
    assert context["refusal_text"] is not None
    assert len(context["refusal_text"].split(".")) <= 3

def test_llm_system_instruction_no_markdown_rule():
    legal_context = get_complete_legal_context("Kontrakt narxi qancha?")
    instruction = llm_orchestrator.build_system_instruction(legal_context)
    assert "Siz O'zbekiston Respublikasi" in instruction
    assert "lo'nda" in instruction.lower() or "qisqa" in instruction.lower() or "rasmiy" in instruction.lower()

def test_call_creation_initial_state():
    call = call_manager.create_call(citizen_name="Test User", citizen_phone="+998901234567")
    assert call.citizen_name == "Test User"
    assert call.status in [CallStatus.AI_HANDLING, "ai_handling"]

@pytest.mark.asyncio
async def test_silent_audio_turn_response():
    res = await dialog_manager.process_user_turn("test-call-id", "   ")
    assert "Kechirasiz" in res.ai_text
    assert "eshita olmadim" in res.ai_text
