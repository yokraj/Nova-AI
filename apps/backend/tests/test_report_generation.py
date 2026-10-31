"""Comprehensive Unit & Integration Test Suite for Phase 10L-D:
Intelligent Research Report Generation & Export Engine.

Validates:
1. Complete report generation across Short, Detailed, and Comprehensive formats
2. Citation correctness & claim-level mapping
3. Bibliography integrity (DOIs, URLs, authors, year, provider provenance)
4. Missing metadata handling (no fabrication of DOIs, URLs, or authors)
5. Contradictory evidence analysis (polarity, numerical, conditional)
6. Unsupported claim handling (strict segregation from verified facts)
7. Markdown, HTML, and PDF exports (valid syntax, styling, PDF 1.4 compliance)
8. Unicode handling and multi-page pagination in PDF export
9. Local Ollama model support with deterministic fallback
10. UniversalResearchEngine facade integration (generate_research_report)
"""

from pathlib import Path
import tempfile
import pytest

from app.ai.research.intelligent_report_generator import IntelligentReportGenerator
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
)
from app.ai.research.pdf_writer import NativePDFWriter
from app.ai.research.report_exporter import ResearchReportExporter
from app.ai.research.research_engine import UniversalResearchEngine


# =============================================================================
# Fixtures & Deterministic Scholarly Test Data
# =============================================================================

