"""
SözLab Uzbek Text & TTS Normalizer Service
- Converts numbers (0..999,999,999) to cardinal and ordinal Uzbek words
- Converts percentages: '0%' -> 'nol foiz', '100%' -> 'yuz foiz', '50%' -> 'ellik foiz'
- Converts law citations:
    VMQ-527 -> 'Vazirlar Mahkamasining besh yuz yigirma yettinchi qarori'
    PF-81 -> 'Prezidentning sakson birinchi farmoni'
    PQ-xxx -> 'Prezidentning ... qarori'
    O'RQ-xxx -> 'O'zbekiston Respublikasining ... qonuni'
- Inflects educational acronyms:
    GPA -> 'ji-pi-ey'
    OTM, OTMga, OTMda, OTMlar -> 'oliy ta'lim muassasasi', 'oliy ta'lim muassasasiga', 'oliy ta'lim muassasalari'
    TTJ, TTJga, TTJda -> 'talabalar turar joyi', 'talabalar turar joyiga'
    HEMIS -> 'xemis', 1006 -> 'bir ming olti', 1007 -> 'bir ming yetti'
- Converts article/ordinal numbers: '1-moddasi' -> 'birinchi moddasi', '44-modda' -> 'qirq to\'rtinchi modda'
- Strips markdown asterisks (*), hashes (#), backticks, and cleans trailing ellipses (...)
"""

import re

HARDCODED_ORDINALS = {
    "1": "birinchi", "2": "ikkinchi", "3": "uchinchi", "4": "to'rtinchi", "5": "beshinchi",
    "6": "oltinchi", "7": "yettinchi", "8": "sakkizinchi", "9": "to'qqizinchi", "10": "o'ninchi",
    "11": "o'n birinchi", "12": "o'n ikkinchi", "13": "o'n uchinchi", "14": "o'n to'rtinchi", "15": "o'n beshinchi",
    "16": "o'n oltinchi", "17": "o'n yettinchi", "18": "o'n sakkizinchi", "19": "o'n to'qqizinchi", "20": "yigirmanchi",
    "30": "o'ttizinchi", "40": "qirqinchi", "44": "qirq to'rtinchi", "50": "elliginchi", "51": "ellik birinchi",
    "52": "ellik ikkinchi", "60": "oltmishinchi", "70": "yetmishinchi", "77": "yetmish yettinchi", "80": "saksoninchi",
    "81": "sakson birinchi", "90": "to'qsoninchi", "100": "yuzinchi"
}

ROMAN_NUMERAL_MAP = {
    "I": "birinchi", "II": "ikkinchi", "III": "uchinchi", "IV": "to'rtinchi",
    "V": "beshinchi", "VI": "oltinchi", "VII": "yettinchi", "VIII": "sakkizinchi",
    "IX": "to'qqizinchi", "X": "o'ninchi"
}

ABBREVIATION_EXPANSIONS = {
    "DXM": "Davlat Xizmatlari Markazi (DXM)",
    "DXMning": "Davlat Xizmatlari Markazining (DXMning)",
}


