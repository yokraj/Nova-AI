"""Citation Engine formatting APA, BibTeX, and Markdown citations.
"""

from app.ai.research.interfaces import ICitationEngine
from app.ai.research.models import CitationItem, KnowledgeSource


class CitationEngine(ICitationEngine):
    """Generates formatted reference citations in APA, BibTeX, or Markdown styles."""

    def generate_citation(self, source: KnowledgeSource, style: str = "APA") -> CitationItem:
        """Formats source into styled citation string.

        Args:
            source: KnowledgeSource payload.
            style: Citation style ("APA", "BibTeX", "Markdown").

        Returns:
            CitationItem model.
        """
        author = source.author or "Nova Research Engine"
        year = 2026
        title = source.title
        url = source.url_or_path

        if style.upper() == "BIBTEX":
            cite_str = f"@article{{{source.source_id}, author={{{author}}}, title={{{title}}}, year={{{year}}}, url={{{url}}}}}"
        elif style.upper() == "MARKDOWN":
            cite_str = f"[{title}]({url}) ({author}, {year})"
        else:
            # APA Default
            cite_str = f"{author} ({year}). {title}. Retrieved from {url}"

        return CitationItem(
            source_title=title,
            url_or_path=url,
            author=author,
            year=year,
            citation_string=cite_str,
        )
