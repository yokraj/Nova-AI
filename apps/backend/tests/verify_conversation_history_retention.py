"""Validation Script for Priority 3: Exact 4-Turn Conversation History Retention.

Conversation Flow:
Turn 1: "My project is called Nova AI."
Turn 2: "It uses Python and React."
Turn 3: "What is my project called?" (Verify 'Nova AI' is retrieved)
Turn 4: "Which technologies does it use?" (Verify 'Python' and 'React' are retrieved)
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

BASE_URL = "http://127.0.0.1:8000"


def run_exact_conversation():
    token = create_access_token({"sub": "conversation-validator", "role": "user"}, expires_delta=timedelta(hours=1))
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "http://127.0.0.1:3000",
    }

    conversation_history = []
    results = []

    dialogue_script = [
        {"role": "user", "prompt": "My project is called Nova AI.", "expected": None},
        {"role": "user", "prompt": "It uses Python and React.", "expected": None},
        {"role": "user", "prompt": "What is my project called?", "expected": ["nova ai", "nova"]},
        {"role": "user", "prompt": "Which technologies does it use?", "expected": ["python", "react"]},
    ]

    with httpx.Client(base_url=BASE_URL, timeout=120.0) as client:
        for idx, turn in enumerate(dialogue_script, 1):
            prompt = turn["prompt"]
            print(f"\n==========================================")
            print(f"TURN {idx}: USER -> \"{prompt}\"")
            print(f"==========================================")

            t0 = time.perf_counter()
            res = client.post(
                "/api/v1/inference/chat",
                headers=headers,
                json={
                    "prompt": prompt,
                    "model": "qwen3:8b",
                    "max_tokens": 500,
                    "messages": conversation_history,
                },
            )
            dur = time.perf_counter() - t0
            assert res.status_code == 200, f"Turn {idx} failed with {res.status_code}: {res.text}"
            data = res.json()
            raw_content = data.get("content", "")

            # Strip thinking trace for clean verification
            clean_content = raw_content
            if "<think>" in clean_content and "</think>" in clean_content:
                clean_content = clean_content.split("</think>")[-1].strip()

            print(f"Status: HTTP 200 in {dur:.2f}s")
            print(f"Assistant Answer:\n{clean_content}\n")

            # Update conversation history turns
            conversation_history.append({"role": "user", "content": prompt})
            conversation_history.append({"role": "assistant", "content": clean_content})

            # Verify expectations if set
            passed = True
            reason = None
            if turn["expected"]:
                content_lower = clean_content.lower()
                passed = all(kw in content_lower for kw in turn["expected"])
                if not passed:
                    reason = f"Expected keywords {turn['expected']} not found in answer."
                print(f"Verification: {'PASS' if passed else 'FAIL'}")

            results.append({
                "turn": idx,
                "user_prompt": prompt,
                "assistant_response": clean_content,
                "raw_response": raw_content,
                "duration_seconds": round(dur, 2),
                "expected": turn["expected"],
                "passed": passed,
                "failure_reason": reason,
            })

    out_file = backend_dir / "tests" / "priority_3_conversation_history_evidence.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nAll 4 turns completed and persisted to {out_file}")
    return results


if __name__ == "__main__":
    run_exact_conversation()

