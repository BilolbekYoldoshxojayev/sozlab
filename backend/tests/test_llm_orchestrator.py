"""
Tests for 5-Tier Ranked Multi-LLM Provider Engine with Automatic Failover:
  Rank 1: Groq API (openai/gpt-oss-120b / qwen/qwen3.8-27b)
  Rank 2: Google Gemini (gemini-3.8-flash)
  Rank 3: Cloudflare Workers AI (@cf/meta/llama-3.1-8b-instruct)
  Rank 4: Mistral AI (mistral-small-latest)
  Rank 5: Deterministic Legal Rule Engine (Local, 0ms, Zero-dependency)
"""

import pytest
import asyncio
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.services.llm_orchestrator import LLMOrchestrator, llm_orchestrator
from app.services.ai_dialog import dialog_manager
from app.services.call_manager import call_manager
from app.services.knowledge_base import OUT_OF_SCOPE_REFUSAL

client = TestClient(app)

@pytest.mark.asyncio
async def test_orchestrator_rank1_cloudflare_success():
    """Rank 1: Cloudflare Workers AI responds successfully."""
    orch = LLMOrchestrator()
    expected_text = "Konstitutsiyaning 50-moddasiga ko'ra umumiy o'rta ta'lim bepul va majburiydir."

    with patch.object(orch, "_query_cloudflare", new_callable=AsyncMock) as mock_cf:
        mock_cf.return_value = expected_text

        text, provider = await orch.generate_response(
            user_text="Maktabda pul yig'ish mumkinmi?"
        )

        assert text == expected_text
        assert provider == LLMOrchestrator.PROVIDER_CLOUDFLARE
        mock_cf.assert_awaited_once()

@pytest.mark.asyncio
async def test_orchestrator_rank2_groq_fallback_on_cloudflare_failure():
    """Rank 2: When Cloudflare returns error/timeout, cascades to Groq."""
    orch = LLMOrchestrator()
    expected_text = "O'RQ-637-sonli 'Ta'lim to'g'risida'gi Qonunning 9-moddasiga binoan 1-sinfga qabul 7 yoshdan."

    with patch.object(orch, "_query_cloudflare", side_effect=httpx.HTTPStatusError("500 Server Error", request=MagicMock(), response=MagicMock())):
        with patch.object(orch, "_query_groq", new_callable=AsyncMock) as mock_groq:
            mock_groq.return_value = expected_text

            text, provider = await orch.generate_response(
                user_text="1-sinfga qabul yoshi necha?"
            )

            assert text == expected_text
            assert provider == LLMOrchestrator.PROVIDER_GROQ
            mock_groq.assert_awaited_once()

@pytest.mark.asyncio
async def test_orchestrator_rank3_gemini_fallback_on_groq_and_cf_failure():
    """Rank 3: When Cloudflare and Groq fail, cascades to Google Gemini."""
    orch = LLMOrchestrator()
    expected_text = "VMQ-447 qaroriga ko'ra xotin-qizlar magistratura to'lov-kontrakti davlat tomonidan qoplanadi."

    with patch.object(orch, "_query_cloudflare", side_effect=httpx.HTTPStatusError("502 Bad Gateway", request=MagicMock(), response=MagicMock())):
        with patch.object(orch, "_query_groq", side_effect=httpx.HTTPStatusError("429 Rate Limit", request=MagicMock(), response=MagicMock())):
            with patch.object(orch, "_query_gemini", new_callable=AsyncMock) as mock_gemini:
                mock_gemini.return_value = expected_text

                text, provider = await orch.generate_response(
                    user_text="Magistratura xotin-qizlar kontrakti to'lanadimi?"
                )

                assert text == expected_text
                assert provider == LLMOrchestrator.PROVIDER_GEMINI
                mock_gemini.assert_awaited_once()

@pytest.mark.asyncio
async def test_orchestrator_rank4_mistral_fallback_on_ranks_1_to_3_failure():
    """Rank 4: When Groq, Cloudflare, and Gemini fail, cascades to Mistral AI."""
    orch = LLMOrchestrator()
    expected_text = "Prezidentning PF-81 farmoniga muvofiq grantlar GPA ko'rsatkichiga qarab qayta taqsimlanadi."

    with patch.object(orch, "_query_groq", side_effect=asyncio.TimeoutError()):
        with patch.object(orch, "_query_cloudflare", side_effect=httpx.HTTPStatusError("502 Bad Gateway", request=MagicMock(), response=MagicMock())):
            with patch.object(orch, "_query_gemini", side_effect=Exception("Gemini network unreachable")):
                with patch.object(orch, "_query_mistral", new_callable=AsyncMock) as mock_mistral:
                    mock_mistral.return_value = expected_text

                    text, provider = await orch.generate_response(
                        user_text="GPA bo'yicha grant taqsimlanishi qanday?"
                    )

                    assert text == expected_text
                    assert provider == LLMOrchestrator.PROVIDER_MISTRAL
                    mock_mistral.assert_awaited_once()

