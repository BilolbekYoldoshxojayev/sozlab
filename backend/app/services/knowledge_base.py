"""
SözLab Unified Legal Knowledge Base Service
Combines:
1. Top-50 Official Education FAQs (Maktabgacha, Maktab, OTM, Pedagoglar huquqlari)
2. Education Legislation Encyclopedia (Constitution 50, 51, 52, 77, O'RQ-637, O'RQ-901, Decrees)
3. Smart Grounding Filter: High-precision in-scope education detection & STT noise resilience
"""

import re
from typing import List, Optional, Tuple, Dict, Any
from app.models.schemas import KnowledgeItem, TopicCategory
from app.data.education_faq_50 import FAQ_50_ITEMS, search_faq_items
from app.data.education_legislation_encyclopedia import LEGAL_ENCYCLOPEDIA_ARTICLES, search_encyclopedia

# Out-of-scope refusal message
OUT_OF_SCOPE_REFUSAL = (
    "Kechirasiz, men faqat maktab va oliy ta'lim qonunchiligi bo'yicha rasmiy savollarga javob bera olaman."
)

# Explicit non-educational out-of-scope blacklist triggers (full phrases & strict word tokens)
OUT_OF_SCOPE_PHRASES = [
    "ob-havo", "havo qanday", "yomg'ir", "harorat",
    "ovqat", "retsept", "pishirish", "osh pishirish", "taom", "sho'rva",
    "futbol", "chempionlar ligasi", "real madrid", "barselona", "kino", "serial",
    "dollar kursi", "valyuta kursi", "rubl kursi", "yevro kursi", "dollar",
    "mashina sotib", "avtomobil", "haydovchilik", "prava olish", "zapchast",
    "pasport stoli", "propiska", "pensiya jamg'armasi", "kadastr", "kommunal",
    "tibbiyot retsepti", "dori ichish", "bosh og'rig'i", "dori",
    "latifa", "she'r ayt", "anekdot"
]

OUT_OF_SCOPE_ROOTS = {
    "ob-havo", "retsept", "futbol", "avtomobil", "haydovchilik",
    "propiska", "kadastr", "kommunal", "latifa", "anekdot", "pishirish"
}

# Comprehensive educational keywords, stems & STT phonetic variants
EDUCATION_SCOPE_KEYWORDS = {
    # Schools & Preschools
    "maktab", "maktablar", "maktabga", "sinf", "sinflar", "1-sinf", "birinchi sinf",
    "o'quvchi", "o'quvchilar", "oquvchi", "oquvchilar", "dars", "darslar", "darslik", "darsliklar",
    "bog'cha", "bogcha", "bog'chaga", "tarbiyachi", "tarbiyachilar", "maktabgacha",
    "forma", "maktab formasi", "kitob", "mashq daftari", "bepul", "pullik", "remont", "ta'mirlash", "fond",

    # Higher Education & Students
    "otm", "otmlar", "otmga", "oliygoh", "oliygohlar", "universitet", "universitetlar",
    "institut", "institutlar", "fakultet", "dekanat", "rektor", "akademik",
    "talaba", "talabalar", "talabalarga", "abituriyent", "abiturient", "abituriyentlar",
    "kurs", "1-kurs", "2-kurs", "3-kurs", "4-kurs", "bakalavr", "bakalavriat",
    "magistr", "magistratura", "doktorantura", "rezidentura", "ordinatura", "diplom", "attestat",

    # Admissions, Grants & Financials (including STT variants like 'byudjet', 'kontakt')
    "qabul", "qabulga", "kvota", "kvotalar", "imtihon", "imtihonlar", "imtixon", "test", "testlar",
    "ball", "ballar", "o'tish bali", "otish bali", "mandat", "natija",
    "grant", "grantlar", "grand", "grandlar", "davlat granti",
    "byudjet", "budjet", "byudjetlar", "budjetlar", "byudjetda", "budjetda", "davlat budjeti",
    "kontrakt", "kontraktlar", "kontraktlari", "kontakt", "kontaktlar", "kontaktlari", "kantrakt",
    "super-kontrakt", "superkontrakt", "to'lov-kontrakt", "tolov-kontrakt", "shartnoma", "to'lov", "tolov",

    # Academic & Student Support
    "gpa", "baho", "baholar", "bsb", "chsb", "reyting", "hemis", "kundalik", "kredit-modul",
    "yotoqxona", "yotoqxonalar", "ttj", "ijara", "ijara kompensatsiyasi", "turar joy",
    "stipendiya", "stipendiyalar", "kredit", "ta'lim krediti", "talim krediti", "0%", "foizsiz",
    "perevod", "ko'chirish", "kochirish", "o'qishni ko'chirish", "oqishni kochirish", "tiklash",
    "nostrifikatsiya", "apostil", "xorijiy diplom", "top-1000",

    # Teachers & Rights
    "pedagog", "pedagoglar", "pedagogning maqomi", "o'qituvchi", "o'qituvchilar", "oqituvchi",
    "ustoz", "ustozlar", "muallim", "attestatsiya", "toifa", "toifalar", "ustama", "ustamalar",
    "staj", "maosh", "oylik", "ish haqi", "stavka", "16 soat", "direktor jamg'armasi", "sinf rahbarligi",
    "majburiy mehnat", "ta'til", "56 kun", "tibbiy ko'rik", "huquq", "huquqlari",

    # General & Legal terminology
    "ta'lim", "talim", "o'qish", "oqish", "o'qishga", "oqishga", "bilim",
    "qonun", "qonunchilik", "o'rq-637", "o'rq-901", "konstitutsiya", "50-modda", "51-modda", "52-modda", "77-modda",
    "qaror", "farmon", "nizom", "vmq-376", "vmq-447", "vmq-527", "vmq-605", "pf-81",
    "vazirlik", "1006", "1007", "ishonch telefoni", "maslahat", "ma'lumot", "malumot", "savol", "yordam",
    "gaplashadigan", "ekspert", "mutaxassis", "ariza", "hujjat", "hujjatlar", "my.gov.uz", "my.maktab.uz", "my.edu.uz",
    "litsey", "kollej", "texnikum", "repetitor", "litsenziya", "nodavlat", "xususiy", "yosh", "yoshi"
}

