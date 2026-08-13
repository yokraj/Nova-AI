"""Prompt Builder Module.

Generates structured LLM prompts strictly separating System Prompt, Retrieved Context,
Conversation History, Current Request, and Factual Grounding Instructions.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class PromptBuilder:
    """Enterprise Grounded Prompt Assembly Engine."""

    def __init__(self) -> None:
        logger.info("prompt_builder_initialized")

    def build_grounded_prompt(
        self,
        query: str,
        context_text: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Constructs a clean, multi-section grounded prompt for Nova AI execution."""
        default_system = (
            "You are Nova AI Operating System's Grounded RAG Intelligence Engine.\n"
            "You answer user requests strictly using the provided grounding context.\n"
            "Rules:\n"
            "1. Base your answer ONLY on the provided context.\n"
            "2. If the context does not contain sufficient facts to answer, explicitly state your uncertainty.\n"
            "3. Do NOT fabricate or invent facts outside the context.\n"
            "4. Include source references using [Source ID] when stating facts."
        )

        sys_prompt = system_instruction or default_system

        prompt = (
            f"=== SYSTEM INSTRUCTION ===\n{sys_prompt}\n\n"
            f"=== GROUNDING CONTEXT ===\n{context_text}\n\n"
            f"=== CURRENT USER REQUEST ===\n{query}\n\n"
            f"=== GROUNDED ANSWER ==="
        )

        logger.info("grounded_prompt_assembled", prompt_len=len(prompt))
        return prompt
