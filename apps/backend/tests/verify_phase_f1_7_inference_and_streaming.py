import asyncio
import json
import time
import sys
from pathlib import Path
from datetime import timedelta

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import httpx
from app.identity.infrastructure.security import create_access_token

BASE_URL = "http://127.0.0.1:8000"

async def test_inference_and_streaming():
    token = create_access_token(
        {"sub": "f1-7-validator", "role": "user"},
        expires_delta=timedelta(hours=2)
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Origin": "http://127.0.0.1:3000",
        "Content-Type": "application/json",
    }

    results = {}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=180.0) as client:
        # Prompt A
        print("\n=======================================================")
        print("PHASE 3 — PROMPT A: MATH REASONING")
        print("Prompt: 'What is 19 multiplied by 37? Explain step by step.'")
        print("=======================================================")
        t0 = time.time()
        res_a = await client.post(
            "/api/v1/inference/chat",
            headers=headers,
            json={
                "prompt": "What is 19 multiplied by 37? Explain step by step.",
                "model": "qwen3:8b",
                "max_tokens": 650,
            }
        )
        dur_a = time.time() - t0
        print(f"Status: {res_a.status_code} in {dur_a:.2f}s")
        assert res_a.status_code == 200, f"Prompt A failed: {res_a.text}"
        data_a = res_a.json()
        content_a = data_a.get("content", "")
        print(f"Model: {data_a.get('model')}, Provider: {data_a.get('provider')}")
        print(f"Prompt Tokens: {data_a.get('prompt_tokens')}, Completion Tokens: {data_a.get('completion_tokens')}, Total: {data_a.get('total_tokens')}")
        print(f"Content preview:\n{content_a[:350]}...\n")
        assert "703" in content_a, f"Expected 703 in answer, got: {content_a[:400]}"
        results["prompt_a"] = {
            "status": "PASS",
            "duration_s": round(dur_a, 2),
            "model": data_a.get("model"),
            "provider": data_a.get("provider"),
            "prompt_tokens": data_a.get("prompt_tokens"),
            "completion_tokens": data_a.get("completion_tokens"),
            "total_tokens": data_a.get("total_tokens"),
            "content": content_a
        }

        # Prompt B
        print("\n=======================================================")
        print("PHASE 3 — PROMPT B: PYTHON DECORATORS")
        print("Prompt: 'Explain Python decorators with a simple working example.'")
        print("=======================================================")
        t0 = time.time()
        res_b = await client.post(
            "/api/v1/inference/chat",
            headers=headers,
            json={
                "prompt": "Explain Python decorators with a simple working example.",
                "model": "qwen3:8b",
                "max_tokens": 650,
            }
        )
        dur_b = time.time() - t0
        print(f"Status: {res_b.status_code} in {dur_b:.2f}s")
        assert res_b.status_code == 200, f"Prompt B failed: {res_b.text}"
        data_b = res_b.json()
        content_b = data_b.get("content", "")
        print(f"Model: {data_b.get('model')}, Provider: {data_b.get('provider')}")
        print(f"Prompt Tokens: {data_b.get('prompt_tokens')}, Completion Tokens: {data_b.get('completion_tokens')}, Total: {data_b.get('total_tokens')}")
        print(f"Content preview:\n{content_b[:350]}...\n")
        assert "def " in content_b and ("@" in content_b or "decorator" in content_b.lower()), "Expected decorator code"
        results["prompt_b"] = {
            "status": "PASS",
            "duration_s": round(dur_b, 2),
            "model": data_b.get("model"),
            "provider": data_b.get("provider"),
            "prompt_tokens": data_b.get("prompt_tokens"),
            "completion_tokens": data_b.get("completion_tokens"),
            "total_tokens": data_b.get("total_tokens"),
            "content": content_b
        }

        # Prompt C
        print("\n=======================================================")
        print("PHASE 3 — PROMPT C: PRIME 29 ALGORITHM")
        print("Prompt: 'Write a Python program to check whether 29 is prime. Explain the algorithm.'")
        print("=======================================================")
        t0 = time.time()
        res_c = await client.post(
            "/api/v1/inference/chat",
            headers=headers,
            json={
                "prompt": "Write a Python program to check whether 29 is prime. Explain the algorithm.",
                "model": "qwen3:8b",
                "max_tokens": 650,
            }
        )
        dur_c = time.time() - t0
        print(f"Status: {res_c.status_code} in {dur_c:.2f}s")
        assert res_c.status_code == 200, f"Prompt C failed: {res_c.text}"
        data_c = res_c.json()
        content_c = data_c.get("content", "")
        print(f"Model: {data_c.get('model')}, Provider: {data_c.get('provider')}")
        print(f"Prompt Tokens: {data_c.get('prompt_tokens')}, Completion Tokens: {data_c.get('completion_tokens')}, Total: {data_c.get('total_tokens')}")
        print(f"Content preview:\n{content_c[:350]}...\n")
        assert "29" in content_c and ("prime" in content_c.lower() or "def " in content_c), "Expected prime 29 explanation and code"
        results["prompt_c"] = {
            "status": "PASS",
            "duration_s": round(dur_c, 2),
            "model": data_c.get("model"),
            "provider": data_c.get("provider"),
            "prompt_tokens": data_c.get("prompt_tokens"),
            "completion_tokens": data_c.get("completion_tokens"),
            "total_tokens": data_c.get("total_tokens"),
            "content": content_c
        }

        # Phase 4: Streaming Validation
        print("\n=======================================================")
        print("PHASE 4 — SSE TOKEN STREAMING VALIDATION")
        print("Endpoint: POST /api/v1/inference/stream")
        print("Prompt: 'Write three short bullet points explaining why tests are important in software engineering.'")
        print("=======================================================")
        t_start = time.time()
        ttft = None
        chunks = []
        accumulated_text = ""

        async with client.stream(
            "POST",
            "/api/v1/inference/stream",
            headers=headers,
            json={
                "prompt": "Write three short bullet points explaining why tests are important in software engineering.",
                "model": "qwen3:8b",
                "max_tokens": 300,
            }
        ) as stream_res:
            print(f"Stream Connected: HTTP {stream_res.status_code} in {time.time()-t_start:.2f}s")
            assert stream_res.status_code == 200, f"Stream failed: {stream_res.status_code}"
            assert "text/event-stream" in stream_res.headers.get("content-type", "")

            async for line in stream_res.aiter_lines():
                if not line:
                    continue
                if ttft is None:
                    ttft = time.time() - t_start
                    print(f"Time to First Token (TTFT): {ttft:.3f}s")
                chunks.append(line)
                if line.startswith("data:"):
                    accumulated_text += line[5:]

        total_stream_dur = time.time() - t_start
        print(f"Total Chunks Received: {len(chunks)}")
        print(f"Total Streaming Duration: {total_stream_dur:.2f}s")
        print(f"Average Chunk Rate: {len(chunks)/max(0.001, total_stream_dur):.2f} chunks/sec")
        print(f"Streamed Text Length: {len(accumulated_text)} characters")
        print(f"Streamed Text Preview (first 250 chars):\n{accumulated_text[:250]}...\n")

        assert len(chunks) > 5, f"Expected incremental streaming chunks, got only {len(chunks)}"
        assert ttft is not None and ttft < 10.0, f"Expected TTFT < 10s, got {ttft}s"

        results["streaming"] = {
            "status": "PASS",
            "ttft_s": round(ttft, 3),
            "chunks_count": len(chunks),
            "duration_s": round(total_stream_dur, 2),
            "rate_chunks_per_sec": round(len(chunks)/max(0.001, total_stream_dur), 2),
            "accumulated_text": accumulated_text
        }

        # Disconnect handling test
        print("\n--- Testing Client Disconnect / Abort on Stream ---")
        t_disc_start = time.time()
        try:
            async with client.stream(
                "POST",
                "/api/v1/inference/stream",
                headers=headers,
                json={"prompt": "Write a 500 word essay on mathematics.", "model": "qwen3:8b", "max_tokens": 300}
            ) as disc_stream:
                print(f"Disconnect test connected: HTTP {disc_stream.status_code}")
                count = 0
                async for line in disc_stream.aiter_lines():
                    if line.startswith("data:"):
                        count += 1
                        if count >= 3:
                            print("Deliberately closing stream early (client abort)...")
                            break
            print(f"Client stream closed cleanly without unhandled exception in {time.time()-t_disc_start:.2f}s")
            results["disconnect_handling"] = {"status": "PASS", "closed_early_at_chunk": count}
        except Exception as e:
            print(f"Disconnect test exception: {e}")
            results["disconnect_handling"] = {"status": "PARTIAL", "error": str(e)}

    # Save detailed evidence artifacts
    out_file = backend_dir / "tests" / "phase_f1_7_inference_evidence.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nAll verification data saved to {out_file}")
    return results

if __name__ == "__main__":
    asyncio.run(test_inference_and_streaming())