@pytest.fixture
def sample_synthesis_vaswani() -> GroundedAnswerSynthesis:
    ref1 = ReferenceEntry(
        citation_number=1,
        citation_key="[1]",
        source_id="src_vaswani_2017",
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
        publication_year=2017,
        doi="10.48550/arxiv.1706.03762",
        canonical_url="https://arxiv.org/abs/1706.03762",
        venue="Advances in Neural Information Processing Systems",
        provider="arxiv",
        contributing_providers=["arxiv", "crossref"],
        retrieval_timestamp=1700000000.0,
    )

    ref2 = ReferenceEntry(
        citation_number=2,
        citation_key="[2]",
        source_id="src_low_resource_2024",
        title="Empirical Limits of Attention in Low-Resource Regimes",
        authors=["Jane Doe", "John Smith"],
        publication_year=2024,
        doi="10.1000/limits.2024",
        canonical_url="https://doi.org/10.1000/limits.2024",
        venue="Journal of Empirical AI",
        provider="crossref",
        contributing_providers=["crossref"],
        retrieval_timestamp=1700000100.0,
    )

    ref3 = ReferenceEntry(
        citation_number=3,
        citation_key="[3]",
        source_id="src_unpublished_2025",
        title="Novel Sparse Attention in Edge Computing",
        authors=["Alice Johnson"],
        publication_year=2025,
        doi=None,  # Missing DOI intentionally
        canonical_url=None,  # Missing URL intentionally
        venue=None,
        provider="scholarly",
        contributing_providers=["scholarly"],
        retrieval_timestamp=1700000200.0,
    )

    fact1 = GroundedClaim(
        claim_id="clm_01",
        statement="The Transformer establishes a new state-of-the-art BLEU score of 28.4 on English-to-German translation.",
        epistemic_status=ClaimEpistemicStatus.VERIFIED_FACT,
        confidence=ConfidenceLevel.HIGH,
        confidence_score=0.95,
        citation_keys=["[1]"],
        independent_sources_count=2,
    )

    fact2 = GroundedClaim(
        claim_id="clm_02",
        statement="Recurrent models outperform attention in small vocabulary low-resource environments.",
        epistemic_status=ClaimEpistemicStatus.VERIFIED_FACT,
        confidence=ConfidenceLevel.HIGH,
        confidence_score=0.90,
        citation_keys=["[2]"],
        independent_sources_count=1,
    )

    inference1 = GroundedClaim(
        claim_id="clm_inf_01",
        statement="Sparse attention may imply lower memory footprint across edge nodes.",
        epistemic_status=ClaimEpistemicStatus.INFERENCE,
        confidence=ConfidenceLevel.MEDIUM,
        confidence_score=0.70,
        citation_keys=["[3]"],
        is_hedged=True,
        hedging_rationale="Explicit hedging: 'may imply'",
        independent_sources_count=1,
    )

    unsupported1 = GroundedClaim(
        claim_id="clm_uns_01",
        statement="Attention mechanisms achieve zero latency on quantum hardware.",
        epistemic_status=ClaimEpistemicStatus.UNSUPPORTED,
        confidence=ConfidenceLevel.UNVERIFIED,
        confidence_score=0.05,
        citation_keys=[],
        independent_sources_count=0,
    )

    contra1 = ContradictionReport(
        contradiction_id="contra_01",
        topic_or_claim="Transformer superiority across translation regimes",
        source_a_summary="The Transformer outperforms recurrent networks on all translation benchmarks.",
        source_a_citation={"source_id": "src_vaswani_2017", "title": "Attention Is All You Need", "year": 2017},
        source_b_summary="The Transformer fails to achieve acceptable BLEU scores in low-resource environments.",
        source_b_citation={"source_id": "src_low_resource_2024", "title": "Empirical Limits of Attention in Low-Resource Regimes", "year": 2024},
        nature_of_conflict="CONDITIONAL_VARIATION",
        resolution_or_synthesis="Divergent findings stem from training data scale (WMT benchmark vs low-resource vocabularies).",
    )

    return GroundedAnswerSynthesis(
        research_question="How does the Transformer architecture compare with recurrent networks across translation regimes?",
        subtopics=[
            "Architecture principles of attention vs recurrence",
            "Empirical benchmark performance on WMT English-to-German",
            "Low-resource and small vocabulary translation limits",
            "Memory complexity and edge optimization",
        ],
        executive_summary=(
            "Synthesis of attention mechanisms vs recurrent architectures across translation regimes. "
            "Evidence confirms state-of-the-art BLEU of 28.4 on standard high-resource benchmarks, "
            "while identifying significant performance drops in low-resource environments."
        ),
        grounded_response=(
            "### Overview & Empirical Evaluation\n"
            "The Transformer architecture dispenses with recurrence entirely [1]. "
            "On standard benchmarks, it establishes a state-of-the-art BLEU score of 28.4 [1]. "
            "However, empirical testing in low-resource regimes demonstrates that recurrent models remain superior for small vocabularies [2]. "
            "Sparse attention may imply lower memory footprint in distributed setups [3]."
        ),
        verified_facts=[fact1, fact2],
        derived_inferences=[inference1],
        unsupported_claims=[unsupported1],
        contradictions=[contra1],
        uncertainties_and_gaps=[
            "Lack of large-scale pre-training data limits transformer convergence in sub-10k vocabulary regimes.",
            "Edge deployment memory metrics remain contingent on quantization methods.",
        ],
        references=[ref1, ref2, ref3],
        overall_confidence=ConfidenceLevel.HIGH,
        overall_confidence_score=0.88,
        model_used="qwen3:8b",
        is_local_model=True,
    )


# =============================================================================
# Test 1: Complete Report Generation Across Formats (Short, Detailed, Comprehensive)
# =============================================================================

