"""Multi-Format Research Report Exporter for Phase 10L-D.

Handles exporting StructuredResearchReport models into professional Markdown,
responsive HTML5, and native PDF 1.4 documents with professional formatting,
typography, callouts, tables, citations, and provenance tracking.
"""

import html
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Union
import structlog

from app.ai.research.models import (
    ReportDetailLevel,
    ReportExportFormat,
    ReportExportResult,
    StructuredResearchReport,
)
from app.ai.research.pdf_writer import NativePDFWriter

logger = structlog.get_logger("report_exporter")


class ResearchReportExporter:
    """Exports structured research reports into Markdown, HTML, and PDF formats."""

    def __init__(self) -> None:
        pass

    # -------------------------------------------------------------------------
    # 1. Markdown Export
    # -------------------------------------------------------------------------

    def export_markdown(
        self,
        report: StructuredResearchReport,
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """Exports report as standard publication-grade Markdown."""
        md_content = report.to_markdown()
        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(md_content, encoding="utf-8")
            logger.info("Exported markdown report", path=str(p), size_bytes=len(md_content.encode("utf-8")))
        return md_content

    # -------------------------------------------------------------------------
    # 2. HTML Export
    # -------------------------------------------------------------------------

    def export_html(
        self,
        report: StructuredResearchReport,
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """Exports report as a standalone, styled, responsive HTML5 document."""
        title_esc = html.escape(report.title)
        q_esc = html.escape(report.research_question)
        conf_esc = html.escape(f"{report.overall_confidence.value} ({report.overall_confidence_score * 100:.1f}%)")
        model_esc = html.escape(f"{report.model_used} ({'Local Model' if report.is_local_model else 'Remote Model'})")

        html_lines = [
            "<!DOCTYPE html>",
            "<html lang=\"en\">",
            "<head>",
            "  <meta charset=\"UTF-8\">",
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
            f"  <title>{title_esc} - Nova-AI Research Report</title>",
            "  <style>",
            "    :root {",
            "      --primary: #143866; --secondary: #33598c; --text: #1f242b; --text-muted: #64748b;",
            "      --bg: #f8fafc; --card-bg: #ffffff; --border: #e2e8f0; --accent: #2563eb;",
            "      --fact-border: #16a34a; --fact-bg: #f0fdf4;",
            "      --inf-border: #0284c7; --inf-bg: #f0f9ff;",
            "      --contra-border: #d97706; --contra-bg: #fffbeb;",
            "      --unsupp-border: #dc2626; --unsupp-bg: #fef2f2;",
            "    }",
            "    * { box-sizing: border-box; margin: 0; padding: 0; }",
            "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;",
            "           line-height: 1.65; color: var(--text); background: var(--bg); padding: 2rem 1rem; }",
            "    .container { max-width: 900px; margin: 0 auto; background: var(--card-bg); padding: 3rem;",
            "                 border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid var(--border); }",
            "    header { border-bottom: 2px solid var(--border); padding-bottom: 1.5rem; margin-bottom: 2rem; }",
            "    h1 { color: var(--primary); font-size: 2rem; line-height: 1.25; margin-bottom: 0.5rem; }",
            "    .subtitle { color: var(--secondary); font-size: 1.1rem; font-weight: 500; margin-bottom: 1rem; }",
            "    .metadata-bar { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1rem; }",
            "    .badge { font-size: 0.8rem; padding: 0.25rem 0.65rem; border-radius: 9999px; background: var(--bg);",
            "             border: 1px solid var(--border); color: var(--text-muted); font-weight: 600; }",
            "    .badge-primary { background: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; }",
            "    .badge-success { background: #f0fdf4; color: #15803d; border-color: #bbf7d0; }",
            "    h2 { color: var(--primary); font-size: 1.35rem; margin-top: 2rem; margin-bottom: 0.75rem; border-bottom: 1px solid var(--border); padding-bottom: 0.35rem; }",
            "    h3 { color: var(--secondary); font-size: 1.1rem; margin-top: 1.25rem; margin-bottom: 0.5rem; }",
            "    p { margin-bottom: 1rem; text-align: justify; }",
            "    ul, ol { margin-left: 1.5rem; margin-bottom: 1rem; }",
            "    li { margin-bottom: 0.35rem; }",
            "    .card { padding: 1rem 1.25rem; border-radius: 6px; margin-bottom: 1rem; border-left: 4px solid; }",
            "    .card-fact { background: var(--fact-bg); border-color: var(--fact-border); }",
            "    .card-inf { background: var(--inf-bg); border-color: var(--inf-border); }",
            "    .card-contra { background: var(--contra-bg); border-color: var(--contra-border); }",
            "    .card-unsupp { background: var(--unsupp-bg); border-color: var(--unsupp-border); }",
            "    .card-title { font-weight: 700; font-size: 0.95rem; margin-bottom: 0.35rem; }",
            "    table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; font-size: 0.9rem; }",
            "    th { background: var(--primary); color: white; text-align: left; padding: 0.65rem 0.75rem; font-weight: 600; }",
            "    td { padding: 0.65rem 0.75rem; border-bottom: 1px solid var(--border); }",
            "    tr:nth-child(even) { background: var(--bg); }",
            "    .cite-link { color: var(--accent); text-decoration: none; font-weight: 600; padding: 0 2px; }",
            "    .cite-link:hover { text-decoration: underline; }",
            "    .reference-item { margin-bottom: 0.75rem; font-size: 0.9rem; padding-left: 1.75rem; text-indent: -1.75rem; }",
            "    footer { margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--border); font-size: 0.8rem; color: var(--text-muted); text-align: center; }",
            "    @media print {",
            "      body { background: white; padding: 0; }",
            "      .container { box-shadow: none; border: none; padding: 0; max-width: 100%; }",
            "      h2 { page-break-after: avoid; }",
            "      .card { page-break-inside: avoid; }",
            "      table { page-break-inside: avoid; }",
            "    }",
            "  </style>",
            "</head>",
            "<body>",
            "  <div class=\"container\">",
            "    <header>",
            f"      <h1>{title_esc}</h1>",
            f"      <div class=\"subtitle\">Inquiry: {q_esc}</div>",
            "      <div class=\"metadata-bar\">",
            f"        <span class=\"badge badge-primary\">Format: {report.detail_level.value.upper()}</span>",
            f"        <span class=\"badge badge-success\">Confidence: {conf_esc}</span>",
            f"        <span class=\"badge\">Model: {model_esc}</span>",
            f"        <span class=\"badge\">Report ID: {report.report_id}</span>",
            "      </div>",
            "    </header>",
            "",
            "    <section id=\"executive-summary\">",
            "      <h2>1. Executive Summary</h2>",
            f"      <p>{html.escape(report.executive_summary)}</p>",
            "    </section>",
        ]

        # 2. Objectives & Subtopics
        html_lines.extend([
            "    <section id=\"objectives\">",
            "      <h2>2. Research Objectives & Investigated Subtopics</h2>",
        ])
        if report.research_objectives:
            html_lines.append("      <h3>Primary Objectives:</h3><ul>")
            for obj in report.research_objectives:
                html_lines.append(f"        <li>{html.escape(obj)}</li>")
            html_lines.append("      </ul>")
        if report.subtopics:
            html_lines.append("      <h3>Target Subtopics:</h3><ul>")
            for st in report.subtopics:
                html_lines.append(f"        <li>{html.escape(st)}</li>")
            html_lines.append("      </ul>")
        html_lines.append("    </section>")

        # 3. Introduction & Background
        if report.introduction_and_background:
            html_lines.extend([
                "    <section id=\"background\">",
                "      <h2>3. Introduction & Background</h2>",
                f"      <p>{html.escape(report.introduction_and_background).replace(chr(10), '<br>')}</p>",
                "    </section>",
            ])

        # 4. Literature Review
        if report.literature_review:
            html_lines.extend([
                "    <section id=\"literature-review\">",
                "      <h2>4. Literature Review</h2>",
                f"      <p>{html.escape(report.literature_review).replace(chr(10), '<br>')}</p>",
                "    </section>",
            ])

        # 5. Methodology
        if report.methodology_and_source_selection:
            html_lines.extend([
                "    <section id=\"methodology\">",
                "      <h2>5. Methodology & Source Provenance</h2>",
                f"      <p>{html.escape(report.methodology_and_source_selection).replace(chr(10), '<br>')}</p>",
                "    </section>",
            ])

        # 6. Evidence-Backed Findings
        html_lines.extend([
            "    <section id=\"findings\">",
            "      <h2>6. Evidence-Backed Findings</h2>",
            f"      <p>{html.escape(report.evidence_backed_findings).replace(chr(10), '<br>')}</p>",
        ])

        if report.verified_facts:
            html_lines.extend([
                "      <h3>Verified Factual Claims</h3>",
                "      <table>",
                "        <thead><tr><th>Factual Assertion</th><th>Confidence</th><th>Citations</th><th>Sources</th></tr></thead>",
                "        <tbody>",
            ])
            for f in report.verified_facts:
                cites = " ".join(f"<a class=\"cite-link\" href=\"#ref-{k.strip('[]')}\">{k}</a>" for k in f.citation_keys) if f.citation_keys else "[N/A]"
                html_lines.append(
                    f"          <tr><td>{html.escape(f.statement)}</td>"
                    f"<td><span class=\"badge badge-success\">{f.confidence.value}</span></td>"
                    f"<td>{cites}</td>"
                    f"<td style=\"text-align:center;\">{f.independent_sources_count}</td></tr>"
                )
            html_lines.extend(["        </tbody>", "      </table>"])

        if report.derived_inferences:
            html_lines.append("      <h3>Derived Inferences & Theoretical Deductions</h3>")
            for inf in report.derived_inferences:
                cites = " ".join(f"<a class=\"cite-link\" href=\"#ref-{k.strip('[]')}\">{k}</a>" for k in inf.citation_keys) if inf.citation_keys else ""
                reason = html.escape(inf.hedging_rationale or "Derived inference")
                html_lines.append(
                    f"      <div class=\"card card-inf\">"
                    f"        <div class=\"card-title\">Inference {cites}</div>"
                    f"        <div>{html.escape(inf.statement)} <em>({reason})</em></div>"
                    f"      </div>"
                )

        html_lines.append("    </section>")

        # 7. Contradictions
        if report.contradictions or report.contradiction_analysis:
            html_lines.extend([
                "    <section id=\"contradictions\">",
                "      <h2>7. Contradiction & Disagreement Analysis</h2>",
                f"      <p>{html.escape(report.contradiction_analysis)}</p>",
            ])
            for c in report.contradictions:
                html_lines.append(
                    f"      <div class=\"card card-contra\">"
                    f"        <div class=\"card-title\">Conflict: {html.escape(c.topic_or_claim)} ({html.escape(c.nature_of_conflict)})</div>"
                    f"        <div><strong>Source A:</strong> {html.escape(c.source_a_summary)} <em>({html.escape(c.source_a_citation.get('title', ''))})</em></div>"
                    f"        <div><strong>Source B:</strong> {html.escape(c.source_b_summary)} <em>({html.escape(c.source_b_citation.get('title', ''))})</em></div>"
                    f"        <div style=\"margin-top:0.4rem; color:var(--text-muted); font-size:0.85rem;\"><strong>Synthesis:</strong> {html.escape(c.resolution_or_synthesis)}</div>"
                    f"      </div>"
                )
            html_lines.append("    </section>")

        # 8. Unsupported Claims (Segregated)
        if report.unsupported_claims:
            html_lines.extend([
                "    <section id=\"unsupported-claims\">",
                "      <h2>8. Unsupported Claims & Unverified Assumptions</h2>",
                "      <p style=\"color:var(--text-muted); font-style:italic;\">The following claims lacked passage evidence in the retrieved corpus and are strictly segregated from verified facts:</p>",
            ])
            for u in report.unsupported_claims:
                html_lines.append(
                    f"      <div class=\"card card-unsupp\">"
                    f"        <div class=\"card-title\">Unsupported Claim ({html.escape(u.epistemic_status.value)})</div>"
                    f"        <div>{html.escape(u.statement)}</div>"
                    f"      </div>"
                )
            html_lines.append("    </section>")

        # 9. Limitations & Gaps
        if report.limitations_and_knowledge_gaps:
            html_lines.extend([
                "    <section id=\"limitations\">",
                "      <h2>9. Research Limitations & Knowledge Gaps</h2><ul>",
            ])
            for gap in report.limitations_and_knowledge_gaps:
                html_lines.append(f"        <li>{html.escape(gap)}</li>")
            html_lines.extend(["      </ul></section>"])

        # 10. Discussion & Conclusion
        if report.discussion_and_conclusion:
            html_lines.extend([
                "    <section id=\"conclusion\">",
                "      <h2>10. Discussion & Conclusion</h2>",
                f"      <p>{html.escape(report.discussion_and_conclusion).replace(chr(10), '<br>')}</p>",
                "    </section>",
            ])

        # 11. Bibliography & Provenance
        if report.references:
            html_lines.extend([
                "    <section id=\"bibliography\">",
                "      <h2>11. References & Bibliography</h2>",
            ])
            for ref in report.references:
                num = ref.citation_number
                authors_str = html.escape(", ".join(ref.authors) if ref.authors else "Unknown Authors")
                year_str = f"({ref.publication_year})" if ref.publication_year else "(n.d.)"
                title_s = html.escape(ref.title)
                venue_s = f" <em>{html.escape(ref.venue)}</em>." if ref.venue else ""
                doi_link = f" DOI: <a href=\"https://doi.org/{html.escape(ref.doi)}\" target=\"_blank\">{html.escape(ref.doi)}</a>" if ref.doi else ""
                url_link = f" <a href=\"{html.escape(ref.canonical_url)}\" target=\"_blank\">[URL]</a>" if ref.canonical_url and not ref.doi else ""
                prov_s = f" <span style=\"color:var(--text-muted); font-size:0.8rem;\">[Providers: {', '.join(ref.contributing_providers)}]</span>" if ref.contributing_providers else ""

                html_lines.append(
                    f"      <div class=\"reference-item\" id=\"ref-{num}\">"
                    f"        <strong>[{num}]</strong> {authors_str} {year_str}. <strong>{title_s}</strong>.{venue_s}{doi_link}{url_link}{prov_s}"
                    f"      </div>"
                )
            html_lines.append("    </section>")

        html_lines.extend([
            "    <footer>",
            "      Nova-AI Autonomous Scientific Research Engine &bull; Generated local research document",
            "    </footer>",
            "  </div>",
            "</body>",
            "</html>",
        ])

        html_doc = "\n".join(html_lines)
        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(html_doc, encoding="utf-8")
            logger.info("Exported HTML report", path=str(p), size_bytes=len(html_doc.encode("utf-8")))

        return html_doc

    # -------------------------------------------------------------------------
    # 3. PDF Export
    # -------------------------------------------------------------------------

    def export_pdf(
        self,
        report: StructuredResearchReport,
        output_path: Optional[Union[str, Path]] = None,
    ) -> bytes:
        """Exports report as a publication-grade PDF 1.4 document using NativePDFWriter."""
        pdf_writer = NativePDFWriter(doc_title=report.title)

        # 1. Title Block
        pdf_writer.add_title_block(
            title=report.title,
            research_question=report.research_question,
            confidence_str=f"{report.overall_confidence.value} ({report.overall_confidence_score * 100:.1f}%)",
            model_name=report.model_used,
            report_id=report.report_id,
            detail_level=report.detail_level.value,
        )

        # 2. Executive Summary
        pdf_writer.add_heading("1. Executive Summary", level=1)
        pdf_writer.add_paragraph(report.executive_summary if report.executive_summary else "No executive summary available.")

        # 3. Objectives & Subtopics
        pdf_writer.add_heading("2. Research Objectives & Subtopics", level=1)
        if report.research_objectives:
            pdf_writer.add_heading("Primary Objectives:", level=2)
            for obj in report.research_objectives:
                pdf_writer.add_bullet(obj)
        if report.subtopics:
            pdf_writer.add_heading("Key Subtopics Investigated:", level=2)
            for st in report.subtopics:
                pdf_writer.add_bullet(st)

        # 4. Introduction & Background (if detailed/comprehensive)
        if report.introduction_and_background:
            pdf_writer.add_heading("3. Introduction & Background", level=1)
            pdf_writer.add_paragraph(report.introduction_and_background)

        # 5. Literature Review
        if report.literature_review:
            pdf_writer.add_heading("4. Literature Review", level=1)
            pdf_writer.add_paragraph(report.literature_review)

        # 6. Methodology & Source Provenance
        if report.methodology_and_source_selection:
            pdf_writer.add_heading("5. Methodology & Source Provenance", level=1)
            pdf_writer.add_paragraph(report.methodology_and_source_selection)

        # 7. Evidence-Backed Findings
        pdf_writer.add_heading("6. Evidence-Backed Findings", level=1)
        pdf_writer.add_paragraph(report.evidence_backed_findings if report.evidence_backed_findings else "No empirical findings recorded.")

        # Verified Facts Table
        if report.verified_facts:
            pdf_writer.add_heading("Verified Factual Claims:", level=2)
            headers = ["Factual Assertion", "Confidence", "Citations", "Sources"]
            rows: List[List[str]] = []
            for f in report.verified_facts:
                cites = " ".join(f.citation_keys) if f.citation_keys else "[N/A]"
                rows.append([f.statement, f.confidence.value, cites, str(f.independent_sources_count)])
            pdf_writer.add_table(headers, rows, col_widths=[275.0, 75.0, 75.0, 70.0])

        # Derived Inferences Callouts
        if report.derived_inferences:
            pdf_writer.add_heading("Derived Inferences & Theoretical Deductions:", level=2)
            for inf in report.derived_inferences:
                cites = " ".join(inf.citation_keys) if inf.citation_keys else ""
                card_title = f"Inference {cites} (Hedging: {inf.hedging_rationale or 'derived'})"
                pdf_writer.add_callout(card_title, inf.statement, style="inference")

        # 8. Contradiction Analysis
        if report.contradictions or report.contradiction_analysis:
            pdf_writer.add_heading("7. Contradiction & Disagreement Analysis", level=1)
            if report.contradiction_analysis:
                pdf_writer.add_paragraph(report.contradiction_analysis)
            for c in report.contradictions:
                card_title = f"Conflict: {c.topic_or_claim} ({c.nature_of_conflict})"
                card_body = (
                    f"Source A: {c.source_a_summary} ({c.source_a_citation.get('title', '')})\n"
                    f"Source B: {c.source_b_summary} ({c.source_b_citation.get('title', '')})\n"
                    f"Synthesis: {c.resolution_or_synthesis}"
                )
                pdf_writer.add_callout(card_title, card_body, style="conflict")

        # 9. Unsupported Claims (Segregated)
        if report.unsupported_claims:
            pdf_writer.add_heading("8. Unsupported Claims & Unverified Hypotheses", level=1)
            pdf_writer.add_paragraph(
                "The following statements lacked passage evidence in the retrieved corpus and are strictly segregated from verified facts:",
                italic=True,
            )
            for u in report.unsupported_claims:
                card_title = f"Unsupported Statement ({u.epistemic_status.value})"
                pdf_writer.add_callout(card_title, u.statement, style="unsupported")

        # 10. Limitations & Knowledge Gaps
        if report.limitations_and_knowledge_gaps:
            pdf_writer.add_heading("9. Research Limitations & Knowledge Gaps", level=1)
            for gap in report.limitations_and_knowledge_gaps:
                pdf_writer.add_bullet(gap)

        # 11. Discussion & Conclusion
        if report.discussion_and_conclusion:
            pdf_writer.add_heading("10. Discussion & Conclusion", level=1)
            pdf_writer.add_paragraph(report.discussion_and_conclusion)

        # 12. References & Bibliography
        if report.references:
            pdf_writer.add_heading("11. References & Bibliography", level=1)
            for ref in report.references:
                authors = ", ".join(ref.authors) if ref.authors else "Unknown Authors"
                year = f"({ref.publication_year})" if ref.publication_year else "(n.d.)"
                venue = f" {ref.venue}." if ref.venue else ""
                doi_str = f" DOI: {ref.doi}" if ref.doi else ""
                url_str = f" URL: {ref.canonical_url}" if ref.canonical_url and not ref.doi else ""
                ref_line = f"{ref.citation_key} {authors} {year}. {ref.title}.{venue}{doi_str}{url_str}"
                pdf_writer.add_paragraph(ref_line, font_size=8.5, indent=14.0)

        # Compile PDF binary
        pdf_bytes = pdf_writer.build_pdf()

        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(pdf_bytes)
            logger.info("Exported PDF report", path=str(p), size_bytes=len(pdf_bytes))

        return pdf_bytes

    # -------------------------------------------------------------------------
    # 4. Multi-Format Export Batch
    # -------------------------------------------------------------------------

    def export_all(
        self,
        report: StructuredResearchReport,
        output_dir: Union[str, Path],
        base_filename: Optional[str] = None,
    ) -> ReportExportResult:
        """Exports report in Markdown, HTML, and PDF formats to output_dir."""
        start_t = time.time()
        out_d = Path(output_dir)
        out_d.mkdir(parents=True, exist_ok=True)

        fname = base_filename or f"research_report_{report.report_id}"
        md_path = out_d / f"{fname}.md"
        html_path = out_d / f"{fname}.html"
        pdf_path = out_d / f"{fname}.pdf"

        # Generate all 3 formats
        md_text = self.export_markdown(report, md_path)
        html_text = self.export_html(report, html_path)
        pdf_bytes = self.export_pdf(report, pdf_path)

        file_paths = {
            "markdown": str(md_path),
            "html": str(html_path),
            "pdf": str(pdf_path),
        }
        file_sizes = {
            "markdown": len(md_text.encode("utf-8")),
            "html": len(html_text.encode("utf-8")),
            "pdf": len(pdf_bytes),
        }

        # Save paths back to report model
        report.export_files = file_paths
        duration = time.time() - start_t

        return ReportExportResult(
            report_id=report.report_id,
            formats_generated=["markdown", "html", "pdf"],
            file_paths=file_paths,
            file_sizes_bytes=file_sizes,
            duration_sec=duration,
        )