def is_in_educational_scope(query: str) -> bool:
    """
    Determines if query falls under education legislation, FAQs, or 1006/1007 helpline competence.
    """
    q = query.lower().strip()
    if not q or len(q) < 2:
        return False

    # 1. Check explicit non-educational blacklist phrases FIRST
    for phrase in OUT_OF_SCOPE_PHRASES:
        if phrase in q:
            return False

    words = re.findall(r'\b[\w\'-]+\b', q)
    for w in words:
        if w in OUT_OF_SCOPE_ROOTS:
            return False

    # 2. Match education keywords and phonetic variants
    for w in words:
        if w in EDUCATION_SCOPE_KEYWORDS:
            return True

    for kw in EDUCATION_SCOPE_KEYWORDS:
        if kw in q:
            return True

    # 3. Check for polite greetings and conversational openers
    greetings = ["salom", "assalomu", "assalom", "aloh", "alo", "eshityapsizmi"]
    if any(g in q for g in greetings) and len(words) <= 4:
        return True

    # 4. Check if knowledge base database finds matches
    matched_faqs = search_faq_items(query, limit=1)
    if matched_faqs:
        return True

    matched_articles = search_encyclopedia(query, limit=1)
    if matched_articles:
        return True

    return False


def get_complete_legal_context(query: str, max_faqs: int = 3, max_articles: int = 2) -> Dict[str, Any]:
    """
    Retrieves legal context from both the 50 FAQs and the Encyclopedia.
    Formats exact law citations for direct LLM injection.
    """
    in_scope = is_in_educational_scope(query)

    # Search database
    faqs = search_faq_items(query, limit=max_faqs)
    articles = search_encyclopedia(query, limit=max_articles)

    # Fallback search on common synonym terms (e.g. byudjet -> grant, kontakt -> kontrakt)
    q_low = query.lower()
    if not faqs and ("byudjet" in q_low or "budjet" in q_low or "grant" in q_low):
        faqs = search_faq_items("davlat granti stipendiya", limit=max_faqs)
    elif not faqs and ("kontakt" in q_low or "kontrakt" in q_low or "shartnoma" in q_low or "to'lov" in q_low):
        faqs = search_faq_items("to'lov-kontrakt magistratura", limit=max_faqs)
    elif not faqs and ("1-sinf" in q_low or "maktab" in q_low or "yosh" in q_low):
        faqs = search_faq_items("1-sinfga qabul yoshi", limit=max_faqs)

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
        "in_scope": in_scope,
        "refusal_text": OUT_OF_SCOPE_REFUSAL if not in_scope else None,
        "faqs": faqs,
        "articles": articles,
        "formatted_context": "\n".join(context_lines) if context_lines else "Umumiy ta'lim qonunchiligi asosida ixcham, aniq javob bering."
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
