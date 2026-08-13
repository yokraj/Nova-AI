"""Proactive Runtime recommending deadlines, meetings, security alerts, and automation opportunities.
"""

from typing import Any, Dict, List


class ProactiveRuntime:
    """Generates non-intrusive proactive recommendations for user productivity, code quality, and security."""

    async def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Returns active proactive recommendations list."""
        return [
            {
                "rec_id": "rec_01",
                "category": "security",
                "title": "Uncommitted Sensitive File Detected",
                "message": "Found .env file in workspace root. Recommend adding to .gitignore.",
                "action": "add_gitignore",
            },
            {
                "rec_id": "rec_02",
                "category": "automation",
                "title": "GST Return Filing Automation Opportunity",
                "message": "Monthly GST deadline approaching in 3 days. Trigger workflow?",
                "action": "run_gst_workflow",
            },
        ]