@pytest.mark.anyio
async def test_complete_report_generation_formats(sample_synthesis_vaswani):
    """Validates that reports can be generated in SHORT, DETAILED, and COMPREHENSIVE detail levels."""
    generator = IntelligentReportGenerator()

    # 1. SHORT format
    report_short = await generator.generate_from_synthesis(
        synthesis=sample_synthesis_vaswani,
        detail_level=ReportDetailLevel.SHORT,
    )
    assert report_short.detail_level == ReportDetailLevel.SHORT
    assert len(report_short.executive_summary) > 30
    assert len(report_short.verified_facts) == 2
    # In SHORT format, background/literature review are omitted
    assert report_short.introduction_and_background == ""
    assert report_short.literature_review == ""

    # 2. DETAILED format
    report_detailed = await generator.generate_from_synthesis(
        synthesis=sample_synthesis_vaswani,
        detail_level=ReportDetailLevel.DETAILED,
    )
    assert report_detailed.detail_level == ReportDetailLevel.DETAILED
    assert len(report_detailed.introduction_and_background) > 20
    assert len(report_detailed.literature_review) > 20

    # 3. COMPREHENSIVE format
    report_comp = await generator.generate_from_synthesis(
        synthesis=sample_synthesis_vaswani,
        detail_level=ReportDetailLevel.COMPREHENSIVE,
    )
    assert report_comp.detail_level == ReportDetailLevel.COMPREHENSIVE
    assert len(report_comp.methodology_and_source_selection) > 20
    assert len(report_comp.discussion_and_conclusion) > 20
    assert len(report_comp.contradictions) == 1
    assert len(report_comp.references) == 3


# =============================================================================
# Test 2: Citation Correctness & Claim-Level Mapping
# =============================================================================

@pytest.mark.anyio
async def test_citation_correctness_and_mapping(sample_synthesis_vaswani):
    """Validates that citations are attached to claims and reference numbers match the bibliography."""
    generator = IntelligentReportGenerator()
    report = await generator.generate_from_synthesis(sample_synthesis_vaswani)

    # Validate verified facts have correct citation markers
    fact_bleu = next(f for f in report.verified_facts if "28.4" in f.statement)
    assert fact_bleu.citation_keys == ["[1]"]

    fact_low_res = next(f for f in report.verified_facts if "low-resource" in f.statement)
    assert fact_low_res.citation_keys == ["[2]"]

    # Validate derived inferences citation
    inf = report.derived_inferences[0]
    assert inf.citation_keys == ["[3]"]

    # Validate that [1], [2], [3] exist in report.references
    ref_keys = {r.citation_key for r in report.references}
    assert {"[1]", "[2]", "[3]"}.issubset(ref_keys)


# =============================================================================
# Test 3: Bibliography Integrity & Source Provenance
# =============================================================================

@pytest.mark.anyio
async def test_bibliography_integrity_and_provenance(sample_synthesis_vaswani):
    """Validates that bibliography entries preserve original authors, year, DOI, venue, and contributing providers."""
    generator = IntelligentReportGenerator()
    report = await generator.generate_from_synthesis(sample_synthesis_vaswani)

    ref1 = next(r for r in report.references if r.citation_number == 1)
    assert ref1.title == "Attention Is All You Need"
    assert "Ashish Vaswani" in ref1.authors
    assert ref1.publication_year == 2017
    assert ref1.doi == "10.48550/arxiv.1706.03762"
    assert ref1.canonical_url == "https://arxiv.org/abs/1706.03762"
    assert "crossref" in ref1.contributing_providers


# =============================================================================
# Test 4: Missing Metadata Handling (No Fabrication)
# =============================================================================

@pytest.mark.anyio
async def test_missing_metadata_no_fabrication(sample_synthesis_vaswani):
    """Validates that sources missing DOIs or URLs are stored strictly as None without synthetic fabrication."""
    generator = IntelligentReportGenerator()
    report = await generator.generate_from_synthesis(sample_synthesis_vaswani)

    ref3 = next(r for r in report.references if r.citation_number == 3)
    assert ref3.doi is None  # NO FABRICATION of fake DOI
    assert ref3.canonical_url is None  # NO FABRICATION of fake URL
    assert ref3.venue is None

    # Check Markdown representation: does not display broken or fake links
    md = report.to_markdown()
    assert "[3] Alice Johnson (2025). **Novel Sparse Attention in Edge Computing**." in md
    assert "DOI: [None]" not in md
    assert "http://None" not in md


