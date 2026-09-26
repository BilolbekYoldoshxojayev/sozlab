"""
Unit & Integration Tests for SözLab Strict Legal Guardrails & Ingestion of 2 PDFs:
1. In-Scope Queries: Must cite exact laws, articles, and decrees.
2. Out-of-Scope Queries: Must strictly refuse without hallucination.
"""

import pytest
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.knowledge_base import (
    is_in_educational_scope,
    get_complete_legal_context,
    OUT_OF_SCOPE_REFUSAL
)
from app.services.ai_dialog import dialog_manager
from app.data.education_faq_50 import FAQ_50_ITEMS, search_faq_items
from app.data.education_legislation_encyclopedia import LEGAL_ENCYCLOPEDIA_ARTICLES, search_encyclopedia

def test_scope_detection_in_scope():
    in_scope_queries = [
        "Maktabda o'quvchilardan fond puli yig'ish mumkinmi?",
        "O'qituvchini majburiy mehnatga jalb qilish taqiqlanganmi?",
        "Magistraturada o'qiyotgan xotin-qizlar kontrakti to'lab beriladimi?",
        "1-sinfga qabul yoshi necha yosh?",
        "GPA reytingi bo'yicha grant qayta taqsimlanadimi?",
        "Talabalar turar joyiga my.gov.uz orqali ariza berish",
        "Talabalarga 50 foiz ijara kompensatsiyasi",
        "Pedagoglar uchun yillik ta'til 56 kunmi?",
        "Xususiy maktab ochish uchun litsenziya qanday olinadi?",
        "Umumta'lim maktablarida 1 stavka necha soat?"
    ]
    for q in in_scope_queries:
        assert is_in_educational_scope(q) is True, f"Failed for query: {q}"

def test_scope_detection_out_of_scope():
    out_of_scope_queries = [
        "Bugun Toshkentda ob-havo qanday bo'ladi?",
        "Osh pishirish retseptini aytib bering",
        "Futbol bo'yicha Chempionlar ligasini kim yutadi?",
        "Bugun dollar kursi qancha bo'ldi?",
        "Menga bitta yaxshi latifa aytib ber",
        "Avtomobil haydovchilik guvohnomasini qanday olaman?",
        "Bosh og'rig'iga qanday dori ichish kerak?"
    ]
    for q in out_of_scope_queries:
        assert is_in_educational_scope(q) is False, f"Query should be out of scope: {q}"

def test_legal_context_citations():
    # Test Question 2: Pul yig'ish
    ctx_pul = get_complete_legal_context("Maktabda pul yig'ish qonuniymi?")
    assert ctx_pul["in_scope"] is True
    assert len(ctx_pul["faqs"]) > 0
    top_faq = ctx_pul["faqs"][0]
    assert top_faq["id"] == 2
    assert "50-modda" in top_faq["legal_basis"]

    # Test Question 9: Pedagog majburiy mehnati
    ctx_pedagog = get_complete_legal_context("O'qituvchini ko'cha tozalashga majburlash mumkinmi?")
    assert ctx_pedagog["in_scope"] is True
    assert any("51" in str(f["legal_basis"]) or "52" in str(f["legal_basis"]) or "901" in str(f["legal_basis"]) for f in ctx_pedagog["faqs"])

    # Test Question 20: Xotin-qizlar magistraturasi
    ctx_magistr = get_complete_legal_context("Magistratura xotin-qizlar kontrakti qoplanadimi?")
    assert ctx_magistr["in_scope"] is True
    assert any("447" in str(f["legal_basis"]) for f in ctx_magistr["faqs"])

@pytest.mark.asyncio
async def test_ai_dialog_strict_refusal_on_out_of_scope():
    res = await dialog_manager.process_user_turn("test-call-1", "Bugun Toshkentda ob-havo qanday bo'ladi?")
    assert res.intent == "Doiradan_Tashqari_Rad"
    assert OUT_OF_SCOPE_REFUSAL in res.ai_text
    assert "rasmiy savollarga javob bera olaman" in res.ai_text

@pytest.mark.asyncio
async def test_ai_dialog_answers_with_legal_citation_for_pul_yigish():
    res = await dialog_manager.process_user_turn("test-call-2", "Maktabda remontga pul yig'ish mumkinmi?")
    assert res.intent != "Doiradan_Tashqari_Rad"
    # Response must mention prohibition and legal basis
    t_low = res.ai_text.lower()
    assert "taqiq" in t_low or "mumkin emas" in t_low or "noqonuniy" in t_low or "bepul" in t_low or "qonun" in t_low
