"""LLM Runtime executing text generation, reasoning, coding, and tool calling via LocalModelRouter and OllamaProvider.
"""

import threading
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.ai.kernel.model_router import CognitiveWorkloadType, LocalModelRouter, RoutingConstraints
from app.ai.models.models import GenerationRequest
from app.ai.models.providers.ollama_provider import OllamaProvider
from app.ai.runtime.interfaces import ILLMRuntime
from app.ai.runtime.models import DeviceType, RuntimeRequest, RuntimeResponse


class LLMRuntime(ILLMRuntime):
    """LLM execution runtime connecting to LocalModelRouter and local Ollama provider."""

    _instance: Optional["LLMRuntime"] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "LLMRuntime":
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(
        self,
        ollama_provider: Optional[OllamaProvider] = None,
        router: Optional[LocalModelRouter] = None,
    ) -> None:
        self.provider = ollama_provider or OllamaProvider()
        self.router = router or LocalModelRouter.get_instance()

    def _infer_workload_type(self, prompt: str) -> CognitiveWorkloadType:
        """Infers CognitiveWorkloadType from prompt content."""
        p = prompt.lower()
        if "code" in p or "def " in p or "import " in p or "script" in p:
            return CognitiveWorkloadType.CODE_GENERATION
        elif "plan" in p or "dag" in p or "decompose" in p:
            return CognitiveWorkloadType.PLANNING
        elif "tool" in p or "capability" in p or "schema" in p:
            return CognitiveWorkloadType.TOOL_SELECTION
        elif "verify" in p or "critique" in p or "check" in p:
            return CognitiveWorkloadType.VERIFICATION_CRITIQUE
        elif "recover" in p or "retry" in p or "error" in p:
            return CognitiveWorkloadType.RECOVERY_REPLANNING
        elif "summary" in p or "compress" in p:
            return CognitiveWorkloadType.CONTEXT_COMPRESSION
        return CognitiveWorkloadType.REASONING

    async def generate(self, request: RuntimeRequest) -> RuntimeResponse:
        """Executes text/code/reasoning generation request via routed local model."""
        start_t = time.time()
        workload = self._infer_workload_type(request.prompt)

        constraints = RoutingConstraints(
            preferred_model_id=request.model_id,
            require_structured_output=False,
        )

        routing_decision = await self.router.route_workload(workload, constraints)
        target_model_id = routing_decision.selected_model_id

        gen_req = GenerationRequest(
            prompt=request.prompt,
            model_id=target_model_id,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        res = await self.provider.generate(gen_req)
        latency_ms = round((time.time() - start_t) * 1000.0, 2)

        return RuntimeResponse(
            model_id=res.model_id or target_model_id,
            text_or_data=res.text,
            finish_reason="stop",
            token_usage={
                "prompt_tokens": res.token_usage.prompt_tokens,
                "completion_tokens": res.token_usage.completion_tokens,
                "total_tokens": res.token_usage.total_tokens,
            },
            latency_ms=latency_ms,
            device_used=DeviceType.CUDA,
        )

    async def generate_stream(self, request: RuntimeRequest) -> AsyncGenerator[str, None]:
        """Streams text chunks from routed OllamaProvider."""
        workload = self._infer_workload_type(request.prompt)
        constraints = RoutingConstraints(preferred_model_id=request.model_id)
        routing_decision = await self.router.route_workload(workload, constraints)
        target_model_id = routing_decision.selected_model_id

        gen_req = GenerationRequest(
            prompt=request.prompt,
            model_id=target_model_id,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        async for chunk in self.provider.generate_stream(gen_req):
            yield chunk
