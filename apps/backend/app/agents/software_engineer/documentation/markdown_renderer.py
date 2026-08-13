"""Markdown Renderer rendering documentation sections into unified text.
"""


class TechnicalMarkdownRenderer:
    """Renders formatted technical reports layouts."""

    def render_markdown(self, sections: dict) -> str:
        """Formats headers and body blocks.

        Args:
            sections: Dictionary of section keys to content values.

        Returns:
            Markdown formatted string.
        """
        lines = []
        for header, body in sections.items():
            lines.append(f"# {header}\n\n{body}\n")
        return "\n".join(lines)
