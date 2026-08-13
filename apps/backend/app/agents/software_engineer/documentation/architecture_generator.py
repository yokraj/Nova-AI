"""Architecture Generator generating component diagrams describing structural links.
"""

import os
from app.agents.software_engineer.documentation.interfaces import ArchitectureGenerator
from app.agents.software_engineer.documentation.models import ArchitectureDocument


class SystemArchitectureGenerator(ArchitectureGenerator):
    """Maps high level architecture modules directories relationships."""

    def generate_architecture(
        self, workspace_path: str
    ) -> ArchitectureDocument:
        """Walks folders mapping top-level directories.

        Args:
            workspace_path: Workspace absolute path root.

        Returns:
            ArchitectureDocument.
        """
        components = []
        app_dir = os.path.join(workspace_path, "app")
        if os.path.exists(app_dir):
            for entry in os.listdir(app_dir):
                if os.path.isdir(os.path.join(app_dir, entry)) and not entry.startswith("__"):
                    components.append(entry)

        if not components:
            components = ["core", "agents", "api"]

        # Synthesize Mermaid structural block
        diagram = (
            "graph TD\n"
            "    subgraph Workspace\n"
        )
        for comp in components:
            diagram += f"        {comp}[{comp} module]\n"
        diagram += (
            "        core --> agents\n"
            "        api --> agents\n"
            "    end"
        )

        return ArchitectureDocument(
            components=components,
            relationships={"app": components},
            mermaid_diagram=diagram,
        )
