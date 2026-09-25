"""
SözLab Unified Legal Knowledge Base Service
Combines:
1. Top-50 Official Education FAQs (Maktabgacha, Maktab, OTM, Pedagoglar huquqlari)
2. Education Legislation Encyclopedia (Constitution 50, 51, 52, 77, O'RQ-637, O'RQ-901, Decrees)
3. Strict Grounding Filter: Detects in-scope education queries vs out-of-scope queries
"""

import re
from typing import List, Optional, Tuple, Dict, Any
from app.models.schemas import KnowledgeItem, TopicCategory
from app.data.education_faq_50 import FAQ_50_ITEMS, search_faq_items
from app.data.education_legislation_encyclopedia import LEGAL_ENCYCLOPEDIA_ARTICLES, search_encyclopedia

# Out-of-scope refusal message
OUT_OF_SCOPE_REFUSAL = (
    "Kechirasiz, ushbu masala vazirlikning rasmiy ta'lim qonunchiligi bazasiga kirmaydi. "
    "Men faqat maktabgacha ta'lim (bog'cha), umumta'lim maktablari, oliy ta'lim (qabul, grant, kontrakt, "
    "yotoqxona, perevod), pedagoglar huquqlari va ta'lim kafolatlari bo'yicha rasmiy savollarga javob beraman. "
    "Iltimos, ta'limga oid savolingizni bering."
)

# Core educational keywords across all 8 sectors
EDUCATION_SCOPE_KEYWORDS = {
    "maktab", "sinf", "o'quvchi", "o'qituvchi", "pedagog", "bog'cha", "tarbiyachi",
    "otm", "oliygoh", "universitet", "institut", "talaba", "rektor", "dekanat",
    "qabul", "grant", "kontrakt", "super-kontrakt", "to'lov-kontrakt", "kvota",
    "gpa", "baho", "bsb", "chsb", "reyting", "hemis", "attestatsiya", "toifa",
    "yotoqxona", "ttj", "ijara", "kompensatsiya", "stipendiya", "kredit", "ta'lim krediti",
    "perevod", "ko'chirish", "tiklash", "diplom", "attestat", "nostrifikatsiya", "apostil",
    "1-sinf", "forma", "darslik", "majburiy mehnat", "ta'til", "56 kun", "tibbiy ko'rik",
    "inklyuziv", "nogiron", "yetim", "xotin-qizlar", "litsenziya", "xususiy maktab",
    "nodavlat", "kurs", "repetitor", "1006", "1007", "vazirlik", "ishonch telefoni",
    "dars", "hafta", "stavka", "16 soat", "direktor jamg'armasi", "sinf rahbarligi",
    "qonun", "o'rq-637", "o'rq-901", "konstitutsiya", "50-modda", "52-modda",
    "magistratura", "magistr", "bakalavr", "doktorantura", "sertifikat", "til", "chet tili",
    "cefr", "ielts", "toefl", "imtihon", "test", "bilim", "ta'lim", "fakultet", "yo'nalish",
    "ball", "o'tish bali", "vmq-376", "vmq-447", "vmq-527", "vmq-605", "qaror"
}

# Explicit out-of-scope topic triggers
OUT_OF_SCOPE_TRIGGERS = {
    "ob-havo", "havo qanday", "ovqat", "retsept", "pishirish", "futbol", "kino",
    "siyosat", "dollar kursi", "valyuta", "mashina", "avtomobil", "haydovchilik",
    "pasport stoli", "propiska", "pensiya jamg'armasi", "kadastr", "kommunal",
    "tibbiyot retsepti", "dori-darmon", "dori", "kasallik", "bosh og'rig'i",
    "qiziqarli fakt", "latifa", "she'r ayt"
}

