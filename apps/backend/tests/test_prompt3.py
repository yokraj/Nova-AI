import sys
import time
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from starlette.testclient import TestClient
from app.main import app

def test_prompt3():
    client = TestClient(app)
    print("\n--- Testing Prompt 3: Prime Number Checker ---")
    t0 = time.time()
    res = client.post(
        "/api/v1/inference/chat",
        json={
            "prompt": "Write a Python program to check whether a number is prime.",
            "model": "qwen3:8b",
        },
        headers={"Origin": "http://localhost:3000"}
    )
    print(f"Status Code: {res.status_code} in {time.time()-t0:.2f}s")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    content = res.json().get("content", "")
    (backend_dir / "tests" / "prompt3_prime.txt").write_text(content, encoding="utf-8")
    print(f"Successfully saved {len(content)} characters to prompt3_prime.txt")
    safe_preview = content[:200].encode("ascii", errors="replace").decode("ascii")
    print("Preview:\n", safe_preview)

if __name__ == "__main__":
    test_prompt3()

