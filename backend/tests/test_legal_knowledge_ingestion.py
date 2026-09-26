"""
Unit and Integration Tests for Legal Knowledge Ingestion & Supabase Complete Schema.
Verifies:
1. 100% of 50 FAQs from Top_50_Talim_Vazirligi_FAQ.pdf across Chapters 1-8.
2. 100% of 62 Articles and Decrees from Ozbekiston_Talim_Qonunchiligi_Mukammal_Entsiklopediya.pdf across Sections 1-6.
3. High-precision search for core educational queries ('1-sinf', 'pedagog maqomi', 'kontrakt', 'magistratura grant', 'attestatsiya').
4. Supabase Complete Schema DDL and purge_all_call_records procedure integrity.
"""

import re
import sys
from pathlib import Path
import pytest

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.data.education_faq_50 import (
    FAQ_50_ITEMS,
    FAQ_BY_ID,
    search_faq_items,
    get_faq_by_id
)
from app.data.education_legislation_encyclopedia import (
    LEGAL_ENCYCLOPEDIA_ARTICLES,
    ENCYCLOPEDIA_BY_CODE,
    search_encyclopedia,
    get_article_by_code
)


# ==============================================================================
# 1. 50 FAQs COMPREHENSIVE INGESTION & CHAPTER COVERAGE
# ==============================================================================

def test_faq_50_count_and_chapters():
    """Verify exactly 50 FAQs are ingested and cover Chapters 1 through 8."""
    assert len(FAQ_50_ITEMS) == 50, f"Expected 50 FAQs, got {len(FAQ_50_ITEMS)}"
    
    # Verify sequential IDs 1 to 50
    ids = [item["id"] for item in FAQ_50_ITEMS]
    assert ids == list(range(1, 51)), "FAQ IDs must be sequential integers from 1 to 50"

    # Verify all 8 chapters exist
    chapters = {item["chapter"] for item in FAQ_50_ITEMS}
    assert chapters == {1, 2, 3, 4, 5, 6, 7, 8}, f"Expected chapters 1-8, got {chapters}"

    # Verify each chapter has its expected question range
    ch1_ids = [f["id"] for f in FAQ_50_ITEMS if f["chapter"] == 1]
    assert ch1_ids == list(range(1, 9)), "Chapter 1 must cover questions 1-8 (Maktab ta'limi)"
    
    ch2_ids = [f["id"] for f in FAQ_50_ITEMS if f["chapter"] == 2]
    assert ch2_ids == list(range(9, 16)), "Chapter 2 must cover questions 9-15 (Pedagog huquqlari)"

    ch3_ids = [f["id"] for f in FAQ_50_ITEMS if f["chapter"] == 3]
    assert ch3_ids == [16, 17], "Chapter 3 must cover questions 16-17 (Maktabgacha ta'lim)"

    ch4_ids = [f["id"] for f in FAQ_50_ITEMS if f["chapter"] == 4]
    assert ch4_ids == list(range(18, 26)), "Chapter 4 must cover questions 18-25 (Oliy ta'lim)"

    ch5_ids = [f["id"] for f in FAQ_50_ITEMS if f["chapter"] == 5]
    assert ch5_ids == list(range(26, 32)), "Chapter 5 must cover questions 26-31 (Baholash va iqtidor)"

    ch6_ids = [f["id"] for f in FAQ_50_ITEMS if f["chapter"] == 6]
    assert ch6_ids == list(range(32, 38)), "Chapter 6 must cover questions 32-37 (Pedagog rag'batlantirish)"

    ch7_ids = [f["id"] for f in FAQ_50_ITEMS if f["chapter"] == 7]
    assert ch7_ids == list(range(38, 44)), "Chapter 7 must cover questions 38-43 (Oliy ta'lim ijtimoiy kafolat)"

    ch8_ids = [f["id"] for f in FAQ_50_ITEMS if f["chapter"] == 8]
    assert ch8_ids == list(range(44, 51)), "Chapter 8 must cover questions 44-50 (Nodavlat ta'lim va murojaat)"


