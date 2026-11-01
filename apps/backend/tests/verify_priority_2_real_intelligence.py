"""Priority 2: Real Intelligence Verification Suite for Nova AI Core Intelligence.

Verifies:
1. Deterministic arithmetic: 19 * 37 = 703.
2. Code explanation: Python decorators with working example.
3. Prime-number checker: Algorithm & code for prime 29.
4. Multi-step reasoning: Probability drawing 2 red balls from (5 red, 4 blue, 3 green).
5. Follow-up question: Context retrieval from previous turn.
6. Error correction: Correcting 12 * 12 = 154 claim to 144.
7. Intent distinction: Calculation (deterministic) vs. Conceptual Reasoning (LLM).
"""

import json
import sys
import time
from datetime import timedelta
from pathlib import Path
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.identity.infrastructure.security import create_access_token
from app.intelligence.response_validator import ResponseValidator

BASE_URL = "http://127.0.0.1:8000"


def run_priority_2_verification():
    token = create_access_token({"sub": "p2-validator", "role": "user"}, expires_delta=timedelta(hours=1))
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "http://127.0.0.1:3000",
    }

    validator = ResponseValidator()
    results = {}

    with httpx.Client(base_url=BASE_URL, timeout=120.0) as client:
        # 1. Deterministic Arithmetic
        print("\n--- 1. DETERMINISTIC ARITHMETIC (19 x 37 = 703) ---")
        t0 = time.perf_counter()
        r1 = client.post(
            "/api/v1/inference/chat",
            headers=headers,
            json={"prompt": "What is 19 multiplied by 37? Explain step by step.", "use_deterministic_tools": True},
        )
        dur1 = time.perf_counter() - t0
        d1 = r1.json()
        c1 = d1.get("content", "")
        passed1 = "703" in c1 and d1.get("is_deterministic") is True
        print(f"Status: {r1.status_code} in {dur1:.4f}s | Model: {d1.get('model')} | Deterministic: {d1.get('is_deterministic')}")
        results["1_arithmetic"] = {
            "status": "PASS" if passed1 else "FAIL",
            "provider": d1.get("provider"),
            "model": d1.get("model"),
            "duration_s": round(dur1, 4),
            "response": c1,
        }

        # 2. Python Decorators Explanation
        print("\n--- 2. PYTHON DECORATORS EXPLANATION ---")
        t0 = time.perf_counter()
        r2 = client.post(
            "/api/v1/inference/chat",
            headers=headers,
            json={"prompt": "Explain Python decorators with a simple working example.", "model": "qwen3:8b", "max_tokens": 400},
        )
        dur2 = time.perf_counter() - t0
        d2 = r2.json()
        c2 = d2.get("content", "")
        code_v = validator.validate_code_in_response(c2)
        passed2 = ("@" in c2 or "decorator" in c2.lower()) and code_v["valid"]
        print(f"Status: {r2.status_code} in {dur2:.2f}s | Code Valid: {code_v['valid']}")
        results["2_decorators"] = {
            "status": "PASS" if passed2 else "FAIL",
            "provider": d2.get("provider"),
            "model": d2.get("model"),
            "duration_s": round(dur2, 2),
            "code_syntax_valid": code_v["valid"],
            "response": c2[:300] + "...",
        }

        # 3. Prime Number Checker (29)
        print("\n--- 3. PRIME-NUMBER CHECKER (29) ---")
        t0 = time.perf_counter()
        r3 = client.post(
            "/api/v1/inference/chat",
            headers=headers,
            json={"prompt": "Write a Python program to check whether 29 is prime. Explain the algorithm.", "model": "qwen3:8b", "max_tokens": 400},
        )
        dur3 = time.perf_counter() - t0
        d3 = r3.json()
        c3 = d3.get("content", "")
        passed3 = "29" in c3 and ("prime" in c3.lower())
        print(f"Status: {r3.status_code} in {dur3:.2f}s | Contains 29 & Prime: {passed3}")
        results["3_prime_checker"] = {
            "status": "PASS" if passed3 else "FAIL",
            "provider": d3.get("provider"),
            "model": d3.get("model"),
            "duration_s": round(dur3, 2),
            "response": c3[:300] + "...",
        }

        # 4. Multi-Step Probability Reasoning
        print("\n--- 4. MULTI-STEP REASONING (PROBABILITY) ---")
        t0 = time.perf_counter()
        prompt_prob = (
            "A box contains 5 red balls, 4 blue balls, and 3 green balls. "
            "You draw two balls without replacement. What is the probability that both are red? "
            "Show your reasoning step by step."
        )
        r4 = client.post(
            "/api/v1/inference/chat",
            headers=headers,
            json={"prompt": prompt_prob, "model": "qwen3:8b", "max_tokens": 850},
        )
        dur4 = time.perf_counter() - t0
        d4 = r4.json()
        c4 = d4.get("content", "")
        # 5/12 * 4/11 = 20/132 = 5/33 or 10/66
        passed4 = any(frac in c4 for frac in ["5/33", "20/132", "10/66", "10 / 66", "0.151", "0.15", "5 / 33", "20 / 132"])
        print(f"Status: {r4.status_code} in {dur4:.2f}s | Probability 5/33 found: {passed4}")
        results["4_multi_step_reasoning"] = {
            "status": "PASS" if passed4 else "FAIL",
            "provider": d4.get("provider"),
            "model": d4.get("model"),
            "duration_s": round(dur4, 2),
            "response": c4,
        }

        # 5. Follow-Up Question (Context)
        print("\n--- 5. FOLLOW-UP CONTEXT QUESTION ---")
        t0 = time.perf_counter()
        r5 = client.post(
            "/api/v1/inference/chat",
            headers=headers,
            json={
                "prompt": "What port does my server run on?",
                "model": "qwen3:8b",
                "max_tokens": 350,
                "messages": [
                    {"role": "user", "content": "My server runs on port 9000."},
                    {"role": "assistant", "content": "Understood, your server is running on port 9000."},
                ],
            },
        )
        dur5 = time.perf_counter() - t0
        d5 = r5.json()
        c5 = d5.get("content", "")
        passed5 = "9000" in c5
        print(f"Status: {r5.status_code} in {dur5:.2f}s | Port 9000 retained: {passed5}")
        results["5_followup_question"] = {
            "status": "PASS" if passed5 else "FAIL",
            "provider": d5.get("provider"),
            "model": d5.get("model"),
            "duration_s": round(dur5, 2),
            "response": c5[:200] + "...",
        }

        # 6. Correct An Intentionally Incorrect Answer
        print("\n--- 6. CORRECTION OF INCORRECT CLAIM (12 x 12 = 154) ---")
        t0 = time.perf_counter()
        prompt_corr = "Someone claimed that 12 multiplied by 12 is 154. Is that correct? If not, what is the correct answer?"
        r6 = client.post(
            "/api/v1/inference/chat",
            headers=headers,
            json={"prompt": prompt_corr, "model": "qwen3:8b", "max_tokens": 350},
        )
        dur6 = time.perf_counter() - t0
        d6 = r6.json()
        c6 = d6.get("content", "")
        passed6 = "144" in c6 and any(neg in c6.lower() for neg in ["not correct", "incorrect", "false", "wrong", "no"])
        print(f"Status: {r6.status_code} in {dur6:.2f}s | Identified incorrect & gave 144: {passed6}")
        results["6_error_correction"] = {
            "status": "PASS" if passed6 else "FAIL",
            "provider": d6.get("provider"),
            "model": d6.get("model"),
            "duration_s": round(dur6, 2),
            "response": c6[:200] + "...",
        }

        # 7. Intent Distinction: Calculation vs. Reasoning
        print("\n--- 7. INTENT DISTINCTION (CALCULATION VS. REASONING) ---")
        t0 = time.perf_counter()
        rc = client.post("/api/v1/inference/classify", headers=headers, json={"prompt": "Calculate 25 * 32"})
        rr = client.post("/api/v1/inference/classify", headers=headers, json={"prompt": "Why is the sky blue during the day and red during sunset? Explain the physics."})
        dur7 = time.perf_counter() - t0
        dc = rc.json()
        dr = rr.json()
        passed7 = dc.get("is_deterministic_arithmetic") is True and dr.get("task_category") in ("Knowledge retrieval", "Logical reasoning", "Conversation")
        print(f"Status: {rc.status_code} / {rr.status_code} in {dur7:.4f}s")
        print(f"  - Calculation: Category='{dc.get('task_category')}', Deterministic={dc.get('is_deterministic_arithmetic')}")
        print(f"  - Reasoning: Category='{dr.get('task_category')}', Deterministic={dr.get('is_deterministic_arithmetic')}")
        results["7_intent_distinction"] = {
            "status": "PASS" if passed7 else "FAIL",
            "duration_s": round(dur7, 4),
            "calc_intent": dc,
            "reason_intent": dr,
        }

    out_file = backend_dir / "tests" / "priority_2_real_intelligence_evidence.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nAll Priority 2 tests completed and persisted to {out_file}")
    return results


if __name__ == "__main__":
    run_priority_2_verification()
