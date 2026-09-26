"""
SözLab Constitution 50-Page Database Loader
Ingests Ozbekiston_Konstitutsiyasi_Talim_Moddalari_50_Sahifa.json and extracts:
- All 9 chapters and 18 constitutional articles
- All 50 page contents (legal quotes, in-depth analyses, case studies, tables)
- Laws catalog & violation/penalty records (MJtK 197-5, MJtK 47, JK 148-2, etc.)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def _resolve_json_path() -> Optional[Path]:
    candidates = [
        Path("c:/dev/Projects/vazir-chat/Ozbekiston_Konstitutsiyasi_Talim_Moddalari_50_Sahifa.json"),
        Path(__file__).parents[3] / "Ozbekiston_Konstitutsiyasi_Talim_Moddalari_50_Sahifa.json",
        Path(__file__).parents[2] / "Ozbekiston_Konstitutsiyasi_Talim_Moddalari_50_Sahifa.json",
        Path.cwd() / "Ozbekiston_Konstitutsiyasi_Talim_Moddalari_50_Sahifa.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

def _extract_text_content(obj: Any) -> str:
    """Recursively converts nested dictionaries/lists into searchable clean text."""
    if isinstance(obj, str):
        return obj.strip()
    elif isinstance(obj, list):
        return "\n".join([_extract_text_content(item) for item in obj if item])
    elif isinstance(obj, dict):
        parts = []
        for k, v in obj.items():
            val_text = _extract_text_content(v)
            if val_text:
                parts.append(f"{k.replace('_', ' ').title()}: {val_text}")
        return "\n".join(parts)
    return str(obj) if obj is not None else ""

def load_raw_constitution_50_json() -> Dict[str, Any]:
    path = _resolve_json_path()
    if not path:
        logger.error("[Constitution50Loader] Could not locate Ozbekiston_Konstitutsiyasi_Talim_Moddalari_50_Sahifa.json")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"[Constitution50Loader] Exception loading JSON file: {e}")
        return {}

def get_constitution_50_articles() -> List[Dict[str, Any]]:
    """
    Transforms JSON 50 pages, chapters, and violations into standardized legal encyclopedia articles.
    """
    raw_data = load_raw_constitution_50_json()
    if not raw_data:
        return []

    articles: List[Dict[str, Any]] = []

    # 1. Ingest 50 Pages
    pages = raw_data.get("pages", [])
    for p in pages:
        p_num = p.get("page_number", 0)
        ch_hdr = p.get("chapter_header", f"Konstitutsiya {p_num}-Sahifa")
        title = p.get("title", f"Konstitutsiya {p_num}-Sahifa Tahlili")
        sub_hdr = p.get("sub_header", "")
        subtitle = p.get("subtitle", "")
        keywords = p.get("search_keywords", [])
        
        overview = _extract_text_content(p.get("overview_paragraphs", ""))
        quotes = _extract_text_content(p.get("legal_norms_and_quotes", ""))
        analyses = _extract_text_content(p.get("in_depth_analyses", ""))
        tables = _extract_text_content(p.get("structured_data_tables", ""))
        cases = _extract_text_content(p.get("practical_cases_and_impacts", ""))

        full_body = f"{ch_hdr}\n{sub_hdr}\n{subtitle}\n{overview}\n{quotes}\n{analyses}\n{tables}\n{cases}".strip()

        articles.append({
            "code": f"CONST-PAGE-{p_num}",
            "section_id": 1,
            "section_name": "Konstitutsiyaviy Ta'lim Huquqi va Pedagog Maqomi (50 Sahifalik Entsiklopediya)",
            "title": f"Konstitutsiya Entsiklopediyasi Sahifa {p_num}: {title}",
            "category": "Konstitutsiya 50-Sahifa Entsiklopediya",
            "doc_number": f"PAGE-{p_num}",
            "doc_date": "2026-yil (Yangi Tahrir)",
            "lex_url": f"https://{p.get('lex_uz_or_source')}" if str(p.get("lex_uz_or_source", "")).startswith("lex.uz") else "https://lex.uz/docs/-6445145",

            "summary": (overview[:250] + "...") if len(overview) > 250 else (title or subtitle),
            "full_text": full_body,
            "text": full_body,
            "keywords": (keywords if isinstance(keywords, list) else [str(keywords)]) + ["konstitutsiya", f"sahifa {p_num}", "50 sahifa", "ta'lim huquqi"],

            "related_faq_ids": [1, 2, 5, 9, 18, 50]
        })

    # 2. Ingest Violations and Penalties
    violations = raw_data.get("violations_and_penalties", [])
    for vio in violations:
        v_id = vio.get("violation_id", "VIO")
        v_type = vio.get("violation_type", "Qonunbuzarlik")
        v_action = vio.get("prohibited_action", "")
        v_const = vio.get("constitutional_violation", "")
        v_legal = vio.get("legal_basis", "")
        v_sanc1 = vio.get("sanction_first_time", "")
        v_sanc2 = vio.get("sanction_repeated", "")

        body = (
            f"Qonunbuzarlik turi: {v_type}\n"
            f"Taqiqlangan harakat: {v_action}\n"
            f"Konstitutsiyaviy norma: {v_const}\n"
            f"Qonuniy asos: {v_legal}\n"
            f"Birinchi marta sanksiya: {v_sanc1}\n"
            f"Takroriy sanksiya: {v_sanc2}"
        )

        articles.append({
            "code": v_id,
            "section_id": 4,
            "section_name": "Pedagoglar Daxlsizligi va Qonunbuzarliklar uchun Javobgarlik",
            "title": f"Javobgarlik Mezoni ({v_id}): {v_type}",
            "category": "Qonunbuzarlik va Sanksiyalar",
            "doc_number": v_id,
            "doc_date": "2026-yil",
            "lex_url": "https://lex.uz/docs/-97661",
            "summary": f"{v_action}. Qonuniy asos: {v_legal}. Sanksiya: {v_sanc1}",
            "full_text": body,
            "text": body,
            "keywords": [v_id.lower(), v_type.lower(), "jarima", "javobgarlik", "sanksiya", "mjtik", "jk"],
            "related_faq_ids": [9, 10, 11, 37]
        })

    return articles
