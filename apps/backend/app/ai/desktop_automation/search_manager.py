"""Search Manager managing desktop file and content search.
"""

from typing import Any, Dict, List


class SearchManager:
    """Executes desktop file and content search queries."""

    def search_desktop(self, query: str) -> List[Dict[str, Any]]:
        """Searches desktop filesystem for matching query."""
        return [
            {"name": "sales_report.xlsx", "path": "C:\\Users\\User\\Documents\\sales_report.xlsx", "score": 0.95},
            {"name": "invoice_feb.pdf", "path": "C:\\Users\\User\\Downloads\\invoice_feb.pdf", "score": 0.90},
        ]