# =============================================================================
# Test 5: Contradictory Evidence Analysis
# =============================================================================

@pytest.mark.anyio
async def test_contradictory_evidence_analysis(sample_synthesis_vaswani):
    """Validates that conflicting findings across sources are highlighted in contradiction sections."""
    generator = IntelligentReportGenerator()
    report = await generator.generate_from_synthesis(sample_synthesis_vaswani)

    assert len(report.contradictions) == 1
    contra = report.contradictions[0]
    assert contra.nature_of_conflict == "CONDITIONAL_VARIATION"
    assert "Transformer superiority" in contra.topic_or_claim
    assert "2017" in str(contra.source_a_citation.get("year"))
    assert "2024" in str(contra.source_b_citation.get("year"))

    # Assert Markdown contains Contradiction section
    md = report.to_markdown()
    assert "## 7. Contradiction & Disagreement Analysis" in md
    assert "CONDITIONAL_VARIATION" in md


# =============================================================================
# Test 6: Unsupported Claim Handling (Strict Segregation)
# =============================================================================

@pytest.mark.anyio
async def test_unsupported_claim_handling_strict_segregation(sample_synthesis_vaswani):
    """Validates that unsupported claims are strictly segregated from verified facts."""
    generator = IntelligentReportGenerator()
    report = await generator.generate_from_synthesis(sample_synthesis_vaswani)

    # 1. Assert unsupported claim exists in unsupported_claims
    assert len(report.unsupported_claims) == 1
    unsupp = report.unsupported_claims[0]
    assert "quantum hardware" in unsupp.statement
    assert unsupp.epistemic_status == ClaimEpistemicStatus.UNSUPPORTED

    # 2. Assert unsupported claim is NOT in verified_facts
    fact_statements = [f.statement for f in report.verified_facts]
    assert not any("quantum hardware" in s for s in fact_statements)

    # 3. Assert Markdown has a segregated Section 8
    md = report.to_markdown()
    assert "## 8. Unsupported Claims & Unverified Assumptions" in md
    assert "strictly segregated from verified facts" in md


# =============================================================================
# Test 7: Export to Markdown, HTML, and PDF
# =============================================================================

@pytest.mark.anyio
async def test_report_export_markdown_html_pdf(sample_synthesis_vaswani):
    """Validates exporting report into Markdown, HTML, and PDF formats."""
    exporter = ResearchReportExporter()
    generator = IntelligentReportGenerator(exporter=exporter)
    report = await generator.generate_from_synthesis(sample_synthesis_vaswani)

    with tempfile.TemporaryDirectory() as tmp_dir:
        res: ReportExportResult = exporter.export_all(
            report=report,
            output_dir=tmp_dir,
            base_filename="test_vaswani_report",
        )

        assert res.report_id == report.report_id
        assert "markdown" in res.file_paths
        assert "html" in res.file_paths
        assert "pdf" in res.file_paths

        md_file = Path(res.file_paths["markdown"])
        html_file = Path(res.file_paths["html"])
        pdf_file = Path(res.file_paths["pdf"])

        # Check file existence and non-zero size
        assert md_file.exists() and md_file.stat().st_size > 500
        assert html_file.exists() and html_file.stat().st_size > 1000
        assert pdf_file.exists() and pdf_file.stat().st_size > 1000

        # Validate Markdown Content
        md_text = md_file.read_text(encoding="utf-8")
        assert f"# {report.title}" in md_text
        assert "## 1. Executive Summary" in md_text
        assert "## 11. References & Bibliography" in md_text

        # Validate HTML Content
        html_text = html_file.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in html_text
        assert "<title>" in html_text
        assert "class=\"cite-link\"" in html_text
        assert "id=\"ref-1\"" in html_text

        # Validate PDF 1.4 Binary Structure
        pdf_bytes = pdf_file.read_bytes()
        assert pdf_bytes.startswith(b"%PDF-1.4")
        assert b"%%EOF" in pdf_bytes
        assert b"xref" in pdf_bytes
        assert b"/Type /Catalog" in pdf_bytes


