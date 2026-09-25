import re
from typing import List, Optional, Tuple
from app.models.schemas import KnowledgeItem, TopicCategory

MINISTRY_KNOWLEDGE_BASE: List[KnowledgeItem] = [
    KnowledgeItem(
        id="kb-qabul-2026",
        topic=TopicCategory.QABUL,
        title="Oliy ta'lim muassasalariga qabul va ro'yxatdan o'tish tartibi",
        summary="Abituriyentlar my.uzbmb.uz portali orqali 5 tagacha ta'lim yo'nalishini tanlaydi. Test sinovlari 'Avval test, so'ng tanlov' tamoyili asosida o'tkaziladi.",
        official_regulation="O'zbekiston Respublikasi Vazirlar Mahkamasining OTMlarga qabul to'g'risidagi nizomi va Prezident qarorlari.",
        faq_questions=[
            "OTMlarga hujjat topshirish qachon boshlanadi va qayerdan qilinadi?",
            "Nechta oliygoh yoki yo'nalish tanlash mumkin?",
            "Abituriyent qanday hujjatlarni yuklashi shart?",
            "Chet tili sertifikati qanday ball beradi?"
        ],
        action_steps=[
            "1. my.uzbmb.uz saytida OneID orqali ro'yxatdan o'ting.",
            "2. Pasport va attestat/diplom ma'lumotlarini tasdiqlang.",
            "3. Test topshirish hududi va chet tili sertifikatini (agar mavjud bo'lsa) kiriting.",
            "4. 5 tagacha yo'nalishni tanlang va to'lov kvitansiyasini tasdiqlang."
        ],
        links=["https://my.uzbmb.uz", "https://edu.uz"]
    ),
    KnowledgeItem(
        id="kb-grant-2026",
        topic=TopicCategory.GRANT,
        title="Davlat grantlari va ijtimoiy-rag'batlantiruvchi kvotalar",
        summary="Davlat grantlari har yili talabalarning akademik o'zlashtirish reytingiga (GPA) qarab qayta taqsimlanadi. Ijtimoiy himoyaga muhtoj qizlar va ehtiyojmand oilalar uchun qo'shimcha grant kvotalari mavjud.",
        official_regulation="Ta'lim sohasida davlat buyurtmasi va ta'lim grantlarini qayta taqsimlash to'g'risidagi qonunchilik hujjatlari.",
        faq_questions=[
            "Davlat granti har yili qayta taqsimlanadimi?",
            "Grantda o'qigan talaba o'qishni bitirgach ishlab berishi shartmi?",
            "Xotin-qizlar uchun 4 foizli davlat granti qanday olinadi?",
            "GPA baholarim tushib ketsa grantdan kontraktga tushamanmi?"
        ],
        action_steps=[
            "1. O'quv yili yakunida HEMIS tizimidagi umumiy GPA ballingizni tekshiring.",
            "2. Ijtimoiy kvota uchun 'Ijtimoiy himoya yagona reyestri' ma'lumotnomasini taqdim eting.",
            "3. Fakultet dekanatiga ariza bilan murojaat qiling."
        ],
        links=["https://edu.uz/uz/pages/grants", "https://hemis.uz"]
    ),
    KnowledgeItem(
        id="kb-kontrakt-super",
        topic=TopicCategory.KONTRAKT,
        title="Tabaqalashtirilgan to'lov-shartnoma (Super-kontrakt) tartibi",
        summary="Kirish baliga 4.05 ballgacha yetmagan abituriyentlar tabaqalashtirilgan kontrakt asosida o'qishga qabul qilinadi. To'lov miqdori yetmagan ballga proporsional ravishda belgilanadi.",
        official_regulation="Davlat komissiyasining to'lov-shartnoma asosida o'qishga qabul qilish parametrlari to'g'risidagi bayonlari.",
        faq_questions=[
            "Super kontrakt arizasini qayerdan yuboraman?",
            "Super kontrakt miqdori qancha?",
            "Kontrakt to'lovini bo'lib to'lasa bo'ladimi?",
            "56.7 balldan past to'plaganlar o'qiy oladimi?"
        ],
        action_steps=[
            "1. my.uzbmb.uz yoki OTMning my.edu.uz platformasida ariza qoldiring.",
            "2. Hisoblangan tabaqalashtirilgan shartnoma kvitansiyasini yuklab oling.",
            "3. Shartnoma summasining 50 foizini belgilangan muddatgacha to'lang."
        ],
        links=["https://my.edu.uz", "https://t-kontrakt.edu.uz"]
    ),
    KnowledgeItem(
        id="kb-ttj-turar-joy",
        topic=TopicCategory.TTJ,
        title="Talabalar turar joyi (TTJ) va ijara kompensatsiyasi",
        summary="Talabalarni yotoqxona bilan ta'minlash to'liq my.gov.uz portali orqali inson omilisiz amalga oshiriladi. TTJ yetmagan talabalarga oylik ijara to'lovining 50 foizi (BHM ning 1 baravarigacha) davlat tomonidan qoplab beriladi.",
        official_regulation="Vazirlar Mahkamasining 2021-yil 9-sentyabrdagi 605-son qarori.",
        faq_questions=[
            "Yotoqxonaga arizani qanday topshirish kerak?",
            "Ijara kompensatsiyasini olish uchun qanday hujjat kerak?",
            "Birinchi kurslar yotoqxona bilan to'liq ta'minlanadimi?",
            "Ijara shartnomasi soliq idorasida ro'yxatdan o'tgan bo'lishi shartmi?"
        ],
        action_steps=[
            "1. my.gov.uz portalida 'Talabalar turar joyiga joylashish' xizmatini tanlang.",
            "2. Imtiyoz toifalari (chin yetim, nogironlik, kam ta'minlangan) bo'lsa hujjatlarni ilova qiling.",
            "3. Ijara kompensatsiyasi uchun ijara.soliq.uz orqali ro'yxatdan o'tgan shartnomani dekanatga topshiring."
        ],
        links=["https://my.gov.uz", "https://ijara.soliq.uz"]
    ),
    KnowledgeItem(
        id="kb-nostrifikatsiya",
        topic=TopicCategory.NOSTRIFIKATSIYA,
        title="Xorijiy diplomlarni tan olish va nostrifikatsiya qilish",
        summary="Xorijiy davlatlarda berilgan oliy ta'lim diplomlari Ta'lim sifatini nazorat qilish inspeksiyasi / Bilimni baholash agentligi orqali my.gov.uz orqali tan olinadi. TOP-1000 talikka kirgan OTM diplomlari to'g'ridan-to'g'ri (imtihonsiz) tan olinadi.",
        official_regulation="Vazirlar Mahkamasining 2019-yil 24-iyuldagi 620-son qarori.",
        faq_questions=[
            "Chet el diplomini O'zbekistonda tan olish tartibi qanday?",
            "Qaysi oliygohlar diplomi imtihonsiz tan olinadi?",
            "Masofaviy (onlayn) o'qigan diplomlar nostrifikatsiya qilinadimi?",
            "Nostrifikatsiya arizasini ko'rib chiqish muddati qancha?"
        ],
        action_steps=[
            "1. my.gov.uz saytida 'Xorijiy ta'lim to'g'risidagi hujjatlarni tan olish' xizmatini oching.",
            "2. Diplom, ilova va ularning notarial tasdiqlangan o'zbekcha tarjimasini yuklang.",
            "3. Davlat bojini to'lang va belgilangan test sinovida qatnashing (TOP-1000 OTMlar bundan mustasno)."
        ],
        links=["https://my.gov.uz/uz/service/263", "https://uzbmb.uz"]
    ),
    KnowledgeItem(
        id="kb-stipendiya-kredit",
        topic=TopicCategory.STIPENDIYA,
        title="Talabalar stipendiyalari va imtiyozli ta'lim kreditlari",
        summary="Davlat granti talabalariga bazaviy stipendiya to'lanadi. Xotin-qizlar uchun ta'lim krediti foizsiz (0% stavkada) beriladi. Boshqa toifadagi talabalarga Markaziy bank asosiy stavkasida ta'lim kreditlari ajratiladi.",
        official_regulation="O'zbekiston Respublikasi Prezidentining 2021-yil 30-iyuldagi PQ-5203-son qarori.",
        faq_questions=[
            "Ta'lim kreditini qaysi banklardan va qanday shartlarda olish mumkin?",
            "Qizlar uchun ta'lim krediti rostdan ham foizsizmi?",
            "Stipendiya miqdori a'lo baholarga qarab oshadimi?",
            "Kreditni qaytarish qachondan boshlanadi?"
        ],
        action_steps=[
            "1. talim-krediti.mf.uz portali orqali onlayn ariza yuboring.",
            "2. OTM bilan tuzilgan to'lov-kontrakt shartnomasini taqdim eting.",
            "3. O'qishni tamomlagandan so'ng 7-oydan boshlab 7 yil davomida qaytaring."
        ],
        links=["https://talim-krediti.mf.uz", "https://cbu.uz"]
    ),
    KnowledgeItem(
        id="kb-perevod-transfer",
        topic=TopicCategory.PEREVOD,
        title="O'qishni ko'chirish va qayta tiklash (Perevod) qoidalari",
        summary="O'qishni bir OTMdan boshqasiga ko'chirish faqat transfer.edu.uz portali orqali 15-iyuldan 5-avgustgacha qabul qilinadi. Uzrli sabablarga (turmushga chiqish, davlat xizmatchisining ish joyi o'zgarishi) ega talabalar arizasi ko'rib chiqiladi.",
        official_regulation="Vazirlar Mahkamasining 2017-yil 20-iyundagi 393-son qarori.",
        faq_questions=[
            "Xorijiy OTMdan O'zbekistonga o'qishni ko'chirishda test topshiriladimi?",
            "Turmushga chiqqan qizlarning o'qishini ko'chirish tartibi qanday?",
            "Perevod arizalari qaysi sayt orqali yuboriladi?",
            "O'qishdan chetlashtirilgan talaba qanday qilib o'qishini tiklaydi?"
        ],
        action_steps=[
            "1. transfer.edu.uz saytida pasport va transkript (reyting daftarchasi) ma'lumotlarini kiriting.",
            "2. Uzrli sababni tasdiqlovchi hujjatlarni yuklang.",
            "3. Bilimni baholash agentligi (UzBMB) o'tkazadigan maxsus testda o'tish balini to'plang."
        ],
        links=["https://transfer.edu.uz", "https://edu.uz"]
    )
]

