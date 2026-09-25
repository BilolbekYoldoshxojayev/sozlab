import os
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Register TrueType fonts for Uzbek Unicode
pdfmetrics.registerFont(TTFont('SegoeUI', 'C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUI-Bold', 'C:/Windows/Fonts/segoeuib.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUI-Italic', 'C:/Windows/Fonts/segoeuii.ttf'))

FONT_REGULAR = 'SegoeUI'
FONT_BOLD = 'SegoeUI-Bold'
FONT_ITALIC = 'SegoeUI-Italic'

NAVY = colors.HexColor('#081E38')
BLUE = colors.HexColor('#0B2B50')
SKY = colors.HexColor('#1E6091')
EMERALD = colors.HexColor('#0D9488')
GOLD = colors.HexColor('#D97706')
PURPLE = colors.HexColor('#7C3AED')
LIGHT_BG = colors.HexColor('#F8FAFC')
CARD_BG = colors.HexColor('#F1F5F9')
TEXT_DARK = colors.HexColor('#0F172A')
TEXT_MUTED = colors.HexColor('#475569')
BORDER_COLOR = colors.HexColor('#CBD5E1')

OUTPUT_DIR = Path('c:/dev/Projects/vazir-chat/team_guides')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, total_pages):
        self.saveState()
        self.setFont(FONT_REGULAR, 7.5)
        self.setFillColor(TEXT_MUTED)

        # Header
        self.drawString(45, 804, "UMUMMILLIY AI XAKATON (NAMANGAN 2026) • TA'LIM TREKI")
        self.drawRightString(A4[0] - 45, 804, "SÖZLAB — SHAXSIY HARAKATLAR DASTURI")
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(45, 796, A4[0] - 45, 796)

        # Footer
        self.line(45, 38, A4[0] - 45, 38)
        self.drawString(45, 26, "Oliy ta'lim, fan va innovatsiyalar vazirligi AI Call-Markazi • Maxfiy jamoaviy reja")
        page_str = f"Sahifa {self._pageNumber} / {total_pages}"
        self.drawRightString(A4[0] - 45, 26, page_str)

        self.restoreState()

def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='MainTitle',
        fontName=FONT_BOLD,
        fontSize=15,
        leading=18,
        textColor=NAVY,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='MainSub',
        fontName=FONT_BOLD,
        fontSize=9,
        leading=12,
        textColor=EMERALD,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='SecHead',
        fontName=FONT_BOLD,
        fontSize=10.5,
        leading=13,
        textColor=BLUE,
        spaceBefore=7,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='SubSecHead',
        fontName=FONT_BOLD,
        fontSize=8.5,
        leading=11,
        textColor=GOLD,
        spaceBefore=4,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='Body',
        fontName=FONT_REGULAR,
        fontSize=7.8,
        leading=11,
        textColor=TEXT_DARK,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='BodyB',
        fontName=FONT_BOLD,
        fontSize=7.8,
        leading=11,
        textColor=TEXT_DARK,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='BulletText',
        fontName=FONT_REGULAR,
        fontSize=7.8,
        leading=10.8,
        textColor=TEXT_DARK,
        leftIndent=8,
        firstLineIndent=-8,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='LinkStyle',
        fontName=FONT_BOLD,
        fontSize=7.5,
        leading=10.5,
        textColor=SKY,
        leftIndent=8,
        firstLineIndent=-8,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='MetaBox',
        fontName=FONT_REGULAR,
        fontSize=7.5,
        leading=10.5,
        textColor=TEXT_DARK
    ))
    return styles

def create_header(canvas, role_title, member_name, tag_text, styles):
    content = []
    header_data = [
        [
            Paragraph(f"<b>{role_title}</b>", styles['MainTitle']),
            Paragraph(f"<font color='#0D9488'><b>{tag_text}</b></font>", styles['MainSub'])
        ],
        [
            Paragraph(f"Mas'ul a'zo: <b>{member_name}</b> | Loyiha: <b>SözLab (Oliy ta'lim AI Call Markazi)</b>", styles['BodyB']),
            Paragraph("Bosqichlar: <b>CP1 ➔ CP2 ➔ Final Pitch</b>", styles['Body'])
        ]
    ]
    t = Table(header_data, colWidths=[340, 165])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    content.append(t)
    content.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceBefore=4, spaceAfter=5))
    return content

def create_box(title, items, styles, border_color=BORDER_COLOR, bg_color=LIGHT_BG):
    p_title = Paragraph(f"<b>{title}</b>", styles['SecHead'])
    rows = [[p_title]]
    for it in items:
        rows.append([Paragraph(it, styles['BulletText'])])
    
    t = Table(rows, colWidths=[505])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_color),
        ('BOX', (0,0), (-1,-1), 0.75, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,0), 0.5, border_color),
    ]))
    return t

