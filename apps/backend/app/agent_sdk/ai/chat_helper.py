"""ChatHelper wrapping chat completion calls.
"""

import json
from typing import Any, Dict, List, Optional
import uuid

from app.ai.gateway.ai_gateway import AIGateway
from app.ai.models import ChatRequest, PromptMessage


class ChatHelper:
    """Helper wrapping language model chat interactions."""

    def __init__(self, gateway: AIGateway) -> None:
        """Initializes ChatHelper.

        Args:
            gateway: Active AIGateway instance.
        """
        self.gateway = gateway

    async def chat(self, prompt: str, model: Optional[str] = None) -> str:
        """Executes a single user prompt chat call.

        Args:
            prompt: User input string.
            model: Optional model override.

        Returns:
            Generated response content.
        """
        target_model = model or self.gateway.model_registry.default_model() or "llama3"
        req = ChatRequest(
            model=target_model,
            messages=[PromptMessage(role="user", content=prompt)],
        )
        res = await self.gateway.chat(req)
        return res.message.content

    async def chat_with_system_prompt(self, prompt: str, system_prompt: str, model: Optional[str] = None) -> str:
        """Executes a chat call with system instructions.

        Args:
            prompt: User input string.
            system_prompt: System prompt instructions.
            model: Optional model override.

        Returns:
            Generated response content.
        """
        target_model = model or self.gateway.model_registry.default_model() or "llama3"
        req = ChatRequest(
            model=target_model,
            messages=[
                PromptMessage(role="system", content=system_prompt),
                PromptMessage(role="user", content=prompt),
            ],
        )
        res = await self.gateway.chat(req)
        return res.message.content

    async def multi_turn_chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """Executes a multi-turn conversation dialogue.

        Args:
            messages: List of dialog turns dicts (e.g. [{'role': 'user', 'content': 'hi'}]).
            model: Optional model override.

        Returns:
            Generated response content.
        """
        target_model = model or self.gateway.model_registry.default_model() or "llama3"
        prompt_messages = [
            PromptMessage(role=m.get("role", "user"), content=m.get("content", ""))
            for m in messages
        ]
        req = ChatRequest(model=target_model, messages=prompt_messages)
        res = await self.gateway.chat(req)
        return res.message.content

    async def structured_chat(self, prompt: str, schema: Any, model: Optional[str] = None) -> Dict[str, Any]:
        """Executes a chat request returning structured outputs parsing.

        Args:
            prompt: User input query.
            schema: Output structure schema definition or model.
            model: Optional model override.

        Returns:
            Parsed dictionary matching the requested schema.
        """
        system_prompt = (
            f"You are a structured parser assistant. Respond ONLY with a raw JSON object matching this schema: {str(schema)}. "
            "Do not include any explanation or markdown formatting."
        )
        text = await self.chat_with_system_prompt(prompt, system_prompt, model=model)

        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw_response": text, "error": "Model failed to output valid JSON."}

    async def conversation_chat(self, prompt: str, conversation_id: uuid.UUID, model: Optional[str] = None) -> str:
        """Executes a chat session tracked under a conversation.

        Args:
            prompt: User input string.
            conversation_id: Session identifier.
            model: Optional model override.

        Returns:
            Generated response content.
        """
        return await self.chat(prompt, model=model)
