import os
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Register TrueType fonts
pdfmetrics.registerFont(TTFont('SegoeUI', 'C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUI-Bold', 'C:/Windows/Fonts/segoeuib.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUI-Italic', 'C:/Windows/Fonts/segoeuii.ttf'))

FONT_REGULAR = 'SegoeUI'
FONT_BOLD = 'SegoeUI-Bold'

NAVY = colors.HexColor('#081E38')
BLUE = colors.HexColor('#0B2B50')
SKY = colors.HexColor('#1E6091')
EMERALD = colors.HexColor('#0D9488')
GOLD = colors.HexColor('#D97706')
LIGHT_BG = colors.HexColor('#F8FAFC')
CARD_BG = colors.HexColor('#FFFFFF')
TEXT_DARK = colors.HexColor('#0F172A')
TEXT_MUTED = colors.HexColor('#475569')
BORDER_COLOR = colors.HexColor('#CBD5E1')
ORANGE_ACCENT = colors.HexColor('#EA580C')

OUTPUT_FILE = Path('c:/dev/Projects/vazir-chat/team_guides/06_SozLab_Lean_Canvas.pdf')
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

class LandscapeNumberedCanvas(canvas.Canvas):
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
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, total_pages):
        self.saveState()
        self.setFont(FONT_REGULAR, 7)
        self.setFillColor(TEXT_MUTED)
        self.drawString(25, 14, "LEAN CANVAS • SÖZLAB — Ta'lim va Innovatsiyalar Vazirligi AI Call-Markazi • Umummilliy AI Xakaton, Namangan 2026")
        self.drawRightString(landscape(A4)[0] - 25, 14, f"Bitta Sahifada Butun Biznes • Sahifa {self._pageNumber} / {total_pages}")
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_FILE),
        pagesize=landscape(A4),
        leftMargin=25, rightMargin=25,
        topMargin=20, bottomMargin=25
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='TopTag',
        fontName=FONT_BOLD,
        fontSize=7.5,
        leading=9.5,
        textColor=ORANGE_ACCENT,
    ))
    styles.add(ParagraphStyle(
        name='MainTitle',
        fontName=FONT_BOLD,
        fontSize=14,
        leading=16,
        textColor=NAVY,
    ))
    styles.add(ParagraphStyle(
        name='SubTitle',
        fontName=FONT_REGULAR,
        fontSize=8,
        leading=10,
        textColor=TEXT_MUTED,
    ))
    styles.add(ParagraphStyle(
        name='BoxNum',
        fontName=FONT_BOLD,
        fontSize=9,
        leading=11,
        textColor=ORANGE_ACCENT,
    ))
    styles.add(ParagraphStyle(
        name='BoxTitle',
        fontName=FONT_BOLD,
        fontSize=9,
        leading=11,
        textColor=BLUE,
    ))
    styles.add(ParagraphStyle(
        name='BoxSub',
        fontName=FONT_REGULAR,
        fontSize=6.5,
        leading=8.5,
        textColor=TEXT_MUTED,
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name='BoxItem',
        fontName=FONT_REGULAR,
        fontSize=6.8,
        leading=9.2,
        textColor=TEXT_DARK,
        leftIndent=5,
        firstLineIndent=-5,
        spaceAfter=1.5,
    ))
    styles.add(ParagraphStyle(
        name='BoxItemUVP',
        fontName=FONT_BOLD,
        fontSize=7.5,
        leading=10.5,
        textColor=EMERALD,
        spaceAfter=4,
    ))

    story = []

    # Header Row
    header_table = Table([
        [
            Paragraph("LEAN CANVAS · RAQAMLAR – TO'LDIRISH TARTIBI (1 DAN 9 GACHA)", styles['TopTag']),
            Paragraph("Loyiha: <b>SözLab</b> • Trek: <b>Ta'lim (Education)</b>", styles['SubTitle'])
        ],
        [
            Paragraph("<b>Butun biznes bitta sahifada</b> — Biznes-reja emas, tekshirilishi kerak bo'lgan gipotezalar", styles['MainTitle']),

            Paragraph("Tayyorladi: <b>Jamoa (Bilolbek, Fayzulloh, Iskandar, Temurmalik, Ziyovuddin)</b>", styles['SubTitle'])
        ]
    ], colWidths=[550, 241])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceBefore=4, spaceAfter=5))

    # Helper function for cell contents
    def make_cell(num, title, sub, items, is_uvp=False):
        c = [
            Paragraph(f"<font color='#EA580C'><b>{num}</b></font>  <b>{title}</b>", styles['BoxTitle']),
            Paragraph(sub, styles['BoxSub']),
        ]
        if is_uvp:
            c.append(Paragraph(items[0], styles['BoxItemUVP']))
            for it in items[1:]:
                c.append(Paragraph(it, styles['BoxItem']))
        else:
            for it in items:
                c.append(Paragraph(it, styles['BoxItem']))
        return c

    # 1. Problem
    c_problem = make_cell(
        "1", "Problem (Muammo)", "Top-3 muammo va bugungi muqobillar",
        [
            "• <b>Call-markaz (1006) qulashi:</b> Yozgi qabul, kvota, super-kontrakt paytida 100k+ qo'ng'iroq, 42% uzilib ketadi (call drop).",
            "• <b>Kutish vaqti 8-12 daqiqa:</b> Fuqarolar uzoq kutadi, 70-80% savollar standart va takroriy.",
            "• <b>Operator charchog'i:</b> Qimmat inson resurslari bir xil savollarga sarflanadi, analitika yo'q.",
            "• <i>Bugungi muqobillar:</i> 1006 telefon (navbat uzun), my.gov.uz (faqat matn, noqulay), OTM binosiga borish (sarsonlik, korrupsiya)."
        ]
    )

    # 2. Customer Segments
    c_customers = make_cell(
        "2", "Customer Segments", "Kim? Early adopter'lar kim?",
        [
            "• <b>B2G Xaridor:</b> Oliy ta'lim, fan va innovatsiyalar vazirligi, UzBMBA agentligi, 210+ OTMlar.",
            "• <b>Oxirgi Foydalanuvchilar:</b> 1.2 mln abituriyent, 1 mln+ talaba, ularning ota-onalari.",
            "• <b>Early Adopter'lar:</b> 2026 qabul mavsumida 1006 ga telefon qiluvchi abituriyentlar va vazirlik Call-markazi rahbariyati.",
            "• <b>Qamrov:</b> Qishloq joylardagi va internet sekin hududlardagi barcha o'zbekzabon fuqarolar."
        ]
    )

    # 3. Unique Value Proposition
    c_uvp = make_cell(
        "3", "Unique Value Proposition", "Nega aynan siz? Bir jumlada",
        [
            "\"Abituriyent va talabaning har qanday savoliga 1 soniyada tabiiy o'zbek tilida rasmiy qonuniy javob beruvchi, navbatsiz va 24/7 ishlovchi birinchi davlat AI call-markazi.\"",
            "• <b>Konsept:</b> Oliy ta'lim vazirligi 1006 uchun aqlli o'zbek ovozli egizagi (Siri/Alexa for Ministry).",
            "• <b>Tezlik:</b> Javob < 1.2s, kutish navbati: 0s.",
            "• <b>100% Huquqiy:</b> Faqat rasmiy qarorlar (VMQ 468, PF-81, VMQ 345) asosida, halusinatsiyasiz.",
            "• <b>Tabiiy Nutq:</b> Madina neyron ovozida o'zbekcha ravon muloqot va sleng tushunish."
        ],
        is_uvp=True
    )

    # 4. Solution
    c_solution = make_cell(
        "4", "Solution (Yechim)", "Har bir muammoga eng oddiy yechim",
        [
            "• <b>Real-vaqt Ovozli AI:</b> O'zbek nutqini darhol tushunib, 1.2s da ovozli javob qaytarish.",
            "• <b>Me'yoriy RAG Bazasi:</b> Qabul, grant, super-kontrakt va TTJ bo'yicha rasmiy qarorlar integratsiyasi.",
            "• <b>Smart Operator Dispatching:</b> AI hal qilolmaganda 3 ta navbatchi liniyaga va FIFO navbatga yo'naltirish."
        ]
    )

    # 5. Channels
    c_channels = make_cell(
        "5", "Channels (Kanallar)", "Mijozga qanday yetasiz",
        [
            "• <b>1006 Ishonch Telefoni:</b> Davlat SIP/PBX ATS tarmog'iga integratsiya.",
            "• <b>Veb-vidjet:</b> edu.uz va my.uzbmb.uz dagi ovozli qo'ng'iroq moduli.",
            "• <b>Telegram & my.gov.uz:</b> Ovozli bot va davlat ilovalari.",
            "• <b>B2G Davlat Xaridlari:</b> Innovatsion pilot shartnoma."
        ]
    )

    # 6. Revenue Streams
    c_revenue = make_cell(
        "6", "Revenue Streams (Daromad Oqimlari & Pul Modeli)", "Pul modeli, narx, LTV",
        [
            "• <b>B2G Yillik SaaS Shartnomasi:</b> Vazirlik uchun yiliga <b>400 — 600 mln so'm</b> (an'anaviy call-markazdan 3x arzon).",
            "• <b>OTMlar Uchun Obuna:</b> 210 ta OTM har biri o'z dekanat va qabul boti uchun oyiga <b>3 — 5 mln so'm</b> (Yillik bozor: ~8-10 mlrd so'm).",
            "• <b>Maxsus Integratsiyalar:</b> Shaxsiy SMS xabarnoma va bank to'lov tizimlari orqali shartnoma tekshirish xizmatlari."
        ]
    )

    # 7. Cost Structure
    c_cost = make_cell(
        "7", "Cost Structure (Xarajatlar Strukturasi)", "Mijoz jalb qilish, jamoa, infratuzilma, AI xarajatlari",
        [
            "• <b>AI & Cloud Hosting:</b> Gemini 2.5 API tokenlari, VPS, Edge-TTS kesh serveri: ~$400/oy.",
            "• <b>Jamoa va R&D:</b> AI/ML muhandis, backend, frontend, huquqshunos maoshi: ~$3,500/oy.",
            "• <b>Telekom & SIP:</b> Telefon liniyalari va tarmoq oqimi: ~$200/oy | <b>Yuridik monitoring:</b> ~$400/oy.",
            "• <b>Unit Economics:</b> 1 ta AI qo'ng'irog'i = <b>40 so'm ($0.003)</b> vs Inson operatori = <b>5,500 so'm ($0.45)</b>. <b>130 barobar arzon!</b>"
        ]
    )

    # 8. Key Metrics
    c_metrics = make_cell(
        "8", "Key Metrics (Asosiy Metrikalar)", "Ish yurayotganini qaysi raqam ko'rsatadi",
        [
            "• <b>AI Resolution Rate:</b> 85%+ (avtomatik yechim).",
            "• <b>Average Handle Time:</b> < 45 soniya.",
            "• <b>Call Drop Rate:</b> 42% dan 2% gacha tushirish.",
            "• <b>CSAT Qoniqish:</b> 4.8 / 5.0 yulduz.",
            "• <b>Yillik Tejamkorlik:</b> 1.2 milliard so'm."
        ]
    )

    # 9. Unfair Advantage
    c_advantage = make_cell(
        "9", "Unfair Advantage", "Nusxa ko'chirib yoki sotib olib bo'lmaydigan narsa",
        [
            "• <b>Rasmiy Normativ RAG:</b> ChatGPT bilmaydigan O'zbekiston VMQ va PF qonunchiligi bilan 100% integratsiya.",
            "• <b>Hybrid Human-in-the-Loop:</b> 3 ta inson-operatori bilan choksiz FIFO navbat va auto-pop.",
            "• <b>O'zbek Tili Slengi:</b> 'super', 'perevod', 'stipuxa' kabi talabalar jargonini tushunish.",
            "• <b>Davlat Suvereniteti:</b> Mahalliy serverlar va oflayn rejimda ishlash chidamliligi."
        ]
    )

    col_w = 791.89 / 5.0  # ~158.37 pt
    h_top = 175
    h_mid = 175
    h_bot = 120

    grid_data = [
        # Row 0: Upper
        [c_problem, c_solution, c_uvp, c_advantage, c_customers],
        # Row 1: Lower
        ['', c_metrics, '', c_channels, ''],
        # Row 2: Bottom
        [c_cost, '', '', c_revenue, '']
    ]

    grid_table = Table(
        grid_data,
        colWidths=[col_w, col_w, col_w, col_w, col_w],
        rowHeights=[h_top, h_mid, h_bot]
    )

    grid_table.setStyle(TableStyle([
        # Backgrounds
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        # Spans
        ('SPAN', (0,0), (0,1)),   # 1. Problem spans row 0-1
        ('SPAN', (2,0), (2,1)),   # 3. UVP spans row 0-1
        ('SPAN', (4,0), (4,1)),   # 2. Customer Segments spans row 0-1
        ('SPAN', (0,2), (2,2)),   # 7. Cost Structure spans col 0-2
        ('SPAN', (3,2), (4,2)),   # 6. Revenue Streams spans col 3-4

        # Grid lines
        ('GRID', (0,0), (-1,-1), 0.75, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1.5, BLUE),

        # UVP highlight box
        ('BACKGROUND', (2,0), (2,1), colors.HexColor('#F0FDF4')),
        ('BOX', (2,0), (2,1), 1.25, EMERALD),

        # Padding
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))

    story.append(grid_table)
    doc.build(story, canvasmaker=LandscapeNumberedCanvas)
    print(f"Lean Canvas PDF created successfully: {OUTPUT_FILE}")

if __name__ == '__main__':
    build_pdf()