# -------------------------------------------------------------
# 1. BILOLBEK
# -------------------------------------------------------------
def build_bilolbek_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_DIR / "01_Bilolbek_Lead_Developer_SozLab.pdf"),
        pagesize=A4,
        leftMargin=45, rightMargin=45,
        topMargin=45, bottomMargin=45
    )
    styles = get_styles()
    story = []

    # Header
    story.extend(create_header(
        None,
        "1. LEAD DEVELOPER / AI & SYSTEM INTEGRATOR",
        "Bilolbek (Siz)",
        "TEXNIK POYDEVOR & TIZIM INTEGRATSIYASI",
        styles
    ))

    # CP1 Section
    cp1_tasks = [
        "• <b>FastAPI Backend & CORS Setup:</b> API routing (`/api/calls`, `/api/knowledge`), CORS middleware va Pydantic v2 sxemalarini barqarorlashtirish.",
        "• <b>Gemini Dialog Manager Integratsiyasi:</b> Google GenAI SDK (Gemini 2.5/2.0) orqali o'zbek tilidagi niyatlarni aniqlash (Intent Recognition) va dialog boshqaruvini ulash.",
        "• <b>Edge-TTS Ovoz Sintezi:</b> `uz-UZ-MadinaNeural` va `uz-UZ-SardorNeural` neyron modellarini MD5 keshlash va oqimli uzatish bilan integratsiya qilish.",
        "• <b>Next.js 14 Boshlang'ich UI:</b> Call Simulator oynasi, jonli audio to'lqin visualizatori va dastlabki muloqot transkripsiyasini ishga tushirish.",
        "• <b>CP1 Handoff:</b> Mentorlarga ko'rsatish uchun `http://localhost:3000` yoki lokal IP havolasini jamoaga taqdim etish."
    ]
    story.append(create_box("📌 CHECKPOINT 1 (CP1) GACHA VAZIFALAR (Foundation & Prototype)", cp1_tasks, styles, SKY, LIGHT_BG))
    story.append(Spacer(1, 5))

    # CP2 Section
    cp2_tasks = [
        "• <b>Ovozni Aniqlash (Speech Recognizer Fix):</b> `frontend/lib/audioRecorder.ts` dagi MediaRecorder orqali mikrofondan real o'zbekcha audioni yozib olib, `POST /api/calls/{call_id}/audio-turn` endpointiga yuborish va Gemini multimodal orqali transkripsiya qilish.",
        "• <b>3 Ta Foydalanuvchi Roli (Tri-Role):</b> Fuqaro (`/call`), Operator (`/operator` - 3 ta navbatchi liniya) va Admin (`/admin` - fleet & queue monitor) boshqaruvini to'liq ajratish.",
        "• <b>Aqlli Operator Navbati (FIFO Dispatcher):</b> Fuqaroni ketma-ketlikda tekshirish (Op 1 ➔ Op 2 ➔ Op 3 ➔ FIFO Navbat). Barcha operatorlar band bo'lsa, navbat raqamini real-vaqtda ekranda ko'rsatish (`#1-o'rinda kutmoqdasiz`).",
        "• <b>Auto-Pop mexanizmi:</b> Operator `Yakunlash & Keyingisi`ni bosgan paytda, backend navbatdagi fuqaroni avtomatik ravishda ushbu operatorga biriktirishi va WebSocket orqali bildirishnoma berishi.",
        "• <b>Avtomatlashtirilgan Tekshiruv:</b> `pytest backend/tests/test_backend.py` (8 ta test) va `npm run build` (9 ta sahifa) to'liq 100% xatosiz o'tishi."
    ]
    story.append(create_box("🚀 CHECKPOINT 2 (CP2) GACHA VAZIFALAR (MVP Integration & Smart Queue)", cp2_tasks, styles, BLUE, LIGHT_BG))
    story.append(Spacer(1, 5))

    # Final Stage Section
    final_tasks = [
        "• <b>Oflayn Barqarorlik (Offline Resilience):</b> Wi-Fi uzilib qolgan holatda ham lokal IP (`start_dev.ps1`) orqali demo to'xtovsiz ishlashini ta'minlash.",
        "• <b>Sahna Repetitsiyasi:</b> Fayzulloh (Pitcher) bilan 3 daqiqalik jonli qo'ng'iroq ssenariysini 3 marta mashq qilish (savol berish, Madina ovozida javob olish, operatorga o'tish).",
        "• <b>Ziyovuddin bilan Video Backup:</b> Jonli ishlayotgan interfeysdan 60 soniyalik sifatli screen-recording yozib olishda ko'maklashish.",
        "• <b>Hakamlar Q&A Texnik Himoyasi:</b> Kechikish (Latency < 1.2s), token optimizatsiyasi, xavfsizlik va lokal LLM skalatsiyasi bo'yicha texnik dalillarni hozirlash."
    ]
    story.append(create_box("🏆 XAKATON YAKUNIGACHA VAZIFALAR (Final Pitch & Live Demo Defense)", final_tasks, styles, GOLD, LIGHT_BG))
    
    story.append(PageBreak())

    # PAGE 2: Connections & Resources
    story.extend(create_header(
        None,
        "1. BILOLBEK — BOG'LIQLIKLAR VA MANBALAR",
        "Lead Developer",
        "TEAM CONNECTIONS & USEFUL RESOURCES",
        styles
    ))

    connections = [
        "• <b>Iskandardan olasiz:</b> Vazirlikning rasmiy qarorlari (VMQ 468, PF-81, VMQ 345) va 25 ta rasmiy FAQ JSON ma'lumotlar to'plami.",
        "• <b>Temurmalikdan olasiz:</b> Tizimning o'tkazuvchanlik metrikalari (RPM, concurrent calls) va tejamkorlik parametrlarini kesh sozlamalariga kiritish uchun.",
        "• <b>Fayzullohga topshirasiz:</b> Ishlayotgan dastur havolasi (`http://localhost:3000` va Wi-Fi lokal IP), jonli qo'ng'iroq testi va hakamlar oldida ko'rsatiladigan demo stsenariysi.",
        "• <b>Ziyovuddinga topshirasiz:</b> Barcha ekranlarning toza demo ma'lumotlari bilan to'ldirilgan holati (mockup va 60 soniyalik video olish uchun)."
    ]
    story.append(create_box("🤝 JAMOA A'ZOLARI BILAN BOG'LIQLIK (Handoffs & Inputs)", connections, styles, EMERALD, LIGHT_BG))
    story.append(Spacer(1, 5))

    resources = [
        "• <b>FastAPI Official Docs:</b> https://fastapi.tiangolo.com — Asinxron marshrutlash va WebSocket protokoli.",
        "• <b>Google Gemini API Guides:</b> https://ai.google.dev/docs — Multimodal audio processing va funksiya chaqirish (function calling).",
        "• <b>Microsoft Edge-TTS Repository:</b> https://github.com/rany2/edge-tts — O'zbek tilidagi eng tabiiy neyron ovozlar kutubxonasi.",
        "• <b>Next.js 14 App Router:</b> https://nextjs.org/docs/app — Server & Client Components, Web Audio API integratsiyasi.",
        "• <b>Tailscale / Localhost Tunnel:</b> https://tailscale.com — Tashqi hakamlar noutbukiga lokal demoga kirish huquqini ochish."
    ]
    story.append(create_box("🔗 FOYDALI HAVOLALAR, MANBALAR VA VOSITALAR", resources, styles, SKY, LIGHT_BG))
    story.append(Spacer(1, 5))

    checklist = [
        "✔ Backend testi: <code>pytest backend/tests/test_backend.py</code> buyrug'i 8/8 testdan 100% o'tganligini tekshirish.",
        "✔ Frontend build: <code>npm run build</code> xatosiz yakunlanganligi va 9 ta sahifa statik/dinamik generatsiyalanganligi.",
        "✔ Lokal tarmoq: Noutbuk Wi-Fi IP manzili orqali telefon va boshqa noutbuklardan kirish imkoniyati borligi (`start_dev.ps1`).",
        "✔ Demo xavfsizligi: API kalitlari `.env` faylida saqlanganligi va frontend kodiga oshkor etilmaganligi."
    ]
    story.append(create_box("✅ LEAD DEVELOPER QAT'IY CHECKLISTI", checklist, styles, PURPLE, LIGHT_BG))

    doc.build(story, canvasmaker=NumberedCanvas)

