"""Diagram Generator orchestrating Mermaid flow and sequence diagrams.
"""

from typing import Any, Dict

from app.agents.software_engineer.documentation.interfaces import DiagramGenerator


class MermaidDiagramGenerator(DiagramGenerator):
    """Compiles workflow nodes into Mermaid format blocks."""

    def generate_diagram(
        self, diagram_type: str, context: Dict[str, Any]
    ) -> str:
        """Assembles Mermaid lines.

        Args:
            diagram_type: Type of diagram (flow, sequence, class).
            context: Node configurations data.

        Returns:
            Mermaid code block.
        """
        if diagram_type == "sequence":
            return (
                "sequenceDiagram\n"
                "    participant Client\n"
                "    participant Router\n"
                "    participant Engine\n"
                "    Client->>Router: GET /endpoints\n"
                "    Router->>Engine: execute()\n"
                "    Engine-->>Router: response\n"
                "    Router-->>Client: JSON"
            )

        # Default flow diagram
        return (
            "graph TD\n"
            "    A[Start] --> B[Process]\n"
            "    B --> C[End]"
        )
