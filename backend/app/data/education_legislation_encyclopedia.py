"""
O'zbekiston Respublikasi Ta'lim Qonunchiligi Ensiklopediyasi (2024–2026)
Oliy ta'lim, fan va innovatsiyalar vazirligi hamda Maktabgacha va maktab ta'limi vazirligi
Yuridik Normativ Hujjatlar Arxivi va Kodekslar To'plami.
Ingested 100% from Ozbekiston_Talim_Qonunchiligi_Mukammal_Entsiklopediya.pdf (6 Sections, 62 Articles/Decrees).
"""

from typing import Any, List, Dict, Optional
import re

LEGAL_ENCYCLOPEDIA_ARTICLES: List[Dict[str, Any]] = [
    {
        "code": "CONST-50",
        "section_id": 1,
        "section_name": "Konstitutsiyaviy Ta'lim Huquqi va Pedagog Maqomi",
        "title": "O'zbekiston Respublikasi Konstitutsiyasi 50-moddasi",
        "category": "Konstitutsiya",
        "doc_number": "50",
        "doc_date": "2023-yil 30-aprel",
        "lex_url": "https://lex.uz/docs/-6445145",
        "summary": "Har kim ta'lim olish huquqiga ega. Davlat bepul umumiy o'rta ta'lim va boshlang'ich professional ta'lim olishni kafolatlaydi. Umumiy o'rta ta'lim majburiydir. Inklyuziv ta'lim ta'minlanadi.",
        "full_text": "1. Har kim ta'lim olish huquqiga ega.\n2. Davlat bepul umumiy o'rta ta'lim va boshlang'ich professional ta'lim olishni kafolatlaydi. Umumiy o'rta ta'lim majburiydir.\n3. Maktab ishlari davlat nazoratidadir.\n4. Alohida ta'lim ehtiyojlariga ega bo'lgan bolalar uchun ta'lim tashkilotlarida inklyuziv ta'lim va tarbiya ta'minlanadi.",
        "text": "1. Har kim ta'lim olish huquqiga ega.\n2. Davlat bepul umumiy o'rta ta'lim va boshlang'ich professional ta'lim olishni kafolatlaydi. Umumiy o'rta ta'lim majburiydir.\n3. Maktab ishlari davlat nazoratidadir.\n4. Alohida ta'lim ehtiyojlariga ega bo'lgan bolalar uchun ta'lim tashkilotlarida inklyuziv ta'lim va tarbiya ta'minlanadi.",
        "keywords": [
            "bepul ta'lim",
            "1-sinf",
            "maktab",
            "majburiy ta'lim",
            "konstitutsiya 50",
            "umumiy o'rta ta'lim",
            "inklyuziv ta'lim",
            "davlat nazorati"
        ],
        "related_faq_ids": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            46
        ]
    },
    {
        "code": "CONST-51",
        "section_id": 1,
        "section_name": "Konstitutsiyaviy Ta'lim Huquqi va Pedagog Maqomi",
        "title": "O'zbekiston Respublikasi Konstitutsiyasi 51-moddasi",
        "category": "Konstitutsiya",
        "doc_number": "51",
        "doc_date": "2023-yil 30-aprel",
        "lex_url": "https://lex.uz/docs/-6445145",
        "summary": "Fuqarolar davlat ta'lim tashkilotlarida tanlov asosida davlat budjeti mablag'lari hisobidan oliy ma'lumot olish huquqiga ega. Oliy ta'lim tashkilotlari akademik erkinlik va o'zini o'zi boshqarish huquqiga ega.",
        "full_text": "1. Fuqarolar davlat ta'lim tashkilotlarida tanlov asosida davlat budjeti mablag'lari hisobidan oliy ma'lumot olish huquqiga ega.\n2. Oliy ta'lim tashkilotlari qonunga muvofiq akademik erkinlik, o'zini o'zi boshqarish, tadqiqotlar o'tkazish va o'qitish erkinligi huquqiga ega.",
        "text": "1. Fuqarolar davlat ta'lim tashkilotlarida tanlov asosida davlat budjeti mablag'lari hisobidan oliy ma'lumot olish huquqiga ega.\n2. Oliy ta'lim tashkilotlari qonunga muvofiq akademik erkinlik, o'zini o'zi boshqarish, tadqiqotlar o'tkazish va o'qitish erkinligi huquqiga ega.",
        "keywords": [
            "oliy ma'lumot",
            "davlat granti",
            "akademik erkinlik",
            "konstitutsiya 51",
            "o'zini o'zi boshqarish",
            "tanlov asosida"
        ],
        "related_faq_ids": [
            18,
            19,
            20,
            22,
            23,
            24,
            25,
            40,
            43
        ]
    },
    {
        "code": "CONST-52",
        "section_id": 1,
        "section_name": "Konstitutsiyaviy Ta'lim Huquqi va Pedagog Maqomi",
        "title": "O'zbekiston Respublikasi Konstitutsiyasi 52-moddasi",
        "category": "Konstitutsiya",
        "doc_number": "52",
        "doc_date": "2023-yil 30-aprel",
        "lex_url": "https://lex.uz/docs/-6445145",
        "summary": "O'qituvchining mehnati jamiyat va davlatni rivojlantirishning asosi sifatida e'tirof etiladi. Davlat o'qituvchilarning sha'ni va qadr-qimmatini himoya qiladi, moddiy farovonligi va kasbiy o'sishi to'g'risida g'amxo'rlik qiladi.",
        "full_text": "1. O'zbekiston Respublikasida o'qituvchining mehnati jamiyat va davlatni rivojlantirish, sog'lom, barkamol avlodni shakllantirish hamda tarbiyalash, xalqning ma'naviy va madaniy salohiyatini saqlash hamda boyitishning asosi sifatida e'tirof etiladi.\n2. Davlat o'qituvchilarning sha'ni va qadr-qimmatini himoya qilish, ularning ijtimoiy va moddiy farovonligi, kasbiy jihatdan o'sishi to'g'risida g'amxo'rlik qiladi.",
        "text": "1. O'zbekiston Respublikasida o'qituvchining mehnati jamiyat va davlatni rivojlantirish, sog'lom, barkamol avlodni shakllantirish hamda tarbiyalash, xalqning ma'naviy va madaniy salohiyatini saqlash hamda boyitishning asosi sifatida e'tirof etiladi.\n2. Davlat o'qituvchilarning sha'ni va qadr-qimmatini himoya qilish, ularning ijtimoiy va moddiy farovonligi, kasbiy jihatdan o'sishi to'g'risida g'amxo'rlik qiladi.",
        "keywords": [
            "pedagog mehnati",
            "o'qituvchi sha'ni",
            "pedagog huquqi",
            "konstitutsiya 52",
            "qadr-qimmati",
            "ijtimoiy himoya",
            "kasbiy o'sish"
        ],
        "related_faq_ids": [
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            32,
            33,
            34,
            35,
            36,
            37,
            49
        ]
    },
    {
        "code": "CONST-77",
        "section_id": 1,
        "section_name": "Konstitutsiyaviy Ta'lim Huquqi va Pedagog Maqomi",
        "title": "O'zbekiston Respublikasi Konstitutsiyasi 77-moddasi 2-qismi",
        "category": "Konstitutsiya",
        "doc_number": "77",
        "doc_date": "2023-yil 30-aprel",
        "lex_url": "https://lex.uz/docs/-6445145",
        "summary": "Ota-onalar va ularning o'rnini bosuvchi shaxslar o'z farzandlarini voyaga yetguniga qadar boqishi, ularning tarbiyasi, ta'lim olishi, sog'lom va har tomonlama kamol topishi to'g'risida g'amxo'rlik qilishga majburdirlar.",
        "full_text": "Ota-onalar va ularning o'rnini bosuvchi shaxslar o'z farzandlarini voyaga yetguniga qadar boqishi, ularning tarbiyasi, ta'lim olishi, sog'lom, to'laqonli va har tomonlama kamol topishi xususida g'amxo'rlik qilishga majburdirlar.",
        "text": "Ota-onalar va ularning o'rnini bosuvchi shaxslar o'z farzandlarini voyaga yetguniga qadar boqishi, ularning tarbiyasi, ta'lim olishi, sog'lom, to'laqonli va har tomonlama kamol topishi xususida g'amxo'rlik qilishga majburdirlar.",
        "keywords": [
            "ota-ona majburiyati",
            "farzand tarbiyasi",
            "ta'lim majburiyati",
            "konstitutsiya 77",
            "g'amxo'rlik"
        ],
        "related_faq_ids": [
            1,
            2,
            5,
            27,
            46
        ]
    },
    {
        "code": "ORQ-637",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 3-modda: Ta'lim sohasidagi asosiy tushunchalar",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "standart, akkreditatsiya, inklyuziv ta'lim, malaka ramkasi",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 3-modda: Ta'lim sohasidagi asosiy tushunchalar. Mazmuni: standart, akkreditatsiya, inklyuziv ta'lim, malaka ramkasi.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 3-modda: Ta'lim sohasidagi asosiy tushunchalar. Mazmuni: standart, akkreditatsiya, inklyuziv ta'lim, malaka ramkasi.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "asosiy tushunchalar",
            "ta'lim qonuni",
            "orq-637",
            "3-modda:",
            "ta'lim",
            "sohasidagi",
            "asosiy",
            "tushunchalar"
        ],
        "related_faq_ids": [
            7,
            20,
            28,
            44
        ]
    },
    {
        "code": "ORQ-637-ART-4",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 4-modda: Ta'lim sohasidagi asosiy prinsiplar",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "jinsi, irqi, millatidan qat'i nazar teng huquqlilik, bepul umumiy o'rta ta'lim, dunyoviylik",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 4-modda: Ta'lim sohasidagi asosiy prinsiplar. Mazmuni: jinsi, irqi, millatidan qat'i nazar teng huquqlilik, bepul umumiy o'rta ta'lim, dunyoviylik.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 4-modda: Ta'lim sohasidagi asosiy prinsiplar. Mazmuni: jinsi, irqi, millatidan qat'i nazar teng huquqlilik, bepul umumiy o'rta ta'lim, dunyoviylik.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "4-modda:",
            "ta'lim",
            "sohasidagi",
            "asosiy",
            "prinsiplar"
        ],
        "related_faq_ids": [
            2,
            3,
            6,
            7
        ]
    },
    {
        "code": "ORQ-637-ART-7",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 7-modda: Ta'lim turlari",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "maktabgacha, umumiy o'rta, o'rta maxsus, professional, oliy, oliy o'quv yurtidan keyingi, qayta tayyorlash",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 7-modda: Ta'lim turlari. Mazmuni: maktabgacha, umumiy o'rta, o'rta maxsus, professional, oliy, oliy o'quv yurtidan keyingi, qayta tayyorlash.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 7-modda: Ta'lim turlari. Mazmuni: maktabgacha, umumiy o'rta, o'rta maxsus, professional, oliy, oliy o'quv yurtidan keyingi, qayta tayyorlash.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "7-modda:",
            "ta'lim",
            "turlari"
        ],
        "related_faq_ids": [
            1,
            10,
            16,
            18
        ]
    },
    {
        "code": "ORQ-637-ART-8",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 8-modda: Maktabgacha ta'lim va tarbiya",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "oila, davlat va nodavlat tashkilotlar, 6 yoshdan 7 yoshgacha 1 yillik majburiy bepul tayyorlov",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 8-modda: Maktabgacha ta'lim va tarbiya. Mazmuni: oila, davlat va nodavlat tashkilotlar, 6 yoshdan 7 yoshgacha 1 yillik majburiy bepul tayyorlov.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 8-modda: Maktabgacha ta'lim va tarbiya. Mazmuni: oila, davlat va nodavlat tashkilotlar, 6 yoshdan 7 yoshgacha 1 yillik majburiy bepul tayyorlov.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "8-modda:",
            "maktabgacha",
            "ta'lim",
            "tarbiya"
        ],
        "related_faq_ids": [
            16,
            17
        ]
    },
    {
        "code": "ORQ-637-ART-9",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 9-modda: Umumiy o'rta va o'rta maxsus ta'lim",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "bepullik, 1-sinfga 7 yoshga to'ladigan yilda qabul qilish kafolati, majburiylik",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 9-modda: Umumiy o'rta va o'rta maxsus ta'lim. Mazmuni: bepullik, 1-sinfga 7 yoshga to'ladigan yilda qabul qilish kafolati, majburiylik.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 9-modda: Umumiy o'rta va o'rta maxsus ta'lim. Mazmuni: bepullik, 1-sinfga 7 yoshga to'ladigan yilda qabul qilish kafolati, majburiylik.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "9-modda:",
            "umumiy",
            "o'rta",
            "maxsus",
            "ta'lim"
        ],
        "related_faq_ids": [
            1,
            4,
            5,
            8,
            27
        ]
    },
    {
        "code": "ORQ-637-ART-10",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 10-modda: Professional ta'lim bosqichlari",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "kasb-hunar maktablari, kollejlar va texnikumlar",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 10-modda: Professional ta'lim bosqichlari. Mazmuni: kasb-hunar maktablari, kollejlar va texnikumlar.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 10-modda: Professional ta'lim bosqichlari. Mazmuni: kasb-hunar maktablari, kollejlar va texnikumlar.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "10-modda:",
            "professional",
            "ta'lim",
            "bosqichlari"
        ],
        "related_faq_ids": [
            1,
            10
        ]
    },
    {
        "code": "ORQ-637-ART-11",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 11-modda: Oliy ta'lim bosqichlari",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "bakalavriat va magistratura, davlat granti va to'lov-shartnoma asoslari",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 11-modda: Oliy ta'lim bosqichlari. Mazmuni: bakalavriat va magistratura, davlat granti va to'lov-shartnoma asoslari.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 11-modda: Oliy ta'lim bosqichlari. Mazmuni: bakalavriat va magistratura, davlat granti va to'lov-shartnoma asoslari.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "11-modda:",
            "oliy",
            "ta'lim",
            "bosqichlari"
        ],
        "related_faq_ids": [
            18,
            19,
            20,
            40
        ]
    },
    {
        "code": "ORQ-637-ART-12",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 12-modda: Oliy ta'limdan keyingi ta'lim",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "tayanch doktorantura PhD va doktorantura DSc, stajor-tadqiqotchilik",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 12-modda: Oliy ta'limdan keyingi ta'lim. Mazmuni: tayanch doktorantura PhD va doktorantura DSc, stajor-tadqiqotchilik.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 12-modda: Oliy ta'limdan keyingi ta'lim. Mazmuni: tayanch doktorantura PhD va doktorantura DSc, stajor-tadqiqotchilik.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "12-modda:",
            "oliy",
            "ta'limdan",
            "keyingi",
            "ta'lim"
        ],
        "related_faq_ids": [
            18,
            20
        ]
    },
    {
        "code": "ORQ-637-ART-13-14",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 13 va 14-moddalar: Kadrlarni qayta tayyorlash va maktabdan tashqari ta'lim",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "malaka oshirish, to'garaklar, musiqa va san'at maktablari",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 13 va 14-moddalar: Kadrlarni qayta tayyorlash va maktabdan tashqari ta'lim. Mazmuni: malaka oshirish, to'garaklar, musiqa va san'at maktablari.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 13 va 14-moddalar: Kadrlarni qayta tayyorlash va maktabdan tashqari ta'lim. Mazmuni: malaka oshirish, to'garaklar, musiqa va san'at maktablari.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "14-moddalar:",
            "kadrlarni",
            "qayta",
            "tayyorlash",
            "maktabdan",
            "tashqari",
            "ta'lim"
        ],
        "related_faq_ids": [
            12,
            13
        ]
    },
    {
        "code": "ORQ-637-ART-15",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 15-modda: Ta'lim olish shakllari",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "kunduzgi, sirtqi, kechki, masofaviy, dual, inklyuziv, oilaviy va mustaqil ta'lim",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 15-modda: Ta'lim olish shakllari. Mazmuni: kunduzgi, sirtqi, kechki, masofaviy, dual, inklyuziv, oilaviy va mustaqil ta'lim.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 15-modda: Ta'lim olish shakllari. Mazmuni: kunduzgi, sirtqi, kechki, masofaviy, dual, inklyuziv, oilaviy va mustaqil ta'lim.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "15-modda:",
            "ta'lim",
            "olish",
            "shakllari"
        ],
        "related_faq_ids": [
            39,
            43,
            48
        ]
    },
    {
        "code": "ORQ-637-ART-20",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 20-modda: Inklyuziv ta'lim kafolatlari",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "alohida ta'lim ehtiyojlari bo'lgan bolalarning umumiy maktabda teng ta'lim olishi",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 20-modda: Inklyuziv ta'lim kafolatlari. Mazmuni: alohida ta'lim ehtiyojlari bo'lgan bolalarning umumiy maktabda teng ta'lim olishi.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 20-modda: Inklyuziv ta'lim kafolatlari. Mazmuni: alohida ta'lim ehtiyojlari bo'lgan bolalarning umumiy maktabda teng ta'lim olishi.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "20-modda:",
            "inklyuziv",
            "ta'lim",
            "kafolatlari"
        ],
        "related_faq_ids": [
            7,
            38
        ]
    },
    {
        "code": "ORQ-637-ART-21-22",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 21 va 22-moddalar: Ta'lim berish tili va davlat ta'lim standartlari",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "davlat tili va boshqa tillar, davlat ta'lim standartlari majburiyligi",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 21 va 22-moddalar: Ta'lim berish tili va davlat ta'lim standartlari. Mazmuni: davlat tili va boshqa tillar, davlat ta'lim standartlari majburiyligi.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 21 va 22-moddalar: Ta'lim berish tili va davlat ta'lim standartlari. Mazmuni: davlat tili va boshqa tillar, davlat ta'lim standartlari majburiyligi.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "22-moddalar:",
            "ta'lim",
            "berish",
            "tili",
            "davlat",
            "standartlari"
        ],
        "related_faq_ids": [
            8,
            49
        ]
    },
    {
        "code": "ORQ-637-ART-29",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 29-modda: Nodavlat ta'lim tashkilotlari maqomi va diplomlar tengligi",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "litsenziya asosida faoliyat, berilgan diplomlarning davlat diplomi bilan teng yuridik kuchi",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 29-modda: Nodavlat ta'lim tashkilotlari maqomi va diplomlar tengligi. Mazmuni: litsenziya asosida faoliyat, berilgan diplomlarning davlat diplomi bilan teng yuridik kuchi.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 29-modda: Nodavlat ta'lim tashkilotlari maqomi va diplomlar tengligi. Mazmuni: litsenziya asosida faoliyat, berilgan diplomlarning davlat diplomi bilan teng yuridik kuchi.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "29-modda:",
            "nodavlat",
            "ta'lim",
            "tashkilotlari",
            "maqomi",
            "diplomlar",
            "tengligi"
        ],
        "related_faq_ids": [
            25,
            44,
            45,
            49
        ]
    },
    {
        "code": "ORQ-637-ART-41",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 41-modda: Ta'lim oluvchilarning huquq va majburiyatlari",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "sha'ni daxlsizligi, darsdan noqonuniy chetlatilmaslik, darsliklardan bepul foydalanish",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 41-modda: Ta'lim oluvchilarning huquq va majburiyatlari. Mazmuni: sha'ni daxlsizligi, darsdan noqonuniy chetlatilmaslik, darsliklardan bepul foydalanish.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 41-modda: Ta'lim oluvchilarning huquq va majburiyatlari. Mazmuni: sha'ni daxlsizligi, darsdan noqonuniy chetlatilmaslik, darsliklardan bepul foydalanish.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "41-modda:",
            "ta'lim",
            "oluvchilarning",
            "huquq",
            "majburiyatlari"
        ],
        "related_faq_ids": [
            3,
            4,
            6,
            27,
            41
        ]
    },
    {
        "code": "ORQ-637-ART-44",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 44-modda: Pedagogik faoliyat bilan shug'ullanish huquqi",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "pedagogik ma'lumot talabi, og'ir jinoyat sodir etgan shaxslarga qo'yiladigan taqiqlar",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 44-modda: Pedagogik faoliyat bilan shug'ullanish huquqi. Mazmuni: pedagogik ma'lumot talabi, og'ir jinoyat sodir etgan shaxslarga qo'yiladigan taqiqlar.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 44-modda: Pedagogik faoliyat bilan shug'ullanish huquqi. Mazmuni: pedagogik ma'lumot talabi, og'ir jinoyat sodir etgan shaxslarga qo'yiladigan taqiqlar.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "44-modda:",
            "pedagogik",
            "faoliyat",
            "bilan",
            "shug'ullanish",
            "huquqi"
        ],
        "related_faq_ids": [
            9,
            10,
            36
        ]
    },
    {
        "code": "ORQ-637-ART-47",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 47-modda: Ota-onalar majburiyatlari va noqonuniy pul yig'imlar taqiqi",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "farzand ta'limi uchun mas'uliyat, pul yig'ish noqonuniyligi",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 47-modda: Ota-onalar majburiyatlari va noqonuniy pul yig'imlar taqiqi. Mazmuni: farzand ta'limi uchun mas'uliyat, pul yig'ish noqonuniyligi.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 47-modda: Ota-onalar majburiyatlari va noqonuniy pul yig'imlar taqiqi. Mazmuni: farzand ta'limi uchun mas'uliyat, pul yig'ish noqonuniyligi.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "47-modda:",
            "ota-onalar",
            "majburiyatlari",
            "noqonuniy",
            "yig'imlar",
            "taqiqi"
        ],
        "related_faq_ids": [
            2,
            5,
            27
        ]
    },
    {
        "code": "ORQ-637-ART-62",
        "section_id": 2,
        "section_name": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637)",
        "title": "'Ta'lim to'g'risida'gi Qonun (O'RQ-637) — 62-modda: Xorijiy diplomlarni tan olish (nostrifikatsiya)",
        "category": "Qonun",
        "doc_number": "O'RQ-637",
        "doc_date": "2020-yil 23-sentyabr",
        "lex_url": "https://lex.uz/docs/-5013007",
        "summary": "xorijiy davlatlarda berilgan ta'lim to'g'risidagi hujjatlarni tan olish tartibi",
        "full_text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 62-modda: Xorijiy diplomlarni tan olish (nostrifikatsiya). Mazmuni: xorijiy davlatlarda berilgan ta'lim to'g'risidagi hujjatlarni tan olish tartibi.",
        "text": "O'zbekiston Respublikasi 'Ta'lim to'g'risida'gi Qonunining 62-modda: Xorijiy diplomlarni tan olish (nostrifikatsiya). Mazmuni: xorijiy davlatlarda berilgan ta'lim to'g'risidagi hujjatlarni tan olish tartibi.",
        "keywords": [
            "o'rq-637",
            "ta'lim to'g'risida",
            "62-modda:",
            "xorijiy",
            "diplomlarni",
            "olish",
            "(nostrifikatsiya)"
        ],
        "related_faq_ids": [
            25,
            32
        ]
    },
    {
        "code": "ORQ-901",
        "section_id": 3,
        "section_name": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901)",
        "title": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901) — 1 va 2-moddalar: Qonunning maqsadi va qo'llanish sohasi",
        "category": "Qonun",
        "doc_number": "O'RQ-901",
        "doc_date": "2024-yil 1-fevral",
        "lex_url": "https://lex.uz/docs/-6831415",
        "summary": "pedagogning huquqiy maqomini belgilash, barcha ta'lim tashkilotlariga tatbiq etilishi",
        "full_text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 1 va 2-moddalar: Qonunning maqsadi va qo'llanish sohasi. Mazmuni: pedagogning huquqiy maqomini belgilash, barcha ta'lim tashkilotlariga tatbiq etilishi.",
        "text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 1 va 2-moddalar: Qonunning maqsadi va qo'llanish sohasi. Mazmuni: pedagogning huquqiy maqomini belgilash, barcha ta'lim tashkilotlariga tatbiq etilishi.",
        "keywords": [
            "o'rq-901",
            "pedagog maqomi",
            "pedagogning maqomi to'g'risida",
            "majburiy mehnat taqiqlangan",
            "orq-901",
            "2-moddalar:",
            "qonunning",
            "maqsadi",
            "qo'llanish",
            "sohasi"
        ],
        "related_faq_ids": [
            9,
            10
        ]
    },
    {
        "code": "ORQ-901-ART-3",
        "section_id": 3,
        "section_name": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901)",
        "title": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901) — 3-modda: Pedagogning huquqiy maqomi va asosiy prinsiplari",
        "category": "Qonun",
        "doc_number": "O'RQ-901",
        "doc_date": "2024-yil 1-fevral",
        "lex_url": "https://lex.uz/docs/-6831415",
        "summary": "pedagog shaxsining daxlsizligi, kasbiy faoliyatga noqonuniy aralashmaslik, hurmat va e'tirof",
        "full_text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 3-modda: Pedagogning huquqiy maqomi va asosiy prinsiplari. Mazmuni: pedagog shaxsining daxlsizligi, kasbiy faoliyatga noqonuniy aralashmaslik, hurmat va e'tirof.",
        "text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 3-modda: Pedagogning huquqiy maqomi va asosiy prinsiplari. Mazmuni: pedagog shaxsining daxlsizligi, kasbiy faoliyatga noqonuniy aralashmaslik, hurmat va e'tirof.",
        "keywords": [
            "o'rq-901",
            "pedagog maqomi",
            "3-modda:",
            "pedagogning",
            "huquqiy",
            "maqomi",
            "asosiy",
            "prinsiplari"
        ],
        "related_faq_ids": [
            9,
            10,
            31
        ]
    },
    {
        "code": "ORQ-901-ART-4",
        "section_id": 3,
        "section_name": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901)",
        "title": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901) — 4-modda: Pedagogik odob-axloq qoidalari",
        "category": "Qonun",
        "doc_number": "O'RQ-901",
        "doc_date": "2024-yil 1-fevral",
        "lex_url": "https://lex.uz/docs/-6831415",
        "summary": "xizmat vazifalarini bajarishdagi axloqiy mezonlar, vatanparvarlik va manfaatlar to'qnashuvi taqiqi",
        "full_text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 4-modda: Pedagogik odob-axloq qoidalari. Mazmuni: xizmat vazifalarini bajarishdagi axloqiy mezonlar, vatanparvarlik va manfaatlar to'qnashuvi taqiqi.",
        "text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 4-modda: Pedagogik odob-axloq qoidalari. Mazmuni: xizmat vazifalarini bajarishdagi axloqiy mezonlar, vatanparvarlik va manfaatlar to'qnashuvi taqiqi.",
        "keywords": [
            "o'rq-901",
            "pedagog maqomi",
            "4-modda:",
            "pedagogik",
            "odob-axloq",
            "qoidalari"
        ],
        "related_faq_ids": [
            10,
            37
        ]
    },
    {
        "code": "ORQ-901-ART-5",
        "section_id": 3,
        "section_name": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901)",
        "title": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901) — 5-modda: Pedagogning kasbiy huquqlari",
        "category": "Qonun",
        "doc_number": "O'RQ-901",
        "doc_date": "2024-yil 1-fevral",
        "lex_url": "https://lex.uz/docs/-6831415",
        "summary": "metodik erkinlik, mualliflik dasturlari yaratish, ortiqcha qog'ozbozlik va hisobotlardan bosh tortish",
        "full_text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 5-modda: Pedagogning kasbiy huquqlari. Mazmuni: metodik erkinlik, mualliflik dasturlari yaratish, ortiqcha qog'ozbozlik va hisobotlardan bosh tortish.",
        "text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 5-modda: Pedagogning kasbiy huquqlari. Mazmuni: metodik erkinlik, mualliflik dasturlari yaratish, ortiqcha qog'ozbozlik va hisobotlardan bosh tortish.",
        "keywords": [
            "o'rq-901",
            "pedagog maqomi",
            "5-modda:",
            "pedagogning",
            "kasbiy",
            "huquqlari"
        ],
        "related_faq_ids": [
            10,
            11,
            33
        ]
    },
    {
        "code": "ORQ-901-ART-6",
        "section_id": 3,
        "section_name": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901)",
        "title": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901) — 6-modda: Pedagog faoliyatiga aralashishga yo'l qo'yilmasligi",
        "category": "Qonun",
        "doc_number": "O'RQ-901",
        "doc_date": "2024-yil 1-fevral",
        "lex_url": "https://lex.uz/docs/-6831415",
        "summary": "obodonlashtirish, tadbirlar, obuna majburlash, bahoga ta'sir o'tkazish qat'iyan taqiqlanishi",
        "full_text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 6-modda: Pedagog faoliyatiga aralashishga yo'l qo'yilmasligi. Mazmuni: obodonlashtirish, tadbirlar, obuna majburlash, bahoga ta'sir o'tkazish qat'iyan taqiqlanishi.",
        "text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 6-modda: Pedagog faoliyatiga aralashishga yo'l qo'yilmasligi. Mazmuni: obodonlashtirish, tadbirlar, obuna majburlash, bahoga ta'sir o'tkazish qat'iyan taqiqlanishi.",
        "keywords": [
            "o'rq-901",
            "pedagog maqomi",
            "6-modda:",
            "pedagog",
            "faoliyatiga",
            "aralashishga",
            "yo'l",
            "qo'yilmasligi"
        ],
        "related_faq_ids": [
            9,
            10,
            33
        ]
    },
    {
        "code": "ORQ-901-ART-7",
        "section_id": 3,
        "section_name": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901)",
        "title": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901) — 7-modda: Pedagogning sha'ni, qadr-qimmati va ishchanlik obro'sini himoya qilish",
        "category": "Qonun",
        "doc_number": "O'RQ-901",
        "doc_date": "2024-yil 1-fevral",
        "lex_url": "https://lex.uz/docs/-6831415",
        "summary": "davlat himoyasi, ota-onalar va mansabdorlar tomonidan haqorat yoki bosimga yo'l qo'yilmasligi",
        "full_text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 7-modda: Pedagogning sha'ni, qadr-qimmati va ishchanlik obro'sini himoya qilish. Mazmuni: davlat himoyasi, ota-onalar va mansabdorlar tomonidan haqorat yoki bosimga yo'l qo'yilmasligi.",
        "text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 7-modda: Pedagogning sha'ni, qadr-qimmati va ishchanlik obro'sini himoya qilish. Mazmuni: davlat himoyasi, ota-onalar va mansabdorlar tomonidan haqorat yoki bosimga yo'l qo'yilmasligi.",
        "keywords": [
            "o'rq-901",
            "pedagog maqomi",
            "7-modda:",
            "pedagogning",
            "sha'ni,",
            "qadr-qimmati",
            "ishchanlik",
            "obro'sini",
            "himoya",
            "qilish"
        ],
        "related_faq_ids": [
            10,
            37
        ]
    },
    {
        "code": "ORQ-901-ART-8-9",
        "section_id": 3,
        "section_name": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901)",
        "title": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901) — 8 va 9-moddalar: Kasbiy majburiyatlar va faoliyatga qo'yilmaydigan cheklovlar",
        "category": "Qonun",
        "doc_number": "O'RQ-901",
        "doc_date": "2024-yil 1-fevral",
        "lex_url": "https://lex.uz/docs/-6831415",
        "summary": "dars sifatini ta'minlash, og'ir jinoyat sodir etgan yoki dispanserda hisobda turganlarga taqiq",
        "full_text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 8 va 9-moddalar: Kasbiy majburiyatlar va faoliyatga qo'yilmaydigan cheklovlar. Mazmuni: dars sifatini ta'minlash, og'ir jinoyat sodir etgan yoki dispanserda hisobda turganlarga taqiq.",
        "text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 8 va 9-moddalar: Kasbiy majburiyatlar va faoliyatga qo'yilmaydigan cheklovlar. Mazmuni: dars sifatini ta'minlash, og'ir jinoyat sodir etgan yoki dispanserda hisobda turganlarga taqiq.",
        "keywords": [
            "o'rq-901",
            "pedagog maqomi",
            "9-moddalar:",
            "kasbiy",
            "majburiyatlar",
            "faoliyatga",
            "qo'yilmaydigan",
            "cheklovlar"
        ],
        "related_faq_ids": [
            10,
            36
        ]
    },
    {
        "code": "ORQ-901-ART-10",
        "section_id": 3,
        "section_name": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901)",
        "title": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901) — 10-modda: Pedagog kadrlarni attestatsiyadan o'tkazish kafolatlari",
        "category": "Qonun",
        "doc_number": "O'RQ-901",
        "doc_date": "2024-yil 1-fevral",
        "lex_url": "https://lex.uz/docs/-6831415",
        "summary": "navbatdagi majburiy va navbatdan tashqari ixtiyoriy attestatsiya, toifa pasaytirilmasligi kafolati",
        "full_text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 10-modda: Pedagog kadrlarni attestatsiyadan o'tkazish kafolatlari. Mazmuni: navbatdagi majburiy va navbatdan tashqari ixtiyoriy attestatsiya, toifa pasaytirilmasligi kafolati.",
        "text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 10-modda: Pedagog kadrlarni attestatsiyadan o'tkazish kafolatlari. Mazmuni: navbatdagi majburiy va navbatdan tashqari ixtiyoriy attestatsiya, toifa pasaytirilmasligi kafolati.",
        "keywords": [
            "o'rq-901",
            "pedagog maqomi",
            "10-modda:",
            "pedagog",
            "kadrlarni",
            "attestatsiyadan",
            "o'tkazish",
            "kafolatlari"
        ],
        "related_faq_ids": [
            12,
            13
        ]
    },
    {
        "code": "ORQ-901-ART-11",
        "section_id": 3,
        "section_name": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901)",
        "title": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901) — 11-modda: Mehnat va dam olish vaqti",
        "category": "Qonun",
        "doc_number": "O'RQ-901",
        "doc_date": "2024-yil 1-fevral",
        "lex_url": "https://lex.uz/docs/-6831415",
        "summary": "qisqartirilgan haftalik 36 soatlik ish vaqti va 56 kalendar kunlik uzaytirilgan mehnat ta'tili",
        "full_text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 11-modda: Mehnat va dam olish vaqti. Mazmuni: qisqartirilgan haftalik 36 soatlik ish vaqti va 56 kalendar kunlik uzaytirilgan mehnat ta'tili.",
        "text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 11-modda: Mehnat va dam olish vaqti. Mazmuni: qisqartirilgan haftalik 36 soatlik ish vaqti va 56 kalendar kunlik uzaytirilgan mehnat ta'tili.",
        "keywords": [
            "o'rq-901",
            "pedagog maqomi",
            "11-modda:",
            "mehnat",
            "olish",
            "vaqti"
        ],
        "related_faq_ids": [
            11,
            14
        ]
    },
    {
        "code": "ORQ-901-ART-12-13",
        "section_id": 3,
        "section_name": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901)",
        "title": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901) — 12 va 13-moddalar: Mehnatga haq to'lash va ijtimoiy himoya choralari",
        "category": "Qonun",
        "doc_number": "O'RQ-901",
        "doc_date": "2024-yil 1-fevral",
        "lex_url": "https://lex.uz/docs/-6831415",
        "summary": "lavozim, toifa, dars soatlariga mos ish haqi, ipoteka va avtokredit imtiyozlari",
        "full_text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 12 va 13-moddalar: Mehnatga haq to'lash va ijtimoiy himoya choralari. Mazmuni: lavozim, toifa, dars soatlariga mos ish haqi, ipoteka va avtokredit imtiyozlari.",
        "text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 12 va 13-moddalar: Mehnatga haq to'lash va ijtimoiy himoya choralari. Mazmuni: lavozim, toifa, dars soatlariga mos ish haqi, ipoteka va avtokredit imtiyozlari.",
        "keywords": [
            "o'rq-901",
            "pedagog maqomi",
            "13-moddalar:",
            "mehnatga",
            "to'lash",
            "ijtimoiy",
            "himoya",
            "choralari"
        ],
        "related_faq_ids": [
            13,
            15,
            32,
            35
        ]
    },
    {
        "code": "ORQ-901-ART-14-16",
        "section_id": 3,
        "section_name": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901)",
        "title": "'Pedagogning maqomi to'g'risida'gi Qonun (O'RQ-901) — 14, 15 va 16-moddalar: Tibbiy ko'rik, bojlardan ozodlik va javobgarlik",
        "category": "Qonun",
        "doc_number": "O'RQ-901",
        "doc_date": "2024-yil 1-fevral",
        "lex_url": "https://lex.uz/docs/-6831415",
        "summary": "bepul majburiy tibbiy ko'rik, sudda davlat bojidan ozodlik, MJtK 197-5 bo'yicha jazo",
        "full_text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 14, 15 va 16-moddalar: Tibbiy ko'rik, bojlardan ozodlik va javobgarlik. Mazmuni: bepul majburiy tibbiy ko'rik, sudda davlat bojidan ozodlik, MJtK 197-5 bo'yicha jazo.",
        "text": "O'zbekiston Respublikasining 'Pedagogning maqomi to'g'risida'gi Qonuni 14, 15 va 16-moddalar: Tibbiy ko'rik, bojlardan ozodlik va javobgarlik. Mazmuni: bepul majburiy tibbiy ko'rik, sudda davlat bojidan ozodlik, MJtK 197-5 bo'yicha jazo.",
        "keywords": [
            "o'rq-901",
            "pedagog maqomi",
            "16-moddalar:",
            "tibbiy",
            "ko'rik,",
            "bojlardan",
            "ozodlik",
            "javobgarlik"
        ],
        "related_faq_ids": [
            10,
            37,
            49
        ]
    },
    {
        "code": "PF-81",
        "section_id": 4,
        "section_name": "Oliy Ta'lim Sohasidagi Asosiy Islohotlar va Hukumat Nizomlari",
        "title": "Prezidentning PF-81-son Farmoni",
        "category": "Prezident Farmoni",
        "doc_number": "PF-81",
        "doc_date": "2024-yil 24-may",
        "lex_url": "https://lex.uz/docs/-6935398",
        "summary": "Bakalavriatga qabulning yangi tartibi: 'Avval test, so'ng tanlov', 15 kunlik muddatda 5 ta yo'nalish tanlash.",
        "full_text": "PF-81-son Farmon bilan oliy ta'limga qabul ikki bosqichga ajratildi: 1) Fanlar majmuasi bo'yicha test topshirish; 2) Test natijalari e'lon qilingach, 5 tagacha OTM va yo'nalishni tanlash. Davlat grantlari sohalar bo'yicha taqsimlanadi.",
        "text": "PF-81-son Farmon bilan oliy ta'limga qabul ikki bosqichga ajratildi: 1) Fanlar majmuasi bo'yicha test topshirish; 2) Test natijalari e'lon qilingach, 5 tagacha OTM va yo'nalishni tanlash. Davlat grantlari sohalar bo'yicha taqsimlanadi.",
        "keywords": [
            "avval test so'ng tanlov",
            "yangi qabul",
            "5 ta yo'nalish",
            "grant taqsimoti",
            "pf-81",
            "qabul",
            "tanlov",
            "avval test"
        ],
        "related_faq_ids": [
            18,
            40
        ]
    },
    {
        "code": "VMQ-149",
        "section_id": 4,
        "section_name": "Oliy Ta'lim Sohasidagi Asosiy Islohotlar va Hukumat Nizomlari",
        "title": "Vazirlar Mahkamasining 149-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-149",
        "doc_date": "2025-yil 10-mart",
        "lex_url": "https://lex.uz/docs/-7429154",
        "summary": "Davlat grantlarini GPA reytingi bo'yicha har yili qayta taqsimlash nizomi (100% grant, 50% grant).",
        "full_text": "2024/2025-o'quv yilidan boshlab davlat granti talabaga 1 yil muddatga beriladi. 2-kursdan boshlab HEMIS tizimidagi GPA ko'rsatkichi 4.0+ bo'lgan kontrakt talabalariga 100% grant, GPA 3.5-3.9 bo'lganlarga 50% grant beriladi. O'zlashtirmagan grant talabalari kontraktga o'tkaziladi.",
        "text": "2024/2025-o'quv yilidan boshlab davlat granti talabaga 1 yil muddatga beriladi. 2-kursdan boshlab HEMIS tizimidagi GPA ko'rsatkichi 4.0+ bo'lgan kontrakt talabalariga 100% grant, GPA 3.5-3.9 bo'lganlarga 50% grant beriladi. O'zlashtirmagan grant talabalari kontraktga o'tkaziladi.",
        "keywords": [
            "gpa reytingi",
            "grant qayta taqsimlash",
            "gpa 4.0",
            "100 foiz grant",
            "vmq-149",
            "grant taqsimoti",
            "yangi grant",
            "hemis"
        ],
        "related_faq_ids": [
            18,
            22
        ]
    },
    {
        "code": "VMQ-376",
        "section_id": 4,
        "section_name": "Oliy Ta'lim Sohasidagi Asosiy Islohotlar va Hukumat Nizomlari",
        "title": "Vazirlar Mahkamasining 376-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-376",
        "doc_date": "2023-yil 14-avgust",
        "lex_url": "https://lex.uz/docs/-6563604",
        "summary": "Talabalar turar joyiga joylashtirish bo'yicha davlat xizmatlari ko'rsatish ma'muriy reglamenti (my.gov.uz orqali ariza).",
        "full_text": "Davlat OTMlarining talabalar turar joyiga arizalar har yili 1-avgustdan my.gov.uz yoki DXM orqali elektron qabul qilinadi. Imtiyozli ro'yxatdagilar (chin yetimlar, nogironligi bo'lganlar, 'Ijtimoiy himoya yagona reyestri') navbatsiz qabul qilinadi.",
        "text": "Davlat OTMlarining talabalar turar joyiga arizalar har yili 1-avgustdan my.gov.uz yoki DXM orqali elektron qabul qilinadi. Imtiyozli ro'yxatdagilar (chin yetimlar, nogironligi bo'lganlar, 'Ijtimoiy himoya yagona reyestri') navbatsiz qabul qilinadi.",
        "keywords": [
            "ttj",
            "yotoqxona",
            "my.gov.uz",
            "yotoqxona arizasi",
            "vmq-376",
            "ariza"
        ],
        "related_faq_ids": [
            21
        ]
    },
    {
        "code": "VMQ-605",
        "section_id": 4,
        "section_name": "Oliy Ta'lim Sohasidagi Asosiy Islohotlar va Hukumat Nizomlari",
        "title": "Vazirlar Mahkamasining 605-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-605",
        "doc_date": "2021-yil 24-sentyabr",
        "lex_url": "https://lex.uz/docs/-5653457",
        "summary": "Talabalarga oylik ijara to'lovining 50 foizini davlat budjetidan qoplab berish tartibi.",
        "full_text": "Yotoqxonaga joylasha olmagan, ijarada yashovchi kunduzgi ta'lim talabalariga oylik ijaraning 50 foizi (Toshkentda BHM 1 baravarigacha, viloyatlarda 0.5 baravarigacha) davlat budjetidan to'lab beriladi. Ijara shartnomasi E-ijara soliq bazasida ro'yxatdan o'tgan bo'lishi shart.",
        "text": "Yotoqxonaga joylasha olmagan, ijarada yashovchi kunduzgi ta'lim talabalariga oylik ijaraning 50 foizi (Toshkentda BHM 1 baravarigacha, viloyatlarda 0.5 baravarigacha) davlat budjetidan to'lab beriladi. Ijara shartnomasi E-ijara soliq bazasida ro'yxatdan o'tgan bo'lishi shart.",
        "keywords": [
            "ijara",
            "ijara kompensatsiyasi",
            "50 foiz ijara",
            "talaba kvartira",
            "vmq-605",
            "50 foiz",
            "bhm"
        ],
        "related_faq_ids": [
            21
        ]
    },
    {
        "code": "VMQ-447",
        "section_id": 4,
        "section_name": "Oliy Ta'lim Sohasidagi Asosiy Islohotlar va Hukumat Nizomlari",
        "title": "Vazirlar Mahkamasining 447-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-447",
        "doc_date": "2022-yil 15-avgust",
        "lex_url": "https://lex.uz/docs/-6158223",
        "summary": "Davlat OTMlari magistraturasida tahsil olayotgan barcha xotin-qizlarning to'lov-kontraktini 100% davlat budjetidan qoplash.",
        "full_text": "Barcha davlat OTMlarining magistratura mutaxassisliklariga kontrakt asosida qabul qilingan barcha xotin-qizlarning kontrakt summasi to'liq 100% davlat budjetidan qoplab beriladi. Ariza my.gov.uz orqali yoki OTM rektoratiga topshiriladi.",
        "text": "Barcha davlat OTMlarining magistratura mutaxassisliklariga kontrakt asosida qabul qilingan barcha xotin-qizlarning kontrakt summasi to'liq 100% davlat budjetidan qoplab beriladi. Ariza my.gov.uz orqali yoki OTM rektoratiga topshiriladi.",
        "keywords": [
            "magistratura",
            "xotin-qizlar",
            "100 foiz bepul",
            "ayollar magistraturasi",
            "vmq-447",
            "100% bepul",
            "kontrakt qoplash"
        ],
        "related_faq_ids": [
            20
        ]
    },
    {
        "code": "VMQ-527-PF-87",
        "section_id": 4,
        "section_name": "Oliy Ta'lim Sohasidagi Asosiy Islohotlar va Hukumat Nizomlari",
        "title": "Vazirlar Mahkamasining 527-son qarori va PF-87-son Farmon",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-527",
        "doc_date": "2021-yil 18-avgust",
        "lex_url": "https://lex.uz/docs/-5583592",
        "summary": "Imtiyozli ta'lim kreditlari: xotin-qizlarga 0% (foizsiz), erkaklarga Markaziy bank asosiy stavkasida 7 yilga.",
        "full_text": "To'lov-kontrakt asosida o'qiyotgan talabalar uchun imtiyozli ta'lim krediti ajratiladi. Xotin-qizlarning foiz stavkasi 0% bo'lib, davlat jamg'armasi tomonidan to'lanadi. Asosiy qarz o'qish tamomlanganidan 7 oy o'tib, 7 yil davomida qaytariladi.",
        "text": "To'lov-kontrakt asosida o'qiyotgan talabalar uchun imtiyozli ta'lim krediti ajratiladi. Xotin-qizlarning foiz stavkasi 0% bo'lib, davlat jamg'armasi tomonidan to'lanadi. Asosiy qarz o'qish tamomlanganidan 7 oy o'tib, 7 yil davomida qaytariladi.",
        "keywords": [
            "ta'lim krediti",
            "0 foiz",
            "foizsiz kredit",
            "xotin-qizlar krediti",
            "vmq-527",
            "pf-87",
            "xotin-qizlar"
        ],
        "related_faq_ids": [
            38
        ]
    },
    {
        "code": "VMQ-59",
        "section_id": 4,
        "section_name": "Oliy Ta'lim Sohasidagi Asosiy Islohotlar va Hukumat Nizomlari",
        "title": "Vazirlar Mahkamasining 59-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-59",
        "doc_date": "2020-yil 31-yanvar",
        "lex_url": "https://lex.uz/docs/-4725068",
        "summary": "Talabalarga stipendiya tayinlash va to'lash tartibi (bazaviy stipendiya va reyting bo'yicha +20%).",
        "full_text": "Davlat granti va stipendiyali to'lov-kontrakt talabalariga har oy bazaviy stipendiya to'lanadi. Semestr yakunida barcha fanlardan 'a'lo' (86-100 ball) baholarga erishgan talabalarga stipendiya 20 foizga oshirilib to'lanadi.",
        "text": "Davlat granti va stipendiyali to'lov-kontrakt talabalariga har oy bazaviy stipendiya to'lanadi. Semestr yakunida barcha fanlardan 'a'lo' (86-100 ball) baholarga erishgan talabalarga stipendiya 20 foizga oshirilib to'lanadi.",
        "keywords": [
            "vmq-59",
            "stipendiya",
            "bazaviy stipendiya",
            "a'lochi stipendiya"
        ],
        "related_faq_ids": [
            22
        ]
    },
    {
        "code": "VMQ-824",
        "section_id": 4,
        "section_name": "Oliy Ta'lim Sohasidagi Asosiy Islohotlar va Hukumat Nizomlari",
        "title": "Vazirlar Mahkamasining 824-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-824",
        "doc_date": "2020-yil 31-dekabr",
        "lex_url": "https://lex.uz/docs/-5193557",
        "summary": "Oliy ta'limda kredit-modul tizimi (ECTS, 60 kredit/yil, dars qoldirish 25% limiti, retake tartibi).",
        "full_text": "Kredit-modul tizimida 1 yillik akademik yuklama 60 ECTS kreditni tashkil etadi. Talaba semestr davomida darslarning 25% dan ortig'ini sababsiz qoldirsa, talabalar safidan chetlashtiriladi. Fandan o'ta olmagan talaba yozgi semestrda (Summer school) qayta o'qishi (retake) shart.",
        "text": "Kredit-modul tizimida 1 yillik akademik yuklama 60 ECTS kreditni tashkil etadi. Talaba semestr davomida darslarning 25% dan ortig'ini sababsiz qoldirsa, talabalar safidan chetlashtiriladi. Fandan o'ta olmagan talaba yozgi semestrda (Summer school) qayta o'qishi (retake) shart.",
        "keywords": [
            "vmq-824",
            "kredit-modul",
            "ects",
            "retake",
            "qayta o'qish",
            "25 foiz"
        ],
        "related_faq_ids": [
            40,
            43
        ]
    },
    {
        "code": "VMQ-393-PQ-279",
        "section_id": 4,
        "section_name": "Oliy Ta'lim Sohasidagi Asosiy Islohotlar va Hukumat Nizomlari",
        "title": "Vazirlar Mahkamasining 393-son qarori va PQ-279-son qaror",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-393",
        "doc_date": "2017-yil 18-iyun",
        "lex_url": "https://lex.uz/docs/-3244181",
        "summary": "Talabalar o'qishini ko'chirish (perevod) va qayta tiklash: davlat OTMlararo ko'chirishga faqat 2 ta uzrli sabab.",
        "full_text": "Davlat OTMsidan boshqasiga o'qishni ko'chirishga faqat 2 sabab bilan ruxsat beriladi: 1) Talaba turmush qurishi munosabati bilan turmush o'rtog'i hududiga; 2) Davlat xizmatchisi bo'lgan ota-onasi yoki turmush o'rtog'i boshqa hududga xizmatga tayinlanganda. Nodavlat va xorijiy OTMlardan perevodda test sinovi topshirish shart.",
        "text": "Davlat OTMsidan boshqasiga o'qishni ko'chirishga faqat 2 sabab bilan ruxsat beriladi: 1) Talaba turmush qurishi munosabati bilan turmush o'rtog'i hududiga; 2) Davlat xizmatchisi bo'lgan ota-onasi yoki turmush o'rtog'i boshqa hududga xizmatga tayinlanganda. Nodavlat va xorijiy OTMlardan perevodda test sinovi topshirish shart.",
        "keywords": [
            "vmq-393",
            "pq-279",
            "perevod",
            "o'qishni ko'chirish",
            "uzrli sabab"
        ],
        "related_faq_ids": [
            23
        ]
    },
    {
        "code": "VMQ-344",
        "section_id": 4,
        "section_name": "Oliy Ta'lim Sohasidagi Asosiy Islohotlar va Hukumat Nizomlari",
        "title": "Vazirlar Mahkamasining 344-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-344",
        "doc_date": "2021-yil 3-iyun",
        "lex_url": "https://lex.uz/docs/-5444390",
        "summary": "Talabalarga akademik ta'til berish tartibi: harbiy xizmat, salomatlik, homiladorlik va bola parvarishi.",
        "full_text": "Akademik ta'til davrida talaba OTM safidan chiqarilmaydi. Davlat granti joyi to'liq saqlanadi. Qaytganida to'xtagan semestridan o'qishni davom ettiradi. Akademik ta'tilda kontrakt yoki stipendiya to'lanmaydi.",
        "text": "Akademik ta'til davrida talaba OTM safidan chiqarilmaydi. Davlat granti joyi to'liq saqlanadi. Qaytganida to'xtagan semestridan o'qishni davom ettiradi. Akademik ta'tilda kontrakt yoki stipendiya to'lanmaydi.",
        "keywords": [
            "vmq-344",
            "akademik ta'til",
            "tmk xulosasi",
            "grant saqlanishi"
        ],
        "related_faq_ids": [
            24
        ]
    },
    {
        "code": "VMQ-620",
        "section_id": 4,
        "section_name": "Oliy Ta'lim Sohasidagi Asosiy Islohotlar va Hukumat Nizomlari",
        "title": "Vazirlar Mahkamasining 620-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-620",
        "doc_date": "2019-yil 24-iyul",
        "lex_url": "https://lex.uz/docs/-4438343",
        "summary": "Xorijiy diplomlarni tan olish (nostrifikatsiya): TOP-1000 universitetlar diplomlarini to'g'ridan-to'g'ri imtihonsiz tan olish.",
        "full_text": "Xalqaro reytinglarda (QS, THE, ARWU) birinchi 1000 talikka kirgan xorijiy OTMlar diplomlari O'zbekistonda hech qanday sinovlarsiz to'g'ridan-to'g'ri tan olinadi. Boshqa diplomlar mutaxassislik testlaridan o'tgach tan olinadi. Arizalar my.gov.uz orqali beriladi.",
        "text": "Xalqaro reytinglarda (QS, THE, ARWU) birinchi 1000 talikka kirgan xorijiy OTMlar diplomlari O'zbekistonda hech qanday sinovlarsiz to'g'ridan-to'g'ri tan olinadi. Boshqa diplomlar mutaxassislik testlaridan o'tgach tan olinadi. Arizalar my.gov.uz orqali beriladi.",
        "keywords": [
            "vmq-620",
            "nostrifikatsiya",
            "top-1000",
            "diplom tan olish",
            "my.gov.uz"
        ],
        "related_faq_ids": [
            25,
            32
        ]
    },
    {
        "code": "VMQ-214",
        "section_id": 4,
        "section_name": "Oliy Ta'lim Sohasidagi Asosiy Islohotlar va Hukumat Nizomlari",
        "title": "Vazirlar Mahkamasining 214-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-214",
        "doc_date": "2022-yil 3-oktyabr",
        "lex_url": "https://lex.uz/docs/-6221774",
        "summary": "OTMlarda masofaviy ta'lim shaklini tashkil etish va joriy etish nizomi (LMS, yakuniy nazorat OTMda).",
        "full_text": "OTMlarda masofaviy ta'lim platformasi (LMS) yaratiladi. Yakuniy nazoratlar va diplom himoyasi talabaning bevosita OTMda ishtirokida o'tkaziladi. Masofaviy ta'lim diplomi kunduzgi ta'lim diplomi bilan teng yuridik kuchga ega.",
        "text": "OTMlarda masofaviy ta'lim platformasi (LMS) yaratiladi. Yakuniy nazoratlar va diplom himoyasi talabaning bevosita OTMda ishtirokida o'tkaziladi. Masofaviy ta'lim diplomi kunduzgi ta'lim diplomi bilan teng yuridik kuchga ega.",
        "keywords": [
            "vmq-214",
            "masofaviy ta'lim",
            "lms",
            "onlayn o'qish",
            "diplom tengligi"
        ],
        "related_faq_ids": [
            48
        ]
    },
    {
        "code": "VMQ-295",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "Vazirlar Mahkamasining 295-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-295",
        "doc_date": "2022-yil 1-iyun",
        "lex_url": "https://lex.uz/docs/-6045952",
        "summary": "Bolalarni 1-sinfga qabul qilish va maktabdan maktabga ko'chirish bo'yicha ma'muriy reglamentlar.",
        "full_text": "1-bosqichda 20-iyundan 31-iyulgacha mikrohudud bo'yicha my.maktab.uz orqali bepul qabul qilinadi. 2-bosqichda 1-avgustdan 15-avgustgacha mikrohududdan tashqari bo'sh o'rinlar to'ldiriladi. Imtihon o'tkazish taqiqlanadi.",
        "text": "1-bosqichda 20-iyundan 31-iyulgacha mikrohudud bo'yicha my.maktab.uz orqali bepul qabul qilinadi. 2-bosqichda 1-avgustdan 15-avgustgacha mikrohududdan tashqari bo'sh o'rinlar to'ldiriladi. Imtihon o'tkazish taqiqlanadi.",
        "keywords": [
            "1-sinf",
            "1-sinfga qabul",
            "mikrohudud",
            "my.maktab.uz",
            "vmq-295",
            "maktabga qabul"
        ],
        "related_faq_ids": [
            1,
            5
        ]
    },
    {
        "code": "VMQ-140-SANQVAN",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "VMQ-140 va SanQvaN 0341-16",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-140",
        "doc_date": "2017-yil 15-mart",
        "lex_url": "https://lex.uz/docs/-3141443",
        "summary": "Umumiy o'rta ta'lim nizomi: sinfda 35 nafardan oshmaslik, 25+ bo'lganda 2 guruhga bo'lish, o'quvchini haydash taqiqlanishi.",
        "full_text": "Umumta'lim maktablarida bitta sinfda o'quvchilar soni ko'pi bilan 35 nafar bo'lishi shart. Sinfda 25 va undan ortiq o'quvchi bo'lsa, chet tili, informatika, o'zbek/rus tili fanlarida guruhlarga bo'linadi. O'quvchini darsdan haydash qat'iyan taqiqlanadi.",
        "text": "Umumta'lim maktablarida bitta sinfda o'quvchilar soni ko'pi bilan 35 nafar bo'lishi shart. Sinfda 25 va undan ortiq o'quvchi bo'lsa, chet tili, informatika, o'zbek/rus tili fanlarida guruhlarga bo'linadi. O'quvchini darsdan haydash qat'iyan taqiqlanadi.",
        "keywords": [
            "vmq-140",
            "sanqvan",
            "35 nafar",
            "guruhlarga bo'lish",
            "haydash taqiqlangan"
        ],
        "related_faq_ids": [
            3,
            4,
            8
        ]
    },
    {
        "code": "VMQ-666-558",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "VMQ-666 va VMQ-558-son qarorlar",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-666",
        "doc_date": "2018-yil 15-avgust",
        "lex_url": "https://lex.uz/docs/-3869279",
        "summary": "Yagona maktab formasi tartibi va kiyim sababli darsdan chetlashtirish taqiqlanishi (ro'mol va do'ppiga ruxsat).",
        "full_text": "Yagona maktab formasi talabi majburiy emas, tavsiyaviy hisoblanadi. O'quvchi qizlarning oq/och rangli ro'mol, o'g'il bolalarning do'ppida kelishiga to'sqinlik qilish man etiladi. Kiyimi tufayli darsga kiritmaslik noqonuniydir.",
        "text": "Yagona maktab formasi talabi majburiy emas, tavsiyaviy hisoblanadi. O'quvchi qizlarning oq/och rangli ro'mol, o'g'il bolalarning do'ppida kelishiga to'sqinlik qilish man etiladi. Kiyimi tufayli darsga kiritmaslik noqonuniydir.",
        "keywords": [
            "vmq-666",
            "vmq-558",
            "maktab formasi",
            "ro'mol",
            "do'ppi",
            "kiyim taqiqi"
        ],
        "related_faq_ids": [
            3
        ]
    },
    {
        "code": "PF-134-3515",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "Prezidentning PF-134-son Farmoni va 3515-sonli qaror",
        "category": "Prezident Farmoni",
        "doc_number": "PF-134",
        "doc_date": "2022-yil 11-may",
        "lex_url": "https://lex.uz/docs/-6009855",
        "summary": "Pedagoglarga xalqaro va milliy sertifikatlar uchun har oylik 20% dan 50% gacha ustamalar to'lash.",
        "full_text": "Xalqaro tan olingan sertifikatga (IELTS 7.0+, TOEFL 95+, CEFR C1) ega o'qituvchilarga har oy 50 foiz, milliy sertifikat (CEFR B2) egalariga 20 foiz ustama to'lanadi.",
        "text": "Xalqaro tan olingan sertifikatga (IELTS 7.0+, TOEFL 95+, CEFR C1) ega o'qituvchilarga har oy 50 foiz, milliy sertifikat (CEFR B2) egalariga 20 foiz ustama to'lanadi.",
        "keywords": [
            "pf-134",
            "3515-son",
            "sertifikat ustamasi",
            "ielts 50 foiz",
            "cefr b2"
        ],
        "related_faq_ids": [
            13
        ]
    },
    {
        "code": "VMQ-572",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "Vazirlar Mahkamasining 572-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-572",
        "doc_date": "2021-yil 17-sentyabr",
        "lex_url": "https://lex.uz/docs/-5638209",
        "summary": "Pedagog kadrlarni attestatsiyadan o'tkazish va malaka toifalarini berish tartibi to'g'risidagi Nizom.",
        "full_text": "Attestatsiya 2 bosqichda: mutaxassislik fani va pedagogik mahorat (80 ball) hamda o'quv fani standarti (20 ball) asosida 100 ballik tizimda o'tkaziladi. Oliy toifa uchun kamida 80 ball to'plash lozim.",
        "text": "Attestatsiya 2 bosqichda: mutaxassislik fani va pedagogik mahorat (80 ball) hamda o'quv fani standarti (20 ball) asosida 100 ballik tizimda o'tkaziladi. Oliy toifa uchun kamida 80 ball to'plash lozim.",
        "keywords": [
            "attestatsiya",
            "toifa",
            "pedagog attestatsiya",
            "malaka toifasi",
            "vmq-572",
            "oliy toifa",
            "pedagog sinov"
        ],
        "related_faq_ids": [
            12
        ]
    },
    {
        "code": "YORIQNOMA-3271",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "Adliya vazirligida 3271-son bilan ro'yxatga olingan Yo'riqnoma",
        "category": "Idoraviy Nizom",
        "doc_number": "3271",
        "doc_date": "2020-yil 30-iyun",
        "lex_url": "https://lex.uz/docs/-4878411",
        "summary": "Umumta'lim maktablarida pedagog xodimlarga dars soatlarini pedagogik kengash orqali ochiq taqsimlash mezonlari.",
        "full_text": "Dars soatlari 1 stavka (16 soat) me'yorida taqsimlanadi. Birinchi navbatda xalqaro sertifikatli, oliy toifali, fan olimpiadasi g'olibi tayyorlagan pedagoglarga ko'proq dars soatlari ustuvor beriladi. Direktor yakka tartibda dars taqsimlay olmaydi.",
        "text": "Dars soatlari 1 stavka (16 soat) me'yorida taqsimlanadi. Birinchi navbatda xalqaro sertifikatli, oliy toifali, fan olimpiadasi g'olibi tayyorlagan pedagoglarga ko'proq dars soatlari ustuvor beriladi. Direktor yakka tartibda dars taqsimlay olmaydi.",
        "keywords": [
            "3271-son",
            "dars taqsimoti",
            "16 soat",
            "pedkengash",
            "dars soati"
        ],
        "related_faq_ids": [
            11,
            33
        ]
    },
    {
        "code": "VMQ-823",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "Vazirlar Mahkamasining 823-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-823",
        "doc_date": "2019-yil 30-sentyabr",
        "lex_url": "https://lex.uz/docs/-4532274",
        "summary": "Direktor jamg'armasidan pedagog xodimlarga har oylik 10 foizdan 40 foizgacha ustama tayinlash tartibi.",
        "full_text": "Maktab direktori jamg'armasi hisobidan namunali dars o'tgan, o'quvchilari fan olimpiadalarida g'olib bo'lgan va tashabbuskor pedagoglarga har oylik 10% dan 40% gacha ustamalar belgilanadi.",
        "text": "Maktab direktori jamg'armasi hisobidan namunali dars o'tgan, o'quvchilari fan olimpiadalarida g'olib bo'lgan va tashabbuskor pedagoglarga har oylik 10% dan 40% gacha ustamalar belgilanadi.",
        "keywords": [
            "vmq-823",
            "direktor jamg'armasi",
            "direktor fondi",
            "ustama",
            "10-40 foiz"
        ],
        "related_faq_ids": [
            15,
            32
        ]
    },
    {
        "code": "VMQ-275",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "Vazirlar Mahkamasining 275-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-275",
        "doc_date": "2005-yil 21-dekabr",
        "lex_url": "https://lex.uz/docs/-951478",
        "summary": "Sinf rahbarligi va daftarlar tekshiruvi uchun qo'shimcha oylik haq to'lash stavkalari.",
        "full_text": "Sinfdagi o'quvchilar soniga qarab sinf rahbarligi uchun BHMning 26.4 foizidan 52.8 foizigacha, daftarlar tekshiruvi uchun 8.8 foizdan 17.6 foizigacha qo'shimcha haq to'lanadi.",
        "text": "Sinfdagi o'quvchilar soniga qarab sinf rahbarligi uchun BHMning 26.4 foizidan 52.8 foizigacha, daftarlar tekshiruvi uchun 8.8 foizdan 17.6 foizigacha qo'shimcha haq to'lanadi.",
        "keywords": [
            "vmq-275",
            "sinf rahbarligi",
            "daftar tekshirish",
            "qo'shimcha haq",
            "bhm"
        ],
        "related_faq_ids": [
            15
        ]
    },
    {
        "code": "ORQ-595",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "'Maktabgacha ta'lim va tarbiya to'g'risida'gi Qonun (O'RQ-595)",
        "category": "Qonun",
        "doc_number": "O'RQ-595",
        "doc_date": "2019-yil 16-dekabr",
        "lex_url": "https://lex.uz/docs/-4646908",
        "summary": "Maktabgacha ta'lim davlat kafolatlari, 6 yoshli bolalarni 1 yillik bepul umumiy tayyorlash.",
        "full_text": "Har bir bola 6 yoshdan 7 yoshgacha bo'lgan davrda umumiy o'rta ta'limga 1 yillik majburiy bepul tayyorlovdan o'tish huquqiga ega.",
        "text": "Har bir bola 6 yoshdan 7 yoshgacha bo'lgan davrda umumiy o'rta ta'limga 1 yillik majburiy bepul tayyorlovdan o'tish huquqiga ega.",
        "keywords": [
            "o'rq-595",
            "bog'cha",
            "1 yillik tayyorlov",
            "maktabgacha ta'lim",
            "bepul tayyorlash"
        ],
        "related_faq_ids": [
            16
        ]
    },
    {
        "code": "VMQ-244",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "Vazirlar Mahkamasining 244-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-244",
        "doc_date": "2018-yil 28-mart",
        "lex_url": "https://lex.uz/docs/-3601246",
        "summary": "Davlat maktabgacha ta'lim tashkilotlariga bolalarni qabul qilish bo'yicha davlat xizmatlari reglamenti.",
        "full_text": "Bolalarni bog'chaga qabul qilish faqat my.gov.uz yoki Davlat xizmatlari markazlari orqali yuborilgan elektron yo'llanma asosida amalga oshiriladi. Imtiyozli ro'yxatdagilar navbatsiz yo'llanma oladi.",
        "text": "Bolalarni bog'chaga qabul qilish faqat my.gov.uz yoki Davlat xizmatlari markazlari orqali yuborilgan elektron yo'llanma asosida amalga oshiriladi. Imtiyozli ro'yxatdagilar navbatsiz yo'llanma oladi.",
        "keywords": [
            "vmq-244",
            "bog'cha qabul",
            "yo'llanma",
            "my.gov.uz",
            "bog'chaga navbat"
        ],
        "related_faq_ids": [
            16
        ]
    },
    {
        "code": "NIZOM-3319",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "Adliya vazirligida 3319-son bilan ro'yxatga olingan Nizom",
        "category": "Idoraviy Nizom",
        "doc_number": "3319",
        "doc_date": "2021-yil 24-avgust",
        "lex_url": "https://lex.uz/docs/-5589021",
        "summary": "Davlat bog'chalarida 15% kam ta'minlangan oilalarni ota-onalar to'lovidan 100% ozod qilish.",
        "full_text": "Davlat bog'chalarida umumiy tarbiyalanuvchilar sonining 15 foizi miqdorida kam ta'minlangan va boquvchisini yo'qotgan oilalar farzandlari ota-onalar to'lovidan 100 foiz to'liq ozod etiladi.",
        "text": "Davlat bog'chalarida umumiy tarbiyalanuvchilar sonining 15 foizi miqdorida kam ta'minlangan va boquvchisini yo'qotgan oilalar farzandlari ota-onalar to'lovidan 100 foiz to'liq ozod etiladi.",
        "keywords": [
            "3319-son",
            "bog'cha to'lovi",
            "100% bepul bog'cha",
            "kam ta'minlangan",
            "15 foiz"
        ],
        "related_faq_ids": [
            17
        ]
    },
    {
        "code": "MEHNAT-483",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "O'zbekiston Respublikasi Mehnat kodeksining 483-moddasi",
        "category": "Kodeks",
        "doc_number": "MK-483",
        "doc_date": "2022-yil 28-oktyabr",
        "lex_url": "https://lex.uz/docs/-6257288",
        "summary": "Pedagog xodimlar mehnati kafolatlari va 56 kalendar kunlik uzaytirilgan asosiy mehnat ta'tili.",
        "full_text": "Pedagog xodimlarga davomiyligi 56 kalendar kun bo'lgan har yillik uzaytirilgan asosiy mehnat ta'tili beriladi. Xodimni ta'tildan chaqirib olishga faqat uning yozma roziligi bilan yo'l qo'yiladi.",
        "text": "Pedagog xodimlarga davomiyligi 56 kalendar kun bo'lgan har yillik uzaytirilgan asosiy mehnat ta'tili beriladi. Xodimni ta'tildan chaqirib olishga faqat uning yozma roziligi bilan yo'l qo'yiladi.",
        "keywords": [
            "mehnat kodeksi 483",
            "56 kunlik ta'til",
            "ta'tildan chaqirish taqiqlangan",
            "mehnat kafolati"
        ],
        "related_faq_ids": [
            14
        ]
    },
    {
        "code": "MJTK-197-5",
        "section_id": 5,
        "section_name": "Maktab va Maktabgacha Ta'lim Sohasidagi Asosiy Hukumat Qarorlari",
        "title": "Ma'muriy javobgarlik to'g'risidagi kodeks 197-5-moddasi",
        "category": "Kodeks",
        "doc_number": "MJtK-197-5",
        "doc_date": "1994-yil 22-sentyabr",
        "lex_url": "https://lex.uz/docs/-97664",
        "summary": "Pedagog xodimning kasbiy faoliyatiga qonunga xilof aralashganlik uchun javobgarlik: fuqarolarga 20-40 BHM, mansabdorlarga 30-50 BHM yoki 15 sutka qamoq.",
        "full_text": "Pedagogning darsiga noqonuniy aralashish, asossiz hisobotlar talab qilish, majburiy mehnatga jalb etish fuqarolarga BHM 20-40 baravari, mansabdor shaxslarga 30-50 baravari miqdorida jarima yoki 15 sutkagacha ma'muriy qamoq jazosiga sabab bo'ladi.",
        "text": "Pedagogning darsiga noqonuniy aralashish, asossiz hisobotlar talab qilish, majburiy mehnatga jalb etish fuqarolarga BHM 20-40 baravari, mansabdor shaxslarga 30-50 baravari miqdorida jarima yoki 15 sutkagacha ma'muriy qamoq jazosiga sabab bo'ladi.",
        "keywords": [
            "mjtk 197-5",
            "pedagog daxlsizligi",
            "aralashish jarimasi",
            "ma'muriy qamoq",
            "bhm 30-50"
        ],
        "related_faq_ids": [
            9,
            10,
            37
        ]
    },
    {
        "code": "VMQ-610",
        "section_id": 6,
        "section_name": "Nodavlat Ta'lim va Maxsus Ta'lim Dasturlari Huquqiy Asoslari",
        "title": "Vazirlar Mahkamasining 610-son qarori",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-610",
        "doc_date": "2019-yil 27-mart",
        "lex_url": "https://lex.uz/docs/-4259508",
        "summary": "Nodavlat ta'lim xizmatlari faoliyatini litsenziyalash va berilgan diplomlarning tengligi nizomi.",
        "full_text": "Nodavlat ta'lim tashkilotlari (xususiy universitetlar, maktablar, bog'chalar) faoliyatini boshlashdan oldin litsenziya olishi shart. Litsenziyaga ega va akkreditatsiyalangan xususiy OTMlar diplomlari davlat OTMlari diplomlari bilan teng yuridik kuchga ega.",
        "text": "Nodavlat ta'lim tashkilotlari (xususiy universitetlar, maktablar, bog'chalar) faoliyatini boshlashdan oldin litsenziya olishi shart. Litsenziyaga ega va akkreditatsiyalangan xususiy OTMlar diplomlari davlat OTMlari diplomlari bilan teng yuridik kuchga ega.",
        "keywords": [
            "vmq-610",
            "xususiy ta'lim",
            "litsenziya",
            "nodavlat otm",
            "diplom tengligi"
        ],
        "related_faq_ids": [
            25,
            44,
            45
        ]
    },
    {
        "code": "PQ-4860",
        "section_id": 6,
        "section_name": "Nodavlat Ta'lim va Maxsus Ta'lim Dasturlari Huquqiy Asoslari",
        "title": "Prezidentning PQ-4860-son qarori",
        "category": "Prezident Qarori",
        "doc_number": "PQ-4860",
        "doc_date": "2020-yil 13-oktyabr",
        "lex_url": "https://lex.uz/docs/-5047814",
        "summary": "Alohida ta'lim ehtiyojlari bo'lgan bolalarga ta'lim-tarbiya berish tizimini yanada takomillashtirish chora-tadbirlari (Inklyuziv ta'lim).",
        "full_text": "Umumta'lim maktablarida alohida ehtiyojli bolalar uchun inklyuziv sinflar ochiladi (har bir sinfga ko'pi bilan 3 nafar). O'qituvchilar va maxsus tyutorlarga 10% dan 30% gacha qo'shimcha oylik ustama to'lanadi.",
        "text": "Umumta'lim maktablarida alohida ehtiyojli bolalar uchun inklyuziv sinflar ochiladi (har bir sinfga ko'pi bilan 3 nafar). O'qituvchilar va maxsus tyutorlarga 10% dan 30% gacha qo'shimcha oylik ustama to'lanadi.",
        "keywords": [
            "pq-4860",
            "inklyuziv ta'lim",
            "tyutor",
            "3 nafar bola",
            "10-30 foiz ustama"
        ],
        "related_faq_ids": [
            7,
            38
        ]
    },
    {
        "code": "PF-5742-VMQ-606",
        "section_id": 6,
        "section_name": "Nodavlat Ta'lim va Maxsus Ta'lim Dasturlari Huquqiy Asoslari",
        "title": "Prezidentning PF-5742-son Farmoni va VMQ-606-son qarori",
        "category": "Prezident Farmoni",
        "doc_number": "PF-5742",
        "doc_date": "2019-yil 4-iyun",
        "lex_url": "https://lex.uz/docs/-4360349",
        "summary": "'El-yurt umidi' jamg'armasi orqali yetakchi xorijiy OTMlarda (TOP-300/500) 100% davlat granti hisobidan ta'lim olish.",
        "full_text": "Iqtidorli yoshlarning xorijiy nufuzli OTMlarida bakalavr, magistr va doktoranturada o'qishi Jamg'arma tomonidan 100% moliyalashtiriladi: to'lov-shartnoma, oylik stipendiya, aviabilet va sug'urta qoplanadi. Bitiruvchi O'zbekistonda 3-5 yil ishlab berish majburiyatini oladi.",
        "text": "Iqtidorli yoshlarning xorijiy nufuzli OTMlarida bakalavr, magistr va doktoranturada o'qishi Jamg'arma tomonidan 100% moliyalashtiriladi: to'lov-shartnoma, oylik stipendiya, aviabilet va sug'urta qoplanadi. Bitiruvchi O'zbekistonda 3-5 yil ishlab berish majburiyatini oladi.",
        "keywords": [
            "pf-5742",
            "vmq-606",
            "el-yurt umidi",
            "xorijda grant",
            "top-300"
        ],
        "related_faq_ids": [
            25
        ]
    },
    {
        "code": "VMQ-746-DARSLIK",
        "section_id": 6,
        "section_name": "Nodavlat Ta'lim va Maxsus Ta'lim Dasturlari Huquqiy Asoslari",
        "title": "VMQ-746 va Prezident topshirig'i (Darsliklarning 100% bepulligi)",
        "category": "Hukumat Qarori",
        "doc_number": "VMQ-746",
        "doc_date": "2022-yil 5-sentyabr",
        "lex_url": "https://lex.uz/docs/-6188231",
        "summary": "Barcha davlat umumta'lim maktablarining 1-11-sinf o'quvchilari uchun darsliklar va mashq daftarlari ijara to'lovining butunlay bekor qilinishi.",
        "full_text": "Davlat umumta'lim maktablarining barcha o'quvchilari darsliklar va ish daftarlari bilan 100% bepul ta'minlanadi. Kitoblar uchun pul yig'ish mutlaqo noqonuniy bo'lib, qat'iyan man etiladi.",
        "text": "Davlat umumta'lim maktablarining barcha o'quvchilari darsliklar va ish daftarlari bilan 100% bepul ta'minlanadi. Kitoblar uchun pul yig'ish mutlaqo noqonuniy bo'lib, qat'iyan man etiladi.",
        "keywords": [
            "vmq-746",
            "darslik",
            "bepul darslik",
            "ijara bekor",
            "mashq daftari"
        ],
        "related_faq_ids": [
            6
        ]
    },
    {
        "code": "PF-158",
        "section_id": 6,
        "section_name": "Nodavlat Ta'lim va Maxsus Ta'lim Dasturlari Huquqiy Asoslari",
        "title": "Prezidentning PF-158-son Farmoni",
        "category": "Prezident Farmoni",
        "doc_number": "PF-158",
        "doc_date": "2023-yil 11-sentyabr",
        "lex_url": "https://lex.uz/docs/-6600413",
        "summary": "'O'zbekiston — 2030' strategiyasi: Maktabgacha ta'lim qamrovi 80%, oliy ta'lim qamrovi 50%, inklyuziv maktablar tarmog'i.",
        "full_text": "Prezidentning PF-158-son Farmoni bilan tasdiqlangan 'O'zbekiston — 2030' strategiyasining ta'lim bo'yicha maqsadlari: maktabgacha ta'lim qamrovini 80% ga, oliy ta'lim qamrovini 50% ga yetkazish; umumta'lim maktablarida yangi baholash tizimini joriy etish; har bir tumanda kamida bittadan inklyuziv maktab faoliyatini yo'lga qo'yish.",
        "text": "Prezidentning PF-158-son Farmoni bilan tasdiqlangan 'O'zbekiston — 2030' strategiyasining ta'lim bo'yicha maqsadlari: maktabgacha ta'lim qamrovini 80% ga, oliy ta'lim qamrovini 50% ga yetkazish; umumta'lim maktablarida yangi baholash tizimini joriy etish; har bir tumanda kamida bittadan inklyuziv maktab faoliyatini yo'lga qo'yish.",
        "keywords": [
            "pf-158",
            "o'zbekiston-2030",
            "strategiya",
            "qamrov 80 foiz",
            "inklyuziv maktab"
        ],
        "related_faq_ids": [
            1,
            7,
            16,
            18
        ]
    }
]