def search_knowledge_base(query: str, limit: int = 2) -> List[KnowledgeItem]:
    """
    Search ministry regulations using weighted keyword & intent matching.
    """
    if not query:
        return MINISTRY_KNOWLEDGE_BASE[:limit]

    q_lower = query.lower()
    scores: List[Tuple[float, KnowledgeItem]] = []

    keyword_map = {
        TopicCategory.QABUL: ["qabul", "hujjat", "topshirish", "my.uzbmb", "bmb", "dtm", "abituriyent", "yo'nalish", "ball", "imtihon", "sertifikat"],
        TopicCategory.GRANT: ["grant", "davlat granti", "byudjet", "bepul", "gpa", "xotin-qizlar", "kvota", "ijtimoiy"],
        TopicCategory.KONTRAKT: ["kontrakt", "super", "tabaqalashtirilgan", "shartnoma", "to'lov", "narxi", "qimmat", "56.7", "kvitansiya"],
        TopicCategory.TTJ: ["ttj", "yotoqxona", "turar joy", "ijara", "kompensatsiya", "kvartira", "joylashish", "my.gov.uz"],
        TopicCategory.NOSTRIFIKATSIYA: ["nostrifikatsiya", "diplom", "tan olish", "xorijiy", "chet el", "rossiya", "qozog'iston", "qirg'iziston", "top 1000", "top-1000"],
        TopicCategory.STIPENDIYA: ["stipendiya", "kredit", "ta'lim krediti", "foizsiz", "bank", "moliya", "talim-krediti"],
        TopicCategory.PEREVOD: ["perevod", "ko'chirish", "transfer", "tiklash", "qayta tiklash", "boshqa oliygoh", "boshqa shahar"]
    }

    for item in MINISTRY_KNOWLEDGE_BASE:
        score = 0.0
        # Title match
        if any(word in item.title.lower() for word in q_lower.split()):
            score += 3.0

        # Topic keyword bonus
        target_words = keyword_map.get(item.topic, [])
        for word in target_words:
            if word in q_lower:
                score += 2.5

        # FAQ queries match
        for faq in item.faq_questions:
            if any(term in faq.lower() for term in q_lower.split() if len(term) > 3):
                score += 1.5

        # Summary match
        if any(term in item.summary.lower() for term in q_lower.split() if len(term) > 3):
            score += 1.0

        if score > 0:
            scores.append((score, item))

    # Sort descending by score
    scores.sort(key=lambda x: x[0], reverse=True)
    results = [item for _, item in scores]

    return results[:limit] if results else MINISTRY_KNOWLEDGE_BASE[:limit]
