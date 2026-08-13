"""PDF Renderer formatting documentation sections into PDF binary bytes strings.
"""

from app.agents.software_engineer.documentation.interfaces import Renderer


class TechnicalPDFRenderer(Renderer):
    """Compiles technical layouts to PDF format bytes."""

    def render_to_html(self, markdown_text: str) -> str:
        """Formats layout into HTML.

        Args:
            markdown_text: Raw markdown.

        Returns:
            HTML string.
        """
        return f"<html><body>{markdown_text}</body></html>"

    def render_to_pdf(self, markdown_text: str) -> bytes:
        """Compiles technical layout to PDF mock binary bytes representation.

        Args:
            markdown_text: Raw markdown.

        Returns:
            Mock PDF binary data bytes.
        """
        # Synthesize standard PDF skeleton bytes
        pdf_header = b"%PDF-1.4\n"
        pdf_body = f"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n".encode("utf-8")
        pdf_metadata = f"% Mock PDF representation of markdown:\n% {markdown_text[:100]}\n".encode("utf-8")
        pdf_eof = b"%%EOF"

        return pdf_header + pdf_body + pdf_metadata + pdf_eof