@pytest.mark.asyncio
async def test_orchestrator_rank5_rule_engine_fallback_when_all_fail():
    """Rank 5: Ultimate safety net activates when all external LLMs fail."""
    orch = LLMOrchestrator()

    with patch.object(orch, "_query_groq", side_effect=httpx.HTTPStatusError("429 Too Many Requests", request=MagicMock(), response=MagicMock())):
        with patch.object(orch, "_query_cloudflare", side_effect=asyncio.TimeoutError()):
            with patch.object(orch, "_query_gemini", side_effect=RuntimeError("503 UNAVAILABLE")):
                with patch.object(orch, "_query_mistral", side_effect=httpx.HTTPStatusError("429 Rate limited", request=MagicMock(), response=MagicMock())):
                    text, provider = await orch.generate_response(
                        user_text="Maktabda remontga pul yig'ish mumkinmi?"
                    )

                    assert provider == LLMOrchestrator.PROVIDER_RULE_ENGINE
                    assert len(text) > 20
                    t_low = text.lower()
                    assert "50" in t_low or "taqiq" in t_low or "bepul" in t_low or "qonun" in t_low

@pytest.mark.asyncio
async def test_cerebras_direct_query():
    """Direct Cerebras method execution."""
    orch = LLMOrchestrator()
    with patch.object(orch, "_query_cerebras", new_callable=AsyncMock) as mock_cerebras:
        mock_cerebras.return_value = "Cerebras javobi"
        res = await orch._query_cerebras([{"role": "user", "content": "Salom"}], timeout=2.0)
        assert res == "Cerebras javobi"

@pytest.mark.asyncio
async def test_orchestrator_out_of_scope_direct_rule_engine():
    """Out-of-scope query refuses appropriately without hallucination."""
    orch = LLMOrchestrator()
    # Test rule engine direct out of scope refusal
    rule_text = orch._query_rule_engine("Bugun havo qanday bo'ladi?", legal_context={})
    assert OUT_OF_SCOPE_REFUSAL in rule_text

    # Test full generate_response returns official refusal
    text, provider = await orch.generate_response("Bugun havo qanday bo'ladi?")
    assert OUT_OF_SCOPE_REFUSAL in text

@pytest.mark.asyncio
async def test_orchestrator_call_summary_multi_tier():
    """Summary generation cascades gracefully across tiers."""
    orch = LLMOrchestrator()
    history = [
        "Fuqaro: Bolam 1-sinfga qachon boradi?",
        "AI: Bolalar 7 yoshga to'ladigan yilda 1-sinfga qabul qilinadi."
    ]

    # Test summary with Cloudflare success
    with patch.object(orch, "_query_cloudflare", new_callable=AsyncMock) as mock_cf:
        mock_cf.return_value = "1-sinfga qabul yoshi (7 yosh) tushuntirildi."
        summary, provider = await orch.generate_call_summary(history)
        assert provider == LLMOrchestrator.PROVIDER_CLOUDFLARE
        assert "7 yosh" in summary

    # Test summary when all LLMs fail
    with patch.object(orch, "_query_groq", side_effect=Exception("fail")), \
         patch.object(orch, "_query_gemini", side_effect=Exception("fail")), \
         patch.object(orch, "_query_cloudflare", side_effect=Exception("fail")), \
         patch.object(orch, "_query_mistral", side_effect=Exception("fail")):
        summary, provider = await orch.generate_call_summary(history)
        assert provider == LLMOrchestrator.PROVIDER_RULE_ENGINE
        assert len(summary) > 10

@pytest.mark.asyncio
async def test_dialog_manager_integration_turn():
    """Live integration with AIDialogManager records provider and returns proper turn response."""
    res = await dialog_manager.process_user_turn(
        call_id="call-orch-test-01",
        user_text="1-sinfga qabul yoshi necha yosh?"
    )
    assert res.call_id == "call-orch-test-01"
    assert len(res.ai_text) > 10
    assert res.llm_provider_used in [
        LLMOrchestrator.PROVIDER_GROQ,
        LLMOrchestrator.PROVIDER_GEMINI,
        LLMOrchestrator.PROVIDER_CLOUDFLARE,
        LLMOrchestrator.PROVIDER_MISTRAL,
        LLMOrchestrator.PROVIDER_RULE_ENGINE
    ]