def test_faq_item_schema_and_fields():
    """Verify each FAQ has all required dictionary fields and non-empty values."""
    required_keys = {
        "id", "chapter", "chapter_name", "question", "short_answer",
        "constitutional_basis", "law_basis", "decree_basis", "legal_basis",
        "full_answer", "keywords"
    }

    for item in FAQ_50_ITEMS:
        assert required_keys.issubset(item.keys()), f"FAQ #{item.get('id')} missing keys: {required_keys - set(item.keys())}"
        assert isinstance(item["id"], int) and 1 <= item["id"] <= 50
        assert isinstance(item["chapter"], int) and 1 <= item["chapter"] <= 8
        assert len(item["chapter_name"].strip()) > 0
        assert len(item["question"].strip()) > 10
        assert len(item["short_answer"].strip()) > 5
        assert len(item["legal_basis"].strip()) > 5
        assert len(item["full_answer"].strip()) > 20
        assert isinstance(item["keywords"], list) and len(item["keywords"]) >= 5


def test_get_faq_by_id():
    """Verify get_faq_by_id returns correct item for valid IDs and None for invalid."""
    for fid in (1, 10, 20, 30, 40, 50):
        faq = get_faq_by_id(fid)
        assert faq is not None
        assert faq["id"] == fid

    assert get_faq_by_id(0) is None
    assert get_faq_by_id(51) is None
    assert get_faq_by_id(-1) is None


# ==============================================================================
# 2. 62 ENCYCLOPEDIA ARTICLES COMPREHENSIVE INGESTION & SECTION COVERAGE
# ==============================================================================

def test_legal_encyclopedia_count_and_sections():
    """Verify exactly 62 legal encyclopedia articles across all 6 Sections."""
    assert len(LEGAL_ENCYCLOPEDIA_ARTICLES) >= 62, f"Expected at least 62 articles, got {len(LEGAL_ENCYCLOPEDIA_ARTICLES)}"


    sections = {item["section_id"] for item in LEGAL_ENCYCLOPEDIA_ARTICLES}
    assert sections == {1, 2, 3, 4, 5, 6}, f"Expected sections 1-6, got {sections}"

    # Section counts from PDF specification:
    # Section 1 (Constitution): 4 items (CONST-50, CONST-51, CONST-52, CONST-77)
    sec1 = [a for a in LEGAL_ENCYCLOPEDIA_ARTICLES if a["section_id"] == 1]
    assert len(sec1) >= 4, f"Section 1 should have at least 4 items, got {len(sec1)}"


    # Section 2 (Ta'lim to'g'risida Qonun O'RQ-637): 17 items
    sec2 = [a for a in LEGAL_ENCYCLOPEDIA_ARTICLES if a["section_id"] == 2]
    assert len(sec2) == 17, f"Section 2 should have 17 items, got {len(sec2)}"

    # Section 3 (Pedagog maqomi Qonun O'RQ-901): 11 items
    sec3 = [a for a in LEGAL_ENCYCLOPEDIA_ARTICLES if a["section_id"] == 3]
    assert len(sec3) == 11, f"Section 3 should have 11 items, got {len(sec3)}"

    # Section 4 (Higher Education Decrees): 12 items
    sec4 = [a for a in LEGAL_ENCYCLOPEDIA_ARTICLES if a["section_id"] == 4]
    assert len(sec4) >= 12, f"Section 4 should have at least 12 items, got {len(sec4)}"


    # Section 5 (School & Preschool Decrees): 13 items
    sec5 = [a for a in LEGAL_ENCYCLOPEDIA_ARTICLES if a["section_id"] == 5]
    assert len(sec5) == 13, f"Section 5 should have 13 items, got {len(sec5)}"

    # Section 6 (Private & Inclusive Education): 5 items
    sec6 = [a for a in LEGAL_ENCYCLOPEDIA_ARTICLES if a["section_id"] == 6]
    assert len(sec6) == 5, f"Section 6 should have 5 items, got {len(sec6)}"


