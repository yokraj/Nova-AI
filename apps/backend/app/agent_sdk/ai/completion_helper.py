"""CompletionHelper wrapping general text completion and generation utilities.
"""

from typing import Optional

from app.ai.gateway.ai_gateway import AIGateway
from app.agent_sdk.ai.chat_helper import ChatHelper


class CompletionHelper:
    """Helper wrapping standard text generation, summarisation, and translation prompts."""

    def __init__(self, gateway: AIGateway) -> None:
        """Initializes CompletionHelper.

        Args:
            gateway: Active AIGateway instance.
        """
        self.gateway = gateway
        self._chat_helper = ChatHelper(gateway)

    async def complete(self, prompt: str, model: Optional[str] = None) -> str:
        """Executes general text completion for a prompt.

        Args:
            prompt: User input prompt.
            model: Optional model override.

        Returns:
            Completion response text.
        """
        return await self._chat_helper.chat(prompt, model=model)

    async def summarize(self, text: str, max_length: int = 150, model: Optional[str] = None) -> str:
        """Summarizes a long block of text.

        Args:
            text: Text to summarize.
            max_length: Target maximum output character length.
            model: Optional model override.

        Returns:
            Summarized output.
        """
        prompt = f"Summarize the following text in under {max_length} characters:\n\n{text}"
        return await self._chat_helper.chat(prompt, model=model)

    async def rewrite(self, text: str, tone: str = "professional", model: Optional[str] = None) -> str:
        """Rewrites a text block to sound more in line with a target tone.

        Args:
            text: Text to rewrite.
            tone: Target style or tone description (e.g. 'professional', 'casual').
            model: Optional model override.

        Returns:
            Rewritten output.
        """
        prompt = f"Rewrite this text to sound more {tone}:\n\n{text}"
        return await self._chat_helper.chat(prompt, model=model)

    async def explain(self, topic: str, target_audience: str = "5 year old", model: Optional[str] = None) -> str:
        """Explains a topic tailored to a target audience group.

        Args:
            topic: Topic description to explain.
            target_audience: Persona/audience target definition.
            model: Optional model override.

        Returns:
            Explanation output.
        """
        prompt = f"Explain '{topic}' like I am a {target_audience}."
        return await self._chat_helper.chat(prompt, model=model)

    async def translate(self, text: str, target_lang: str = "English", model: Optional[str] = None) -> str:
        """Translates text content into a target language.

        Args:
            text: Text block to translate.
            target_lang: Name of target language.
            model: Optional model override.

        Returns:
            Translated output.
        """
        prompt = f"Translate the following text into {target_lang}. Respond ONLY with the translation:\n\n{text}"
        return await self._chat_helper.chat(prompt, model=model)
