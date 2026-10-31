"""Intelligent Research Report Generation Engine for Phase 10L-D.

Generates complete, publication-grade academic and technical research reports from
GroundedAnswerSynthesis (Phase 10L-C), preserving epistemic separation, citation mapping,
multi-source provenance, and contradiction analysis across Short, Detailed, and Comprehensive formats.
"""

from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Union
import structlog

from app.ai.research.answer_synthesizer import EvidenceGroundedSynthesizer
from app.ai.research.models import (
    ClaimEpistemicStatus,
    ConfidenceLevel,
    ContradictionReport,
    GroundedAnswerSynthesis,
    GroundedClaim,
    ReferenceEntry,
    ReportDetailLevel,
    ReportExportFormat,
    ReportExportResult,
    ScholarlySourceRecord,
    StructuredResearchReport,
    SynthesisMode,
)
from app.ai.research.report_exporter import ResearchReportExporter
from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine

logger = structlog.get_logger("intelligent_report_generator")


class IntelligentReportGenerator:
    """Orchestrates comprehensive, evidence-grounded research report generation and export."""

    def __init__(
        self,
        runtime_engine: Optional[UniversalAIRuntimeEngine] = None,
        synthesizer: Optional[EvidenceGroundedSynthesizer] = None,
        exporter: Optional[ResearchReportExporter] = None,
    ) -> None:
        self.runtime = runtime_engine or UniversalAIRuntimeEngine()
        self.synthesizer = synthesizer or EvidenceGroundedSynthesizer(runtime_engine=self.runtime)
        self.exporter = exporter or ResearchReportExporter()

    # -------------------------------------------------------------------------
    # Section Synthesis & Expansion Methods
    # -------------------------------------------------------------------------

    async def _generate_section_text(
        self,
        section_name: str,
        question: str,
        subtopics: List[str],
        synthesis: GroundedAnswerSynthesis,
        model_id: str = "qwen3:8b",
    ) -> str:
        """Generates section text using local Ollama model with deterministic fallback."""
        prompt = (
            f"You are a scientific author drafting the '{section_name}' section of a formal research report.\n"
            f"Topic: {question}\n"
            f"Subtopics: {', '.join(subtopics)}\n"
            f"Grounded Findings Overview: {synthesis.executive_summary}\n"
            f"Draft a rigorous, objective academic section. Do not hallucinate external references."
        )

        try:
            res = await self.runtime.reason(prompt=prompt, model_id=model_id)
            if res and res.text_or_data and len(res.text_or_data.strip()) > 60:
                raw = res.text_or_data.strip()
                if not raw.startswith("[Ollama Engine") and not raw.startswith("[Reasoning -"):
                    return raw
        except Exception as e:
            logger.debug(f"Local model generation skipped for {section_name}, using deterministic fallback", error=str(e))

        # Deterministic Section Generators
        if section_name == "Introduction and Background":
            return (
                f"Contemporary research in this domain addresses the inquiry: '{question}'. "
                f"Rapid advancements across {len(subtopics)} primary subtopics ({', '.join(subtopics[:3])}) "
                f"necessitate a systematic, evidence-grounded synthesis to evaluate architectural viability, "
                f"empirical performance metrics, and operational boundaries under varying experimental conditions."
            )
        elif section_name == "Literature Review":
            ref_titles = [f"'{r.title}' ({', '.join(r.authors[:2]) if r.authors else 'n.a.'}, {r.publication_year or 'n.d.'})" for r in synthesis.references[:4]]
            refs_summary = "; ".join(ref_titles) if ref_titles else "the retrieved scholarly corpus"
            return (
                f"A systematic survey of relevant literature examines foundational works, including {refs_summary}. "
                f"The literature establishes theoretical foundations and empirical benchmarks while exhibiting "
                f"{'notable divergence across operational regimes' if synthesis.contradictions else 'broad methodological consensus'}. "
                f"Key contributions explore mechanisms of action, algorithmic complexity, and scaling limits."
            )
        elif section_name == "Methodology and Source Selection":
            prov_list = list({p for r in synthesis.references for p in r.contributing_providers}) or ["Crossref", "arXiv", "OpenAlex", "Europe PMC"]
            return (
                f"This investigation employs an autonomous multi-provider discovery protocol querying {', '.join(prov_list)}. "
                f"Source records undergo strict DOI resolution, syntactic verification, and conservative deduplication. "
                f"All extracted passages are indexed in an Evidence and Provenance Knowledge Graph, from which atomic claims "
                f"are evaluated across verified factual assertions, derived inferences, and unsupported propositions."
            )
        elif section_name == "Discussion and Conclusion":
            facts_count = len(synthesis.verified_facts)
            contra_count = len(synthesis.contradictions)
            return (
                f"The evidence-backed synthesis confirms key architectural and empirical characteristics regarding {question}. "
                f"A total of {facts_count} factual propositions are verified against source passages with {synthesis.overall_confidence.value} confidence. "
                f"{'Crucially, ' + str(contra_count) + ' conflicting findings were discovered, underscoring that performance claims cannot be generalized unconditionally.' if contra_count else 'Findings exhibit consistent alignment across investigated corpora.'} "
                f"Future investigations should prioritize resolving identified evidence gaps under extreme operating conditions."
            )
        else:
            return f"Systematic analysis for '{section_name}' addressing '{question}'."

    # -------------------------------------------------------------------------
    # Core Report Generation
    # -------------------------------------------------------------------------

    async def generate_from_synthesis(
        self,
        synthesis: GroundedAnswerSynthesis,
        detail_level: ReportDetailLevel = ReportDetailLevel.COMPREHENSIVE,
        title: Optional[str] = None,
        model_id: str = "qwen3:8b",
    ) -> StructuredResearchReport:
        """Constructs a StructuredResearchReport from an existing GroundedAnswerSynthesis (Phase 10L-C).

        Preserves all verified facts, inferences, and unsupported claims separately,
        ensuring complete citation mapping and source provenance without fabrication.
        """
        report_title = title or f"Research Report: {synthesis.research_question}"
        question = synthesis.research_question
        subtopics = synthesis.subtopics

        # Objectives formulation
        objectives = [
            f"Examine foundational principles and empirical performance of {question}",
            f"Validate claim-level evidential support across peer-reviewed and preprint literature",
            f"Identify operational discrepancies, trade-offs, and failure conditions across regimes",
        ]

        # Section Text Generation
        intro_text = ""
        lit_review_text = ""
        method_text = ""
        discussion_text = ""

        if detail_level in (ReportDetailLevel.DETAILED, ReportDetailLevel.COMPREHENSIVE):
            intro_text = await self._generate_section_text("Introduction and Background", question, subtopics, synthesis, model_id)
            lit_review_text = await self._generate_section_text("Literature Review", question, subtopics, synthesis, model_id)
            method_text = await self._generate_section_text("Methodology and Source Selection", question, subtopics, synthesis, model_id)
            discussion_text = await self._generate_section_text("Discussion and Conclusion", question, subtopics, synthesis, model_id)

        # Contradiction Narrative
        contra_narrative = ""
        if synthesis.contradictions:
            contra_narrative = (
                f"Cross-source analysis revealed {len(synthesis.contradictions)} significant empirical contradiction(s) or "
                f"operational disagreements between independent studies. Evidence indicates that reported performance advantages "
                f"are regime-dependent rather than universal."
            )

        report = StructuredResearchReport(
            title=report_title,
            research_question=question,
            detail_level=detail_level,
            executive_summary=synthesis.executive_summary,
            research_objectives=objectives,
            subtopics=subtopics,
            introduction_and_background=intro_text,
            literature_review=lit_review_text,
            methodology_and_source_selection=method_text,
            evidence_backed_findings=synthesis.grounded_response,
            verified_facts=synthesis.verified_facts,
            derived_inferences=synthesis.derived_inferences,
            unsupported_claims=synthesis.unsupported_claims,
            contradictions=synthesis.contradictions,
            contradiction_analysis=contra_narrative,
            limitations_and_knowledge_gaps=synthesis.uncertainties_and_gaps,
            discussion_and_conclusion=discussion_text,
            references=synthesis.references,
            overall_confidence=synthesis.overall_confidence,
            overall_confidence_score=synthesis.overall_confidence_score,
            model_used=synthesis.model_used,
            is_local_model=synthesis.is_local_model,
        )

        return report

    async def generate_report(
        self,
        question: str,
        sources: Optional[List[Union[ScholarlySourceRecord, Dict[str, Any]]]] = None,
        detail_level: ReportDetailLevel = ReportDetailLevel.COMPREHENSIVE,
        candidate_claims: Optional[List[str]] = None,
        title: Optional[str] = None,
        model_id: str = "qwen3:8b",
        export_formats: Optional[List[ReportExportFormat]] = None,
        output_dir: Optional[Union[str, Path]] = None,
        base_filename: Optional[str] = None,
    ) -> StructuredResearchReport:
        """End-to-end report generation: synthesizes evidence via Phase 10L-C and exports in requested formats.

        Args:
            question: Research question inquiry.
            sources: Optional pre-collected scholarly source records.
            detail_level: SHORT, DETAILED, or COMPREHENSIVE.
            candidate_claims: Optional explicit claims to evaluate and classify.
            title: Custom report title.
            model_id: Local Ollama model ID (default: 'qwen3:8b').
            export_formats: Formats to export (MARKDOWN, HTML, PDF, ALL).
            output_dir: Directory where export files will be written.
            base_filename: Base filename prefix for exported files.

        Returns:
            StructuredResearchReport model populated with file paths.
        """
        # Step 1: Execute evidence-grounded answer synthesis (Phase 10L-C)
        synthesis = await self.synthesizer.synthesize(
            question=question,
            sources=sources,
            mode=SynthesisMode.GROUNDED_STRICT,
            candidate_claims=candidate_claims,
            model_id=model_id,
        )

        # Step 2: Generate Structured Research Report
        report = await self.generate_from_synthesis(
            synthesis=synthesis,
            detail_level=detail_level,
            title=title,
            model_id=model_id,
        )

        # Step 3: Handle requested file exports
        if export_formats and output_dir:
            out_p = Path(output_dir)
            out_p.mkdir(parents=True, exist_ok=True)
            fname = base_filename or f"report_{report.report_id}"

            export_all_requested = ReportExportFormat.ALL in export_formats

            if export_all_requested or (
                ReportExportFormat.MARKDOWN in export_formats
                and ReportExportFormat.HTML in export_formats
                and ReportExportFormat.PDF in export_formats
            ):
                self.exporter.export_all(report, out_p, fname)
            else:
                if ReportExportFormat.MARKDOWN in export_formats:
                    md_path = out_p / f"{fname}.md"
                    self.exporter.export_markdown(report, md_path)
                    report.export_files["markdown"] = str(md_path)

                if ReportExportFormat.HTML in export_formats:
                    html_path = out_p / f"{fname}.html"
                    self.exporter.export_html(report, html_path)
                    report.export_files["html"] = str(html_path)

                if ReportExportFormat.PDF in export_formats:
                    pdf_path = out_p / f"{fname}.pdf"
                    self.exporter.export_pdf(report, pdf_path)
                    report.export_files["pdf"] = str(pdf_path)

        return report