def is_in_educational_scope(query: str) -> bool:
    """
    Checks if a query is related to educational laws, decrees, or 1006/1007 competence.
    Returns True if in scope, False if out of scope.
    """
    q = query.lower().strip()
    if not q:
        return False
        
    # Check out-of-scope triggers first
    for trigger in OUT_OF_SCOPE_TRIGGERS:
        if trigger in q:
            return False
            
    # Check educational scope keywords
    words = re.findall(r'\b\w+\b', q)
    for w in words:
        if w in EDUCATION_SCOPE_KEYWORDS:
            return True
            
    for kw in EDUCATION_SCOPE_KEYWORDS:
        if kw in q:
            return True
            
    # Greeting / generic courteous openers are in-scope
    greetings = ["salom", "assalomu", "assalom", "aloh", "alo", "eshityapsizmi", "qanday", "yordam"]
    if any(g in q for g in greetings) and len(words) <= 4:
        return True

    return False

def get_complete_legal_context(query: str, max_faqs: int = 3, max_articles: int = 2) -> Dict[str, Any]:
    """
    Retrieves legal context from both the 50 FAQs and the Encyclopedia.
    Formats exact law citations for direct LLM injection.
    """
    in_scope = is_in_educational_scope(query)
    if not in_scope:
        return {
            "in_scope": False,
            "refusal_text": OUT_OF_SCOPE_REFUSAL,
            "faqs": [],
            "articles": [],
            "formatted_context": "SAVOL TA'LIM DOIRASIDAN TASHQARIDA. RASMIY RAD JAVOBINI BERING."
        }

    faqs = search_faq_items(query, limit=max_faqs)
    articles = search_encyclopedia(query, limit=max_articles)

    context_lines = []
    if faqs:
        context_lines.append("--- RASMIY 50 SAVOL-JAVOB BAZASIDAN TOPILGAN MATERIALLAR ---")
        for f in faqs:
            context_lines.append(
                f"SAVOL #{f['id']} ({f['chapter_name']}): {f['question']}\n"
                f"QONUNIY ASOS: {f['legal_basis']}\n"
                f"LO'NDA JAVOB: {f['short_answer']}\n"
                f"BATAFSIL JAVOB: {f['full_answer']}\n"
            )

    if articles:
        context_lines.append("--- TA'LIM QONUNCHILIGI ENSIKLOPEDIYASI MODDALARI ---")
        for a in articles:
            context_lines.append(
                f"HUJJAT: {a['title']} ({a['category']})\n"
                f"MAZMUNI: {a['summary']}\n"
                f"ANIQ MATN: {a['text']}\n"
            )

    return {
        "in_scope": True,
        "refusal_text": None,
        "faqs": faqs,
        "articles": articles,
        "formatted_context": "\n".join(context_lines) if context_lines else "Umumiy ta'lim qonunchiligi asosida javob bering."
    }


# Backwards compatibility legacy items
MINISTRY_KNOWLEDGE_BASE: List[KnowledgeItem] = [
    KnowledgeItem(
        id=f"faq-{f['id']}",
        topic=TopicCategory.QABUL if "qabul" in f['keywords'] else (
            TopicCategory.GRANT if "grant" in f['keywords'] else (
                TopicCategory.KONTRAKT if "kontrakt" in f['keywords'] else (
                    TopicCategory.TTJ if "yotoqxona" in f['keywords'] or "ijara" in f['keywords'] else (
                        TopicCategory.NOSTRIFIKATSIYA if "nostrifikatsiya" in f['keywords'] else TopicCategory.STIPENDIYA
                    )
                )
            )
        ),
        title=f["question"],
        summary=f["short_answer"],
        official_regulation=f["legal_basis"],
        faq_questions=[f["question"]],
        action_steps=[f["full_answer"]],
        links=["https://lex.uz", "https://edu.uz"]
    )
    for f in FAQ_50_ITEMS[:10]
]

def search_knowledge_base(query: str, limit: int = 2) -> List[KnowledgeItem]:
    """Legacy compatibility search."""
    ctx = get_complete_legal_context(query, max_faqs=limit)
    items = []
    for f in ctx.get("faqs", []):
        items.append(
            KnowledgeItem(
                id=f"faq-{f['id']}",
                topic=TopicCategory.QABUL,
                title=f["question"],
                summary=f["short_answer"],
                official_regulation=f["legal_basis"],
                faq_questions=[f["question"]],
                action_steps=[f["full_answer"]],
                links=["https://lex.uz"]
            )
        )
    return items if items else MINISTRY_KNOWLEDGE_BASE[:limit]
