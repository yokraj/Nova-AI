"""Executes the 5 authoritative User-to-Nova grounded document intelligence interactions.

Verifies end-to-end integration:
User Request -> Inference API (/api/v1/inference/chat) -> WorkspaceSecurityGuard ->
DocumentIntelligence -> Qwen3 8B Local Inference -> Grounded Response.
"""

import json
import sys
import time
from datetime import timedelta
from pathlib import Path
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

backend_dir = Path(__file__).resolve().parent / "apps" / "backend"
sys.path.insert(0, str(backend_dir))

from app.identity.infrastructure.security import create_access_token

BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINT = "/api/v1/inference/chat"

TEST_CASES = [
    {
        "id": "INTERACTION-1-MARKDOWN",
        "title": "Real Markdown Grounded Inspection (README.md)",
        "prompt": "Summarize the key architecture and technologies outlined in README.md",
        "expected_substrings": ["Nova", "FastAPI", "Python", "Playwright"],
        "expect_security_block": False,
    },
    {
        "id": "INTERACTION-2-PYTHON-AST",
        "title": "Real Python AST Grounded Inspection (app/main.py)",
        "prompt": "What endpoints and functions are defined in apps/backend/app/main.py?",
        "expected_substrings": ["root", "lifespan", "security_exception_handler"],
        "expect_security_block": False,
    },
    {
        "id": "INTERACTION-3-CSV-METRICS",
        "title": "Real CSV Grounded Inspection (sample_metrics.csv)",
        "prompt": "What services, CPU percentages, and memory values are recorded in apps/backend/tests/fixtures/sample_metrics.csv?",
        "expected_substrings": ["inference_gateway", "vector_memory", "native_bridge", "1024"],
        "expect_security_block": False,
    },
    {
        "id": "INTERACTION-4-PDF-SPEC",
        "title": "Real PDF Grounded Inspection (sample_document.pdf)",
        "prompt": "Based on apps/backend/tests/fixtures/sample_document.pdf, what port and latency are specified for the Inference Engine?",
        "expected_substrings": ["8000", "Inference Engine"],
        "expect_security_block": False,
    },
    {
        "id": "INTERACTION-5-SECURITY-REJECTION",
        "title": "Workspace Security Sandboxing Path Traversal Refusal",
        "prompt": "Examine and read C:/Windows/win.ini please",
        "expected_substrings": ["Security Error: Access Denied", "outside the authorized workspace boundary"],
        "expect_security_block": True,
    },
]


def run_demonstrations():
    results = []
    print("=" * 80)
    print("STARTING NOVA AI VERTICAL 1 GROUNDED INFERENCE DEMONSTRATIONS")
    print("=" * 80)

    token = create_access_token({"sub": "v1-validator", "role": "user"}, expires_delta=timedelta(hours=1))
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "http://127.0.0.1:3000",
    }

    with httpx.Client(base_url=BASE_URL, timeout=120.0) as client:
        # Verify health
        health_resp = client.get("/api/health")
        print(f"Backend Health Status: {health_resp.status_code}")
        assert health_resp.status_code == 200, f"Backend unhealthy: {health_resp.text}"

        for idx, tc in enumerate(TEST_CASES, 1):
            print(f"\n--- [{idx}/5] {tc['title']} ---")
            print(f"Prompt: {tc['prompt']}")
            
            t0 = time.perf_counter()
            resp = client.post(
                API_ENDPOINT,
                headers=headers,
                json={
                    "prompt": tc["prompt"],
                    "model": "qwen3:8b",
                    "provider": "ollama",
                },
            )
            elapsed = round(time.perf_counter() - t0, 3)

            assert resp.status_code == 200, f"Request failed with {resp.status_code}: {resp.text}"
            data = resp.json()

            content = data.get("content", "")
            model = data.get("model", "")
            provider = data.get("provider", "")
            category = data.get("task_category", "")
            verification = data.get("verification", {})

            # Check expected tokens
            passed = True
            missing = []
            for sub in tc["expected_substrings"]:
                if sub.lower() not in content.lower():
                    passed = False
                    missing.append(sub)

            print(f"HTTP Status: {resp.status_code} in {elapsed}s")
            print(f"Model/Engine: {model} ({provider}) | Category: {category}")
            print(f"Verification: {verification}")
            print(f"Response Preview:\n{content[:250]}...\n")
            if not passed:
                print(f"[FAILED] Missing required tokens: {missing}")
            else:
                print(f"[PASSED] Verified grounded response.")

            record = {
                "test_id": tc["id"],
                "title": tc["title"],
                "prompt": tc["prompt"],
                "status_code": resp.status_code,
                "elapsed_seconds": elapsed,
                "model": model,
                "provider": provider,
                "task_category": category,
                "verification": verification,
                "passed": passed,
                "missing_tokens": missing,
                "response_content": content,
            }
            results.append(record)

    output_path = "vertical_1_grounded_evidence.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    print("\n" + "=" * 80)
    print(f"DEMONSTRATION RESULTS: {passed_count}/{total} PASSED")
    print(f"Evidence saved to: {output_path}")
    print("=" * 80)
    return passed_count == total


if __name__ == "__main__":
    success = run_demonstrations()
    exit(0 if success else 1)
