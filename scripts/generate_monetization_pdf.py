#!/usr/bin/env python3
"""
So'zLab / Vazir Chat: Monetizatsiya Strategiyasi, B2G Modeli va Unit Economics Hisoboti.
Ushbu skript professional formatdagi A4 PDF hisobotini generatsiya qiladi.
"""

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

# TrueType shriftlarni ro'yxatdan o'tkazish
FONT_REGULAR = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'
FONT_ITALIC = 'Helvetica-Oblique'

segoe_path = 'C:/Windows/Fonts/segoeui.ttf'
segoe_b_path = 'C:/Windows/Fonts/segoeuib.ttf'
segoe_i_path = 'C:/Windows/Fonts/segoeuii.ttf'

if os.path.exists(segoe_path) and os.path.exists(segoe_b_path):
    pdfmetrics.registerFont(TTFont('SegoeUI', segoe_path))
    pdfmetrics.registerFont(TTFont('SegoeUI-Bold', segoe_b_path))
    if os.path.exists(segoe_i_path):
        pdfmetrics.registerFont(TTFont('SegoeUI-Italic', segoe_i_path))
    FONT_REGULAR = 'SegoeUI'
    FONT_BOLD = 'SegoeUI-Bold'
    FONT_ITALIC = 'SegoeUI-Italic'

# Ranglar palitrasi
NAVY = colors.HexColor('#0A192F')
BLUE = colors.HexColor('#1E3A8A')
SKY = colors.HexColor('#0284C7')
EMERALD = colors.HexColor('#059669')
DARK_GREEN = colors.HexColor('#065F46')
LIGHT_GREEN_BG = colors.HexColor('#ECFDF5')
AMBER = colors.HexColor('#D97706')
LIGHT_BG = colors.HexColor('#F8FAFC')
CARD_BG = colors.HexColor('#F1F5F9')
TEXT_DARK = colors.HexColor('#0F172A')
TEXT_MUTED = colors.HexColor('#475569')
BORDER_COLOR = colors.HexColor('#CBD5E1')
PRIMARY_ACCENT = colors.HexColor('#2563EB')

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
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        self.saveState()
        self.setFont(FONT_REGULAR, 7.5)
        self.setFillColor(TEXT_MUTED)

        # Header (2-sahifadan boshlab)
        if self._pageNumber > 1:
            self.drawString(36, 808, "SÖZLAB (VAZIR CHAT) • MONETIZATSIYA STRATEGIYASI VA UNIT ECONOMICS")
            self.drawRightString(A4[0] - 36, 808, "B2G ENTERPRISE SAAS MODELI")
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.5)
            self.line(36, 800, A4[0] - 36, 800)

        # Footer
        self.line(36, 36, A4[0] - 36, 36)
        self.drawString(36, 25, "Konfidentsial • Umummilliy AI Xakaton (Namangan 2026) • Oliy ta'lim, fan va innovatsiyalar vazirligi")
        page_str = f"Sahifa {self._pageNumber} / {total_pages}"
        self.drawRightString(A4[0] - 36, 25, page_str)

        self.restoreState()


def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='MainTitle',
        fontName=FONT_BOLD,
        fontSize=15,
        leading=19,
        textColor=NAVY,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='MainSub',
        fontName=FONT_REGULAR,
        fontSize=8.5,
        leading=12,
        textColor=TEXT_MUTED,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='SecHead',
        fontName=FONT_BOLD,
        fontSize=10,
        leading=13.5,
        textColor=BLUE,
        spaceBefore=7,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='Body',
        fontName=FONT_REGULAR,
        fontSize=7.8,
        leading=11,
        textColor=TEXT_DARK,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='BodyBold',
        fontName=FONT_BOLD,
        fontSize=7.8,
        leading=11,
        textColor=TEXT_DARK,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='CustomBullet',
        fontName=FONT_REGULAR,
        fontSize=7.6,
        leading=10.6,
        textColor=TEXT_DARK,
        leftIndent=8,
        firstLineIndent=-8,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='TableCell',
        fontName=FONT_REGULAR,
        fontSize=7.2,
        leading=9.8,
        textColor=TEXT_DARK
    ))
    styles.add(ParagraphStyle(
        name='TableCellBold',
        fontName=FONT_BOLD,
        fontSize=7.2,
        leading=9.8,
        textColor=NAVY
    ))
    styles.add(ParagraphStyle(
        name='TableCellGreen',
        fontName=FONT_BOLD,
        fontSize=7.2,
        leading=9.8,
        textColor=DARK_GREEN
    ))
    styles.add(ParagraphStyle(
        name='CalloutText',
        fontName=FONT_REGULAR,
        fontSize=7.8,
        leading=11,
        textColor=DARK_GREEN
    ))
    styles.add(ParagraphStyle(
        name='KpiNum',
        fontName=FONT_BOLD,
        fontSize=13,
        leading=15,
        textColor=PRIMARY_ACCENT,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name='KpiLabel',
        fontName=FONT_REGULAR,
        fontSize=7,
        leading=9,
        textColor=TEXT_MUTED,
        alignment=1
    ))
    return styles


