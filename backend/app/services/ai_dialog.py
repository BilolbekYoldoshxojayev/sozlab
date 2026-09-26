"""
SözLab Autonomous AI Dialog Manager
100% Autonomous Voice AI grounded strictly in:
1. Top-50 Official Education FAQs (Maktabgacha, Maktab, OTM, Pedagoglar huquqlari)
2. Education Legislation Encyclopedia (Constitution 50, 51, 52, 77, O'RQ-637, O'RQ-901, Decrees)
Strict Guardrail: Zero speculation outside education laws. Zero operator handovers.
"""

import json
import re
from typing import Dict, Any, List, Tuple
from app.core.config import settings
from app.models.schemas import SentimentType, TopicCategory, DialogTurnResponse
from app.services.knowledge_base import (
    get_complete_legal_context,
    is_in_educational_scope,
    OUT_OF_SCOPE_REFUSAL,
    search_knowledge_base,
    KnowledgeItem
)
from app.services.stt_service import stt_service
from app.services.llm_orchestrator import llm_orchestrator

class AIDialogManager:
    PRIMARY_MODEL = "gemini-flash-lite-latest"

    FAREWELL_KEYWORDS = [
        "rahmat",
        "raxmat",
        "rahmad",
        "katta rahmat",
        "katta raxmat",
        "tashakkur",
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

    GREETING_KEYWORDS = [
        "assalomu alaykum",
        "assalomu aleykum",
        "assalamu alaykum",
        "assalamu alaikum",
        "assalam alaykum",
        "assalom",
        "assalam",
        "asalom",
        "salom alaykum",
        "salam alaykum",
        "salam aleykum",
        "salom aleykum",
        "valaykum assalom",
        "valaykum assalam",
        "va alaykum assalom",
        "va alaykum assalam",
        "vaalaykum assalom",
        "salom",
        "salam",
        "qaleysiz",
        "qalaysiz",
        "xayrli kun",
        "xayrli tong",
        "xayrli kech",
        "alo",
        "aloh",
        "eshityapsizmi",
        "eshitilyaptimi",
        "hello",
        "privet"
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
        if not text or not isinstance(text, str):
            return False
        t_low = text.lower()
        return any(kw in t_low for kw in self.FAREWELL_KEYWORDS)

    def is_greeting(self, text: str) -> bool:
        if not text or not isinstance(text, str):
            return False
        if self.is_farewell(text):
            return False
        t_low = text.lower().strip()
        words = re.findall(r"\b[\w'-]+\b", t_low)
        if len(words) > 5:
            return False
        for g in self.GREETING_KEYWORDS:
            if " " in g:
                if g in t_low:
                    return True
            else:
                if g in words or g == t_low.replace('.', '').replace('!', '').replace('?', '').strip():
                    return True
        greeting_roots = ["assalom", "assalam", "asalom", "salom", "salam", "alaykum", "alaikum", "aleykum", "eshityap", "eshitilyap"]
        if any(r in t_low for r in greeting_roots) and len(words) <= 4:
            return True
        return False

    def _detect_sentiment(self, text: str) -> SentimentType:
        t_low = text.lower()
        negative_words = ["shikoyat", "haqorat", "yomon", "aldash", "ishlamayapti", "noroziman", "qabul qilmadi", "bema'nilik", "yetib bo'lmayapti"]
        positive_words = ["rahmat", "katta rahmat", "tushundim", "ajoyib", "yaxshi", "baraka toping", "minnatdorman", "zo'r", "foydali", "xayr", "sog' bo'ling", "salomat bo'ling"]

        if any(w in t_low for w in negative_words):
            return SentimentType.NEGATIVE
        if any(w in t_low for w in positive_words):
            return SentimentType.POSITIVE
        return SentimentType.NEUTRAL

    def _detect_intent_and_topic(self, text: str, matched_faqs: List[Dict[str, Any]]) -> Tuple[str, TopicCategory]:
        if self.is_farewell(text):
            return "Xayrlashuv", TopicCategory.BOSHQA

        if not matched_faqs:
            return "Umumiy_Savol", TopicCategory.BOSHQA

        faq = matched_faqs[0]
        q_text = faq.get("question", "").lower()
        
        if "grant" in q_text:
            return "Grant_Maslahat", TopicCategory.GRANT
        if "kontrakt" in q_text or "to'lov" in q_text:
            return "Kontrakt_Maslahat", TopicCategory.KONTRAKT
        if "yotoqxona" in q_text or "ijara" in q_text:
            return "TTJ_Maslahat", TopicCategory.TTJ
        if "nostrifikatsiya" in q_text or "apostil" in q_text:
            return "Nostrifikatsiya_Maslahat", TopicCategory.NOSTRIFIKATSIYA
        if "kredit" in q_text or "stipendiya" in q_text:
            return "Stipendiya_Kredit_Maslahat", TopicCategory.STIPENDIYA
        if "perevod" in q_text or "ko'chirish" in q_text:
            return "Perevod_Maslahat", TopicCategory.PEREVOD
        if "1-sinf" in q_text or "maktab" in q_text or "pedagog" in q_text or "qabul" in q_text:
            return "Qabul_Maktab_Maslahat", TopicCategory.QABUL

        return "Huquqiy_Maslahat", TopicCategory.BOSHQA

    def _generate_rule_based_response(self, text: str, legal_context: Dict[str, Any]) -> str:
        """
        High-fidelity rule-based natural Uzbek response grounded exclusively in the 50 FAQs & Encyclopedia.
        """
        t_low = text.lower()

        # Greetings
        if any(g in t_low for g in ["assalomu alaykum", "salom", "salom alaykum", "qaleysiz", "xayrli kun"]):
            return "Assalomu alaykum, eshitaman. Qanday ta'lim masalasi bo'yicha yordam kerak?"

        # Farewell / Gratitude
        if self.is_farewell(text):
            return (
                "Arzimaydi! Murojaat qilganingiz uchun rahmat. "
                "Qonuniy huquqlaringiz doimo davlat himoyasida. Salomat bo'ling!"
            )

        # Check in-scope
        if not legal_context.get("in_scope", False):
            return OUT_OF_SCOPE_REFUSAL

        faqs = legal_context.get("faqs", [])
        if faqs:
            top_faq = faqs[0]
            clean_short = top_faq.get("short_answer", "").strip()
            basis = top_faq.get("legal_basis", "").split(";")[0].strip()
            if not basis:
                basis = "Ta'lim qonunchiligi"
            return f"{basis}ga binoan: {clean_short}"

        articles = legal_context.get("articles", [])
        if articles:
            top_art = articles[0]
            clean_summary = top_art.get("summary", "").strip()
            return f"{top_art['title']}ga muvofiq: {clean_summary}"

        return (
            "Savolingiz rasmiy ta'lim qonunchiligi doirasida qabul qilindi. "
            "Barcha ta'lim xizmatlari my.gov.uz va vazirlikning rasmiy portallari orqali amalga oshiriladi."
        )

    def _generate_smart_suggestions(self, topic: TopicCategory, faqs: List[Dict[str, Any]]) -> List[str]:
        if faqs:
            suggestions = [f["question"][:65] for f in faqs[:3]]
            suggestions.append("Vazirlik ishonch telefoni: 1006 / 1007")
            return suggestions

        suggestions_map = {
            TopicCategory.QABUL: [
                "1-sinfga qabul va mikrohudud qoidalari",
                "Maktabda pul yig'ish qat'iyan taqiqlangan",
                "OTMlarga 5 tagacha yo'nalish tanlash"
            ],
            TopicCategory.GRANT: [
                "PF-81: GPA bo'yicha grantni qayta taqsimlash",
                "VMQ-447: Xotin-qizlar magistraturasi 100% bepul",
                "Ehtiyojmand oilalar uchun 4% davlat granti"
            ],
            TopicCategory.KONTRAKT: [
                "Super-kontrakt shkalasi va to'lov tartibi",
                "Kontraktni 4 ga bo'lib to'lash huquqi",
                "56.7 balldan yuqori to'plaganlar tartibi"
            ],
            TopicCategory.TTJ: [
                "my.gov.uz orqali yotoqxonaga ariza berish",
                "VMQ-605: 50 foizlik ijara kompensatsiyasi",
                "1-kurs talabalarini turar joy bilan ta'minlash"
            ],
            TopicCategory.NOSTRIFIKATSIYA: [
                "TOP-1000 oliygohlar diplomini imtihonsiz tan olish",
                "Nostrifikatsiya arizasini my.gov.uz da topshirish",
                "Masofaviy o'qish diplomining yuridik kuchi"
            ],
            TopicCategory.STIPENDIYA: [
                "VMQ-527: Xotin-qizlar uchun 0% ta'lim krediti",
                "Erkaklar uchun Markaziy bank stavkasida kredit",
                "GPA bo'yicha stipendiya belgilanishi"
            ],
            TopicCategory.PEREVOD: [
                "transfer.edu.uz orqali o'qishni ko'chirish",
                "Turmushga chiqqan qizlarning perevod tartibi",
                "Xususiy OTMdan davlat OTMga test orqali o'tish"
            ]
        }
        return suggestions_map.get(topic, [
            "Pedagoglar sha'ni davlat himoyasida (O'RQ-901)",
            "Vazirlik ishonch telefoni: 1006 / 1007",
            "Rasmiy portal: edu.uz"
        ])

    async def process_user_turn(
        self,
        call_id: str,
        user_text: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> DialogTurnResponse:
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
                    "Vazirlik ishonch telefoni: 1006 / 1007"
                ]
            )


        # Check farewell / gratitude intent
        if self.is_farewell(user_text):
            return DialogTurnResponse(
                call_id=call_id,
                ai_text=(
                    "Arzimaydi! Murojaatingiz uchun tashakkur. "
                    "Qonuniy huquqlaringiz doimo davlat himoyasida. Salomat bo'ling!"
                ),
                sentiment=SentimentType.POSITIVE,
                intent="Xayrlashuv",
                topic=TopicCategory.BOSHQA,
                requires_operator=False,
                knowledge_references=[],
                smart_suggestions=[
                    "Yangi murojaat boshlash",
                    "Vazirlik ishonch telefoni: 1006 / 1007"
                ]
            )

        # Check greeting intent (pure greeting without full legal inquiry)
        if self.is_greeting(user_text):
            return DialogTurnResponse(
                call_id=call_id,
                ai_text="Va alaykum assalom! O'zbekiston ta'lim qonunchiligi bo'yicha qanday savolingiz bor?",
                sentiment=SentimentType.POSITIVE,
                intent="Salomlashuv",
                topic=TopicCategory.BOSHQA,
                requires_operator=False,
                knowledge_references=["O'zbekiston Respublikasi Ta'lim Qonunchiligi"],
                smart_suggestions=[
                    "1-sinfga qabul tartibi",
                    "Davlat granti va kontrakt to'lovlari",
                    "Talabalar turar joyi va ijara kompensatsiyasi",
                    "Vazirlik ishonch telefoni: 1006 / 1007"
                ],
                llm_provider_used="rule_greeting"
            )

        # 1. Retrieve complete legal context from 50 FAQs & Encyclopedia
        legal_context = get_complete_legal_context(user_text, max_faqs=3, max_articles=2)
        sentiment = self._detect_sentiment(user_text)

        # 2. Extract database context and history
        faqs = legal_context.get("faqs", [])
        articles = legal_context.get("articles", [])
        intent, topic = self._detect_intent_and_topic(user_text, faqs)

        # If conversation_history not explicitly supplied, extract from call if available
        if conversation_history is None:
            try:
                from app.services.call_manager import call_manager
                call = call_manager.get_call(call_id)
                if call and call.messages:
                    conversation_history = [
                        {"role": m.role.value, "content": m.text}
                        for m in call.messages
                    ]
            except Exception:
                conversation_history = None

        # 3. 5-Tier Ranked Multi-LLM Provider Engine with Automatic Failover
        ai_response_text, provider_used = await llm_orchestrator.generate_response(
            user_text=user_text,
            conversation_history=conversation_history,
            legal_context=legal_context
        )

        if not ai_response_text:
            ai_response_text = self._generate_rule_based_response(user_text, legal_context)
            provider_used = "deterministic_rule_engine"

        # Check if LLM determined the inquiry is out of educational scope
        if "faqat maktab va oliy ta'lim" in ai_response_text.lower() or OUT_OF_SCOPE_REFUSAL.lower() in ai_response_text.lower():
            intent = "Doiradan_Tashqari_Rad"
            topic = TopicCategory.BOSHQA

        # Extract legal references for UI chips
        kb_refs = []
        for f in faqs[:2]:
            kb_refs.append(f"{f['legal_basis']}")
        for a in articles[:1]:
            kb_refs.append(f"{a['title']}")
        if not kb_refs:
            kb_refs = ["O'zbekiston Respublikasi Ta'lim Qonunchiligi"]

        suggestions = self._generate_smart_suggestions(topic, faqs)

        return DialogTurnResponse(
            call_id=call_id,
            ai_text=ai_response_text,
            sentiment=sentiment,
            intent=intent,
            topic=topic,
            requires_operator=False,
            knowledge_references=kb_refs,
            smart_suggestions=suggestions,
            llm_provider_used=provider_used
        )

    async def process_audio_turn(
        self,
        call_id: str,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        voice_name: str = "Lola"
    ) -> Tuple[str, DialogTurnResponse]:
        """
        Multimodal audio recognition using VoiceLab Studio SDK exclusively.
        Returns: (transcribed_text, dialog_turn_response)
        """
        if not audio_bytes or len(audio_bytes) < 200:
            unrecognized_text = "Kechirasiz, ovozingizni aniq eshita olmadim. Qaytadan gapira olasizmi?"
            dialog_res = DialogTurnResponse(
                call_id=call_id,
                ai_text=unrecognized_text,
                sentiment=SentimentType.NEUTRAL,
                intent="Tushunarsiz_Ovoz",
                topic=TopicCategory.BOSHQA,
                requires_operator=False,
                knowledge_references=[],
                smart_suggestions=["Savolni qaytadan berish"]
            )
            return "(Tushunarsiz ovoz)", dialog_res

        # Transcribe with VoiceLab Studio SDK
        transcribed_text = await stt_service.transcribe(
            audio_bytes=audio_bytes,
            mime_type=mime_type,
            filename="user_call.wav",
            language="uz"
        )

        if not transcribed_text or not isinstance(transcribed_text, str) or not transcribed_text.strip():
            unrecognized_text = "Kechirasiz, ovozingizni aniq eshita olmadim. Qaytadan gapira olasizmi?"
            dialog_res = DialogTurnResponse(
                call_id=call_id,
                ai_text=unrecognized_text,
                sentiment=SentimentType.NEUTRAL,
                intent="Tushunarsiz_Ovoz",
                topic=TopicCategory.BOSHQA,
                requires_operator=False,
                knowledge_references=[],
                smart_suggestions=["Savolni qaytadan berish"]
            )
            return "(Tushunarsiz ovoz)", dialog_res


        dialog_res = await self.process_user_turn(call_id, transcribed_text)
        return transcribed_text, dialog_res

    async def transcribe_live_audio_chunk(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        speaker_role: str = "citizen"
    ) -> str:
        """Fast live transcription via VoiceLab STT."""
        if not audio_bytes or len(audio_bytes) < 200:
            return ""
        return await stt_service.transcribe(audio_bytes=audio_bytes, mime_type=mime_type)

    async def generate_call_summary(self, dialog_history: List[str]) -> str:
        """
        Generate concise analytical summary of citizen AI call using 5-Tier Multi-LLM Engine.
        """
        summary_text, provider_used = await llm_orchestrator.generate_call_summary(dialog_history)
        return summary_text


dialog_manager = AIDialogManager()