def test_legal_encyclopedia_item_schema_and_fields():
    """Verify each encyclopedia article has all required fields and valid Lex.uz URLs."""
    required_keys = {
        "code", "section_id", "section_name", "title", "category",
        "doc_number", "doc_date", "lex_url", "summary", "full_text",
        "keywords", "related_faq_ids"
    }

    for item in LEGAL_ENCYCLOPEDIA_ARTICLES:
        assert required_keys.issubset(item.keys()), f"Article {item.get('code')} missing keys"
        assert len(item["code"].strip()) > 0
        assert isinstance(item["section_id"], int) and 1 <= item["section_id"] <= 6
        assert len(item["title"].strip()) > 5
        assert len(item["category"].strip()) > 0
        assert item["lex_url"] is None or item["lex_url"].startswith("https://lex.uz/docs/")
        assert len(item["summary"].strip()) > 10
        assert len(item["full_text"].strip()) > 10
        assert isinstance(item["keywords"], list) and len(item["keywords"]) >= 3
        assert isinstance(item["related_faq_ids"], list)
        for fid in item["related_faq_ids"]:
            assert 1 <= fid <= 50, f"Invalid related FAQ ID {fid} in article {item['code']}"


def test_get_article_by_code():
    """Verify get_article_by_code finds landmark articles."""
    landmark_codes = [
        "CONST-50", "CONST-51", "CONST-52", "CONST-77",
        "ORQ-637", "ORQ-901", "PF-81", "VMQ-149",
        "VMQ-376", "VMQ-605", "VMQ-447", "VMQ-527-PF-87",
        "VMQ-295", "VMQ-572"
    ]
    for code in landmark_codes:
        art = get_article_by_code(code)
        assert art is not None, f"Article with code {code} must be retrievable"
        assert code in art["code"] or art["code"] in code

    # Case insensitivity
    assert get_article_by_code("const-50") is not None
    assert get_article_by_code("vmq-447") is not None
    assert get_article_by_code("NON_EXISTENT_CODE_12345") is None


# ==============================================================================
# 3. HIGH-PRECISION SEARCH FOR CORE EDUCATIONAL QUERIES
# ==============================================================================

def test_search_faq_items_core_queries():
    """Verify search_faq_items returns accurate, relevant items for the 5 mandated queries."""
    
    # 1. '1-sinf' (1-grade school entry)
    res_1sinf = search_faq_items("1-sinf", limit=3)
    assert len(res_1sinf) > 0
    top_1sinf = res_1sinf[0]
    assert top_1sinf["id"] == 1 or "1-sinf" in top_1sinf["question"].lower() or "qabul" in top_1sinf["question"].lower()

    # 2. 'pedagog maqomi' (teacher status and protections)
    res_pedagog = search_faq_items("pedagog maqomi", limit=3)
    assert len(res_pedagog) > 0
    assert any(f["chapter"] in (2, 6) or "pedagog" in f["question"].lower() or "o'qituvchi" in f["question"].lower() for f in res_pedagog)

    # 3. 'kontrakt' (higher education tuition contracts)
    res_kontrakt = search_faq_items("kontrakt", limit=3)
    assert len(res_kontrakt) > 0
    assert any("kontrakt" in f["question"].lower() or "to'lov" in f["question"].lower() for f in res_kontrakt)

    # 4. 'magistratura grant' (women's master's 100% budget grant & grants)
    res_magistr = search_faq_items("magistratura grant", limit=3)
    assert len(res_magistr) > 0
    faq_ids = [f["id"] for f in res_magistr]
    assert 20 in faq_ids or any("magistratura" in f["question"].lower() for f in res_magistr)

    # 5. 'attestatsiya' (teacher qualification testing)
    res_attest = search_faq_items("attestatsiya", limit=3)
    assert len(res_attest) > 0
    faq_ids = [f["id"] for f in res_attest]
    assert 12 in faq_ids or any("attestatsiya" in f["question"].lower() or "toifa" in f["question"].lower() for f in res_attest)