def build_pdf(target_paths):
    styles = get_styles()
    story = []

    # Title Header
    story.append(Paragraph("SÖZLAB: MONETIZATSIYA STRATEGIYASI VA UNIT ECONOMICS TAHLILI", styles['MainTitle']))
    story.append(Paragraph("<b>Loyiha:</b> Vazir Chat (Oliy ta'lim, fan va innovatsiyalar vazirligi AI Call Markazi) | <b>Model:</b> B2G Enterprise SaaS + B2B OTM Obunasi", styles['MainSub']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_ACCENT, spaceBefore=1, spaceAfter=5))

    # KPI Banner (4 ta asosiy ko'rsatkich)
    kpi_data = [
        [
            Paragraph("500 MLN UZS", styles['KpiNum']),
            Paragraph("1,000 UZS", styles['KpiNum']),
            Paragraph("390.8 UZS", styles['KpiNum']),
            Paragraph("61%", styles['KpiNum']),
            Paragraph("3.97 MLRD UZS", styles['KpiNum'])
        ],
        [
            Paragraph("B2G Yillik Kontrakt Qiymati", styles['KpiLabel']),
            Paragraph("1 ta Qo'ng'iroq Tushumi (ARPU)", styles['KpiLabel']),
            Paragraph("1 ta Qo'ng'iroq Tannarxi (COGS)", styles['KpiLabel']),
            Paragraph("Sof Rentabellik Marjasi", styles['KpiLabel']),
            Paragraph("Davlatga Yillik Tejamkorlik", styles['KpiLabel'])
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[104, 104, 104, 104, 104])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LINEVERTICAL', (1,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 4))

    # Executive Summary Card
    exec_data = [
        [
            Paragraph("<b>STRATEGIK XULOSA VA TANLANGAN MODEL:</b> Loyihamiz uchun <b>B2G (Business-to-Government) Enterprise SaaS</b> modeli tanlandi. B2C (abituriyentlardan pul olish) modeli qat'iyan rad etildi — davlat ishonch telefoniga qo'ng'iroq qiluvchi 1.2 mln abituriyent va talabalar uchun xizmat <b>100% BEPUL</b> bo'ladi. To'lov markazlashgan holda Vazirlik va OTMlarning maxsus rivojlantirish jamg'armalari hisobidan amalga oshiriladi.", styles['CalloutText'])
        ]
    ]
    t_exec = Table(exec_data, colWidths=[520])
    t_exec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GREEN_BG),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#A7F3D0")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_exec)
    story.append(Spacer(1, 4))

    # 1. ASOSIY 3 TA SAVOLGA ANIQ JAVOBLAR
    story.append(Paragraph("1. Monetizatsiyaning 3 Asosiy Ustuni: Kim? Qancha? Nega?", styles['SecHead']))

    t_three_q_data = [
        [
            Paragraph("<b>Savol</b>", styles['TableCellBold']),
            Paragraph("<b>Strategik Yechim va Aniq Ko'rsatkichlar</b>", styles['TableCellBold']),
            Paragraph("<b>Iqtisodiy Asos va Amaliy Mexanizm</b>", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>KIM TO'LAYDI?</b><br/><i>(Who Pays?)</i>", styles['TableCellBold']),
            Paragraph("<b>1. Bosh Mijoz (B2G):</b> O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligi hamda UzBMBA (Bilim va malakalarni baholash agentligi).<br/><b>2. Kengayish Mijozlari (B2B):</b> Respublika bo'yicha 210 dan ortiq davlat, nodavlat va xorijiy OTMlar (har bir universitet qabul komissiyasi).", styles['TableCell']),
            Paragraph("• To'lov davlat byudjeti va OTMlarning maxsus rivojlantirish jamg'armalaridan to'lanadi.<br/>• Fuqarolar va abituriyentlar uchun mutlaqo bepul (1006 / 1007 va veb-vidjet).<br/>• Davlat xaridlari (xarid.uzbmb.uz) orqali yillik to'g'ridan-to'g'ri dasturiy xizmat shartnomasi imzolanadi.", styles['TableCell'])
        ],
        [
            Paragraph("<b>QANCHA TO'LAYDI?</b><br/><i>(How Much?)</i>", styles['TableCellBold']),
            Paragraph("<b>• Vazirlik Yillik Enterprise Litsenziyasi:</b> <b>500,000,000 UZS / yil</b> (~$39,370 USD).<br/><b>• B2B OTMlar Dekanat/Qabul Moduli:</b> Har bir OTM uchun <b>4,000,000 UZS / oy</b> (yiliga 48,000,000 UZS / ~$3,780 USD).", styles['TableCell']),
            Paragraph("• Vazirlik uchun bu amaldagi call-markaz xarajatlaridan <b>88.3% arzonroq</b>.<br/>• OTMlar o'z qabul komissiyasida 10 ta operator ushlash o'rniga 4 mln so'm to'lab 35 mln so'm tejaydi.<br/>• To'lov bosqichma-bosqich: 30% avans, 70% oylik teng taqsimotda.", styles['TableCell'])
        ],
        [
            Paragraph("<b>NEGA TO'LAYDI?</b><br/><i>(Why They Pay?)</i>", styles['TableCellBold']),
            Paragraph("<b>1. Naqd Byudjet Tejami:</b> Vazirlik yiliga <b>3.97 milliard so'm</b> mablag'ni to'g'ridan-to'g'ri saqlab qoladi.<br/><b>2. Qabul Kollapsini Yo'qotish:</b> Yoz oylaridagi 100k+ qo'ng'iroqlarni 500+ parallel oqimda navbatsiz (0 soniya) qabul qiladi.<br/><b>3. 100% Qonuniy Aniq Javob:</b> VMQ 468, PF-81 qarorlari bo'yicha gallyutsinatsiyasiz yuridik javoblar.<br/><b>4. Call Drop 42% ➔ 2%:</b> Aholi noroziligi va shikoyatlari to'xtatiladi.", styles['TableCell']),
            Paragraph("• Inson operatori charchaydi, adashadi va 8-12 daqiqa kuttiradi. AI 1.2 soniyada javob beradi.<br/>• 3.97 mlrd so'm tejam hisobiga vazirlik 12 ta zamonaviy STEM laboratoriyasi qura oladi.<br/>• Davlat xizmatlarining ochiqlik va raqamlashtirish KPI ko'rsatkichlari (CSAT 4.8/5.0) bajariladi.", styles['TableCell'])
        ]
    ]

    t_three_q = Table(t_three_q_data, colWidths=[95, 230, 195])
    t_three_q.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('BACKGROUND', (0,1), (0,-1), LIGHT_BG),
    ]))
    story.append(t_three_q)
    story.append(Spacer(1, 5))

    # 2. UNIT ECONOMICS TAHLILI
    story.append(Paragraph("2. Unit Economics: 1 ta Qo'ng'iroq / Foydalanuvchi Birligi Tahlili", styles['SecHead']))
    story.append(Paragraph("Yillik rejalashtirilgan oqim: <b>500,000 ta qo'ng'iroq</b> (baho/qabul mavsumidagi asosiy yuklama bilan birga).", styles['Body']))

    t_unit_call_data = [
        [Paragraph("<b>Xarajat / Tushum Komponenti</b>", styles['TableCellBold']), Paragraph("<b>Birlik Ko'rsatkichi</b>", styles['TableCellBold']), Paragraph("<b>1 ta Qo'ng'iroqqa (UZS)</b>", styles['TableCellBold']), Paragraph("<b>1 ta Qo'ng'iroqqa (USD)</b>", styles['TableCellBold']), Paragraph("<b>Yillik Umumiy (500k call)</b>", styles['TableCellBold'])],
        [
            Paragraph("<b>B2G Tushum (Revenue per interaction)</b>", styles['TableCellBold']),
            Paragraph("500 mln UZS / 500,000 qo'ng'iroq", styles['TableCell']),
            Paragraph("<b>1,000.0 UZS</b>", styles['TableCellBold']),
            Paragraph("<b>$0.0787</b>", styles['TableCellBold']),
            Paragraph("<b>500,000,000 UZS</b>", styles['TableCellBold'])
        ],
        [
            Paragraph("Google Gemini 2.0 Flash LLM Tokeni", styles['TableCell']),
            Paragraph("2,000 input / 250 output token", styles['TableCell']),
            Paragraph("15.5 UZS", styles['TableCell']),
            Paragraph("$0.0012", styles['TableCell']),
            Paragraph("7,780,000 UZS", styles['TableCell'])
        ],
        [
            Paragraph("VoiceLab O'zbekcha TTS/STT (MD5 Kesh bilan)", styles['TableCell']),
            Paragraph("65% FAQ lokal bepul keshdan", styles['TableCell']),
            Paragraph("19.0 UZS", styles['TableCell']),
            Paragraph("$0.0015", styles['TableCell']),
            Paragraph("42,672,000 UZS", styles['TableCell'])
        ],
        [
            Paragraph("Cloud VPS & WebSocket Infratuzilmasi", styles['TableCell']),
            Paragraph("8 vCPU, 16GB RAM, Fast Redis", styles['TableCell']),
            Paragraph("3.5 UZS", styles['TableCell']),
            Paragraph("$0.0003", styles['TableCell']),
            Paragraph("12,960,000 UZS", styles['TableCell'])
        ],
        [
            Paragraph("SIP-Trunk Telekom Liniyalari (Kiruvchi)", styles['TableCell']),
            Paragraph("500+ parallel oqim kanali", styles['TableCell']),
            Paragraph("120.0 UZS", styles['TableCell']),
            Paragraph("$0.0094", styles['TableCell']),
            Paragraph("60,000,000 UZS", styles['TableCell'])
        ],
        [
            Paragraph("DevOps, Yuridik RAG Nazorati va MLOps", styles['TableCell']),
            Paragraph("Doimiy yangilanish va 24/7 SLA", styles['TableCell']),
            Paragraph("144.0 UZS", styles['TableCell']),
            Paragraph("$0.0113", styles['TableCell']),
            Paragraph("72,000,000 UZS", styles['TableCell'])
        ],
        [
            Paragraph("<b>JAMI TO'LIQ TANNARX (Total Cost / COGS)</b>", styles['TableCellBold']),
            Paragraph("<b>1 ta qo'ng'iroqni to'liq qamrab olish</b>", styles['TableCellBold']),
            Paragraph("<b>390.8 UZS</b>", styles['TableCellBold']),
            Paragraph("<b>$0.0307</b>", styles['TableCellBold']),
            Paragraph("<b>195,412,000 UZS</b>", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>SOF FOYDA (Net Profit per Call)</b>", styles['TableCellBold']),
            Paragraph("<b>Tushum minus To'liq Tannarx</b>", styles['TableCellBold']),
            Paragraph("<b>+609.2 UZS</b>", styles['TableCellGreen']),
            Paragraph("<b>+$0.0480</b>", styles['TableCellGreen']),
            Paragraph("<b>+304,588,000 UZS</b>", styles['TableCellGreen'])
        ],
    ]

    t_unit_call = Table(t_unit_call_data, colWidths=[140, 110, 85, 80, 105])
    t_unit_call.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 2.8),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#EFF6FF")),
        ('BACKGROUND', (0,-2), (-1,-2), colors.HexColor("#FEF3C7")),
        ('BACKGROUND', (0,-1), (-1,-1), LIGHT_GREEN_BG),
    ]))
    story.append(t_unit_call)

    story.append(PageBreak())

    # PAGE 2: QIYOSIY TAHLIL VA PROGNOZ
    story.append(Paragraph("3. An'anaviy Call-Markaz va So'zLab AI O'rtasidagi Iqtisodiy Qiyos", styles['SecHead']))
    story.append(Paragraph("Barcha xarajat moddalari O'zbekiston Respublikasi Soliq Kodeksi (405-modda: 25% byudjet ijtimoiy solig'i), Stat.uz maoshlar hisoboti hamda Uztelecom/Beeline tariflari bilan asoslangan:", styles['Body']))

    t_compare_data = [
        [Paragraph("<b>Taqqoslash Mezoni</b>", styles['TableCellBold']), Paragraph("<b>An'anaviy Inson Call-Markazi</b>", styles['TableCellBold']), Paragraph("<b>So'zLab AI Tizimi</b>", styles['TableCellBold']), Paragraph("<b>Iqtisodiy / Texnologik Yutuq</b>", styles['TableCellBold'])],
        [
            Paragraph("Xodimlar soni va tarkibi", styles['TableCell']),
            Paragraph("40 ta operator + 4 ta supervisor", styles['TableCell']),
            Paragraph("0 ta operator (Avtonom AI) + 1 DevOps", styles['TableCell']),
            Paragraph("<b>43 kishilik shtat qisqaradi</b>", styles['TableCellBold'])
        ],
        [
            Paragraph("Yillik ish haqi fondi (FOT + Soliq)", styles['TableCell']),
            Paragraph("3,450,000,000 UZS (25% soliq bilan)", styles['TableCell']),
            Paragraph("72,000,000 UZS (DevOps SLA)", styles['TableCell']),
            Paragraph("<b>3.37 mlrd UZS maosh tejami</b>", styles['TableCellBold'])
        ],
        [
            Paragraph("Ofis ijarasi va ish o'rni ta'minoti", styles['TableCell']),
            Paragraph("528,000,000 UZS (200 kv.m + PC amortizatsiya)", styles['TableCell']),
            Paragraph("0 UZS (Cloud infratuzilma)", styles['TableCell']),
            Paragraph("<b>528 mln UZS bino xarajati tejaladi</b>", styles['TableCellBold'])
        ],
        [
            Paragraph("Server, AI API va Telekom xarajati", styles['TableCell']),
            Paragraph("192,000,000 UZS (E1/SIP liniya)", styles['TableCell']),
            Paragraph("123,412,000 UZS (Server+Gemini+VoiceLab+SIP)", styles['TableCell']),
            Paragraph("<b>Tejamkor raqamli arxitektura</b>", styles['TableCellBold'])
        ],
        [
            Paragraph("<b>JAMI YILLIK BYUDJET XARAJATI</b>", styles['TableCellBold']),
            Paragraph("<b>4,170,000,000 UZS ($328,346)</b>", styles['TableCellBold']),
            Paragraph("<b>195,412,000 UZS ($15,386)</b>", styles['TableCellBold']),
            Paragraph("<b>-3,974,588,000 UZS (-95.3% Tejam)</b>", styles['TableCellGreen'])
        ],
        [
            Paragraph("<b>1 ta Qo'ng'iroq Tannarxi</b>", styles['TableCellBold']),
            Paragraph("<b>8,340 UZS ($0.66)</b>", styles['TableCellBold']),
            Paragraph("<b>390.8 UZS ($0.030)</b>", styles['TableCellBold']),
            Paragraph("<b>21.3 barobar arzonlashuv!</b>", styles['TableCellGreen'])
        ],
        [
            Paragraph("Parallel qo'ng'iroq qabul qilish sig'imi", styles['TableCell']),
            Paragraph("Maksimal 40 ta (liniyalar band bo'ladi)", styles['TableCell']),
            Paragraph("500+ ta parallel oqim", styles['TableCell']),
            Paragraph("<b>Kutish navbati 0 soniya</b>", styles['TableCellBold'])
        ],
        [
            Paragraph("Call Drop Rate (Uzilgan qo'ng'iroqlar)", styles['TableCell']),
            Paragraph("42% gacha fuqaro tusha olmaydi", styles['TableCell']),
            Paragraph("< 2% texnik uzilish", styles['TableCell']),
            Paragraph("<b>Aholi 100% qamrab olinadi</b>", styles['TableCellBold'])
        ],
        [
            Paragraph("Javoblar qonuniy aniqligi", styles['TableCell']),
            Paragraph("70-80% (insoniy xato, charchoq)", styles['TableCell']),
            Paragraph("100% (RAG rasmiy hujjatlar doirasida)", styles['TableCell']),
            Paragraph("<b>Gallyutsinatsiya va feyk 0%</b>", styles['TableCellBold'])
        ],
    ]

    t_comp = Table(t_compare_data, colWidths=[120, 130, 130, 140])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 2.6),
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor("#FEF3C7")),
        ('BACKGROUND', (0,5), (-1,5), LIGHT_GREEN_BG),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 4))

    # 4. KENGAYISH BOSQICHI: B2B OTM UNIT ECONOMICS
    story.append(Paragraph("4. Kengayish Modeli: B2B OTMlar Obunasi Unit Economics", styles['SecHead']))
    story.append(Paragraph("O'zbekistondagi 210 dan ortiq universitetlar qabul davrida o'zlarining shaxsiy ishonch telefonlariga ega. Har bir OTM ga shaxsiy RAG bilimlar bazasi bilan individual So'zLab moduli beriladi:", styles['Body']))

    t_otm_data = [
        [Paragraph("<b>OTM Birligi Ko'rsatkichi</b>", styles['TableCellBold']), Paragraph("<b>Oylik (1 ta OTM)</b>", styles['TableCellBold']), Paragraph("<b>Yillik (1 ta OTM)</b>", styles['TableCellBold']), Paragraph("<b>25 ta OTM Kengayganda (Yillik)</b>", styles['TableCellBold'])],
        [
            Paragraph("SaaS Litsenziya Tushumi (Revenue)", styles['TableCell']),
            Paragraph("4,000,000 UZS ($315)", styles['TableCell']),
            Paragraph("48,000,000 UZS ($3,780)", styles['TableCell']),
            Paragraph("1,200,000,000 UZS ($94,500)", styles['TableCellBold'])
        ],
        [
            Paragraph("Qo'shimcha Token & Ovoz Xarajati (COGS)", styles['TableCell']),
            Paragraph("660,000 UZS ($52)", styles['TableCell']),
            Paragraph("8,000,000 UZS ($630)", styles['TableCell']),
            Paragraph("200,000,000 UZS ($15,750)", styles['TableCell'])
        ],
        [
            Paragraph("<b>OTM Modulidan Sof Foyda (Net Profit)</b>", styles['TableCellBold']),
            Paragraph("<b>3,340,000 UZS ($263)</b>", styles['TableCellGreen']),
            Paragraph("<b>40,000,000 UZS ($3,150)</b>", styles['TableCellGreen']),
            Paragraph("<b>+1,000,000,000 UZS ($78,750)</b>", styles['TableCellGreen'])
        ],
        [
            Paragraph("<b>Sof Rentabellik Marjasi (Margin)</b>", styles['TableCellBold']),
            Paragraph("<b>83.5%</b>", styles['TableCellBold']),
            Paragraph("<b>83.5%</b>", styles['TableCellBold']),
            Paragraph("<b>83.5% (High-Margin B2B SaaS)</b>", styles['TableCellBold'])
        ]
    ]

    t_otm = Table(t_otm_data, colWidths=[140, 115, 115, 150])
    t_otm.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,2), (-1,2), LIGHT_GREEN_BG),
    ]))
    story.append(t_otm)
    story.append(Spacer(1, 4))

    # 5. 3 YILLIK MOLIYAVIY PROGNOZ (ROADMAP & FINANCIAL FORECAST)
    story.append(Paragraph("5. 3 Yillik Moliyaviy Prognoz va Skalatsiya Modeli (2026 - 2028)", styles['SecHead']))

    t_forecast_data = [
        [Paragraph("<b>Metrika va Yillar</b>", styles['TableCellBold']), Paragraph("<b>2026 (1-Bosqich: Pilot)</b>", styles['TableCellBold']), Paragraph("<b>2027 (2-Bosqich: Skalatsiya)</b>", styles['TableCellBold']), Paragraph("<b>2028 (3-Bosqich: Respublika)</b>", styles['TableCellBold'])],
        [
            Paragraph("Mijozlar Portfeli", styles['TableCell']),
            Paragraph("1 ta Vazirlik (Oliy ta'lim 1006)", styles['TableCell']),
            Paragraph("2 ta Vazirlik + 25 ta OTM", styles['TableCell']),
            Paragraph("5 ta Vazirlik + 80 ta OTM", styles['TableCell'])
        ],
        [
            Paragraph("Yillik Jami Qo'ng'iroqlar Hajmi", styles['TableCell']),
            Paragraph("500,000 ta qo'ng'iroq", styles['TableCell']),
            Paragraph("1,600,000 ta qo'ng'iroq", styles['TableCell']),
            Paragraph("4,500,000 ta qo'ng'iroq", styles['TableCell'])
        ],
        [
            Paragraph("<b>Yillik Umumiy Tushum (ARR)</b>", styles['TableCellBold']),
            Paragraph("<b>500,000,000 UZS ($39.4k)</b>", styles['TableCellBold']),
            Paragraph("<b>2,200,000,000 UZS ($173k)</b>", styles['TableCellBold']),
            Paragraph("<b>6,340,000,000 UZS ($499k)</b>", styles['TableCellBold'])
        ],
        [
            Paragraph("Infratuzilma va Operatsion Xarajatlar", styles['TableCell']),
            Paragraph("195,412,000 UZS ($15.4k)", styles['TableCell']),
            Paragraph("480,000,000 UZS ($37.8k)", styles['TableCell']),
            Paragraph("1,150,000,000 UZS ($90.5k)", styles['TableCell'])
        ],
        [
            Paragraph("<b>YILLIK SOF FOYDA (Net Profit)</b>", styles['TableCellBold']),
            Paragraph("<b>+304,588,000 UZS ($24.0k)</b>", styles['TableCellGreen']),
            Paragraph("<b>+1,720,000,000 UZS ($135.4k)</b>", styles['TableCellGreen']),
            Paragraph("<b>+5,190,000,000 UZS ($408.6k)</b>", styles['TableCellGreen'])
        ],
        [
            Paragraph("<b>EBITDA Rentabelligi</b>", styles['TableCellBold']),
            Paragraph("<b>60.9%</b>", styles['TableCellBold']),
            Paragraph("<b>78.2%</b>", styles['TableCellBold']),
            Paragraph("<b>81.8%</b>", styles['TableCellBold'])
        ]
    ]

    t_forecast = Table(t_forecast_data, colWidths=[130, 125, 130, 135])
    t_forecast.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor("#EFF6FF")),
        ('BACKGROUND', (0,4), (-1,4), LIGHT_GREEN_BG),
    ]))
    story.append(t_forecast)
    story.append(Spacer(1, 4))

    # 6. INVESTOR VA HAKAMLAR UCHUN XULOSA TEZISI
    summary_box_data = [
        [
            Paragraph("<b>HAKAMLAR VA INVESTORLARGA QAT'IY JAVOB (PITCH CLOSER):</b><br/>"
                      "1. <b>Byudjet Tasdig'i:</b> Loyihamiz davlatdan qo'shimcha xarajat talab qilmaydi — aksincha, mavjud 4.17 mlrd so'mlik smetani 95% ga qisqartirib, davlatga <b>3.97 milliard so'm naqd tejaydi</b>.<br/>"
                      "2. <b>Unit Economics Kuchi:</b> 1 ta insoniy qo'ng'iroq 8,340 so'mga tushayotgan bir paytda, So'zLab AI buni bor-yo'g'i <b>390.8 so'mga (texnik xarajat esa 40 so'mga)</b> hal etadi va <b>61% sof marja</b> yaratadi.<br/>"
                      "3. <b>Ijtimoiy Ta'sir:</b> Tejalgan qariyb 4 milliard so'm hisobiga <b>12 ta maktabda zamonaviy STEM laboratoriyasi</b> tashkil etish yoki <b>450 nafar ijtimoiy himoyaga muhtoj talabaning kontraktini to'lab berish</b> mumkin.",
                      styles['CalloutText'])
        ]
    ]
    t_box = Table(summary_box_data, colWidths=[520])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GREEN_BG),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#059669")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_box)

    # Har bir target yo'lga generatsiya qilish
    for path_str in target_paths:
        p = Path(path_str)
        p.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(p),
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        doc.build(story, canvasmaker=NumberedCanvas)
        print(f"[PDF muvaffaqiyatli yaratildi]: {p}")

if __name__ == '__main__':
    targets = [
        'c:/dev/Projects/vazir-chat/SozLab_Monetizatsiya_va_Unit_Economics.pdf',
        'c:/dev/Projects/vazir-chat/team_guides/07_SozLab_Monetizatsiya_va_Unit_Economics.pdf'
    ]
    build_pdf(targets)
