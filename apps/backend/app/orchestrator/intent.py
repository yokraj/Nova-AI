"""Intent classification enums and models.
"""

from enum import Enum
from typing import Optional
from app.ai.gateway.ai_gateway import AIGateway
from app.ai.models import ChatRequest, PromptMessage


class IntentType(str, Enum):
    """Enumeration of prompt intent categories."""

    CHAT = "CHAT"
    CODE = "CODE"
    SEARCH = "SEARCH"
    BROWSER = "BROWSER"
    DESKTOP = "DESKTOP"
    VOICE = "VOICE"
    VISION = "VISION"
    WORKFLOW = "WORKFLOW"
    UNKNOWN = "UNKNOWN"


class IntentClassifier:
    """Classifies user prompts into intents using the AIGateway."""

    def __init__(self, gateway: AIGateway) -> None:
        """Initializes IntentClassifier.

        Args:
            gateway: Active AIGateway.
        """
        self.gateway = gateway

    async def classify(self, prompt: str) -> IntentType:
        """Analyzes prompt string returning target IntentType.

        Args:
            prompt: User input string.

        Returns:
            The classified IntentType.
        """
        prompt_lower = prompt.lower()
        if "code" in prompt_lower or "python" in prompt_lower or "program" in prompt_lower:
            return IntentType.CODE
        if "search" in prompt_lower or "google" in prompt_lower or "find" in prompt_lower:
            return IntentType.SEARCH
        if "browser" in prompt_lower or "web" in prompt_lower or "navigate" in prompt_lower:
            return IntentType.BROWSER
        if "desktop" in prompt_lower or "window" in prompt_lower or "folder" in prompt_lower:
            return IntentType.DESKTOP
        if "voice" in prompt_lower or "speak" in prompt_lower or "audio" in prompt_lower:
            return IntentType.VOICE
        if "vision" in prompt_lower or "image" in prompt_lower or "picture" in prompt_lower:
            return IntentType.VISION
        if "workflow" in prompt_lower or "pipeline" in prompt_lower or "automate" in prompt_lower:
            return IntentType.WORKFLOW
        if "chat" in prompt_lower or "hello" in prompt_lower or "hi" in prompt_lower:
            return IntentType.CHAT

        try:
            request = ChatRequest(
                model="llama3",
                messages=[
                    PromptMessage(
                        role="system",
                        content=(
                            "Classify user prompt into one of these intents: "
                            "CHAT, CODE, SEARCH, BROWSER, DESKTOP, VOICE, VISION, WORKFLOW, UNKNOWN. "
                            "Respond only with the intent name."
                        ),
                    ),
                    PromptMessage(role="user", content=prompt),
                ],
            )
            response = await self.gateway.chat(request)
            intent_str = response.message.content.strip().upper()
            try:
                return IntentType(intent_str)
            except ValueError:
                return IntentType.UNKNOWN
        except Exception:
            return IntentType.UNKNOWN


    async def confidence(self, prompt: str) -> float:
        """Returns intent classification confidence score.

        Args:
            prompt: User input string.

        Returns:
            Float confidence score between 0.0 and 1.0.
        """
        prompt_lower = prompt.lower()
        keywords = [
            "code",
            "python",
            "search",
            "google",
            "browser",
            "web",
            "desktop",
            "voice",
            "vision",
            "workflow",
            "chat",
            "hello",
        ]
        if any(kw in prompt_lower for kw in keywords):
            return 0.95
        return 0.70