# =============================================================================
# Test 8: Unicode Handling and Multi-Page Pagination
# =============================================================================

@pytest.mark.anyio
async def test_unicode_handling_and_multi_page_pdf():
    """Validates that Unicode characters (Greek letters, em-dashes, smart quotes) and long multi-page reports compile safely without PDF errors."""
    writer = NativePDFWriter(doc_title="Unicode & Multi-Page Test — α/β/γ")

    # Add long multi-paragraph content to trigger automatic page breaks
    writer.add_heading("Section 1: Unicode Characters & Typographic Symbols", level=1)
    writer.add_paragraph(
        "Scientific literature frequently utilizes Greek symbols like alpha (\u03b1), beta (\u03b2), "
        "gamma (\u03b3), pi (\u03c0), mathematical relations (\u2265, \u2264, \u00b1), and typographic "
        "punctuations such as em-dashes (\u2014) and smart quotes (\u201cquoted\u201d)."
    )

    # Fill content across multiple pages
    for i in range(1, 15):
        writer.add_heading(f"Subsection 1.{i}: Longitudinal Benchmarks", level=2)
        writer.add_paragraph(
            f"Experimental iteration {i}: Evaluated latency across distributed nodes. "
            f"Observed throughput scaled monotonically from 100 req/s to {i * 250} req/s with low jitter."
        )
        writer.add_callout(f"Benchmark Card {i}", f"Verification outcome for node cluster {i} -- operational.", style="fact")

    pdf_bytes = writer.build_pdf()

    assert pdf_bytes.startswith(b"%PDF-1.4")
    assert b"%%EOF" in pdf_bytes
    # Assert multi-page document was produced
    assert b"Page 2 of" in pdf_bytes or b"/Count 2" in pdf_bytes or b"/Count 3" in pdf_bytes


# =============================================================================
# Test 9: Local Ollama Model Support and Deterministic Fallback
# =============================================================================

@pytest.mark.anyio
async def test_local_model_and_deterministic_fallback(sample_synthesis_vaswani):
    """Validates that report generation utilizes local Ollama model (qwen3:8b) with deterministic offline fallback."""
    generator = IntelligentReportGenerator()

    # Generate with default local model
    report = await generator.generate_from_synthesis(
        synthesis=sample_synthesis_vaswani,
        detail_level=ReportDetailLevel.COMPREHENSIVE,
        model_id="qwen3:8b",
    )

    assert report.is_local_model is True
    assert len(report.introduction_and_background) > 50
    assert len(report.discussion_and_conclusion) > 50


# =============================================================================
# Test 10: UniversalResearchEngine Facade Integration
# =============================================================================

@pytest.mark.anyio
async def test_universal_research_engine_facade_report_generation(sample_synthesis_vaswani):
    """Validates that UniversalResearchEngine exposes generate_research_report cleanly both from synthesis and inquiry."""
    engine = UniversalResearchEngine()

    with tempfile.TemporaryDirectory() as tmp_dir:
        # 1. Generate directly from pre-computed GroundedAnswerSynthesis with all export formats
        report = await engine.generate_research_report(
            question_or_synthesis=sample_synthesis_vaswani,
            detail_level=ReportDetailLevel.COMPREHENSIVE,
            export_formats=[ReportExportFormat.ALL],
            output_dir=tmp_dir,
            base_filename="facade_report_test",
        )

        assert isinstance(report, StructuredResearchReport)
        assert len(report.export_files) == 3
        assert Path(report.export_files["markdown"]).exists()
        assert Path(report.export_files["html"]).exists()
        assert Path(report.export_files["pdf"]).exists()

        # 2. Verify that existing report generator remains functional (backward compatibility)
        citations = await engine.citations()
        assert isinstance(citations, list)