def number_to_uzbek_cardinal(n: int) -> str:
    """Converts integers (0..999,999,999) to cardinal Uzbek words."""
    if n == 0:
        return "nol"
    if n < 0:
        return f"minus {number_to_uzbek_cardinal(abs(n))}"

    units = ["", "bir", "ikki", "uch", "to'rt", "besh", "olti", "yetti", "sakkiz", "to'qqiz"]
    tens = ["", "o'n", "yigirma", "o'ttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "to'qson"]

    if n < 10:
        return units[n]
    if n < 100:
        t = n // 10
        u = n % 10
        return f"{tens[t]} {units[u]}".strip()
    if n < 1000:
        h = n // 100
        rem = n % 100
        prefix = "yuz" if h == 1 else f"{units[h]} yuz"
        if rem > 0:
            return f"{prefix} {number_to_uzbek_cardinal(rem)}"
        return prefix
    if n < 1_000_000:
        th = n // 1000
        rem = n % 1000
        prefix = "bir ming" if th == 1 else f"{number_to_uzbek_cardinal(th)} ming"
        if rem > 0:
            return f"{prefix} {number_to_uzbek_cardinal(rem)}"
        return prefix
    if n < 1_000_000_000:
        mil = n // 1_000_000
        rem = n % 1_000_000
        prefix = f"{number_to_uzbek_cardinal(mil)} million"
        if rem > 0:
            return f"{prefix} {number_to_uzbek_cardinal(rem)}"
        return prefix
    return str(n)


def number_to_uzbek_ordinal(n: int) -> str:
    """Converts integers (1..999,999) to full Uzbek ordinal words (e.g. 1 -> birinchi, 81 -> sakson birinchi)."""
    n_str = str(n)
    if n_str in HARDCODED_ORDINALS:
        return HARDCODED_ORDINALS[n_str]

    cardinal = number_to_uzbek_cardinal(n)
    if not cardinal or cardinal == str(n):
        return f"{n}-chi"

    words = cardinal.split()
    last = words[-1]

    if last in ["ikki", "olti", "yetti", "yigirma"]:
        last_ord = last + "nchi"
    elif last == "ellik":
        last_ord = "elliginchi"
    elif last == "bir":
        last_ord = "birinchi"
    elif last in ["uch", "to'rt", "besh", "sakkiz", "to'qqiz", "o'n", "o'ttiz", "qirq", "oltmish", "yetmish", "sakson", "to'qson", "yuz", "ming", "million"]:
        last_ord = last + "inchi"
    else:
        last_ord = last + "inchi"

    words[-1] = last_ord
    return " ".join(words)


def normalize_law_citations(text: str) -> str:
    """Expands VMQ-527, PF-81, PQ-xxx, and O'RQ-xxx into natural spoken Uzbek."""
    if not text:
        return ""

    def _replace_law(lead: str, default_noun: str, noun_stem: str, m: re.Match) -> str:
        num = int(m.group(1))
        ord_word = number_to_uzbek_ordinal(num)
        direct_suffix = (m.group(2) or "").lower()
        trailing_suffix = (m.group(3) or "").lower()

        sfx = trailing_suffix or direct_suffix
        if sfx in ["ga", "da", "dan", "ning", "ni"]:
            final_noun = f"{default_noun}{sfx}"
        elif sfx.startswith("i"):
            final_noun = f"{noun_stem}{sfx}"
        elif sfx:
            final_noun = f"{default_noun}{sfx}"
        else:
            final_noun = default_noun

        return f"{lead} {ord_word} {final_noun}"

    # 1. VMQ-527 (Vazirlar Mahkamasi qarori)
    text = re.sub(
        r"\bVMQ[- ]?(\d+)(?:-son(?:li)?)?(?:(ga|da|dan|ning|ni))?(?:\s+qaror([a-z']*))?\b",
        lambda m: _replace_law("Vazirlar Mahkamasining", "qarori", "qaror", m),
        text,
        flags=re.IGNORECASE
    )

    # 2. PF-81 (Prezident farmoni)
    text = re.sub(
        r"\bPF[- ]?(\d+)(?:-son(?:li)?)?(?:(ga|da|dan|ning|ni))?(?:\s+farmon([a-z']*))?\b",
        lambda m: _replace_law("Prezidentning", "farmoni", "farmon", m),
        text,
        flags=re.IGNORECASE
    )

    # 3. PQ-xxx (Prezident qarori)
    text = re.sub(
        r"\bPQ[- ]?(\d+)(?:-son(?:li)?)?(?:(ga|da|dan|ning|ni))?(?:\s+qaror([a-z']*))?\b",
        lambda m: _replace_law("Prezidentning", "qarori", "qaror", m),
        text,
        flags=re.IGNORECASE
    )

    # 4. O'RQ-xxx (O'zbekiston Respublikasi qonuni)
    text = re.sub(
        r"\b(?:O[\'‘`]RQ|ORQ)[- ]?(\d+)(?:-son(?:li)?)?(?:(ga|da|dan|ning|ni))?(?:\s+qonun([a-z']*))?\b",
        lambda m: _replace_law("O'zbekiston Respublikasining", "qonuni", "qonun", m),
        text,
        flags=re.IGNORECASE
    )

    return text


def normalize_percentages(text: str) -> str:
    """Converts 0%, 100%, 50% or '50 foiz' to full words."""
    if not text:
        return ""

    def _sub_pct(m):
        num_str = m.group(1)
        suffix = m.group(2) or ""
        if "." in num_str:
            parts = num_str.split(".")
            w1 = number_to_uzbek_cardinal(int(parts[0]))
            w2 = number_to_uzbek_cardinal(int(parts[1]))
            base = f"{w1} butun {w2} foiz"
        else:
            num = int(num_str)
            base = f"{number_to_uzbek_cardinal(num)} foiz"
        if suffix:
            return f"{base}{suffix}"
        return base

    text = re.sub(r"\b(\d+(?:\.\d+)?)\s*%(?:-)?([a-zA-Z']*)", _sub_pct, text)

    def _sub_pct_word(m):
        num = int(m.group(1))
        suffix = m.group(2) or ""
        return f"{number_to_uzbek_cardinal(num)} foiz{suffix}"

    text = re.sub(r"\b(\d+)\s*foiz([a-z']*)\b", _sub_pct_word, text, flags=re.IGNORECASE)
    return text


def normalize_abbreviations(text: str) -> str:
    """Expands educational abbreviations with proper grammatical case inflections."""
    if not text:
        return ""

    # Plural OTM
    def _sub_otm_plural(m):
        suffix = m.group(1) or ""
        return f"oliy ta'lim muassasalari{suffix}"
    text = re.sub(r"\bOTMlar(ga|da|dan|ning|ni)?\b", _sub_otm_plural, text, flags=re.IGNORECASE)

    # Singular OTM with case inflection
    def _sub_otm_singular(m):
        suffix = m.group(1) or ""
        sfx_map = {
            "ga": "siga",
            "da": "sida",
            "dan": "sidan",
            "ning": "sining",
            "ni": "sini",
            "": "si"
        }
        mapped = sfx_map.get(suffix.lower(), suffix)
        return f"oliy ta'lim muassasa{mapped}"
    text = re.sub(r"\bOTM(ga|da|dan|ning|ni)?\b", _sub_otm_singular, text, flags=re.IGNORECASE)

    # Plural TTJ
    def _sub_ttj_plural(m):
        suffix = m.group(1) or ""
        return f"talabalar turar joylari{suffix}"
    text = re.sub(r"\bTTJlar(ga|da|dan|ning|ni)?\b", _sub_ttj_plural, text, flags=re.IGNORECASE)

    # Singular TTJ
    def _sub_ttj_singular(m):
        suffix = m.group(1) or ""
        sfx_map = {
            "ga": "ga",
            "da": "da",
            "dan": "dan",
            "ning": "ning",
            "ni": "ni",
            "": ""
        }
        mapped = sfx_map.get(suffix.lower(), suffix)
        return f"talabalar turar joyi{mapped}"
    text = re.sub(r"\bTTJ(ga|da|dan|ning|ni)?\b", _sub_ttj_singular, text, flags=re.IGNORECASE)

    # GPA
    text = re.sub(r"\bGPA(?:-?(?:si|sining|ga|da|dan))?\b", "ji-pi-ey", text, flags=re.IGNORECASE)

    # Static abbreviations
    static_abbrs = [
        (r"\bHEMIS\b", "xemis"),
        (r"\bmy\.gov\.uz\b", "may gov uz"),
        (r"\bedu\.uz\b", "e-du uz"),
        (r"\b1006\b", "bir ming olti"),
        (r"\b1007\b", "bir ming yetti"),
        (r"\bDXMning\b", "Davlat Xizmatlari Markazining"),
        (r"\bDXMga\b", "Davlat Xizmatlari Markaziga"),
        (r"\bDXMda\b", "Davlat Xizmatlari Markazida"),
        (r"\bDXMdan\b", "Davlat Xizmatlari Markazidan"),
        (r"\bDXMni\b", "Davlat Xizmatlari Markazini"),
        (r"\bDXM\b", "Davlat Xizmatlari Markazi"),
    ]
    for pattern, repl in static_abbrs:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    return text


MONTHS_PATTERN = r"(?:yanvar|fevral|mart|aprel|may|iyun|iyul|avgust|sentabr|sentiyabr|oktabr|oktyabr|noyabr|dekabr)[a-z\']*"
ORDER_NOUNS_PATTERN = r"(?:modda|qism|bob|sinf|bosqich|kurs|yil|oy|kun|hafta|daraja|o[\'‘`]rin|navbat|qavat|guruh|band|paragraf|son|maktab)[a-z\']*"
ALL_ORDER_PATTERN = f"(?:{MONTHS_PATTERN}|{ORDER_NOUNS_PATTERN})"


def normalize_modda_numbers(text: str) -> str:
    """Replaces '31-dekabriga' -> 'o'ttiz birinchi dekabriga', '1-moddasi' -> 'birinchi moddasi', '1-chi' -> 'birinchi', etc."""
    if not text:
        return ""
    res = text

    def _sub_order_word(m):
        num_str = m.group(1)
        suffix = m.group(2)
        try:
            val = int(num_str)
            ord_word = number_to_uzbek_ordinal(val)
            return f"{ord_word} {suffix}"
        except ValueError:
            return m.group(0)

    # 1. Hyphenated order words and dates: '31-dekabriga', '1-sentabr', '44-modda', '2024-yil'
    res = re.sub(
        rf"\b(\d+)\s*-\s*({ALL_ORDER_PATTERN})\b",
        _sub_order_word,
        res,
        flags=re.IGNORECASE
    )

    # 2. Spaced calendar dates: '31 dekabriga', '1 sentabr'
    res = re.sub(
        rf"\b(\d+)\s+({MONTHS_PATTERN})\b",
        _sub_order_word,
        res,
        flags=re.IGNORECASE
    )

    # 3. Explicit ordinals with suffixes: '1-chi', '1 inchi', '31-nchi'
    def _sub_ordinal(m):
        num_str = m.group(1)
        try:
            val = int(num_str)
            return number_to_uzbek_ordinal(val)
        except ValueError:
            return m.group(0)

    res = re.sub(r"\b(\d+)(?:-|\s)?(?:chi|inchi|nchi|ci)\b", _sub_ordinal, res, flags=re.IGNORECASE)

    for k, v in HARDCODED_ORDINALS.items():
        res = re.sub(r"\b" + k + r"-(?:chi|inchi|nchi)\b", v, res, flags=re.IGNORECASE)
        res = re.sub(r"\b" + k + r"(?:chi|inchi|nchi)\b", v, res, flags=re.IGNORECASE)

    return res


def cyrillic_to_latin_uzbek(text: str) -> str:
    """Converts Cyrillic Uzbek text to Latin Uzbek to guarantee keyword matching."""
    if not text or not isinstance(text, str):
        return ""

    cyr_map = {
        'А': 'A', 'а': 'a',
        'Б': 'B', 'б': 'b',
        'В': 'V', 'в': 'v',
        'Г': 'G', 'г': 'g',
        'Д': 'D', 'д': 'd',
        'Е': 'E', 'е': 'e',
        'Ё': 'Yo', 'ё': 'yo',
        'Ж': 'J', 'ж': 'j',
        'З': 'Z', 'з': 'z',
        'И': 'I', 'и': 'i',
        'Й': 'Y', 'й': 'y',
        'К': 'K', 'к': 'k',
        'Л': 'L', 'л': 'l',
        'М': 'M', 'м': 'm',
        'Н': 'N', 'н': 'n',
        'О': 'O', 'о': 'o',
        'П': 'P', 'п': 'p',
        'Р': 'R', 'р': 'r',
        'С': 'S', 'с': 's',
        'Т': 'T', 'т': 't',
        'У': 'U', 'у': 'u',
        'Ф': 'F', 'ф': 'f',
        'Х': 'X', 'х': 'x',
        'Ц': 'Ts', 'ц': 'ts',
        'Ч': 'Ch', 'ch': 'ch',
        'Ш': 'Sh', 'sh': 'sh',
        'Ъ': "'", 'ъ': "'",
        'Ь': "", 'ь': "",
        'Э': 'E', 'э': 'e',
        'Ю': 'Yu', 'ю': 'yu',
        'Я': 'Ya', 'я': 'ya',
        'Ў': "O'", 'ў': "o'",
        'Қ': 'Q', 'қ': 'q',
        'Ғ': "G'", 'ғ': "g'",
        'Ҳ': 'H', 'ҳ': 'h'
    }

    res = []
    for char in text:
        res.append(cyr_map.get(char, char))
    return "".join(res)


def strip_markdown_symbols(text: str) -> str:
    """Strips all asterisks (*), hashes (#), backticks (`), brackets, and cleans trailing ellipses (...)."""
    if not text:
        return ""
    res = re.sub(r"[\*\#\`\[\]\(\)\~\@\$]", "", text)
    res = re.sub(r"\.{3,}", ".", res)
    return res.strip()


def normalize_text_for_tts(text: str) -> str:
    """Full normalization pipeline preparing text for VoiceLab TTS synthesis."""
    if not text or not isinstance(text, str):
        return ""

    res = text

    # 1. Strip markdown artifacts
    res = strip_markdown_symbols(res)

    # 2. Normalize laws (VMQ-527, PF-81, PQ, O'RQ)
    res = normalize_law_citations(res)

    # 3. Normalize percentages (0%, 100%, 50 foiz)
    res = normalize_percentages(res)

    # 4. Educational abbreviations (GPA, OTM, TTJ, HEMIS, 1006, 1007, DXM)
    res = normalize_abbreviations(res)

    # 5. Modda numbers & ordinals (1-chi, 1-moddasi, 44-modda, 1-sinf)
    res = normalize_modda_numbers(res)

    # 6. Roman numerals (I-bob -> birinchi bob)
    def _sub_roman_hyphen(m):
        roman, suffix = m.group(1), m.group(2)
        word = ROMAN_NUMERAL_MAP.get(roman, roman)
        return f"{word} {suffix}"
    res = re.sub(
        r"\b(VIII|VII|III|XII|XI|VI|IV|IX|II|I|V|X)-(bob|sinf|modda[a-z\']*|qism[a-z\']*|bosqich[a-z\']*)\b",
        _sub_roman_hyphen,
        res,
        flags=re.IGNORECASE
    )
    for rom, word in ROMAN_NUMERAL_MAP.items():
        res = re.sub(r"\b" + rom + r"\b", word, res)

    # 7. Decimal numbers (e.g. 56.7, 3.0)
    def _sub_dec(m):
        w1 = number_to_uzbek_cardinal(int(m.group(1)))
        w2 = number_to_uzbek_cardinal(int(m.group(2)))
        return f"{w1} butun {w2}"
    res = re.sub(r"\b(\d+)[.,](\d+)\b", _sub_dec, res)

    # 8. Remaining numbers (hyphenated cases and standalone cardinals)
    def _sub_hyphen_cardinal(m):
        num = int(m.group(1))
        suffix = m.group(2)
        card = number_to_uzbek_cardinal(num)
        return f"{card}{suffix}"
    res = re.sub(r"\b(\d+)-(ga|da|dan|ni|ning|ta)\b", _sub_hyphen_cardinal, res, flags=re.IGNORECASE)

    def _sub_cardinal(m):
        num = int(m.group(1))
        return number_to_uzbek_cardinal(num)
    res = re.sub(r"\b(\d+)\b", _sub_cardinal, res)

    # 9. Clean multiple whitespaces
    res = re.sub(r"\s+", " ", res)

    return res.strip()