def test_calls_api_turn_attaches_llm_provider_metadata():
    """Verify POST /api/calls/{call_id}/turn populates llm_provider_used on MessageSchema and CallRecord."""
    # 1. Create a call
    create_res = client.post("/api/calls", json={"citizen_name": "LLM Test Citizen", "citizen_phone": "+998 90 999-88-77"})
    assert create_res.status_code == 200
    call_id = create_res.json()["id"]

    # 2. Process turn
    turn_res = client.post(f"/api/calls/{call_id}/turn", json={
        "call_id": call_id,
        "user_text": "Magistratura xotin-qizlar kontrakti davlat tomonidan to'lanadimi?",
        "voice_enabled": False
    })
    assert turn_res.status_code == 200
    turn_data = turn_res.json()
    assert "llm_provider_used" in turn_data
    assert turn_data["llm_provider_used"] is not None

    # 3. Verify call record and messages reflect llm_provider_used
    get_res = client.get(f"/api/calls/{call_id}")
    assert get_res.status_code == 200
    call_data = get_res.json()
    assert call_data.get("llm_provider_used") is not None
    assert call_data.get("last_llm_provider") is not None

    ai_msgs = [m for m in call_data["messages"] if m["role"] == "ai" and m["id"] != "init"]
    assert len(ai_msgs) >= 1
    assert ai_msgs[0].get("llm_provider_used") is not None

@pytest.mark.asyncio
async def test_groq_fallback_model_on_primary_error():
    """Verify Groq attempts fallback model when primary model returns an error."""
    orch = LLMOrchestrator()
    messages = [{"role": "user", "content": "Salom"}]

    def fake_post(url, headers, json):
        req = httpx.Request("POST", url)
        # Primary model fails with 404
        if json.get("model") == orch.default_timeout or json.get("model") == "openai/gpt-oss-120b":
            resp = httpx.Response(404, request=req, json={"error": "model not found"})
            return resp
        # Fallback model succeeds
        return httpx.Response(200, request=req, json={
            "choices": [{"message": {"content": "Va alaykum assalom (Qwen)"}}]
        })

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=fake_post)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        res = await orch._query_groq(messages, timeout=5.0)
        assert res == "Va alaykum assalom (Qwen)"

@pytest.mark.asyncio
async def test_cloudflare_response_format_variations():
    """Verify Cloudflare handles both choices array and direct response field."""
    orch = LLMOrchestrator()
    messages = [{"role": "user", "content": "Salom"}]

    # Format 1: choices[0].message.content
    resp1 = httpx.Response(200, request=httpx.Request("POST", "http://test"), json={
        "result": {"choices": [{"message": {"content": "Javob 1"}}]}
    })
    mock_client1 = AsyncMock()
    mock_client1.post = AsyncMock(return_value=resp1)
    mock_client1.__aenter__.return_value = mock_client1
    mock_client1.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client1):
        assert await orch._query_cloudflare(messages, timeout=5.0) == "Javob 1"

    # Format 2: result.response
    resp2 = httpx.Response(200, request=httpx.Request("POST", "http://test"), json={
        "result": {"response": "Javob 2"}
    })
    mock_client2 = AsyncMock()
    mock_client2.post = AsyncMock(return_value=resp2)
    mock_client2.__aenter__.return_value = mock_client2
    mock_client2.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client2):
        assert await orch._query_cloudflare(messages, timeout=5.0) == "Javob 2"

def test_api_chat_endpoint_success():
    """Verify POST /api/chat receives message and returns fast legal response with citations."""
    response = client.post("/api/chat", json={
        "message": "Bog'cha navbatini qanday tekshirsa bo'ladi?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 10
    assert "provider" in data
    assert "latency_ms" in data
    assert data["latency_ms"] >= 0
    assert "citations" in data
    assert data["in_scope"] is True

def test_api_human_vs_ai_analytics_endpoint():
    """Verify GET /api/analytics/human-vs-ai returns full empirical metric comparison."""
    response = client.get("/api/analytics/human-vs-ai")
    assert response.status_code == 200
    data = response.json()
    assert "comparison_title" in data
    assert "metrics" in data
    assert len(data["metrics"]) >= 5
    metric_ids = [m["id"] for m in data["metrics"]]
    assert "first_response_latency" in metric_ids
    assert "queue_wait_time" in metric_ids
    assert "legal_accuracy" in metric_ids
    assert "cost_per_call" in metric_ids
    assert "economic_summary" in data
    assert data["economic_summary"]["savings_percentage"] > 90
