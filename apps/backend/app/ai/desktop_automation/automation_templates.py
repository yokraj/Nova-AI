"""Automation Templates providing built-in automation blueprints for invoices, ERP, sales, devops.
"""

from typing import Any, Dict, List


class AutomationTemplates:
    """Provides built-in automation templates (Invoice processing, Sales reports -> PPT, Project setup, Docker WSL setup)."""

    def list_templates(self) -> List[Dict[str, Any]]:
        """Returns list of built-in automation templates."""
        return [
            {
                "template_id": "tmpl_sales_ppt",
                "title": "Excel Sales Data -> PowerPoint Presentation",
                "description": "Reads sales report from Excel, creates formatted charts, and generates PowerPoint slide deck.",
            },
            {
                "template_id": "tmpl_dev_setup",
                "title": "Full Developer Environment Setup",
                "description": "Configures WSL2, Docker Desktop, clones git repo, opens VS Code, and runs dev server.",
            },
            {
                "template_id": "tmpl_organize_downloads",
                "title": "Downloads Folder Smart Organization",
                "description": "Categorizes files in Downloads into Documents, Images, Executables, and Archives.",
            },
        ]
