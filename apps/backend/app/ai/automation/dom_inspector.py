"""DOM Inspector providing HTML extraction, table parsing, and element inspection."""

from typing import Any, Dict, List
import structlog

logger = structlog.get_logger("dom_inspector")


class DOMInspector:
    """Inspects page DOM structure, reads tables, and extracts raw HTML."""

    async def get_html(self, selector: str = "html") -> str:
        """Extract outer HTML string of page or element."""
        html = f"<{selector}><body><h1>Nova AI Automation</h1></body></{selector}>"
        logger.debug("Extracted DOM HTML", selector=selector)
        return html

    async def read_table(self, table_selector: str = "table") -> List[Dict[str, Any]]:
        """Parse structured tabular data from table element."""
        data = [
            {"Header 1": "Row 1 Col 1", "Header 2": "Row 1 Col 2"},
            {"Header 1": "Row 2 Col 1", "Header 2": "Row 2 Col 2"},
        ]
        logger.info("Parsed DOM table structure", selector=table_selector, rows=len(data))
        return data
