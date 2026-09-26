import sys
import os
import time
import asyncio
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath("backend"))
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv("backend/.env")

from app.services.llm_orchestrator import llm_orchestrator
from app.services.knowledge_base import get_complete_legal_context

TEST_QUESTIONS = [
    {
        "q": "Maktabda o'quvchilardan yoki ota-onalardan pul yig'ish (fond, ta'mirlash) qonuniymi?",
        "expected_law": ["taqiqlanadi", "qonuniy emas", "bepul", "konstitutsiya"]
    },
    {
        "q": "Davlat OTMlari magistraturasida o'qiyotgan xotin-qizlar kontrakti qanday qoplanadi?",
        "expected_law": ["vmq-447", "davlat budjeti", "qoplab", "100%"]
    },
    {
        "q": "O'qituvchini majburiy mehnatga (ko'cha tozalash, hashar) jalb qilish mumkinmi?",
        "expected_law": ["52-modda", "pedagog", "taqiqlanadi", "majburiy mehnat"]
    }
]

async def test_provider(name: str, query_func, q: str, system_instr: str, messages: list):
    start = time.perf_counter()
    try:
        if name == "gemini":
            res = await query_func(q, system_instr, timeout=10.0)
        elif name == "rule_engine":
            res = query_func(q, get_complete_legal_context(q))
        else:
            res = await query_func(messages, timeout=10.0)
        elapsed = time.perf_counter() - start
        return {"success": True, "time": elapsed, "text": res, "error": None}
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {"success": False, "time": elapsed, "text": "", "error": str(e)}

async def run_benchmark():
    providers = [
        ("groq", llm_orchestrator._query_groq),
        ("gemini", llm_orchestrator._query_gemini),
        ("cloudflare", llm_orchestrator._query_cloudflare),
        ("mistral", llm_orchestrator._query_mistral),
        ("rule_engine", llm_orchestrator._query_rule_engine),
    ]

    stats = {p[0]: {"times": [], "successes": 0, "failures": 0, "accuracy_hits": 0, "errors": []} for p in providers}

    print("\n" + "="*80)
    print("SÖZLAB MULTI-LLM BENCHMARK: SPEED & LEGAL ACCURACY TEST")
    print("="*80)

    for item in TEST_QUESTIONS:
        q = item["q"]
        expected = item["expected_law"]
        print(f"\n[SAVOL]: {q}")
        legal_ctx = get_complete_legal_context(q)
        system_instr = llm_orchestrator.build_system_instruction(legal_ctx)
        messages = llm_orchestrator.build_messages(system_instr, q)

        for name, func in providers:
            result = await test_provider(name, func, q, system_instr, messages)
            if result["success"]:
                stats[name]["times"].append(result["time"])
                stats[name]["successes"] += 1
                text_low = result["text"].lower()
                # Check accuracy match against expected legal concepts
                hits = sum(1 for exp in expected if exp in text_low)
                accuracy_pct = (hits / len(expected)) * 100
                stats[name]["accuracy_hits"] += accuracy_pct
                print(f"  -> {name.upper():<12}: {result['time']:.2f}s | Accuracy: {accuracy_pct:.0f}% | Ans: {result['text'][:70]}...")
            else:
                stats[name]["failures"] += 1
                stats[name]["errors"].append(result["error"])
                print(f"  -> {name.upper():<12}: FAILED ({result['time']:.2f}s) | Error: {result['error'][:60]}")

    print("\n" + "="*80)
    print("FINAL BENCHMARK SUMMARY & SPEED-PRIORITIZED RANKING")
    print("="*80)

    ranked_providers = []
    for name in stats:
        times = stats[name]["times"]
        avg_time = (sum(times) / len(times)) if times else 999.0
        success_rate = (stats[name]["successes"] / len(TEST_QUESTIONS)) * 100
        avg_accuracy = (stats[name]["accuracy_hits"] / len(TEST_QUESTIONS))
        ranked_providers.append({
            "name": name,
            "avg_time": avg_time,
            "success_rate": success_rate,
            "avg_accuracy": avg_accuracy,
            "failures": stats[name]["failures"]
        })

    # Sort primarily by success, then by lowest average response time
    ranked_providers.sort(key=lambda x: (-x["success_rate"], x["avg_time"]))

    print(f"{'Rank':<6} | {'Provider':<15} | {'Avg Reply Time':<15} | {'Success Rate':<15} | {'Legal Accuracy':<15}")
    print("-" * 75)
    for idx, p in enumerate(ranked_providers, 1):
        print(f"{idx:<6} | {p['name'].upper():<15} | {p['avg_time']:.3f}s{' ': <8} | {p['success_rate']:.0f}%{' ': <11} | {p['avg_accuracy']:.1f}%")

    print("\nRecommended Priority based on real speed & accuracy:")
    for idx, p in enumerate(ranked_providers, 1):
        status = "ACTIVE & OPTIMAL" if p['success_rate'] > 0 else "RATE LIMITED / OFFLINE"
        print(f"  Rank {idx}: {p['name'].upper()} (avg {p['avg_time']:.2f}s, {p['avg_accuracy']:.0f}% accuracy) - {status}")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
