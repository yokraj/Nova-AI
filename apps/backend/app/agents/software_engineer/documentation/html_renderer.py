"""HTML Renderer rendering markdown blocks to formatted web page documents.
"""


class TechnicalHTMLRenderer:
    """Renders HTML structures descriptions."""

    def render_html(self, title: str, markdown_text: str) -> str:
        """Surrounds markdown.

        Args:
            title: Web page title.
            markdown_text: Raw markdown content.

        Returns:
            HTML template string.
        """
        # Convert markdown headers to html elements (simple fallback parser)
        html_body = markdown_text.replace("\n", "<br>")
        return (
            f"<!DOCTYPE html>\n"
            f"<html>\n"
            f"<head>\n"
            f"  <title>{title}</title>\n"
            f"  <style>body{{font-family: sans-serif; padding: 20px; line-height: 1.6;}}</style>\n"
            f"</head>\n"
            f"<body>\n"
            f"  {html_body}\n"
            f"</body>\n"
            f"</html>"
        )
