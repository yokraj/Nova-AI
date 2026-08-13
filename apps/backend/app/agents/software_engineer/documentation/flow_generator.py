"""Flow Generator outputting standard flow chart nodes.
"""

from typing import List


class MermaidFlowGenerator:
    """Produces Mermaid flow diagrams code strings."""

    def generate_flow(self, nodes: List[str], connections: List[str]) -> str:
        """Assembles connections layout.

        Args:
            nodes: Path nodes.
            connections: Directed lines.

        Returns:
            Mermaid flow diagram.
        """
        lines = ["graph TD"]
        for node in nodes:
            lines.append(f"    {node}")

        for conn in connections:
            lines.append(f"    {conn}")

        return "\n".join(lines)
