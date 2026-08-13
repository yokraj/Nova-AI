"""Shared prompt builder logic for compiling specialized agent prompts.
"""

from typing import Dict, Any, List

class PromptBuilder:
    """Builds system message instructions including domain-specific guidelines."""

    def __init__(self, specialty: str, instructions: List[str]) -> None:
        self.specialty = specialty
        self.instructions = instructions

    def build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Returns standard compiled prompt block."""
        guidelines = "\n".join(f"- {instruction}" for instruction in self.instructions)
        return (
            f"You are the specialized {self.specialty} Agent for Nova AI.\n"
            f"Adhere strictly to Clean Architecture, DDD, SOLID, and offline-first principles.\n\n"
            f"Core Specialty Guidelines:\n{guidelines}\n\n"
            f"Active Context parameters:\n{context}\n\n"
            f"Execute the requested action, outputting structured templates or summaries."
        )
