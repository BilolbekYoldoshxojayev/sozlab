"""
SözLab Multi-LLM Orchestrator Service
Architecture: 5-Tier Multi-Provider Cascade with Automatic Failover
1. Cerebras Ultra-Fast Hardware Inference (0.2s - 0.4s) [Optional, when API key configured]
2. Groq Ultra-Fast LPU Engine (0.35s - 0.7s) [Primary Production]
3. Google Gemini (gemini-2.5-flash / gemini-3.8-flash) (0.8s - 1.5s)
4. Cloudflare Workers AI (@cf/meta/llama-3.1-8b-instruct) (1.5s - 2.5s)
5. Mistral AI (mistral-large-latest / mistral-small-latest) (2.0s - 3.5s)
6. Deterministic Legal Rule Engine (< 0.005s) [Ultimate Safety Net / Zero-Hallucination Fallback]
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Tuple

import httpx
from app.core.config import settings
from app.services.uzbek_text_normalizer import strip_markdown_symbols

logger = logging.getLogger("sozlab.llm")

OUT_OF_SCOPE_REFUSAL = (
    "Kechirasiz, men faqat maktab va oliy ta'lim qonunchiligi bo'yicha rasmiy savollarga javob bera olaman."
)

class LLMOrchestrator:
    PROVIDER_CEREBRAS = "cerebras"
    PROVIDER_GROQ = "groq"
    PROVIDER_GEMINI = "gemini"
    PROVIDER_CLOUDFLARE = "cloudflare"
    PROVIDER_MISTRAL = "mistral"
    PROVIDER_RULE_ENGINE = "deterministic_rule_engine"

    def __init__(self):
        self._gemini_client = None
        self.default_timeout = settings.LLM_TIMEOUT_SECONDS
        self._init_gemini()

    def _init_gemini(self):
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("[LLMOrchestrator] Google GenAI client initialized.")
            except Exception as e:
                logger.warning(f"[LLMOrchestrator] Gemini client init warning: {e}")

    def _get_gemini_client(self):
        if not self._gemini_client and settings.GEMINI_API_KEY:
            self._init_gemini()
        return self._gemini_client

    def build_system_instruction(self, legal_context: Any) -> str:
        """Construct authoritative legal system prompt grounded in Top-50 FAQs & Encyclopedia."""
        if isinstance(legal_context, dict):
            formatted_context = legal_context.get("formatted_context", "")
        elif isinstance(legal_context, str):
            formatted_context = legal_context
        else:
            formatted_context = ""

        return (
            "Siz O'zbekiston Respublikasi Maktabgacha va maktab ta'limi vazirligi (1006) hamda "
            "Oliy ta'lim, fan va innovatsiyalar vazirligi (1007) yagona rasmiy 'SözLab' interaktiv ovozli maslahatchisisiz.\n\n"
            "QAT'IY OVOZLI MULOQOT QOIDALARI:\n"
            "1. NUTQQA TAYYORLIK VA OVOZLI IXCHAMLIK (SPEECH-READY & CONCISE): Siz jonli telefon qo'ng'irog'idasiz. Javobingiz ovoz sintezi (TTS) orqali fuqaroga o'qib eshittiriladi. Shuning uchun javobingiz ko'pi bilan 2-3 ta qisqa, lo'nda va jonli jumlalardan (jami 35-50 so'zdan) oshmasligi SHART. Ensiklopediya bo'limlarini, moddalar ro'yxatini yoki uzun qonun matnlarini HECH QACHON to'kib tashlamang (dump qilmang)!\n"
            "2. BARCHA RAQAMLAR VA QONUNLARNI SO'Z BILAN YOZISH: Ovoz modeli xatosiz va tabiiy o'qishi uchun MATNDAGI BARCHA RAQAMLAR, foizlar, sanalar va qonun nomlarini TO'LIQ O'ZBEKCHA SO'Z BILAN YOZING! Raqamli belgilar (0, 1, 2, 3...) ishlatish qat'iyan taqiqlanadi.\n"
            "   Masalan:\n"
            "   - '0%' emas, balki 'nol foiz'\n"
            "   - '100%' emas, balki 'yuz foiz'\n"
            "   - '4 qismga' emas, balki 'to'rt qismga'\n"
            "   - '50 foiz' (50% emas)\n"
            "   - 'birinchi sinf' (1-sinf emas)\n"
            "   - 'Vazirlar Mahkamasining besh yuz yigirma yettinchi qarori' (VMQ-527 emas)\n"
            "   - 'Prezidentning sakson birinchi farmoni' (PF-81 emas)\n"
            "   - 'bir ming olti' (1006 emas)\n"
            "   - 'ji-pi-ey' (GPA emas)\n"
            "   - 'oliy ta'lim muassasasi' (OTM emas)\n"
            "3. KIRISH SO'ZLARISIZ TO'G'RIDAN-TO'G'RI JAVOB: Javobni hech qachon fuqaro savolini takrorlash yoki kirish monologlari ('...haqida ma'lumot beraman', 'Savolingizga javoban', 'Albatta', 'Assalomu alaykum') bilan BOSHLAMANG! DARHOL asosiy huquqiy yechim, aniq fakt va amaliy harakatni (masalan: my.gov.uz orqali ariza topshirish tartibini) aytishdan boshlang.\n"
            "4. QONUNIY ASOSLAR: Har bir javobda qisqa va aniq me'yoriy hujjat nomini so'z bilan keltiring (masalan: 'Vazirlar Mahkamasining besh yuz yigirma yettinchi qaroriga binoan...').\n"
            "5. JAVOB FORMATI: Hech qanday yulduzcha (*), panjara (#), tire ro'yxat (-), raqamlangan ro'yxat (1., 2.) yoki backtick (`) ishlatmang. Faqat yaxlit, ravon oddiy matn ko'rinishida javob bering.\n"
            "6. DOIRADAN TASHQARI RAD JAVOBI: Agar savol ta'limdan mutlaqo tashqarida bo'lsa (ob-havo, oshxona, futbol, valyuta va h.k.), to'qima ma'lumot bermasdan faqat bitta jumla ayting:\n"
            f"'{OUT_OF_SCOPE_REFUSAL}'\n"
            "7. SALOMLASHUV: Agar fuqaro salom bersa, iliq va lo'nda javob bering ('Va alaykum assalom! O'zbekiston ta'lim qonunchiligi bo'yicha qanday savolingiz bor?').\n"
            "8. TAKRORLASH QAT'IYAN TAQIQLANADI (NO REPETITION): Hech qachon bir xil gapni, fikrni yoki ma'lumotni ikki marta aytmang! Har bir jumla alohida yangi, foydali va aniq amaliy ma'lumot bo'lishi shart.\n\n"
            f"RASMIY YURIDIK BAZA MAZMUNI:\n{formatted_context}"
        )

    def build_messages(
        self,
        system_instruction: str,
        user_text: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, str]]:
        """Construct chat message payload with recent context."""
        messages = [{"role": "system", "content": system_instruction}]
        if conversation_history:
            for m in conversation_history[-6:]:
                role = "user" if m.get("role") in ["user", "citizen"] else "assistant"
                content = m.get("content") or m.get("text", "")
                if content:
                    messages.append({"role": role, "content": str(content)})
        messages.append({"role": "user", "content": user_text})
        return messages

    async def _query_cerebras(
        self,
        messages: List[Dict[str, str]],
        timeout: float
    ) -> str:
        """Rank 1: Cerebras Ultra-Fast Hardware Inference (qwen-3.8-27b / gpt-oss-120b)."""
        if not getattr(settings, "CEREBRAS_API_KEY", None):
            raise ValueError("CEREBRAS_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {settings.CEREBRAS_API_KEY}",
            "Content-Type": "application/json"
        }
        models_to_try = [
            getattr(settings, "CEREBRAS_PRIMARY_MODEL", "qwen-3.8-27b"),
            getattr(settings, "CEREBRAS_FALLBACK_MODEL", "gpt-oss-120b")
        ]
        last_error = None

        async with httpx.AsyncClient(timeout=timeout) as client:
            for model_name in models_to_try:
                try:
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": 0.2,
                        "max_tokens": 350
                    }
                    response = await client.post(
                        settings.CEREBRAS_API_URL,
                        headers=headers,
                        json=payload
                    )
                    if response.status_code == 402:
                        raise httpx.HTTPStatusError("Cerebras 402 Payment Required (Billing Needed)", request=response.request, response=response)
                    if response.status_code == 429:
                        raise httpx.HTTPStatusError("Cerebras 429 Rate Limit Exceeded", request=response.request, response=response)
                    if response.status_code == 200:
                        data = response.json()
                        choices = data.get("choices", [])
                        if choices:
                            content = choices[0].get("message", {}).get("content", "")
                            if content and content.strip():
                                return content.strip()
                    response.raise_for_status()
                except Exception as e:
                    last_error = e
                    if isinstance(e, httpx.HTTPStatusError) and e.response.status_code in [402, 429]:
                        raise
                    logger.debug(f"[LLMOrchestrator] Cerebras model '{model_name}' failed: {e}")

        raise last_error or RuntimeError("Cerebras API returned empty response")

    async def _query_groq(
        self,
        messages: List[Dict[str, str]],
        timeout: float
    ) -> str:
        """Rank 2: Groq API query with ultra-fast models (qwen/qwen3.8-27b @ 0.35s)."""
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        models_to_try = [settings.GROQ_PRIMARY_MODEL, settings.GROQ_FALLBACK_MODEL]
        last_error = None

        async with httpx.AsyncClient(timeout=timeout) as client:
            for model_name in models_to_try:
                try:
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": 0.2,
                        "max_tokens": 350
                    }

                    response = await client.post(
                        settings.GROQ_API_URL,
                        headers=headers,
                        json=payload
                    )
                    if response.status_code == 200:
                        data = response.json()
                        choices = data.get("choices", [])
                        if choices:
                            content = choices[0].get("message", {}).get("content", "")
                            if content and content.strip():
                                return content.strip()
                    elif response.status_code == 429:
                        raise httpx.HTTPStatusError("Groq 429 Rate Limit Exceeded", request=response.request, response=response)
                    else:
                        logger.debug(f"[LLMOrchestrator] Groq model '{model_name}' returned status {response.status_code}. Trying next model...")
                except (httpx.HTTPStatusError, httpx.RequestError, asyncio.TimeoutError) as e:
                    last_error = e
                    if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
                        raise
                    if isinstance(e, asyncio.TimeoutError):
                        raise
                    logger.debug(f"[LLMOrchestrator] Groq model '{model_name}' failed: {e}. Trying next model...")

        raise last_error or RuntimeError("Groq API returned empty response")

    async def _query_gemini(
        self,
        user_text: str,
        system_instruction: str,
        timeout: float
    ) -> str:
        """Rank 3: Google Gemini (gemini-2.5-flash / gemini-3.8-flash) via google.genai."""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")

        client = self._get_gemini_client()
        if not client:
            raise RuntimeError("Gemini client could not be initialized")

        def _sync_call():
            return client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=user_text,
                config={"system_instruction": system_instruction, "temperature": 0.2, "max_output_tokens": 350}
            )

        response = await asyncio.wait_for(
            asyncio.to_thread(_sync_call),
            timeout=timeout
        )
        if response and response.text and response.text.strip():
            return response.text.strip()
        raise RuntimeError("Gemini returned empty response")

    async def _query_cloudflare(
        self,
        messages: List[Dict[str, str]],
        timeout: float
    ) -> str:
        """Rank 4: Cloudflare Workers AI (@cf/meta/llama-3.1-8b-instruct)."""
        if not settings.CLOUDFLARE_API_TOKEN or not settings.CLOUDFLARE_ACCOUNT_ID:
            raise ValueError("Cloudflare Workers AI credentials not configured")

        headers = {
            "Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": messages,
            "max_tokens": 220,
            "temperature": 0.2,
            "repetition_penalty": 1.2
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                settings.CLOUDFLARE_API_URL,
                headers=headers,
                json=payload
            )
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                if isinstance(result, dict):
                    if "response" in result and result["response"]:
                        return result["response"].strip()
                    choices = result.get("choices", [])
                    if choices and isinstance(choices, list) and choices[0].get("message", {}).get("content"):
                        return choices[0]["message"]["content"].strip()
                choices = data.get("choices", [])
                if choices and isinstance(choices, list) and choices[0].get("message", {}).get("content"):
                    return choices[0]["message"]["content"].strip()
            response.raise_for_status()

        raise RuntimeError("Cloudflare Workers AI returned empty response")

    async def _query_mistral(
        self,
        messages: List[Dict[str, str]],
        timeout: float
    ) -> str:
        """Rank 5: Mistral AI (mistral-large-latest)."""
        if not settings.MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.MISTRAL_MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 350
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                settings.MISTRAL_API_URL,
                headers=headers,
                json=payload
            )
            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    if content and content.strip():
                        return content.strip()
            response.raise_for_status()

        raise RuntimeError("Mistral AI returned empty response")

    def _query_rule_engine(self, user_text: str, legal_context: Any) -> str:
        """Ultimate fallback: deterministic rule-based generator from ingested database."""
        from app.services.knowledge_base import is_in_educational_scope
        if not isinstance(legal_context, dict):
            if not is_in_educational_scope(user_text):
                return OUT_OF_SCOPE_REFUSAL
            return "Savolingiz rasmiy ta'lim qonunchiligi asosida qabul qilindi. Barcha xizmatlar my.gov.uz orqali ko'rsatiladi."

        faqs = legal_context.get("faqs", [])
        if faqs:
            top_faq = faqs[0]
            short_ans = top_faq.get("short_answer", "")
            basis = top_faq.get("legal_basis", "Ta'lim qonunchiligi")
            clean_basis = basis.split(";")[0].strip() if basis else "Qonunchilik"
            return f"{clean_basis}ga binoan: {short_ans}"

        articles = legal_context.get("articles", [])
        if articles:
            top_art = articles[0]
            return f"{top_art['title']}ga muvofiq: {top_art['summary']}"

        if not is_in_educational_scope(user_text):
            return OUT_OF_SCOPE_REFUSAL

        return "Ta'lim qonunchiligiga ko'ra barcha davlat ta'lim xizmatlari my.gov.uz va vazirlik portallari orqali ko'rsatiladi."

    def clean_and_refine_response(self, raw_text: str) -> str:
        """Clean markdown, strip leading punctuation, deduplicate repeated sentences, and clean filler phrases."""
        import re
        if not raw_text:
            return ""
        clean = strip_markdown_symbols(raw_text.strip())
        clean = clean.lstrip('. ,;:-!?\n\t')

        # Strip common AI echoing and intro filler patterns
        intro_patterns = [
            r"^[^.!?\n]{1,80}haqida\s+ma'lumot\s+ber(?:aman|amiz)[.!?:]?\s*",
            r"^[^.!?\n]{1,80}to'g'risida\s+quyidagi\s+ma'lumotlar\s+beriladi[.!?:]?\s*",
            r"^(?:sizning\s+)?savolingizga\s+(?:javoban|kelsak|binoan)[.!?:]?\s*",
            r"^(?:albatta|assalomu\s+alaykum|assalamu\s+alaikum|salom)[.!,;:]?\s*",
            r"^(?:ushbu\s+masalada\s+ma'lumot\s+beraman)[.!?:]?\s*",
            r"^(?:quyidagicha\s+ma'lumot\s+beraman)[.!?:]?\s*",
            r"^[^.!?\n]{1,80}(?:quyidagicha|quyidagilar)[.!?:]?\s*",
            r"^(?:quyidagi\s+qonuniy\s+asoslar\s+ko'rilsa\s+kerak)[.!?:]?\s*",
        ]
        for pat in intro_patterns:
            clean = re.sub(pat, "", clean, flags=re.IGNORECASE).strip()
        clean = clean.lstrip('. ,;:-!?\n\t')

        # Strip numbered list markers at start of sentences (e.g. '1. ', '2. ')
        clean = re.sub(r'(?:^|\s)\d+\.\s*', ' ', clean).strip()

        # Split into individual sentences
        raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean) if s.strip()]

        # Deduplicate sentences: remove exact duplicates or sentences with high semantic word overlap (>= 60%)
        unique_sentences = []
        for s in raw_sentences:
            words_s = set(re.findall(r"\w+", s.lower()))
            if not words_s:
                continue
            is_dup = False
            for prev in unique_sentences:
                words_prev = set(re.findall(r"\w+", prev.lower()))
                if not words_prev:
                    continue
                overlap = len(words_s & words_prev) / max(len(words_s), len(words_prev))
                if overlap >= 0.60:
                    is_dup = True
                    break
            if not is_dup:
                unique_sentences.append(s)

        # Limit to 2-3 complete, substantive sentences
        if len(unique_sentences) > 3:
            clean = " ".join(unique_sentences[:3])
        elif len(unique_sentences) > 0:
            clean = " ".join(unique_sentences)
        else:
            clean = raw_text.strip()
        return clean

    async def generate_response(
        self,
        user_text: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        legal_context: Optional[Any] = None,
        prioritize_fastest: bool = True,
        timeout: Optional[float] = None
    ) -> Tuple[str, str]:
        """
        Executes Multi-LLM inference cascade.
        LLM independently reasons if the query is in-scope vs out-of-scope based on system prompt.
        """
        from app.services.knowledge_base import get_complete_legal_context
        req_timeout = timeout or settings.LLM_TIMEOUT_SECONDS

        # Ensure legal context is available
        if legal_context is None:
            legal_context = get_complete_legal_context(user_text, max_faqs=3, max_articles=2)

        system_instruction = self.build_system_instruction(legal_context)
        messages = self.build_messages(system_instruction, user_text, conversation_history)

        print(f"\n============================================================")
        print(f"[LLM-ORCHESTRATOR] Routing Query: '{user_text}'")

        # Working speed hierarchy: Cloudflare (1.5s - prioritized) -> Groq -> Gemini -> Mistral -> Rule Engine
        tiers = [
            (self.PROVIDER_CLOUDFLARE, lambda: self._query_cloudflare(messages, timeout=req_timeout)),
            (self.PROVIDER_GROQ, lambda: self._query_groq(messages, timeout=req_timeout)),
            (self.PROVIDER_GEMINI, lambda: self._query_gemini(user_text, system_instruction, timeout=req_timeout)),
            (self.PROVIDER_MISTRAL, lambda: self._query_mistral(messages, timeout=req_timeout)),
        ]

        import time
        for rank_idx, (provider_name, query_func) in enumerate(tiers, 1):
            t_start = time.perf_counter()
            print(f"[LLM-ATTEMPT] Rank {rank_idx}: Querying {provider_name}...")
            try:
                res = await query_func()
                if res and res.strip():
                    clean_res = self.clean_and_refine_response(res)
                    dur_ms = (time.perf_counter() - t_start) * 1000
                    print(f"[LLM-SUCCESS] Provider: {provider_name.upper()} in {dur_ms:.1f}ms")
                    print(f"[LLM-ANSWER]: {clean_res}")
                    print(f"============================================================\n")
                    logger.info(f"[LLMOrchestrator] Turn resolved via provider: {provider_name}")
                    return clean_res, provider_name
            except Exception as e:
                dur_ms = (time.perf_counter() - t_start) * 1000
                print(f"[LLM-FAILOVER] {provider_name} failed ({dur_ms:.1f}ms): {e}. Cascading...")
                logger.warning(f"[LLMOrchestrator] Provider '{provider_name}' FAILED or TIMED OUT: {e}. Cascading to next tier...")

        # --- RANK 5: Deterministic Legal Rule Engine (Ultimate Safety Net: ~0.005s) ---
        print(f"[LLM-RULE-ENGINE] Resolved via Local Deterministic Rule Engine (~0.005s)")
        print(f"============================================================\n")
        logger.info("[LLMOrchestrator] Turn resolved via Deterministic Legal Rule Engine")
        rule_res = self._query_rule_engine(user_text, legal_context)
        return rule_res.strip(), self.PROVIDER_RULE_ENGINE

    async def generate_call_summary(
        self,
        dialog_history: List[str],
        timeout: Optional[float] = None
    ) -> Tuple[str, str]:
        """Generate concise summary using multi-provider cascade."""
        if not dialog_history:
            return "Fuqaroga rasmiy ta'lim qonunchiligi bo'yicha maslahat berildi.", self.PROVIDER_RULE_ENGINE

        prompt = (
            "Quyidagi fuqaro va AI maslahatchi o'rtasidagi suhbatni 1-2 jumla bilan "
            "o'zbek tilida umumlashtiring (ko'tarilgan asosiy huquqiy masala va qonuniy yechim):\n\n"
            + "\n".join(dialog_history)
        )
        system_instruction = (
            "Siz O'zbekiston Respublikasi ta'lim vazirliklarining tahliliy xizmatitisiz. "
            "Suhbat xulosasini lo'nda va rasmiy bayon eting."
        )
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]

        try:
            summary, prov = await self.generate_response(prompt, conversation_history=None, timeout=timeout or 5.0)
            return summary, prov
        except Exception:
            return "Fuqaroga rasmiy ta'lim qonunchiligi bo'yicha maslahat berildi.", self.PROVIDER_RULE_ENGINE


llm_orchestrator = LLMOrchestrator()
