"""Template Engine rendering parameters into template strings.
"""

from typing import Any, Dict

from app.agents.software_engineer.documentation.interfaces import TemplateEngine
from app.agents.software_engineer.documentation.utils import simple_interpolate


class WorkspaceTemplateEngine(TemplateEngine):
    """Fills placeholders in templates layouts."""

    def __init__(self) -> None:
        self.templates = {
            "readme": "# {{project_name}}\n\n{{description}}\n\nInstallation:\n{{install_steps}}",
            "api": "### API Route: {{endpoint}} ({{method}})\n\nDescription: {{description}}",
        }

    def render_template(
        self, template_name: str, parameters: Dict[str, Any]
    ) -> str:
        """Interpolates layout parameters.

        Args:
            template_name: The name of the template.
            parameters: Dict containing key value matches.

        Returns:
            Rendered document content.
        """
        tpl = self.templates.get(template_name, "# Documentation\n\n{{description}}")
        return simple_interpolate(tpl, parameters)
