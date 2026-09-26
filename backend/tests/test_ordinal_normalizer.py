import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from app.services.uzbek_text_normalizer import (
    number_to_uzbek_ordinal,
    normalize_modda_numbers,
    normalize_text_for_tts
)

def test_number_to_uzbek_ordinal_hardcoded_and_dynamic():
    assert number_to_uzbek_ordinal(1) == "birinchi"
    assert number_to_uzbek_ordinal(2) == "ikkinchi"
    assert number_to_uzbek_ordinal(3) == "uchinchi"
    assert number_to_uzbek_ordinal(4) == "to'rtinchi"
    assert number_to_uzbek_ordinal(5) == "beshinchi"
    assert number_to_uzbek_ordinal(10) == "o'ninchi"
    assert number_to_uzbek_ordinal(44) == "qirq to'rtinchi"
    assert number_to_uzbek_ordinal(50) == "elliginchi"

def test_normalize_modda_numbers_and_chi_patterns():
    assert normalize_modda_numbers("1-chi sinf") == "birinchi sinf"
    assert normalize_modda_numbers("2-chi bosqich") == "ikkinchi bosqich"
    assert normalize_modda_numbers("3chi qism") == "uchinchi qism"
    assert normalize_modda_numbers("1-moddasi") == "birinchi moddasi"
    assert normalize_modda_numbers("44-modda") == "qirq to'rtinchi modda"
    assert normalize_modda_numbers("50-moddasi 2-qismi") == "elliginchi moddasi ikkinchi qismi"

def test_normalize_text_for_tts_full():
    res = normalize_text_for_tts("Konstitutsiyaning 1-moddasi va 1-chi sinf o'quvchisi 44-modda bo'yicha")
    assert "birinchi moddasi" in res
    assert "birinchi sinf" in res
    assert "qirq to'rtinchi modda" in res
    assert "*" not in res