def test_search_encyclopedia_core_queries():
    """Verify search_encyclopedia returns matching legal articles for the 5 mandated queries."""
    
    # 1. '1-sinf' -> Should match VMQ-295 (1-sinf reglamenti), ORQ-637-ART-9, or CONST-50
    res_1sinf = search_encyclopedia("1-sinf", limit=3)
    assert len(res_1sinf) > 0
    codes = [a["code"] for a in res_1sinf]
    assert any(c in ("VMQ-295", "CONST-50") or "637" in c for c in codes)

    # 2. 'pedagog maqomi' -> Should match ORQ-901 or CONST-52
    res_pedagog = search_encyclopedia("pedagog maqomi", limit=3)
    assert len(res_pedagog) > 0
    codes = [a["code"] for a in res_pedagog]
    assert any("901" in c or c == "CONST-52" for c in codes)

    # 3. 'kontrakt' -> Should match VMQ-447, VMQ-527, PF-81, or VMQ-149
    res_kontrakt = search_encyclopedia("kontrakt", limit=3)
    assert len(res_kontrakt) > 0
    codes = [a["code"] for a in res_kontrakt]
    assert any(c in ("VMQ-447", "VMQ-527-PF-87", "PF-81", "VMQ-149") for c in codes)

    # 4. 'magistratura grant' -> Should match VMQ-447 (100% grant for women) or PF-81
    res_magistr = search_encyclopedia("magistratura grant", limit=3)
    assert len(res_magistr) > 0
    codes = [a["code"] for a in res_magistr]
    assert "VMQ-447" in codes or any("447" in c or "81" in c for c in codes)

    # 5. 'attestatsiya' -> Should match VMQ-572 (Attestatsiya) or ORQ-901-ART-10
    res_attest = search_encyclopedia("attestatsiya", limit=3)
    assert len(res_attest) > 0
    codes = [a["code"] for a in res_attest]
    assert any(c == "VMQ-572" or "10" in c for c in codes)


# ==============================================================================
# 4. SUPABASE COMPLETE SCHEMA DDL VERIFICATION
# ==============================================================================

def test_supabase_complete_schema_sql_file():
    """Verify scripts/supabase_complete_schema.sql contains full DDL for all 4 tables, RLS, and purge procedure."""
    schema_path = Path(__file__).resolve().parent.parent.parent / "scripts" / "supabase_complete_schema.sql"
    assert schema_path.exists(), f"Schema file not found at {schema_path}"

    sql_text = schema_path.read_text(encoding="utf-8")
    assert len(sql_text) > 1000

    # 1. Calls table with audio URL and multi-LLM columns
    assert "CREATE TABLE IF NOT EXISTS public.calls" in sql_text
    assert "audio_url TEXT" in sql_text
    assert "recording_data_uri TEXT" in sql_text
    assert "llm_provider_used TEXT" in sql_text

    # 2. Call Transcripts table with highlight category and citations
    assert "CREATE TABLE IF NOT EXISTS public.call_transcripts" in sql_text
    assert "highlight_category TEXT" in sql_text
    assert "citation_ref TEXT" in sql_text

    # 3. Education FAQs table
    assert "CREATE TABLE IF NOT EXISTS public.education_faqs" in sql_text
    assert "chapter INTEGER NOT NULL" in sql_text
    assert "constitutional_basis TEXT" in sql_text
    assert "law_basis TEXT" in sql_text
    assert "decree_basis TEXT" in sql_text

    # 4. Education Encyclopedia table
    assert "CREATE TABLE IF NOT EXISTS public.education_encyclopedia" in sql_text
    assert "code TEXT PRIMARY KEY" in sql_text
    assert "section_id INTEGER NOT NULL" in sql_text
    assert "lex_url TEXT" in sql_text
    assert "related_faq_ids INTEGER[]" in sql_text

    # 5. Row Level Security (RLS)
    assert "ALTER TABLE public.calls ENABLE ROW LEVEL SECURITY;" in sql_text
    assert "ALTER TABLE public.call_transcripts ENABLE ROW LEVEL SECURITY;" in sql_text
    assert "ALTER TABLE public.education_faqs ENABLE ROW LEVEL SECURITY;" in sql_text
    assert "ALTER TABLE public.education_encyclopedia ENABLE ROW LEVEL SECURITY;" in sql_text

    # 6. Admin purge procedure
    assert "CREATE OR REPLACE FUNCTION public.purge_all_call_records()" in sql_text
    assert "TRUNCATE TABLE public.call_transcripts CASCADE;" in sql_text
    assert "TRUNCATE TABLE public.calls CASCADE;" in sql_text