# Quick index by code
ENCYCLOPEDIA_BY_CODE: Dict[str, Dict[str, Any]] = {item["code"]: item for item in LEGAL_ENCYCLOPEDIA_ARTICLES}

def get_article_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Retrieve legal article by exact or partial code."""
    c = code.upper().strip()
    if c in ENCYCLOPEDIA_BY_CODE:
        return ENCYCLOPEDIA_BY_CODE[c]
    for item in LEGAL_ENCYCLOPEDIA_ARTICLES:
        if item["code"].upper() == c:
            return item
    for item in LEGAL_ENCYCLOPEDIA_ARTICLES:
        if c in item["code"].upper() or item["code"].upper() in c:
            return item
    return None

def search_encyclopedia(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Search legal encyclopedia articles by query words and concepts.
    Normalizes Uzbek Latin characters and scores by field relevance.
    """
    if not query or not query.strip():
        return []

    def _normalize(s: str) -> str:
        return s.lower().replace('‘', "'").replace('’', "'").replace('ʻ', "'").replace('ʼ', "'").replace('`', "'")

    q = _normalize(query.strip())
    words = [w for w in re.findall(r'\b[\w\'-]+\b', q) if len(w) > 2]
    
    scored: List[tuple[float, Dict[str, Any]]] = []
    for item in LEGAL_ENCYCLOPEDIA_ARTICLES:
        score = 0.0
        code_norm = _normalize(item["code"])
        title_norm = _normalize(item["title"])
        kws = [_normalize(kw) for kw in item["keywords"]]
        summ_norm = _normalize(item.get("summary", ""))
        text_norm = _normalize(item.get("full_text", ""))

        # Code matches
        if q == code_norm or q.upper() == item["code"]:
            score += 35.0
        elif code_norm in q or q in code_norm:
            score += 15.0

        # Exact query match
        if q in title_norm:
            score += 20.0
        for kw in kws:
            if q == kw:
                score += 15.0
            elif q in kw or kw in q:
                score += 8.0

        # Word token matches
        for w in words:
            if w == code_norm or w in code_norm:
                score += 8.0
            for kw in kws:
                if w == kw:
                    score += 5.0
                elif w in kw:
                    score += 2.5
            if w in title_norm:
                score += 3.5
            if w in summ_norm:
                score += 2.0
            if w in text_norm:
                score += 1.0

        if score > 0.0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:limit]]

# Dynamic loading of 50-page Constitution dataset
try:
    from app.data.constitution_50_loader import get_constitution_50_articles
    _c50_articles = get_constitution_50_articles()
    if _c50_articles:
        LEGAL_ENCYCLOPEDIA_ARTICLES.extend(_c50_articles)
        for _art in _c50_articles:
            ENCYCLOPEDIA_BY_CODE[_art["code"]] = _art
except Exception as _e:
    pass

