"""Model Selector selects and ranks model choices dynamically.
"""

from typing import List
from app.ai.router.models import RoutingRequest, RoutingDecision, TaskType


class ModelSelector:
    """Selects the best available local AI model based on capability priority mappings."""

    def select_best_model(self, request: RoutingRequest) -> RoutingDecision:
        """Returns the primary model and a structured fallback chain based on task type."""
        t_type = request.task_type

        # Defaults
        selected_model = "qwen3:8b"
        provider = "ollama"
        reason = "Selected Qwen3:8B primary reasoning model."
        fallback_chain = ["deepseek-coder:6.7b", "qwen2.5-vl:7b"]

        if t_type in (TaskType.CODE_GENERATION, TaskType.DEBUGGING, TaskType.REFACTORING):
            selected_model = "deepseek-coder:6.7b"
            reason = "Selected DeepSeek Coder for software engineering workloads."
            fallback_chain = ["qwen3:8b", "qwen2.5-coder"]
        elif t_type in (TaskType.PLANNING, TaskType.RESEARCH, TaskType.GENERAL_CHAT, TaskType.SUMMARIZATION):
            selected_model = "qwen3:8b"
            reason = "Selected Qwen3 8B Instruct model for complex reasoning and synthesis."
            fallback_chain = ["deepseek-coder:6.7b", "qwen2.5:7b-instruct"]
        elif t_type == TaskType.EMBEDDING:
            selected_model = "bge-large-en-v1.5"
            provider = "bge_embedding"
            reason = "Selected BGE Large model for dense vector embeddings."
            fallback_chain = ["nomic-embed-text"]
        elif t_type == TaskType.VISION:
            selected_model = "qwen2.5-vl:7b"
            reason = "Selected Qwen2.5-VL vision-language model."
            fallback_chain = ["qwen2.5-vl"]
        elif t_type == TaskType.SPEECH_TO_TEXT:
            selected_model = "whisper-large-v3"
            provider = "whisper"
            reason = "Selected Whisper Large v3 for speech recognition."
            fallback_chain = []
        elif t_type == TaskType.TEXT_TO_SPEECH:
            selected_model = "piper-en-tts"
            provider = "piper"
            reason = "Selected Piper TTS for low-latency voice synthesis."
            fallback_chain = []

        return RoutingDecision(
            selected_model=selected_model,
            provider=provider,
            reason=reason,
            fallback_chain=fallback_chain,
        )