# -------------------------------------------------------------
# 2. FAYZULLOH
# -------------------------------------------------------------
def build_fayzulloh_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_DIR / "02_Fayzulloh_PM_Lead_Pitcher_SozLab.pdf"),
        pagesize=A4,
        leftMargin=45, rightMargin=45,
        topMargin=45, bottomMargin=45
    )
    styles = get_styles()
    story = []

    # Header
    story.extend(create_header(
        None,
        "2. PRODUCT MANAGER & LEAD PITCHER",
        "Fayzulloh",
        "TAQDIMOT, LOYIHA BOSHQARUVI & SAHNA NUTQI",
        styles
    ))

    # CP1 Section
    cp1_tasks = [
        "• <b>Tashkilotchilar Taqdimot Shabloni Tahlili:</b> Tashkilotchilar bergan `Шаблон.pptx` strukturasini tahlil qilib, 10 ta slaydning loyiha matn qoralamasini (Draft 1) yozish.",
        "• <b>Muammoni Aniq Formulalash (The Hook):</b> Oliy ta'lim vazirligi 1006 call-markazining yoz oylarida (qabul, kvota, super-kontrakt, TTJ) 100 000+ qo'ng'iroqlar ostida qulashi va 70% savollarning takroriyligini ko'rsatish.",
        "• <b>Loyiha Brendingi va Shiori:</b> <b>'SözLab — Oliy ta'lim va innovatsiyalar vazirligining intellektual ovozli yordamchisi va aqlli call-markazi'</b>.",
        "• <b>CP1 Mentor Himoyasi:</b> Mentorlar oldida g'oyaning noyobligi, jamoa a'zolari mas'uliyati va texnik amalga oshirish rejasi bo'yicha aniq nutq so'zlash."
    ]
    story.append(create_box("📌 CHECKPOINT 1 (CP1) GACHA VAZIFALAR (Pitch Deck Draft & Problem Validation)", cp1_tasks, styles, SKY, LIGHT_BG))
    story.append(Spacer(1, 5))

    # CP2 Section
    cp2_tasks = [
        "• <b>10 Ta Slaydli Taqdimotni To'liq Yakunlash:</b> Ziyovuddin bilan birga taqdimot dizaynini (Canva/Figma/PowerPoint) 100% tugallash.",
        "• <b>Slaydlarga Aniq Faktlarni Joylash:</b> Iskandardan olingan qonuniy me'yorlar (VMQ 468, PF-81, PQ-323) va Temurmalikdan olingan moliyaviy ROI hisob-kitoblarini (1.2 mlrd so'm tejamkorlik) kiritish.",
        "• <b>Mahsulot Interfeysi Slaydi:</b> Bilolbek yaratgan real ekrandan (Call Simulator, Operator Dashboard, Admin Monitor) skrinshotlarni kiritish (quruq matn emas, real ishlayotgan mahsulot!).",
        "• <b>3 Daqiqalik Nutq Matni (Pitch Script):</b> Har bir soniyasi hisoblangan 180 soniyalik nutq matnini tayyorlash va taymer bilan kamida 3 marta o'qib chiqish."
    ]
    story.append(create_box("🚀 CHECKPOINT 2 (CP2) GACHA VAZIFALAR (Final Presentation & Timing Rehearsal)", cp2_tasks, styles, BLUE, LIGHT_BG))
    story.append(Spacer(1, 5))

    # Final Stage Section
    final_tasks = [
        "• <b>Sahna Nutqi Repetitsiyasi (0:00-3:00):</b> 0:00-0:30 Muammo va og'riq | 0:30-1:15 Jonli ovozli demo | 1:15-2:15 Biznes model, arxitektura va tejamkorlik | 2:15-3:00 Skalatsiya, jamoa va ta'sir.",
        "• <b>Bilolbek bilan Jonli Demo Muloqoti:</b> Sahnada noutbuk yoki telefonda mikrofonni yoqib, SözLab bilan o'zbek tilida gaplashib, Madina ovozida tezkor javob olishni ko'rsatish.",
        "• <b>Backup Video Rejasi:</b> Agar sahnada Wi-Fi yoki proyektor bilan muammo bo'lsa, Ziyovuddin tayyorlagan 60 soniyalik videoni fleshkadan bir zumda ochishga tayyor turish.",
        "• <b>Hakamlar Savol-Javobiga (Q&A) Tayyorgarlik:</b> Halusinatsiya, xavfsizlik, o'zbek tili shevalari va davlat byudjeti bo'yicha beriladigan qaltis savollarga qat'iy javoblar berish."
    ]
    story.append(create_box("🏆 XAKATON YAKUNIGACHA VAZIFALAR (Stage Pitch & Victory Delivery)", final_tasks, styles, GOLD, LIGHT_BG))

    story.append(PageBreak())

    # PAGE 2: Connections & Resources
    story.extend(create_header(
        None,
        "2. FAYZULLOH — BOG'LIQLIKLAR VA MANBALAR",
        "PM & Lead Pitcher",
        "TEAM CONNECTIONS & PITCH TOOLKIT",
        styles
    ))

    connections = [
        "• <b>Bilolbekdan olasiz:</b> Ishlayotgan demo havola, jonli test qo'ng'irog'i, interfeys skrinshotlari va texnik arxitektura chizmasi.",
        "• <b>Iskandardan olasiz:</b> Rasmiy statistik raqamlar, qonun me'yorlari (VMQ, PQ) va abituriyentlar/talabalar murojaatlari ko'lami.",
        "• <b>Temurmalikdan olasiz:</b> Biznes model, Unit economics ($0.003 vs $0.45), ROI hisobi va vazirlik uchun 1.2 mlrd so'mlik tejamkorlik slayd ma'lumotlari.",
        "• <b>Ziyovuddinga topshirasiz:</b> Taqdimotning qoralama matni (tekst) va slayd ketma-ketligini dizaynlashtirish uchun.",
        "• <b>Butun jamoaga topshirasiz:</b> Checkpoint vaqt jadvali, mentorlar fikr-mulohazalari va sahna repetitsiyasi intizomi."
    ]
    story.append(create_box("🤝 JAMOA A'ZOLARI BILAN BOG'LIQLIK (Handoffs & Inputs)", connections, styles, EMERALD, LIGHT_BG))
    story.append(Spacer(1, 5))

    resources = [
        "• <b>Y Combinator Pitch Guide:</b> https://www.ycombinator.com/library/2u-how-to-build-a-better-pitch-deck — 3 daqiqada g'olib bo'lish qoidalari.",
        "• <b>Canva / Pitch.com Templates:</b> https://pitch.com/templates — Slaydlarni professional formatlash uchun.",
        "• <b>Online Speech Timer:</b> https://www.online-stopwatch.com — 3:00 daqiqalik qat'iy vaqt nazorati.",
        "• <b>Oliy ta'lim vazirligi yangiliklar lentasi:</b> https://edu.uz — Taqdimotda vazirlikning eng so'nggi islohotlariga tayanish uchun.",
        "• <b>Techstars Pitch Toolkit:</b> Sahnada tana tili, ovoz tembri va hakamlar nigohini jalb qilish texnikalari."
    ]
    story.append(create_box("🔗 FOYDALI HAVOLALAR, MANBALAR VA VOSITALAR", resources, styles, SKY, LIGHT_BG))
    story.append(Spacer(1, 5))

    checklist = [
        "✔ Slaydlar soni: Aniq 10-12 tadan oshmasligi va matnlar yirik, qisqa tezislarda berilganligi.",
        "✔ Tayming: 3 daqiqadan 1 soniya ham oshib ketmasligi (hakamlar vaqt tugaganda to'xtatadi!).",
        "✔ Demo integratsiyasi: Nutqning 45-soniyasida real jonli ovozli muloqot namoyish qilinishi.",
        "✔ USB Fleshka: Taqdimot PPTX, PDF va 60 soniyalik video fayl alohida fleshkada yoningizda bo'lishi."
    ]
    story.append(create_box("✅ PITCHER QAT'IY CHECKLISTI", checklist, styles, PURPLE, LIGHT_BG))

    doc.build(story, canvasmaker=NumberedCanvas)

