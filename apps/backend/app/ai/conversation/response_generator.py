"""Response Generator producing tailored text and voice-optimized responses via UniversalAIRuntimeEngine.
"""

from typing import Any, Dict, Optional
from app.ai.conversation.models import EmotionMetadata, PersonalityMetadata
from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine


class ResponseGenerator:
    """Generates conversational responses by calling UniversalAIRuntimeEngine.chat()."""

    def __init__(self, runtime_engine: Optional[UniversalAIRuntimeEngine] = None) -> None:
        self.runtime = runtime_engine or UniversalAIRuntimeEngine()

    async def generate_response(self, prompt: str, emotion: EmotionMetadata, personality: PersonalityMetadata) -> str:
        """Generates conversational text response using real LLM runtime."""
        system_context = f"Tone: {personality.tone}. Emotion context: {emotion.primary_emotion}."
        full_prompt = f"{system_context}\nUser: {prompt}"

        res = await self.runtime.chat(prompt=full_prompt, model_id="qwen3:8b")
        if res and res.text_or_data:
            return res.text_or_data

        return f"I understand your request regarding '{prompt[:80]}'. As your {personality.name}, let's solve this together."
