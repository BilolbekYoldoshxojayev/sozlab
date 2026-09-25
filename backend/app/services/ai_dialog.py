import json
import re
from typing import Dict, Any, List, Tuple
from app.core.config import settings
from app.models.schemas import SentimentType, TopicCategory, DialogTurnResponse
from app.services.knowledge_base import search_knowledge_base, KnowledgeItem

class AIDialogManager:
    PRIMARY_MODEL = "gemini-flash-lite-latest"

    FAREWELL_KEYWORDS = [
        "rahmat",
        "katta rahmat",
        "xayr",
        "xayir",
        "sog' bo'ling",
        "sog boling",
        "salomat bo'ling",
        "salomat boling",
        "tushundim",
        "bye",
        "end",
        "tushunarli",
        "minnatdorman",
        "yaxshi qoling"
    ]

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        self._init_client()

    def _init_client(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[Gemini Client Init Warning]: {e}")

    def _get_client(self):
        if not self.client and settings.GEMINI_API_KEY:
            self._init_client()
        return self.client

    def is_farewell(self, text: str) -> bool:
        if not text:
            return False
        t_low = text.lower()
        return any(kw in t_low for kw in self.FAREWELL_KEYWORDS)

    def _detect_sentiment(self, text: str) -> SentimentType:
        t_low = text.lower()
        negative_words = ["shikoyat", "haqorat", "yomon", "aldash", "ishlamayapti", "noroziman", "qabul qilmadi", "bema'nilik", "yetib bo'lmayapti", "operatorga ula", "odam bilan gaplashaman", "rahbariyat"]
        positive_words = ["rahmat", "katta rahmat", "tushundim", "ajoyib", "yaxshi", "baraka toping", "minnatdorman", "zo'r", "foydali", "xayr", "sog' bo'ling", "salomat bo'ling"]

        if any(w in t_low for w in negative_words):
            return SentimentType.NEGATIVE
        if any(w in t_low for w in positive_words):
            return SentimentType.POSITIVE
        return SentimentType.NEUTRAL

    def _detect_intent_and_topic(self, text: str, matched_kb: List[KnowledgeItem]) -> Tuple[str, TopicCategory, bool]:
        t_low = text.lower()
        requires_operator = False

        if any(phrase in t_low for phrase in ["operator", "inson bilan", "odam bilan", "tirik odam", "rahbarga", "shikoyat qilmoqchiman"]):
            return "Operator_Chaqiruvi", TopicCategory.BOSHQA, True

        if self.is_farewell(text):
            return "Xayrlashuv", TopicCategory.BOSHQA, False

        if not matched_kb:
            return "Umumiy_Savol", TopicCategory.BOSHQA, False

        primary_kb = matched_kb[0]
        topic = primary_kb.topic
        intent_name = f"{topic.name}_Maslahat"

        return intent_name, topic, requires_operator

    def _generate_rule_based_response(self, text: str, matched_kb: List[KnowledgeItem], sentiment: SentimentType) -> str:
        """
        High-fidelity rule-based natural Uzbek response grounded in official ministry regulations.
        """
        t_low = text.lower()

        # Greetings
        if any(g in t_low for g in ["assalomu alaykum", "salom", "salom alaykum", "qaleysiz", "xayrli kun"]):
            return (
                "Assalomu alaykum! Oliy ta'lim, fan va innovatsiyalar vazirligi yagona axborot markaziga xush kelibsiz. "
                "Men virtual yordamchiman. OTMga qabul, davlat grantlari, kontrakt, yotoqxona yoki diplom tan olish bo'yicha qanday savolingiz bor?"
            )

        # Farewell / Gratitude
        if self.is_farewell(text):
            return (
                "Arzimaydi! Oliy ta'lim, fan va innovatsiyalar vazirligiga murojaat qilganingiz uchun rahmat. "
                "Salomat bo'ling, kuningiz xayrli o'tsin!"
            )

        # Operator call
        if any(w in t_low for w in ["operator", "operatorga ula", "odam bilan"]):
            return (
                "Tushundim. Sizni vazirlikning mas'ul navbatchi mutaxassisiga ulayapman. "
                "Iltimos, qo'ng'iroqda qoling, navbatingiz birinchi o'rinda saqlanadi."
            )

        if matched_kb:
            item = matched_kb[0]
            steps_text = " ".join(item.action_steps[:2])
            return (
                f"{item.title} bo'yicha rasmiy tartibga ko'ra: {item.summary} "
                f"Amaliy qadamlar: {steps_text} Batafsil ma'lumotni {item.links[0] if item.links else 'edu.uz'} orqali olishingiz mumkin."
            )

        return (
            "Savolingiz qayd etildi. Vazirlik nizomiga muvofiq barcha rasmiy arizalar my.gov.uz yoki my.uzbmb.uz tizimi orqali qabul qilinadi. "
            "Agar savolingiz murakkab bo'lsa, sizni navbatchi operatorga yo'naltirishim mumkin."
        )

    def _generate_smart_suggestions(self, topic: TopicCategory) -> List[str]:
        suggestions_map = {
            TopicCategory.QABUL: [
                "my.uzbmb.uz orqali ro'yxatdan o'tish yo'riqnomasi",
                "5 tagacha ta'lim yo'nalishini tanlash tartibi",
                "Chet tili milliy/xalqaro sertifikat imtiyozi"
            ],
            TopicCategory.GRANT: [
                "GPA bo'yicha grantni qayta taqsimlash mezonlari",
                "Ehtiyojmand oilalar va xotin-qizlar uchun 4% kvota",
                "Davlat grantida o'qish va taqsimot majburiyati"
            ],
            TopicCategory.KONTRAKT: [
                "Super-kontrakt arizasini my.edu.uz da rasmiylashtirish",
                "To'lov shartnomasini 4 qismga bo'lib to'lash tartibi",
                "56.7 balldan yuqori to'plaganlar uchun koeffitsiyentlar"
            ],
            TopicCategory.TTJ: [
                "my.gov.uz da yotoqxona arizasi holatini tekshirish",
                "Oylik ijara kompensatsiyasini (50%) olish talablari",
                "1-kurs talabalari uchun ustuvor joylashtirish"
            ],
            TopicCategory.NOSTRIFIKATSIYA: [
                "TOP-1000 oliygohlar ro'yxatidan OTMni qidirish",
                "Nostrifikatsiya uchun kerakli notarial tarjimalar",
                "UzBMB tomonidan o'tkaziladigan kasbiy test sinovlari"
            ],
            TopicCategory.STIPENDIYA: [
                "Xotin-qizlar uchun foizsiz ta'lim krediti olish",
                "Prezident va nomli davlat stipendiyalari tanlovi",
                "Banklar orqali ta'lim krediti foizlarini hisoblash"
            ],
            TopicCategory.PEREVOD: [
                "transfer.edu.uz portali orqali ariza topshirish",
                "Uzrli sabablar toifasiga kiruvchi holatlar ro'yxati",
                "Xorijiy OTMdan o'qishni ko'chirishda o'tish ballari"
            ]
        }
        return suggestions_map.get(topic, [
            "Operatorga yo'naltirish",
            "Vazirlik ishonch telefoni: 1006",
            "Rasmiy portal: edu.uz"
        ])

    async def process_user_turn(self, call_id: str, user_text: str) -> DialogTurnResponse:
        # Check empty or whitespace user text
        if not user_text or not user_text.strip():
            return DialogTurnResponse(
                call_id=call_id,
                ai_text="Kechirasiz, ovozingizni aniq eshita olmadim. Qaytadan gapira olasizmi?",
                sentiment=SentimentType.NEUTRAL,
                intent="Tushunarsiz_Ovoz",
                topic=TopicCategory.BOSHQA,
                requires_operator=False,
                knowledge_references=[],
                smart_suggestions=[
                    "Savolni qaytadan berish",
                    "Operatorga yo'naltirish",
                    "Vazirlik ishonch telefoni: 1006"
                ]
            )

        # Check farewell / gratitude intent
        if self.is_farewell(user_text):
            return DialogTurnResponse(
                call_id=call_id,
                ai_text=(
                    "Arzimaydi! Oliy ta'lim, fan va innovatsiyalar vazirligiga murojaat qilganingiz uchun rahmat. "
                    "Salomat bo'ling, kuningiz xayrli o'tsin!"
                ),
                sentiment=SentimentType.POSITIVE,
                intent="Xayrlashuv",
                topic=TopicCategory.BOSHQA,
                requires_operator=False,
                knowledge_references=[],
                smart_suggestions=[
                    "Yangi murojaat boshlash",
                    "Vazirlik ishonch telefoni: 1006",
                    "Rasmiy portal: edu.uz"
                ]
            )

        matched_kb = search_knowledge_base(user_text, limit=2)
        sentiment = self._detect_sentiment(user_text)
        intent, topic, operator_needed = self._detect_intent_and_topic(user_text, matched_kb)
        
        # If user expresses strong negative sentiment or insists on an operator, flag for handover
        if sentiment == SentimentType.NEGATIVE and any(w in user_text.lower() for w in ["operator", "odam", "shikoyat"]):
            operator_needed = True

        ai_response_text = ""

        # Try Gemini API if key is present
        client = self._get_client()
        if client and settings.GEMINI_API_KEY:
            try:
                system_instruction = (
                    "Siz O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligining "
                    "rasmiy AI ovozli yordamchisisiz ('SözLab'). Salomlashganda doimo 'Assalomu alaykum!' deb boshlang. "
                    "Fuqaro bilan o'ta xushmuomala, aniq va ixcham o'zbek adabiy tilida gaplashing. "
                    "Javoblaringiz ovozli o'qilishi uchun juda uzun bo'lmasin (2-3 jumla). "
                    "Hukumat qarorlariga asoslaning. Agar fuqaro norozi bo'lsa yoki operatorni so'rasa, operatorga ulashni taklif qiling.\n\n"
                    f"Vazirlik bazasidan tegishli ma'lumot:\n"
                    + "\n".join([f"- {kb.title}: {kb.summary} Qoidalar: {kb.official_regulation}" for kb in matched_kb])
                )
                
                # Gemini call with primary model
                response = client.models.generate_content(
                    model=self.PRIMARY_MODEL,
                    contents=user_text,
                    config={"system_instruction": system_instruction, "temperature": 0.3}
                )
                if response and response.text:
                    ai_response_text = response.text.strip()
            except Exception as e:
                print(f"[Gemini Inference Fallback]: {e}")
                ai_response_text = self._generate_rule_based_response(user_text, matched_kb, sentiment)
        else:
            ai_response_text = self._generate_rule_based_response(user_text, matched_kb, sentiment)

        if not ai_response_text:
            ai_response_text = self._generate_rule_based_response(user_text, matched_kb, sentiment)

        kb_refs = [kb.title for kb in matched_kb]
        suggestions = self._generate_smart_suggestions(topic)

        return DialogTurnResponse(
            call_id=call_id,
            ai_text=ai_response_text,
            sentiment=sentiment,
            intent=intent,
            topic=topic,
            requires_operator=operator_needed,
            knowledge_references=kb_refs,
            smart_suggestions=suggestions
        )

    async def process_audio_turn(
        self,
        call_id: str,
        audio_bytes: bytes,
        mime_type: str = "audio/webm",
        voice_name: str = "uz-UZ-MadinaNeural"
    ) -> Tuple[str, DialogTurnResponse]:
        """
        Multimodal audio recognition and dialog processing.
        Returns: (transcribed_text, dialog_turn_response)
        """
        transcribed_text = ""
        client = self._get_client()
        clean_mime = mime_type.split(";")[0].strip().lower() if mime_type else "audio/webm"

        # 1. Try Gemini Multimodal STT if client & key available
        if client and settings.GEMINI_API_KEY and len(audio_bytes) > 200:
            try:
                from google.genai import types
                audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=clean_mime)
                prompt = (
                    "Quyidagi o'zbek tilidagi audio yozuvni eshiting va fuqaro nima deganini "
                    "faqat o'zbek adabiy tilidagi matn sifatida yozib bering (boshqa hech narsa qo'shmang)."
                )
                res = client.models.generate_content(
                    model=self.PRIMARY_MODEL,
                    contents=[audio_part, prompt]
                )
                if res and res.text:
                    transcribed_text = res.text.strip().replace('"', '').replace("'", "")
            except Exception as e:
                print(f"[Gemini Audio STT Error / Fallback]: {e}")

        # 2. Resilient fallback if audio was empty or speech was not recognized
        if not transcribed_text or not transcribed_text.strip():
            unrecognized_text = "Kechirasiz, ovozingizni aniq eshita olmadim. Qaytadan gapira olasizmi?"
            dialog_res = DialogTurnResponse(
                call_id=call_id,
                ai_text=unrecognized_text,
                sentiment=SentimentType.NEUTRAL,
                intent="Tushunarsiz_Ovoz",
                topic=TopicCategory.BOSHQA,
                requires_operator=False,
                knowledge_references=[],
                smart_suggestions=[
                    "Savolni qaytadan berish",
                    "Operatorga yo'naltirish",
                    "Vazirlik ishonch telefoni: 1006"
                ]
            )
            return "(Tushunarsiz ovoz)", dialog_res

        # 3. Process turn with transcribed text
        dialog_res = await self.process_user_turn(call_id, transcribed_text)
        return transcribed_text, dialog_res

dialog_manager = AIDialogManager()