# -------------------------------------------------------------
# 3. ISKANDAR
# -------------------------------------------------------------
def build_iskandar_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_DIR / "03_Iskandar_Domain_Expert_SozLab.pdf"),
        pagesize=A4,
        leftMargin=45, rightMargin=45,
        topMargin=45, bottomMargin=45
    )
    styles = get_styles()
    story = []

    # Header
    story.extend(create_header(
        None,
        "3. DOMAIN EXPERT & LEGAL/DATA RESEARCHER",
        "Iskandar",
        "NORMATIV-HUQUQIY BAZA & BILIMLAR STRUKTURASI",
        styles
    ))

    # CP1 Section
    cp1_tasks = [
        "• <b>Oliy Ta'lim Me'yoriy Bazasini To'plash:</b> Vazirlikning amaldagi asosiy normativ hujjatlarini tizimlashtirish: VMQ 468-son (Bakalavriatga qabul), PF-81-son (Grantlarni GPA bo'yicha qayta taqsimlash), VMQ 345-son (TTJ arizalari), PQ-5071 (Ijara kompensatsiyasi), VMQ 620 (Nostrifikatsiya), PQ-323 (Xotin-qizlar ta'lim krediti).",
        "• <b>Top-25 Rasmiy Savol-Javob (FAQ) Matnini Shakllantirish:</b> Har bir savolga qonuniy havola (modda, band) ko'rsatilgan aniq o'zbekcha matn yozish.",
        "• <b>CP1 Mentorlariga Huquqiy Dalil:</b> Tizim nima uchun oddiy chatbot emas, balki rasmiy davlat hujjatlariga tayangan ishonchli me'yoriy yordamchi ekanligini isbotlash."
    ]
    story.append(create_box("📌 CHECKPOINT 1 (CP1) GACHA VAZIFALAR (Legal Research & FAQ Dataset)", cp1_tasks, styles, SKY, LIGHT_BG))
    story.append(Spacer(1, 5))

    # CP2 Section
    cp2_tasks = [
        "• <b>Bilolbek uchun Knowledge Base JSON:</b> Barcha 25+ me'yoriy ma'lumotlarni structured JSON formatida Bilolbekka topshirish (`backend/app/services/knowledge_base.py` uchun).",
        "• <b>Talabalar Sleng & Jargon Lug'atini Tuzish:</b> 'perevod', 'super-kontrakt', 'yotoqxona', 'stipuxa', 'propiska', 'kvota' kabi noformal so'zlarni rasmiy atamalarga moslashtirish qoidalarini yozish.",
        "• <b>AI Javoblarini Validatsiya Qilish (Hallucination Check):</b> Tizim generatsiya qilgan javoblarni haqiqiy qonunchilik bilan solishtirib chiqish, yolg'on ma'lumot (feyk) yo'qligini tekshirish.",
        "• <b>Taqdimot Uchun Huquqiy Slayd:</b> Fayzullohga 'Normative & Legal Foundation' slaydiga kiritiladigan rasmiy asoslar ro'yxatini berish."
    ]
    story.append(create_box("🚀 CHECKPOINT 2 (CP2) GACHA VAZIFALAR (Knowledge Dataset & Fact Verification)", cp2_tasks, styles, BLUE, LIGHT_BG))
    story.append(Spacer(1, 5))

    # Final Stage Section
    final_tasks = [
        "• <b>Q&A Himoyasida Ekspert Yordami:</b> Hakamlar hay'atidagi ta'lim sohasi vakillari yoki huquqshunoslar murakkab qonunchilik bo'yicha savol berganda tezkor yordam berish.",
        "• <b>Vazirlik Integratsiyasi Bo'yicha Yo'riqnoma:</b> Kelgusida yangi qarorlar qabul qilinganda bilimlar bazasini yangilash reglamentini ishlab chiqish.",
        "• <b>Yakuniy Nazorat:</b> Web-platformadagi `FAQ` bo'limida barcha VMQ va PQ raqamlari to'g'ri ko'rsatilganligini oxirgi marta tekshirib chiqish."
    ]
    story.append(create_box("🏆 XAKATON YAKUNIGACHA VAZIFALAR (Legal Defense & Accuracy Guarantee)", final_tasks, styles, GOLD, LIGHT_BG))

    story.append(PageBreak())

    # PAGE 2: Connections & Resources
    story.extend(create_header(
        None,
        "3. ISKANDAR — BOG'LIQLIKLAR VA MANBALAR",
        "Domain Expert & Researcher",
        "LEGAL PORTALS & KNOWLEDGE DATASET",
        styles
    ))

    connections = [
        "• <b>Bilolbekka topshirasiz:</b> Rasmiy normativ hujjatlar matni, FAQ savollar to'plami va talabalar sinonimlar lug'atini.",
        "• <b>Fayzullohga topshirasiz:</b> Taqdimot uchun qonuniy raqamlar, qarorlar sanasi va rasmiy statistika tezislari.",
        "• <b>Temurmalikka topshirasiz:</b> Kontrakt stavkalari, ijara kompensatsiyasi me'yorlari (BHM 50%) va kredit foizlari ma'lumotlarini.",
        "• <b>Ziyovuddinga topshirasiz:</b> UI interfeysidagi normativ ma'lumotnoma bloklarining rasmiy nomlari va matnlarini."
    ]
    story.append(create_box("🤝 JAMOA A'ZOLARI BILAN BOG'LIQLIK (Handoffs & Inputs)", connections, styles, EMERALD, LIGHT_BG))
    story.append(Spacer(1, 5))

    resources = [
        "• <b>Lex.uz Qonunchilik Portali:</b> https://lex.uz — O'zbekiston Respublikasi barcha qonun, Farmon va VMQ qarorlari rasmiy matni.",
        "• <b>Oliy ta'lim vazirligi:</b> https://edu.uz — Normativ me'yoriy hujjatlar va yangi qabul nizomlari.",
        "• <b>Bilimni baholash agentligi:</b> https://uzbmb.uz — Qabul kvotalari, test sinovlari va o'tish ballari statistikasi.",
        "• <b>Yagona davlat xizmatlari portali:</b> https://my.gov.uz — TTJ yotoqxona va nostrifikatsiya davlat xizmatlari reglamenti.",
        "• <b>Ta'lim sifatini nazorat qilish inspeksiyasi:</b> TOP-1000 universitetlar ro'yxati va xorijiy diplomlarni tan olish tartibi."
    ]
    story.append(create_box("🔗 FOYDALI HAVOLALAR, MANBALAR VA VOSITALAR", resources, styles, SKY, LIGHT_BG))
    story.append(Spacer(1, 5))

    checklist = [
        "✔ Qonuniylik: Barcha keltirilgan qarorlar 2024-2026 yillarda amalda ekanligini tekshirish (eskirgan nizomlarni kiritmaslik!).",
        "✔ GPA tizimi: PF-81 bo'yicha grantlar har yili qayta taqsimlanishi to'g'risidagi qoidaning to'g'ri bayon etilganligi.",
        "✔ Xotin-qizlar imtiyozi: Foizsiz ta'lim krediti bo'yicha PQ-323 mexanizmi to'g'ri keltirilganligi.",
        "✔ Fakt tekshiruvi: AI javoblarida noaniq yoki to'qima huquqiy normalar yo'qligi."
    ]
    story.append(create_box("✅ DOMAIN EXPERT QAT'IY CHECKLISTI", checklist, styles, PURPLE, LIGHT_BG))

    doc.build(story, canvasmaker=NumberedCanvas)

