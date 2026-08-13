"""Mock Runtime Provider returning deterministic test responses for offline tests and CI.
"""

from typing import Any, List
from app.ai.runtime.models import DeviceType, RuntimeRequest, RuntimeResponse


class MockRuntimeProvider:
    """Mock Runtime Provider returning deterministic test responses."""

    async def mock_generate(self, request: Optional[RuntimeRequest] = None) -> RuntimeResponse:
        model_id = request.model_id if request and hasattr(request, "model_id") and request.model_id else "mock-llm-v1"
        prompt = request.prompt if request and hasattr(request, "prompt") else "mock prompt"
        return RuntimeResponse(
            model_id=model_id,
            text_or_data=f"[Mock Runtime Response] Output for: '{prompt}'",
            finish_reason="stop",
            token_usage={"total_tokens": 30},
            latency_ms=25.0,
            device_used=DeviceType.CPU,
        )

    async def mock_transcribe(self, audio_bytes_or_path: Any) -> RuntimeResponse:
        return RuntimeResponse(
            model_id="mock-whisper-v1",
            text_or_data="Mock Speech Transcript",
            finish_reason="stop",
            token_usage={"total_tokens": 10},
            latency_ms=15.0,
            device_used=DeviceType.CPU,
        )
