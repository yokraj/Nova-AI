import sys
import time
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from starlette.testclient import TestClient
from app.main import app

def test_inference_endpoints():
    client = TestClient(app)

    # 1. Test Prompt: Explain Python decorators with an example
    print("\n--- Testing Prompt 2: Explain Python decorators with an example ---")
    t0 = time.time()
    res = client.post(
        "/api/v1/inference/chat",
        json={
            "prompt": "Explain Python decorators with an example.",
            "model": "qwen3:8b",
        },
        headers={"Origin": "http://127.0.0.1:3000"}
    )
    print(f"Status Code: {res.status_code} in {time.time()-t0:.2f}s")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    content = data.get("content", "")
    print("Content preview (first 300 chars):")
    print(content[:300])
    assert "def " in content or "decorator" in content.lower() or "@" in content, "Expected decorator code or explanation"

    # 2. Test Prompt: Write a Python program to check whether a number is prime
    print("\n--- Testing Prompt 3: Write a Python program to check whether a number is prime ---")
    t0 = time.time()
    res2 = client.post(
        "/api/v1/inference/chat",
        json={
            "prompt": "Write a Python program to check whether a number is prime.",
            "model": "qwen3:8b",
        },
        headers={"Origin": "http://localhost:3000"}
    )
    print(f"Status Code: {res2.status_code} in {time.time()-t0:.2f}s")
    assert res2.status_code == 200, f"Expected 200, got {res2.status_code}: {res2.text}"
    data2 = res2.json()
    content2 = data2.get("content", "")
    print("Content preview (first 300 chars):")
    safe_preview2 = content2[:300].encode("ascii", errors="replace").decode("ascii")
    print(safe_preview2)
    assert "def " in content2 or "prime" in content2.lower() or "%" in content2, "Expected prime check program"

    # Save outputs to files for audit and verification
    (backend_dir / "tests" / "prompt2_decorators.txt").write_text(content, encoding="utf-8")
    (backend_dir / "tests" / "prompt3_prime.txt").write_text(content2, encoding="utf-8")

    print("\nALL INFERENCE PIPELINE TESTS PASSED!")

if __name__ == "__main__":
    test_inference_endpoints()