# -------------------------------------------------------------
# 4. TEMURMALIK
# -------------------------------------------------------------
def build_temurmalik_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_DIR / "04_Temurmalik_Business_Analyst_SozLab.pdf"),
        pagesize=A4,
        leftMargin=45, rightMargin=45,
        topMargin=45, bottomMargin=45
    )
    styles = get_styles()
    story = []

    # Header
    story.extend(create_header(
        None,
        "4. BUSINESS ANALYST & FINANCIAL STRATEGIST",
        "Temurmalik",
        "MOLIYAVIY MODEL, ROI VA B2G BIZNES STRATEGIYASI",
        styles
    ))

    # CP1 Section
    cp1_tasks = [
        "• <b>Hozirgi Call-Markaz Xarajatlari Tahlili:</b> 1006 call-markazining mavjud xarajatlarini hisoblash: 50 ta operator x 4.5 mln so'm = 225 mln so'm/oy. Yozgi 3 oylik qabul mavsumida 675 mln so'm faqat oylik maoshga sarflanadi.",
        "• <b>Mavjud Muammo Metrikasi:</b> Mavsumiy yuklamada qo'ng'iroqlarni o'tkazib yuborish (Call Drop Rate) 40% dan oshadi, fuqarolar o'rtacha 8-12 daqiqa kutadi.",
        "• <b>AI Tejamkorlik Konsepsiyasi:</b> Qo'ng'iroqlarning 80% qismini AI yordamchi 1.2 soniyada javoblab hal etsa, operatorlar yuklamasi 5 baravarga kamayadi.",
        "• <b>CP1 Himoyasi:</b> Mentorlarga loyihaning iqtisodiy jihatdan davlatga keltiradigan naqd foydasini isbotlash."
    ]
    story.append(create_box("📌 CHECKPOINT 1 (CP1) GACHA VAZIFALAR (Cost Baseline & ROI Hypothesis)", cp1_tasks, styles, SKY, LIGHT_BG))
    story.append(Spacer(1, 5))

    # CP2 Section
    cp2_tasks = [
        "• <b>Unit Economics Hisob-Kitobi:</b> 1 ta qo'ng'iroq narxi: An'anaviy inson operatorida = <b>~5,500 so'm ($0.45)</b> | SözLab AI da (Server + Gemini + TTS) = <b>~40 so'm ($0.003)</b>. Tejamkorlik: <b>130 barobar!</b>",
        "• <b>Bozor Hajmi (TAM / SAM / SOM):</b> TAM: O'zbekistondagi barcha 210+ OTM va 10 000+ maktablar (15 mln murojaatlar) | SAM: Oliy va professional ta'lim tizimi (3 mln talaba va abituriyent) | SOM: Vazirlikning 1006 call markazi (yiliga 500k+ qo'ng'iroq).",
        "• <b>Fayzullohga Biznes Slaydlarini Tayyorlash:</b> Taqdimotning 6-slaydi (Business & Revenue Model) va 7-slaydi (Market Size & ROI) uchun tayyor jadvallar va diagrammalarni topshirish.",
        "• <b>Yillik Iqtisodiy Samara Modeli:</b> Vazirlik uchun yillik <b>1.2 milliard so'm</b> to'g'ridan-to'g'ri byudjet mablag'lari tejalishi isboti."
    ]
    story.append(create_box("🚀 CHECKPOINT 2 (CP2) GACHA VAZIFALAR (Financial Model & Market Sizing)", cp2_tasks, styles, BLUE, LIGHT_BG))
    story.append(Spacer(1, 5))

    # Final Stage Section
    final_tasks = [
        "• <b>Roadmap & Go-to-Market Rejasi:</b> 1-bosqich (2026 Q3): Vazirlik 1006 markaziga to'liq integratsiya; 2-bosqich (2027 Q1): Har bir OTM qabul komissiyasiga individual ovozli bot; 3-bosqich (2027 Q3): Barcha ta'lim vazirliklariga yagona SaaS platforma sifatida tatbiq etish.",
        "• <b>Hakamlar Moliyaviy Savollariga Javob:</b> 'Tizimni ushlab turish xarajati qancha?', 'Davlat buni qanday xarid qiladi?' degan savollarga aniq raqamlar bilan javob berish.",
        "• <b>Ijtimoiy Ta'sir (Social Impact):</b> Korrupsiyani kamaytirish, shaffoflikni 100% ga yetkazish va abituriyentlarning sarson bo'lishiga chek qo'yish metrikalari."
    ]
    story.append(create_box("🏆 XAKATON YAKUNIGACHA VAZIFALAR (Roadmap & Economic Defense)", final_tasks, styles, GOLD, LIGHT_BG))

    story.append(PageBreak())

    # PAGE 2: Connections & Resources
    story.extend(create_header(
        None,
        "4. TEMURMALIK — BOG'LIQLIKLAR VA MANBALAR",
        "Business Analyst",
        "FINANCIAL MODELS & MARKET DATA",
        styles
    ))

    connections = [
        "• <b>Bilolbekdan olasiz:</b> Server, GPU va API xarajatlari (Gemini narxlari, cloud hosting) metrikalarini.",
        "• <b>Iskandardan olasiz:</b> Oliy ta'lim tizimidagi talabalar va abituriyentlar soni, murojaatlar hajmi statistikasini.",
        "• <b>Fayzullohga topshirasiz:</b> Taqdimotning 'Biznes model', 'Unit Economics' va 'Moliyaviy samara' slayd ma'lumotlarini.",
        "• <b>Ziyovuddinga topshirasiz:</b> Slaydlarga chiziladigan infografika va taqqoslash diagrammalari uchun aniq raqamlarni."
    ]
    story.append(create_box("🤝 JAMOA A'ZOLARI BILAN BOG'LIQLIK (Handoffs & Inputs)", connections, styles, EMERALD, LIGHT_BG))
    story.append(Spacer(1, 5))

    resources = [
        "• <b>Stat.uz Davlat Statistika Agentligi:</b> https://stat.uz — O'zbekiston ta'lim sektori demografik va moliyaviy ma'lumotlari.",
        "• <b>Gartner AI in Customer Service Report:</b> AI call-centerlarning samaradorlik va xarajat qisqartirish tadqiqotlari.",
        "• <b>B2G Procurement Uzbekistan:</b> https://xarid.uzbmb.uz — Davlat xaridlari tizimida IT loyihalarni joriy etish tartibi.",
        "• <b>Google Sheets Financial Model Template:</b> SaaS unit economics va xarajat-foyda jadvallari.",
        "• <b>O'zbekiston Respublikasi Davlat Byudjeti qonuni:</b> Oliy ta'lim vazirligi uchun ajratiladigan yillik xarajatlar smetasi."
    ]
    story.append(create_box("🔗 FOYDALI HAVOLALAR, MANBALAR VA VOSITALAR", resources, styles, SKY, LIGHT_BG))
    story.append(Spacer(1, 5))

    checklist = [
        "✔ Realistik raqamlar: Barcha xarajatlar O'zbekistonning real oylik maoshlari va bozor narxlariga asoslanganligi.",
        "✔ Unit Economics: 1 ta qo'ng'iroq narxi 130 barobar arzonlashishi aniq formulada ko'rsatilganligi.",
        "✔ B2G modeli: Loyiha davlat byudjeti yoki OTMlarning maxsus rivojlantirish jamg'armasi hisobidan moliyalashtirilishi aniq belgilanganligi.",
        "✔ Slayd mosligi: Fayzulloh aytadigan raqamlar bilan slayddagi raqamlar 100% mos kelishi."
    ]
    story.append(create_box("✅ BUSINESS ANALYST QAT'IY CHECKLISTI", checklist, styles, PURPLE, LIGHT_BG))

    doc.build(story, canvasmaker=NumberedCanvas)

