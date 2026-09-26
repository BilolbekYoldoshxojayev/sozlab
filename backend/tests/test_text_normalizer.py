import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from app.services.uzbek_text_normalizer import (
    number_to_uzbek_cardinal,
    number_to_uzbek_ordinal,
    normalize_law_citations,
    normalize_percentages,
    normalize_abbreviations,
    normalize_modda_numbers,
    strip_markdown_symbols,
    normalize_text_for_tts,
)
from app.services.llm_orchestrator import llm_orchestrator
from app.services.ai_dialog import dialog_manager


def test_cardinal_numbers_range():
    assert number_to_uzbek_cardinal(0) == "nol"
    assert number_to_uzbek_cardinal(-5) == "minus besh"
    assert number_to_uzbek_cardinal(1) == "bir"
    assert number_to_uzbek_cardinal(10) == "o'n"
    assert number_to_uzbek_cardinal(15) == "o'n besh"
    assert number_to_uzbek_cardinal(44) == "qirq to'rt"
    assert number_to_uzbek_cardinal(100) == "yuz"
    assert number_to_uzbek_cardinal(527) == "besh yuz yigirma yetti"
    assert number_to_uzbek_cardinal(1006) == "bir ming olti"
    assert number_to_uzbek_cardinal(1007) == "bir ming yetti"
    assert number_to_uzbek_cardinal(2024) == "ikki ming yigirma to'rt"
    assert number_to_uzbek_cardinal(1_000_000) == "bir million"
    assert number_to_uzbek_cardinal(5_000_000) == "besh million"


def test_ordinal_numbers():
    assert number_to_uzbek_ordinal(1) == "birinchi"
    assert number_to_uzbek_ordinal(81) == "sakson birinchi"
    assert number_to_uzbek_ordinal(527) == "besh yuz yigirma yettinchi"
    assert number_to_uzbek_ordinal(637) == "olti yuz o'ttiz yettinchi"
    assert number_to_uzbek_ordinal(901) == "to'qqiz yuz birinchi"


def test_normalize_law_citations():
    # VMQ
    res_vmq = normalize_law_citations("VMQ-527 bo'yicha imtiyozlar")
    assert "Vazirlar Mahkamasining besh yuz yigirma yettinchi qarori" in res_vmq

    res_vmq_ga = normalize_law_citations("VMQ-527ga binoan")
    assert "Vazirlar Mahkamasining besh yuz yigirma yettinchi qaroriga" in res_vmq_ga

    res_vmq_qaror = normalize_law_citations("VMQ-527 qaroriga muvofiq")
    assert "Vazirlar Mahkamasining besh yuz yigirma yettinchi qaroriga" in res_vmq_qaror

    # PF
    res_pf = normalize_law_citations("PF-81 bilan tasdiqlangan")
    assert "Prezidentning sakson birinchi farmoni" in res_pf

    res_pf_ga = normalize_law_citations("PF-81 farmoniga muvofiq")
    assert "Prezidentning sakson birinchi farmoniga" in res_pf_ga

    # PQ
    res_pq = normalize_law_citations("PQ-140 qaroriga ko'ra")
    assert "Prezidentning" in res_pq and "qaroriga" in res_pq

    # O'RQ
    res_orq = normalize_law_citations("O'RQ-637 qonuniga binoan")
    assert "O'zbekiston Respublikasining olti yuz o'ttiz yettinchi qonuni" in res_orq

    res_orq2 = normalize_law_citations("ORQ-901 qonuniga asosan")
    assert "O'zbekiston Respublikasining to'qqiz yuz birinchi qonuni" in res_orq2


def test_normalize_percentages():
    assert "nol foiz" in normalize_percentages("0%")
    assert "yuz foiz" in normalize_percentages("100%")
    assert "ellik foiz" in normalize_percentages("50%")
    assert "ellik foiz" in normalize_percentages("50 foiz")
    assert "ellik foizga" in normalize_percentages("50 foizga")
    assert "to'rt foiz" in normalize_percentages("4%")


