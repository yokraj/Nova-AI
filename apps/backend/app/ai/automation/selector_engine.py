"""Selector Engine resolving CSS, XPath, text, and role selectors."""

import structlog

logger = structlog.get_logger("selector_engine")


class SelectorEngine:
    """Resolves and normalizes element selectors across CSS, XPath, text, and ARIA roles."""

    def resolve_selector(self, selector: str) -> str:
        """Resolve selector format."""
        if selector.startswith("//") or selector.startswith("("):
            return f"xpath={selector}"
        elif selector.startswith("text="):
            return selector
        return selector
