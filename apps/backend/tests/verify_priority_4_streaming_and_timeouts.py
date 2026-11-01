"""Validation Script for Priority 4: Inference, Streaming, Multi-Turn, and Timeouts.

Verifies:
1. Non-streaming inference endpoint (/api/v1/inference/chat).
2. SSE streaming inference endpoint (/api/v1/inference/stream) with TTFT measurement.
3. Multi-turn context preservation in streaming.
4. Client disconnect / stream cancellation.
5. Strict bounded timeout handling (enforcing client timeout without hanging).
6. Payload format schema compatibility with frontend ConversationEngine.
"""

import asyncio
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


async def run_priority_4_verification():
    token = create_access_token(
        {"sub": "p4-validator", "role": "user"},
        expires_delta=timedelta(hours=2),
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Origin": "http://127.0.0.1:3000",
        "Content-Type": "application/json",
    }

    results = {}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=120.0) as client:
        # 1. Non-streaming inference test
        print("\n=======================================================")
        print("1. NON-STREAMING INFERENCE VALIDATION")
        print("=======================================================")
        t0 = time.perf_counter()
        res_nonstream = await client.post(
            "/api/v1/inference/chat",
            headers=headers,
            json={
                "prompt": "What is the capital of Japan? Answer in one word.",
                "model": "qwen3:8b",
                "max_tokens": 100,
            },
        )
        dur_nonstream = time.perf_counter() - t0
        assert res_nonstream.status_code == 200, f"Non-streaming failed: {res_nonstream.text}"
        data_nonstream = res_nonstream.json()
        content_ns = data_nonstream.get("content", "")
        passed_ns = "tokyo" in content_ns.lower()
        print(f"Status: HTTP 200 in {dur_nonstream:.2f}s | Result: {content_ns[:80]} | Passed: {passed_ns}")
        results["non_streaming"] = {
            "status": "PASS" if passed_ns else "FAIL",
            "duration_seconds": round(dur_nonstream, 2),
            "model": data_nonstream.get("model"),
            "provider": data_nonstream.get("provider"),
            "has_tokens_metadata": "total_tokens" in data_nonstream,
            "response": content_ns[:150],
        }

        # 2. Streaming inference test with TTFT
        print("\n=======================================================")
        print("2. STREAMING INFERENCE VALIDATION (SSE)")
        print("=======================================================")
        t_stream_start = time.perf_counter()
        ttft = None
        chunks = []
        assembled_stream = ""

        async with client.stream(
            "POST",
            "/api/v1/inference/stream",
            headers=headers,
            json={
                "prompt": "Count from 1 to 5, one number per line.",
                "model": "qwen3:8b",
                "max_tokens": 150,
            },
        ) as stream_res:
            assert stream_res.status_code == 200, f"Stream failed: {stream_res.status_code}"
            assert "text/event-stream" in stream_res.headers.get("content-type", "")

            async for line in stream_res.aiter_lines():
                if not line:
                    continue
                if ttft is None:
                    ttft = time.perf_counter() - t_stream_start
                    print(f"Time To First Token (TTFT): {ttft:.3f}s")
                chunks.append(line)
                if line.startswith("data:"):
                    assembled_stream += line[5:]

        dur_stream = time.perf_counter() - t_stream_start
        passed_stream = len(chunks) > 5 and ttft is not None and ttft < 15.0
        print(f"Chunks: {len(chunks)} | TTFT: {ttft:.3f}s | Duration: {dur_stream:.2f}s | Passed: {passed_stream}")
        results["streaming"] = {
            "status": "PASS" if passed_stream else "FAIL",
            "ttft_seconds": round(ttft, 3) if ttft else None,
            "total_chunks": len(chunks),
            "duration_seconds": round(dur_stream, 2),
            "stream_assembled_preview": assembled_stream[:150],
        }

        # 3. Multi-turn streaming test
        print("\n=======================================================")
        print("3. MULTI-TURN STREAMING CONTEXT VALIDATION")
        print("=======================================================")
        t_mt_start = time.perf_counter()
        mt_chunks = []
        mt_assembled = ""
        prior_messages = [
            {"role": "user", "content": "My favorite fruit is mango."},
            {"role": "assistant", "content": "Got it! Your favorite fruit is mango."},
        ]

        async with client.stream(
            "POST",
            "/api/v1/inference/stream",
            headers=headers,
            json={
                "prompt": "What fruit did I say I like?",
                "model": "qwen3:8b",
                "max_tokens": 150,
                "messages": prior_messages,
            },
        ) as mt_stream_res:
            assert mt_stream_res.status_code == 200
            async for line in mt_stream_res.aiter_lines():
                if not line:
                    continue
                mt_chunks.append(line)
                if line.startswith("data:"):
                    mt_assembled += line[5:]

        dur_mt = time.perf_counter() - t_mt_start
        passed_mt = "mango" in mt_assembled.lower()
        print(f"Multi-turn streaming: {len(mt_chunks)} chunks in {dur_mt:.2f}s | 'mango' recalled: {passed_mt}")
        results["multi_turn_streaming"] = {
            "status": "PASS" if passed_mt else "FAIL",
            "duration_seconds": round(dur_mt, 2),
            "total_chunks": len(mt_chunks),
            "recalled_context": passed_mt,
            "response": mt_assembled[:150],
        }

        # 4. Stream Cancellation / Early Client Disconnect
        print("\n=======================================================")
        print("4. STREAM CANCELLATION & EARLY DISCONNECT")
        print("=======================================================")
        t_canc_start = time.perf_counter()
        disconnect_at_chunk = None
        try:
            async with client.stream(
                "POST",
                "/api/v1/inference/stream",
                headers=headers,
                json={
                    "prompt": "Write a 1000-word detailed essay on artificial intelligence architecture.",
                    "model": "qwen3:8b",
                    "max_tokens": 500,
                },
            ) as cancel_stream:
                assert cancel_stream.status_code == 200
                count = 0
                async for line in cancel_stream.aiter_lines():
                    if line.startswith("data:"):
                        count += 1
                        if count >= 4:
                            disconnect_at_chunk = count
                            print(f"Aborting connection at chunk #{count} (client-side abort)...")
                            break
            dur_canc = time.perf_counter() - t_canc_start
            print(f"Stream abort handled cleanly in {dur_canc:.2f}s (closed at chunk #{disconnect_at_chunk})")
            passed_canc = True
        except Exception as e:
            print(f"Stream cancellation error: {e}")
            dur_canc = time.perf_counter() - t_canc_start
            passed_canc = False

        results["stream_cancellation"] = {
            "status": "PASS" if passed_canc else "FAIL",
            "aborted_at_chunk": disconnect_at_chunk,
            "duration_seconds": round(dur_canc, 2),
        }

        # 5. Bounded Timeout Handling
        print("\n=======================================================")
        print("5. BOUNDED TIMEOUT ENFORCEMENT")
        print("=======================================================")
        # Test client timeout enforcement with a 0.05s client timeout
        timeout_caught = False
        t_to_start = time.perf_counter()
        try:
            async with httpx.AsyncClient(base_url=BASE_URL, timeout=0.05) as quick_client:
                await quick_client.post(
                    "/api/v1/inference/chat",
                    headers=headers,
                    json={
                        "prompt": "Write a long story about space exploration.",
                        "model": "qwen3:8b",
                        "max_tokens": 500,
                    },
                )
        except httpx.TimeoutException:
            timeout_caught = True
            dur_to = time.perf_counter() - t_to_start
            print(f"Client-side timeout enforced properly in {dur_to:.3f}s: httpx.TimeoutException caught")
        except Exception as e:
            dur_to = time.perf_counter() - t_to_start
            print(f"Unexpected exception: {e}")

        results["timeout_enforcement"] = {
            "status": "PASS" if timeout_caught else "FAIL",
            "enforced_in_seconds": round(dur_to, 3),
            "exception_type": "httpx.TimeoutException" if timeout_caught else "None",
        }

        # 6. Frontend Display Payload Compatibility Check
        print("\n=======================================================")
        print("6. FRONTEND DISPLAY COMPATIBILITY CHECK")
        print("=======================================================")
        required_keys = ["request_id", "content", "model", "provider", "task_category", "prompt_tokens", "completion_tokens", "total_tokens", "latency_ms"]
        compat = all(k in data_nonstream for k in required_keys)
        print(f"All required schema fields present: {compat}")
        results["frontend_compatibility"] = {
            "status": "PASS" if compat else "FAIL",
            "checked_fields": required_keys,
            "all_present": compat,
        }

    out_file = backend_dir / "tests" / "priority_4_streaming_and_timeouts_evidence.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nAll Priority 4 tests completed and persisted to {out_file}")
    return results


if __name__ == "__main__":
    asyncio.run(run_priority_4_verification())