# -------------------------------------------------------------
# 5. ZIYOVUDDIN
# -------------------------------------------------------------
def build_ziyovuddin_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_DIR / "05_Ziyovuddin_UIUX_Designer_SozLab.pdf"),
        pagesize=A4,
        leftMargin=45, rightMargin=45,
        topMargin=45, bottomMargin=45
    )
    styles = get_styles()
    story = []

    # Header
    story.extend(create_header(
        None,
        "5. UI/UX DESIGNER & MEDIA LEAD",
        "Ziyovuddin",
        "DIZAYN TIZIMI, MEDIA MAHSULOTLAR VA TAQDIMOT VIZUALIZATSIYASI",
        styles
    ))

    # CP1 Section
    cp1_tasks = [
        "• <b>SözLab Davlat Dizayn Tizimi (Design System):</b> Ranglar palitrasi (To'q ko'k `#081e38`, `#0b2b50`, Zumrad `#10b981`, Oltin `#f59e0b`), tipografika (Inter/Segoe UI), O'zbekiston Respublikasi Gerbi va davlat ramzlari piktogrammalarini to'plash.",
        "• <b>Foydalanuvchi Yo'li (User Journey Map):</b> Fuqaroning ovozli muloqot qilishi, inson-operatorning qo'ng'iroqni qabul qilishi va vazirlik adminining boshqaruv paneli chizmalarini yaratish.",
        "• <b>CP1 Mentorlariga Vizual Taqdimot:</b> Loyihaning yuqori darajadagi davlat portali sifatidagi vizual konsepsiyasini ko'rsatish."
    ]
    story.append(create_box("📌 CHECKPOINT 1 (CP1) GACHA VAZIFALAR (Design System & User Flows)", cp1_tasks, styles, SKY, LIGHT_BG))
    story.append(Spacer(1, 5))

    # CP2 Section
    cp2_tasks = [
        "• <b>10 Ta Slaydli Pitch Deck Dizaynini Tugallash:</b> Fayzulloh yozgan matnlar asosida har bir slaydni Figma/Canva da professional darajaga yetkazish.",
        "• <b>Qurilma Ramkalari (Device Mockups):</b> Bilolbek ishga tushirgan haqiqiy SözLab interfeysini iPhone 16 Pro va MacBook Pro ramkalariga joylab, slaydlarga qo'yish.",
        "• <b>Infografika va Diagrammalar:</b> Temurmalik hisoblagan Unit economics ($0.003 vs $0.45) va 1.2 mlrd so'mlik tejamkorlik jadvallarini ko'zga tashlanadigan chiroyli diagrammalarga aylantirish.",
        "• <b>60 Soniyalik Demo Video Rolik:</b> OBS Studio yoki CapCut orqali platformaning real ovozli ishlash jarayonini 60 soniyalik Full HD video formatida yozib olib montaj qilish."
    ]
    story.append(create_box("🚀 CHECKPOINT 2 (CP2) GACHA VAZIFALAR (Slide Polish & 60s Demo Video)", cp2_tasks, styles, BLUE, LIGHT_BG))
    story.append(Spacer(1, 5))

    # Final Stage Section
    final_tasks = [
        "• <b>Backup Media Fleshka:</b> Tayyor 60 soniyalik video, yakuniy taqdimot PDF va PPTX fayllarini fleshkaga yozib, Fayzullohga topshirish.",
        "• <b>Proyektor Kontrasti Tekshiruvi:</b> Sahnadagi proyektorlarda slayd ranglari xira bo'lib qolmasligi uchun yuqori kontrastli (High Contrast) rejimni ta'minlash.",
        "• <b>Sahna Taqdimotida Yordam:</b> Fayzulloh chiqishi paytida slaydlar almashinuvi va video ishga tushishini texnik nazorat qilib turish."
    ]
    story.append(create_box("🏆 XAKATON YAKUNIGACHA VAZIFALAR (Media Backup & Stage Support)", final_tasks, styles, GOLD, LIGHT_BG))

    story.append(PageBreak())

    # PAGE 2: Connections & Resources
    story.extend(create_header(
        None,
        "5. ZIYOVUDDIN — BOG'LIQLIKLAR VA MANBALAR",
        "UI/UX Designer & Media Lead",
        "DESIGN KITS & MEDIA ASSETS",
        styles
    ))

    connections = [
        "• <b>Bilolbekdan olasiz:</b> Haqiqiy ishlayotgan frontenddan skrinshotlar, to'lqin visualizatori va video olish uchun toza ekran.",
        "• <b>Fayzullohdan olasiz:</b> Slaydlardagi matnlar, sarlavhalar va slaydlar almashinish ketma-ketligi.",
        "• <b>Temurmalikdan olasiz:</b> Bozor hajmi (TAM/SAM/SOM) va tejamkorlik grafiklari raqamlarini.",
        "• <b>Iskandardan olasiz:</b> Vazirlikning rasmiy logotiplari va yuridik normativ bloklar nomlanishini.",
        "• <b>Fayzullohga topshirasiz:</b> 100% tayyor 10 ta slaydli taqdimot fayli (PPTX + PDF) va 60 soniyalik video demo."
    ]
    story.append(create_box("🤝 JAMOA A'ZOLARI BILAN BOG'LIQLIK (Handoffs & Inputs)", connections, styles, EMERALD, LIGHT_BG))
    story.append(Spacer(1, 5))

    resources = [
        "• <b>Figma GovTech Design Kits:</b> https://www.figma.com/community — Davlat tashkilotlari va call-markazlar uchun tayyor UI elementlar.",
        "• <b>Mockup World (Apple Devices):</b> https://www.mockupworld.co — iPhone va MacBook Pro yuqori aniqlikdagi PSD/PNG ramkalari.",
        "• <b>Unsplash Education Photos:</b> https://unsplash.com — Slaydlar uchun talabalar va oliygohlar sifatli suratlari.",
        "• <b>OBS Studio:</b> https://obsproject.com — Noutbuk ekranidan toza 60 FPS video yozib olish vositasi.",
        "• <b>CapCut Desktop:</b> O'zbekcha audio va vizual effektlarni 60 soniyalik rolikda tezkor montaj qilish."
    ]
    story.append(create_box("🔗 FOYDALI HAVOLALAR, MANBALAR VA VOSITALAR", resources, styles, SKY, LIGHT_BG))
    story.append(Spacer(1, 5))

    checklist = [
        "✔ Slayd kontrasti: Oq fonda to'q ko'k matn va yorqin zumrad urg'ular (katta zallarda o'qilishi shart).",
        "✔ Ekran tasvirlari: Barcha mockup rasmlari xira emas, yuqori aniqlikda (Retina / 2x) eksport qilinganligi.",
        "✔ Video demo: 60 soniyadan oshmaganligi, ekranda real ovozli suhbat aniq eshitilishi.",
        "✔ Formatlar: Taqdimot ham PPTX, ham PDF formatda saqlanganligi (shriftlar buzilmasligi uchun)."
    ]
    story.append(create_box("✅ UI/UX VA MEDIA LEAD CHECKLISTI", checklist, styles, PURPLE, LIGHT_BG))

    doc.build(story, canvasmaker=NumberedCanvas)

