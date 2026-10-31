import sys
import time
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from starlette.testclient import TestClient
from app.main import app

def run_prompts():
    client = TestClient(app)

    # Prompt 2
    print("\n================== PROMPT 2: PYTHON DECORATORS ==================")
    t0 = time.time()
    res2 = client.post(
        "/api/v1/inference/chat",
        json={
            "prompt": "Explain Python decorators with an example.",
            "model": "qwen3:8b",
        },
        headers={"Origin": "http://127.0.0.1:3000"}
    )
    print(f"Status: {res2.status_code} in {time.time()-t0:.2f}s")
    assert res2.status_code == 200
    content2 = res2.json()["content"]
    (backend_dir / "tests" / "prompt2_decorators.txt").write_text(content2, encoding="utf-8")
    print(f"Saved prompt2_decorators.txt ({len(content2)} chars)")

    # Prompt 3
    print("\n================== PROMPT 3: PRIME NUMBER CHECKER ==================")
    t1 = time.time()
    res3 = client.post(
        "/api/v1/inference/chat",
        json={
            "prompt": "Write a Python program to check whether a number is prime.",
            "model": "qwen3:8b",
        },
        headers={"Origin": "http://localhost:3000"}
    )
    print(f"Status: {res3.status_code} in {time.time()-t1:.2f}s")
    assert res3.status_code == 200
    content3 = res3.json()["content"]
    (backend_dir / "tests" / "prompt3_prime.txt").write_text(content3, encoding="utf-8")
    print(f"Saved prompt3_prime.txt ({len(content3)} chars)")

    print("\nALL PROMPTS SUCCESSFULLY VERIFIED AND SAVED!")

if __name__ == "__main__":
    run_prompts()