def test_normalize_abbreviations():
    assert "ji-pi-ey" in normalize_abbreviations("Talabaning GPAsi 3.0")
    assert "oliy ta'lim muassasasi" in normalize_abbreviations("OTM rektori")
    assert "oliy ta'lim muassasasiga" in normalize_abbreviations("OTMga hujjat topshirish")
    assert "oliy ta'lim muassasalari" in normalize_abbreviations("Barcha OTMlar ro'yxati")
    assert "talabalar turar joyi" in normalize_abbreviations("TTJ arizasi")
    assert "talabalar turar joyiga" in normalize_abbreviations("TTJga joylashish")
    assert "xemis" in normalize_abbreviations("HEMIS tizimi")
    assert "bir ming olti" in normalize_abbreviations("1006 ishonch telefoni")
    assert "bir ming yetti" in normalize_abbreviations("1007 raqamiga")
    assert "may gov uz" in normalize_abbreviations("my.gov.uz portali")


def test_strip_markdown():
    clean = strip_markdown_symbols("**Muhim:** #1-sonli [qaror] `kod`...")
    assert "*" not in clean
    assert "#" not in clean
    assert "[" not in clean
    assert "]" not in clean
    assert "`" not in clean
    assert "..." not in clean


def test_normalize_text_for_tts_dispatch_contract():
    # Exact dispatch assertions
    assert "nol foiz" in normalize_text_for_tts("0%")
    assert "besh yuz yigirma yettinchi qarori" in normalize_text_for_tts("VMQ-527")
    assert "sakson birinchi farmoni" in normalize_text_for_tts("PF-81")
    assert "to'rt qismga" in normalize_text_for_tts("4 qismga")
    assert "ji-pi-ey" in normalize_text_for_tts("GPA")


def test_date_and_order_word_ordinals():
    # 31-dekabriga and all date/order words must be normalized with 'chi' / 'inchi'
    assert "o'ttiz birinchi dekabriga" in normalize_text_for_tts("31-dekabriga")
    assert "o'ttiz birinchi dekabrgacha" in normalize_text_for_tts("31-dekabrgacha")
    assert "o'ttiz birinchi dekabrda" in normalize_text_for_tts("31 dekabrda")
    assert "birinchi sentabr" in normalize_text_for_tts("1-sentabr")
    assert "birinchi sentabrdan" in normalize_text_for_tts("2024-yil 1-sentabrdan")
    assert "yigirma beshinchi may" in normalize_text_for_tts("25-may kuni")


def test_llm_orchestrator_speech_ready_instruction():
    ctx = {"formatted_context": "VMQ-527: Ta'lim krediti"}
    instruction = llm_orchestrator.build_system_instruction(ctx)
    assert "NUTQQA TAYYORLIK VA OVOZLI IXCHAMLIK" in instruction
    assert "BARCHA RAQAMLAR VA QONUNLARNI SO'Z BILAN YOZISH" in instruction
    assert "nol foiz" in instruction
    assert "besh yuz yigirma yettinchi qarori" in instruction
    assert "2-3 ta qisqa" in instruction


def test_ai_dialog_clean_rule_based_response_no_ellipses():
    mock_ctx = {
        "in_scope": True,
        "faqs": [{
            "question": "Ta'lim krediti kimlarga beriladi?",
            "short_answer": "Xotin-qizlarga 0% foizsiz ta'lim krediti beriladi.",
            "full_answer": "Vazirlar Mahkamasining qaroriga ko'ra ta'lim krediti barcha xotin-qizlarga foizsiz taqdim etiladi va o'qish tugaganidan so'ng qaytariladi.",
            "legal_basis": "VMQ-527"
        }]
    }
    resp = dialog_manager._generate_rule_based_response("kredit", mock_ctx)
    assert "..." not in resp
    assert "VMQ-527ga binoan: Xotin-qizlarga 0% foizsiz ta'lim krediti beriladi." == resp
