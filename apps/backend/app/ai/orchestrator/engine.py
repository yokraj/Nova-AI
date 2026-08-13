"""Central UniversalAIOrchestratorEngine facade providing single-source-of-truth APIs for Nova AI Operating System.
"""

from typing import Any, AsyncGenerator, List, Optional
from app.ai.orchestrator.interfaces import IUniversalAIOrchestratorEngine
from app.ai.orchestrator.manager import UniversalAIOrchestratorManager
from app.ai.orchestrator.models import (
    ModelCategory,
    OrchestratorHealth,
    OrchestratorRequest,
    OrchestratorResponse,
    StreamTokenChunk,
)


class UniversalAIOrchestratorEngine(IUniversalAIOrchestratorEngine):
    """Central AI Operating System Brain facade. Every AI subsystem communicates ONLY through this orchestrator."""

    _instance: Optional["UniversalAIOrchestratorEngine"] = None

    def __new__(cls, manager: Optional[UniversalAIOrchestratorManager] = None) -> "UniversalAIOrchestratorEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.manager = manager or UniversalAIOrchestratorManager()
        elif manager is not None:
            cls._instance.manager = manager
        return cls._instance

    async def chat(self, prompt: str, **kwargs: Any) -> OrchestratorResponse:
        req = OrchestratorRequest(
            prompt=prompt,
            category=ModelCategory.CONVERSATION,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
            stream=kwargs.get("stream", False),
        )
        return await self.manager.execute_request(req)

    async def reason(self, prompt: str, **kwargs: Any) -> OrchestratorResponse:
        req = OrchestratorRequest(
            prompt=prompt,
            category=ModelCategory.REASONING,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
        )
        return await self.manager.execute_request(req)

    async def code(self, prompt: str, **kwargs: Any) -> OrchestratorResponse:
        req = OrchestratorRequest(
            prompt=prompt,
            category=ModelCategory.CODING,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
        )
        return await self.manager.execute_request(req)

    async def vision(self, image_path_or_bytes: Any, prompt: str = "", **kwargs: Any) -> OrchestratorResponse:
        req = OrchestratorRequest(
            prompt=prompt or "Analyze visual elements",
            category=ModelCategory.VISION,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
            inputs={"image": image_path_or_bytes},
        )
        return await self.manager.execute_request(req)

    async def transcribe(self, audio_bytes_or_path: Any, **kwargs: Any) -> OrchestratorResponse:
        req = OrchestratorRequest(
            prompt="Transcribe speech input",
            category=ModelCategory.SPEECH,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
            inputs={"audio": audio_bytes_or_path},
        )
        return await self.manager.execute_request(req)

    async def tts(self, text: str, **kwargs: Any) -> OrchestratorResponse:
        req = OrchestratorRequest(
            prompt=text,
            category=ModelCategory.TTS,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
        )
        return await self.manager.execute_request(req)

    async def embed(self, texts: List[str], **kwargs: Any) -> OrchestratorResponse:
        req = OrchestratorRequest(
            prompt=texts[0] if texts else "",
            category=ModelCategory.EMBEDDING,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
            inputs={"texts": texts},
        )
        return await self.manager.execute_request(req)

    async def translate(self, text: str, target_lang: str = "en", **kwargs: Any) -> OrchestratorResponse:
        req = OrchestratorRequest(
            prompt=f"Translate to {target_lang}: {text}",
            category=ModelCategory.TRANSLATION,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
            inputs={"target_lang": target_lang},
        )
        return await self.manager.execute_request(req)

    async def ocr(self, image_bytes_or_path: Any, **kwargs: Any) -> OrchestratorResponse:
        req = OrchestratorRequest(
            prompt="Extract screen document text",
            category=ModelCategory.OCR,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
            inputs={"image": image_bytes_or_path},
        )
        return await self.manager.execute_request(req)

    async def plan(self, goal: str, **kwargs: Any) -> OrchestratorResponse:
        req = OrchestratorRequest(
            prompt=goal,
            category=ModelCategory.PLANNING,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
        )
        return await self.manager.execute_request(req)

    async def summarize(self, text: str, **kwargs: Any) -> OrchestratorResponse:
        req = OrchestratorRequest(
            prompt=f"Summarize text content: {text}",
            category=ModelCategory.REASONING,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
        )
        return await self.manager.execute_request(req)

    async def analyze(self, data: Any, **kwargs: Any) -> OrchestratorResponse:
        req = OrchestratorRequest(
            prompt=str(data),
            category=ModelCategory.RESEARCH,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
        )
        return await self.manager.execute_request(req)

    async def stream(self, prompt: str, **kwargs: Any) -> AsyncGenerator[StreamTokenChunk, None]:
        req = OrchestratorRequest(
            prompt=prompt,
            category=ModelCategory.CONVERSATION,
            model_override=kwargs.get("model_id") or kwargs.get("model"),
            stream=True,
        )
        async for chunk in self.manager.execute_stream(req):
            yield chunk

    def health_check(self) -> OrchestratorHealth:
        return self.manager.health_monitor.check_health()