# -------------------------------------------------------------
# 0. MASTER PLAN (JAMOA UMUMIY REJASI)
# -------------------------------------------------------------
def build_master_plan_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_DIR / "00_Jamoa_Master_Rejasi_SozLab.pdf"),
        pagesize=A4,
        leftMargin=45, rightMargin=45,
        topMargin=45, bottomMargin=45
    )
    styles = get_styles()
    story = []

    # Header
    story.extend(create_header(
        None,
        "SÖZLAB — JAMOA MASTER HARAKATLAR REJASI",
        "Barcha A'zolar (Bilolbek, Fayzulloh, Iskandar, Temurmalik, Ziyovuddin)",
        "UMUMIY SINXRONIZATSIYA & G'ALABA XARITASI",
        styles
    ))

    team_table_data = [
        [
            Paragraph("<b>Ism & Mas'ul</b>", styles['BodyB']),
            Paragraph("<b>Asosiy Rol</b>", styles['BodyB']),
            Paragraph("<b>CP1 Natijasi</b>", styles['BodyB']),
            Paragraph("<b>CP2 Natijasi</b>", styles['BodyB']),
            Paragraph("<b>Final Natijasi</b>", styles['BodyB'])
        ],
        [
            Paragraph("<b>1. Bilolbek</b>", styles['Body']),
            Paragraph("Lead Developer / AI Integrator", styles['Body']),
            Paragraph("FastAPI, Gemini, TTS, Call Simulator", styles['Body']),
            Paragraph("Ovoz STT/TTS, 3 Rol, FIFO Navbat", styles['Body']),
            Paragraph("Offline Demo, Sahna Sinxroni", styles['Body'])
        ],
        [
            Paragraph("<b>2. Fayzulloh</b>", styles['Body']),
            Paragraph("PM & Lead Pitcher", styles['Body']),
            Paragraph("Muammo formulasi, PPTX qoralama", styles['Body']),
            Paragraph("10 ta to'liq slayd, 3:00 nutq matni", styles['Body']),
            Paragraph("Sahna pitchingi, Jonli demo, Q&A", styles['Body'])
        ],
        [
            Paragraph("<b>3. Iskandar</b>", styles['Body']),
            Paragraph("Domain Expert & Legal Researcher", styles['Body']),
            Paragraph("VMQ, PF qarorlari, Top-25 FAQ", styles['Body']),
            Paragraph("Knowledge Base JSON, Sleng lug'ati", styles['Body']),
            Paragraph("Yuridik himoya, Fact-check", styles['Body'])
        ],
        [
            Paragraph("<b>4. Temurmalik</b>", styles['Body']),
            Paragraph("Business Analyst & Strategist", styles['Body']),
            Paragraph("Mavjud 1006 xarajatlar bazasi", styles['Body']),
            Paragraph("Unit economics ($0.003), 1.2 mlrd ROI", styles['Body']),
            Paragraph("Roadmap, B2G savollar himoyasi", styles['Body'])
        ],
        [
            Paragraph("<b>5. Ziyovuddin</b>", styles['Body']),
            Paragraph("UI/UX Designer & Media Lead", styles['Body']),
            Paragraph("Design system, User flow chizmasi", styles['Body']),
            Paragraph("PPTX dizayni, Mockuplar, 60s video", styles['Body']),
            Paragraph("Fleshka backup, Sahna nazorati", styles['Body'])
        ]
    ]
    t_team = Table(team_table_data, colWidths=[70, 115, 105, 110, 105])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 5))

    cp1_all = [
        "• <b>Maqsad:</b> Hakamlar va mentorlarga jamoaning aniq og'riqli muammoga ega ekanligi, arxitektura chizilgani va prototip ishlayotganini ko'rsatish.",
        "• <b>Kutiladigan natija:</b> Ishlayotgan Call Simulator havolasi (Bilolbek), PPTX Draft 1 (Fayzulloh), 25 ta FAQ (Iskandar), 1006 xarajatlar tahlili (Temurmalik), Design System (Ziyovuddin)."
    ]
    story.append(create_box("🚩 CHECKPOINT 1 — ASOSIY MARRA VA TALABLAR", cp1_all, styles, SKY, LIGHT_BG))
    story.append(Spacer(1, 4))

    cp2_all = [
        "• <b>Maqsad:</b> MVP to'liq ishga tushishi, ovozli xabarlar almashinuvi, 3 ta foydalanuvchi roli (Fuqaro, Operator, Admin), smart navbat va 10 ta slaydli to'liq taqdimot tayyor bo'lishi.",
        "• <b>Kutiladigan natija:</b> STT/TTS ovozli xizmat (Bilolbek), 10 ta yakuniy slayd va 180 soniyalik nutq (Fayzulloh), Knowledge Base JSON (Iskandar), Unit economics & ROI (Temurmalik), Mockuplar va 60 soniyalik video demo (Ziyovuddin)."
    ]
    story.append(create_box("🚩 CHECKPOINT 2 — MVP INTEGRATSIYASI VA TAQDIMOT TAYYORLIGI", cp2_all, styles, BLUE, LIGHT_BG))
    story.append(Spacer(1, 4))

    final_all = [
        "• <b>Maqsad:</b> Sahnada 3 daqiqalik yorqin chiqish, real jonli ovozli muloqotni namoyish qilish va hakamlarning barcha savollariga zarba berib 1-o'rinni yutish.",
        "• <b>Vaqt taqsimoti (3:00):</b> 0:00-0:30 Muammo va dolzarblik | 0:30-1:15 Jonli ovozli demo | 1:15-2:15 Biznes & Tejamkorlik | 2:15-3:00 Skalatsiya & Xulosa."
    ]
    story.append(create_box("🚩 FINAL PITCH & SAHNA TAQDIMOTI (G'alaba Mezonlari)", final_all, styles, GOLD, LIGHT_BG))

    story.append(PageBreak())

    # PAGE 2: Risk Management & Communication
    story.extend(create_header(
        None,
        "SÖZLAB — FAVQULODDA REJALAR VA PROTOKOL",
        "Jamoa Protokoli",
        "RISK MANAGEMENT & VICTORY PLAYBOOK",
        styles
    ))

    risks = [
        "• <b>1-Xavf: Sahnada Wi-Fi uzilib qolishi yoki sekinlashishi:</b><br/>"
        "➔ <i>Yechim:</i> Bilolbek noutbukida lokal rejimda backend va frontendni ishga tushirib qo'ygan bo'ladi (`start_dev.ps1`). Internet bo'lmasa ham lokal IP orqali demo ishlaydi. Agar noutbuk proyektorga ulanmasa, Ziyovuddin tayyorlagan 60 soniyalik Full HD video darhol pultdan qo'yiladi.",
        "• <b>2-Xavf: Mikrofon shovqinda ovozni yaxshi yozmasligi:</b><br/>"
        "➔ <i>Yechim:</i> Saytda tayyorlab qo'yilgan 'Tezkor Demo Savollar' (1-klik orqali) tugmasi bitta bosiladi va tizim darhol Madina ovozida rasmiy javobni eshittiradi.",
        "• <b>3-Xavf: Hakam 'Halusinatsiya qilsa nima bo'ladi?' deb so'rashi:</b><br/>"
        "➔ <i>Yechim:</i> Iskandar va Fayzulloh: 'Bizning tizim ochiq internetdan javob qidirmaydi, faqat vazirlikning tasdiqlangan VMQ va PF normativ bazasi (RAG) asosida cheklangan kontekstda ishlaydi. Noaniq savollarda tizim to'qima javob bermay, qo'ng'iroqni avtomatik ravishda inson-operator navbatiga yo'naltiradi.'",
        "• <b>4-Xavf: Hakam 'Xarajatlar o'zini qoplaydimi?' deb so'rashi:</b><br/>"
        "➔ <i>Yechim:</i> Temurmalik va Fayzulloh: 'Bitta inson-operatori har bir qo'ng'iroq uchun ~5,500 so'm xarajat talab qilsa, SözLab AI bor-yo'g'i ~40 so'm ($0.003) sarflaydi. 1 yilda davlat byudjetidan 1.2 milliard so'm mablag' tejaladi.'"
    ]
    story.append(create_box("🛡️ FAVQULODDA VAZIYATLAR UCHUN BACKUP REJALAR (Risk Matrix)", risks, styles, PURPLE, LIGHT_BG))
    story.append(Spacer(1, 5))

    comms = [
        "• <b>Muloqot kanali:</b> Telegram guruhida barcha muhim fayllar (PDF, PPTX, video) 'PIN' qilib qo'yilishi shart.",
        "• <b>Tinchlik va konsentratsiya:</b> CP1 va CP2 oldidan har bir a'zo o'z topshirig'ini 15 daqiqa oldin topshiradi, oxirgi soniyalarda shoshilmaslik uchun.",
        "• <b>Sahnada jamoaviy birlik:</b> Sahnaga 5 kishi birgalikda chiqadi, Fayzulloh gapiradi, boshqalar o'z yo'nalishi bo'yicha savollarga professional javob beradi."
    ]
    story.append(create_box("💬 JAMOA PROTOKOLI VA G'ALABA MADANIYATI", comms, styles, EMERALD, LIGHT_BG))

    doc.build(story, canvasmaker=NumberedCanvas)

def main():
    print("Generating comprehensive team guides with exact members and CP1/CP2/Final tasks...")
    build_bilolbek_pdf()
    build_fayzulloh_pdf()
    build_iskandar_pdf()
    build_temurmalik_pdf()
    build_ziyovuddin_pdf()
    build_master_plan_pdf()
    print("All 6 PDFs successfully generated in team_guides/!")

if __name__ == '__main__':
    main()
