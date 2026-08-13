"""Sequence Generator outputting call traces participant diagrams.
"""

from typing import List


class MermaidSequenceGenerator:
    """Produces Mermaid sequence diagrams code strings."""

    def generate_sequence(self, participants: List[str], steps: List[str]) -> str:
        """Assembles trace blocks.

        Args:
            participants: Component labels list.
            steps: Call actions descriptors.

        Returns:
            Mermaid sequence diagram.
        """
        lines = ["sequenceDiagram"]
        for p in participants:
            lines.append(f"    participant {p}")

        for step in steps:
            lines.append(f"    {step}")

        return "\n".join(lines)
