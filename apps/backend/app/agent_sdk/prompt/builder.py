"""PromptBuilder merging chat history, memory, context, and voice variables.
"""

from typing import Any, Dict, List

from app.agent_sdk.prompt.prompt import Prompt
from app.agent_sdk.prompt.renderer import PromptRenderer


class PromptBuilder:
    """Combines and merges system instructions, history, memory, and voice modes context."""

    def build(self, prompt: Prompt, variables: Dict[str, Any]) -> Dict[str, str]:
        """Renders system_prompt and user_prompt using template variables.

        Args:
            prompt: Prompt definition.
            variables: Runtime variables map.

        Returns:
            Dict containing rendered 'system' and 'user' prompt strings.
        """
        renderer = PromptRenderer()
        rendered_system = renderer.render(prompt.system_prompt, variables)
        rendered_user = renderer.render(prompt.user_prompt, variables)
        return {"system": rendered_system, "user": rendered_user}

    def merge_system_prompt(self, base_system: str, custom_system: str) -> str:
        """Combines base instructions with custom execution instructions.

        Args:
            base_system: Default system instruction.
            custom_system: Custom instructions override/addition.

        Returns:
            Merged system prompt text.
        """
        return f"{base_system}\n\nAdditional Instructions:\n{custom_system}"

    def merge_history(self, prompt_text: str, history: List[Dict[str, str]]) -> str:
        """Appends formatted conversation history to the prompt text.

        Args:
            prompt_text: Target user prompt text.
            history: List of dialog turn dictionaries.

        Returns:
            User prompt text combined with history.
        """
        history_blocks = []
        for turn in history:
            role = turn.get("role", "user").capitalize()
            content = turn.get("content", "")
            history_blocks.append(f"{role}: {content}")
        history_str = "\n".join(history_blocks)
        return f"{prompt_text}\n\nConversation History:\n{history_str}"

    def merge_memory(self, prompt_text: str, memories: List[str]) -> str:
        """Appends long-term memory facts to the prompt text.

        Args:
            prompt_text: Target user prompt text.
            memories: List of string memory facts.

        Returns:
            User prompt text combined with memory logs.
        """
        mem_str = "\n".join([f"- {m}" for m in memories])
        return f"{prompt_text}\n\nRelevant Memories:\n{mem_str}"

    def merge_context(self, prompt_text: str, context: Dict[str, Any]) -> str:
        """Appends application run contexts details to the prompt text.

        Args:
            prompt_text: Target user prompt text.
            context: Dict of runtime context variables.

        Returns:
            User prompt text combined with context listings.
        """
        ctx_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
        return f"{prompt_text}\n\nRuntime Context:\n{ctx_str}"

    def build_voice_prompt(self, voice_context: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """Constructs a voice interaction prompt mapping speed, wake word, and screen contexts.

        Args:
            voice_context: Dict detailing voice configuration constraints.
            variables: Runtime variables.

        Returns:
            Rendered voice prompt string.
        """
        wake_word = voice_context.get("wake_word", "Nova")
        speed = voice_context.get("speech_speed", "1.0")
        app = voice_context.get("active_application", "none")
        summary = voice_context.get("conversation_summary", "")

        return (
            f"Voice Mode Active. Wake word: '{wake_word}'. Speed factor: {speed}.\n"
            f"Active App: {app}.\n"
            f"Context Summary: {summary}.\n"
            f"User input variables: {str(variables)}"
        )

    def build_chat_prompt(self, messages: List[Dict[str, str]], variables: Dict[str, Any]) -> List[Dict[str, str]]:
        """Injects rendered prompt content variables into a chat messages list.

        Args:
            messages: List of turns dicts.
            variables: Mapped variables.

        Returns:
            Messages list with resolved variable values.
        """
        renderer = PromptRenderer()
        resolved = []
        for msg in messages:
            content = msg.get("content", "")
            rendered_content = renderer.render(content, variables)
            resolved.append({"role": msg.get("role", "user"), "content": rendered_content})
        return resolved
