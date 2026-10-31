"""Unit and Integration Tests for Phase 10L-C: Evidence-Grounded Research Answer Synthesis.

Validates:
1. Research question understanding & subtopic decomposition
2. Literature retrieval & evidence graph integration
3. Passage-grounded answer generation
4. Claim-level citation mapping & reference numbering
5. Contradiction detection (polarity, numerical, conditional)
6. Epistemic classification (facts vs inferences vs unsupported claims)
7. Strict prevention of unsupported claims appearing as verified facts
8. Confidence and uncertainty communication
9. Provenance preservation (DOI, URL, metadata without fabrication)
10. Structured research summaries & markdown export
11. Local Ollama model support & deterministic fallback (zero paid APIs)
12. UniversalResearchEngine facade integration
13. GoalVerifier verification types (RESEARCH_SYNTHESIS_GROUNDED, RESEARCH_CITATION_MAPPING_VALID, RESEARCH_CONTRADICTION_DETECTED)
"""

import pytest
from typing import Any, Dict, List

from app.ai.kernel.goal_verifier import (
    GoalRequirement,
    GoalVerifier,
    VerificationStatus,
    VerificationType,
)
from app.ai.research.answer_synthesizer import EvidenceGroundedSynthesizer
from app.ai.research.citation_mapper import ClaimCitationMapper
from app.ai.research.contradiction_detector import ResearchContradictionDetector
from app.ai.research.epistemic_classifier import EpistemicClassifier
from app.ai.research.evidence_graph_builder import EvidenceGraphBuilder
from app.ai.research.models import (
    ClaimEpistemicStatus,
    ClaimVerificationOutcome,
    ConfidenceLevel,
    GroundedAnswerSynthesis,
    GroundedClaim,
    ScholarlySourceRecord,
    SynthesisMode,
)
from app.ai.research.question_analyzer import ResearchQuestionAnalyzer
from app.ai.research.research_engine import UniversalResearchEngine


# =============================================================================
# Fixtures & Deterministic Scholarly Test Data
# =============================================================================

@pytest.fixture
def sample_attention_record() -> ScholarlySourceRecord:
    return ScholarlySourceRecord(
        source_id="src_vaswani_2017",
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
        publication_year=2017,
        doi="10.48550/arxiv.1706.03762",
        canonical_url="https://arxiv.org/abs/1706.03762",
        abstract=(
            "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, "
            "dispensing with recurrence and convolutions entirely. "
            "On the WMT 2014 English-to-German translation task, the Transformer establishes a new state-of-the-art BLEU score of 28.4."
        ),
        venue="Advances in Neural Information Processing Systems",
        provider="arxiv",
        contributing_providers=["arxiv", "crossref"],
        provider_raw_ids={"arxiv": "1706.03762"},
        retrieval_timestamp=1700000000.0,
    )


@pytest.fixture
def sample_low_resource_record() -> ScholarlySourceRecord:
    return ScholarlySourceRecord(
        source_id="src_low_resource_2024",
        title="Limitations of Attention Mechanisms in Low-Resource Regimes",
        authors=["Jane Doe", "John Smith"],
        publication_year=2024,
        doi="10.1000/limitations.2024",
        canonical_url="https://doi.org/10.1000/limitations.2024",
        abstract=(
            "Our extensive empirical experiments demonstrate that the Transformer fails to achieve acceptable BLEU scores in low-resource environments, "
            "and recurrent models are superior for small vocabulary translations. "
            "The algorithm achieved an efficiency gain of 2% in total energy consumption across all test nodes."
        ),
        venue="Journal of Empirical AI",
        provider="crossref",
        contributing_providers=["crossref"],
        provider_raw_ids={"crossref": "limitations.2024"},
        retrieval_timestamp=1700000100.0,
    )


@pytest.fixture
def sample_efficiency_conflict_record() -> ScholarlySourceRecord:
    return ScholarlySourceRecord(
        source_id="src_high_efficiency_2024",
        title="High Efficiency Optimization in Neural Architectures",
        authors=["Alice Johnson", "Bob Lee"],
        publication_year=2024,
        doi=None,  # Intentionally None: preprint with no registered DOI
        canonical_url=None,  # Intentionally None: local unpublished preprint
        abstract=(
            "The algorithm achieved an efficiency gain of 20% in total energy consumption across all test nodes. "
            "Evidence suggests that sparse attention may imply lower memory footprint."
        ),
        venue="arXiv preprint",
        provider="arxiv",
        contributing_providers=["arxiv"],
        provider_raw_ids={"arxiv": "2401.99999"},
        retrieval_timestamp=1700000200.0,
    )


# =============================================================================
# Feature 1: Understand Research Questions & Identify Subtopics
# =============================================================================

def test_question_analyzer_subtopics_and_intent():
    """Validates that research questions are understood and decomposed into subtopics and search queries."""
    analyzer = ResearchQuestionAnalyzer()

    # 1. Comparative Question
    q_comp = "How does RLHF compare with DPO in alignment of large language models, and what are their failure modes?"
    analysis_comp = analyzer.analyze_question(q_comp)

    assert analysis_comp.requires_comparison is True
    assert analysis_comp.domain == "computer_science"
    assert len(analysis_comp.subtopics) >= 3
    assert any("RLHF" in st for st in analysis_comp.subtopics)
    assert any("DPO" in st for st in analysis_comp.subtopics)
    assert len(analysis_comp.search_queries) >= 2

    # 2. Multifaceted Scientific Question
    q_mat = "What are the ionic conductivity and thermal degradation mechanisms of solid-state lithium batteries under high-temperature conditions?"
    analysis_mat = analyzer.analyze_question(q_mat)

    assert analysis_mat.domain in ("physics_and_materials", "energy_and_environment")
    assert len(analysis_mat.subtopics) >= 3
    assert "high-temperature" in analysis_mat.target_conditions


# =============================================================================
# Feature 2 & 3: Retrieval, Graph Integration & Passage-Grounded Answer Generation
# =============================================================================

@pytest.mark.anyio
async def test_grounded_answer_generation(sample_attention_record, sample_low_resource_record):
    """Validates that answer generation is strictly grounded in source passages with citations."""
    synthesizer = EvidenceGroundedSynthesizer()

    synthesis = await synthesizer.synthesize(
        question="What is the Transformer architecture and how does it perform on translation tasks?",
        sources=[sample_attention_record, sample_low_resource_record],
        mode=SynthesisMode.GROUNDED_STRICT,
    )

    assert isinstance(synthesis, GroundedAnswerSynthesis)
    assert len(synthesis.subtopics) >= 2
    assert len(synthesis.grounded_response) > 50
    assert "[1]" in synthesis.grounded_response
    assert len(synthesis.references) >= 2


# =============================================================================
# Feature 4: Claim-Level Citation Mapping
# =============================================================================

@pytest.mark.anyio
async def test_claim_level_citation_mapping(sample_attention_record):
    """Validates that each verified claim maps to exact citation keys and bibliographic entries."""
    synthesizer = EvidenceGroundedSynthesizer()

    synthesis = await synthesizer.synthesize(
        question="What are the empirical findings of Attention Is All You Need?",
        sources=[sample_attention_record],
        candidate_claims=[
            "The Transformer establishes a state-of-the-art BLEU score of 28.4 on English-to-German translation.",
        ],
    )

    assert len(synthesis.verified_facts) >= 1
    fact = next((f for f in synthesis.verified_facts if "28.4" in f.statement), None)
    assert fact is not None
    assert fact.epistemic_status == ClaimEpistemicStatus.VERIFIED_FACT
    assert len(fact.citation_keys) >= 1
    assert fact.citation_keys[0] == "[1]"
    assert fact.confidence in (ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM)

    # Validate Reference Registry
    ref1 = synthesis.references[0]
    assert ref1.citation_key == "[1]"
    assert ref1.title == "Attention Is All You Need"
    assert ref1.doi == "10.48550/arxiv.1706.03762"
    assert "arxiv" in ref1.contributing_providers


# =============================================================================
# Feature 5: Detect Contradictions Between Sources
# =============================================================================

@pytest.mark.anyio
async def test_contradiction_detection(
    sample_attention_record,
    sample_low_resource_record,
    sample_efficiency_conflict_record,
):
    """Validates detection of polarity opposing claims, numerical conflicts, and conditional variations."""
    synthesizer = EvidenceGroundedSynthesizer()

    synthesis = await synthesizer.synthesize(
        question="How does the Transformer perform across translation domains and what is its efficiency?",
        sources=[sample_attention_record, sample_low_resource_record, sample_efficiency_conflict_record],
        candidate_claims=[
            "The Transformer outperforms recurrent architectures across all domains.",
            "The algorithm achieved an efficiency gain of 20% in total energy consumption.",
        ],
    )

    assert len(synthesis.contradictions) >= 1

    # Check for polarity or conditional conflict
    contra_types = [c.nature_of_conflict for c in synthesis.contradictions]
    assert any(t in ("POLARITY_OPPOSING", "CONDITIONAL_VARIATION", "NUMERICAL_DISCREPANCY") for t in contra_types)

    # Assert contradictory findings are surfaced in the narrative response
    markdown = synthesis.to_markdown()
    assert "Contradictions & Differing Findings" in markdown or "Divergence" in synthesis.grounded_response


# =============================================================================
# Feature 6: Distinguish Facts, Inferences, and Unsupported Claims
# Strict Prevention of Unsupported Claims Appearing as Verified Facts
# =============================================================================

@pytest.mark.anyio
async def test_epistemic_classification_and_unsupported_claim_prevention(
    sample_attention_record,
    sample_efficiency_conflict_record,
):
    """Validates that:
    1. Direct entailments are classified as VERIFIED_FACT
    2. Hedged statements are classified as INFERENCE
    3. Unsupported statements are classified as UNSUPPORTED and NEVER appear in verified_facts!
    """
    builder = EvidenceGraphBuilder()
    builder.add_scholarly_source(sample_attention_record)
    builder.add_scholarly_source(sample_efficiency_conflict_record)

    classifier = EpistemicClassifier()

    test_statements = [
        "The Transformer is based solely on attention mechanisms.",  # VERIFIED_FACT
        "Evidence suggests that sparse attention may imply lower memory footprint.",  # INFERENCE (hedged)
        "Quantum superposition instantly optimizes neural weights at zero latency.",  # UNSUPPORTED (no evidence)
    ]

    facts, inferences, unsupported = classifier.classify_statements(test_statements, builder)

    # 1. Fact Check
    assert any("solely on attention mechanisms" in f.statement for f in facts)
    assert all(f.epistemic_status == ClaimEpistemicStatus.VERIFIED_FACT for f in facts)

    # 2. Inference Check
    assert any("sparse attention" in inf.statement for inf in inferences)
    inference_claim = next(inf for inf in inferences if "sparse attention" in inf.statement)
    assert inference_claim.epistemic_status == ClaimEpistemicStatus.INFERENCE
    assert inference_claim.is_hedged is True

    # 3. Unsupported Check & Prevention
    assert any("Quantum superposition" in u.statement for u in unsupported)
    unsupported_claim = next(u for u in unsupported if "Quantum superposition" in u.statement)
    assert unsupported_claim.epistemic_status == ClaimEpistemicStatus.UNSUPPORTED

    # STRICT ASSERTION: Unsupported claim is NOT in verified_facts!
    assert not any("Quantum superposition" in f.statement for f in facts)


# =============================================================================
# Feature 7: Communicate Confidence and Uncertainty
# =============================================================================

@pytest.mark.anyio
async def test_confidence_and_uncertainty_quantification(sample_attention_record):
    """Validates quantitative and qualitative communication of confidence and knowledge gaps."""
    synthesizer = EvidenceGroundedSynthesizer()

    synthesis = await synthesizer.synthesize(
        question="What are the limitations of transformers in deep reinforcement learning?",
        sources=[sample_attention_record],  # Only machine translation paper provided; RL is missing evidence
        candidate_claims=[
            "Transformers replace actor-critic networks in all deep RL environments with zero sample inefficiency.",
        ],
    )

    # Confidence should reflect lack of direct evidence for the question
    assert synthesis.overall_confidence in (ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.UNCERTAIN)
    assert len(synthesis.uncertainties_and_gaps) >= 1
    assert any("lacked direct passage grounding" in gap or "density" in gap for gap in synthesis.uncertainties_and_gaps)


# =============================================================================
# Feature 8: Provenance Preservation Without Fabrication
# =============================================================================

@pytest.mark.anyio
async def test_provenance_preservation_no_fabrication(
    sample_attention_record,
    sample_efficiency_conflict_record,
):
    """Validates that valid DOIs/URLs are preserved, and missing DOIs/URLs are NOT fabricated."""
    synthesizer = EvidenceGroundedSynthesizer()

    synthesis = await synthesizer.synthesize(
        question="Efficiency in neural models",
        sources=[sample_attention_record, sample_efficiency_conflict_record],
    )

    ref_map = {r.source_id: r for r in synthesis.references}

    # Vaswani has valid DOI and URL
    vaswani_ref = ref_map["src_vaswani_2017"]
    assert vaswani_ref.doi == "10.48550/arxiv.1706.03762"
    assert vaswani_ref.canonical_url == "https://arxiv.org/abs/1706.03762"

    # Efficiency conflict source has NO DOI and NO URL
    eff_ref = ref_map["src_high_efficiency_2024"]
    assert eff_ref.doi is None  # NO FABRICATION
    assert eff_ref.canonical_url is None  # NO FABRICATION
    assert eff_ref.title == "High Efficiency Optimization in Neural Architectures"


# =============================================================================
# Feature 9: Structured Research Summaries & Markdown Export
# =============================================================================

@pytest.mark.anyio
async def test_structured_synthesis_and_markdown_export(sample_attention_record):
    """Validates that structured summaries, executive summaries, and markdown exports are produced cleanly."""
    synthesizer = EvidenceGroundedSynthesizer()

    synthesis = await synthesizer.synthesize(
        question="Attention mechanisms in deep learning",
        sources=[sample_attention_record],
    )

    assert synthesis.executive_summary.startswith("Evidence-grounded synthesis")
    markdown = synthesis.to_markdown()

    assert "# Research Synthesis:" in markdown
    assert "## Executive Summary" in markdown
    assert "## Synthesized Findings" in markdown
    assert "## References & Provenance" in markdown
    assert "[1] Ashish Vaswani" in markdown


# =============================================================================
# Feature 10: Local Ollama Model Support by Default (Zero Paid APIs)
# =============================================================================

@pytest.mark.anyio
async def test_local_model_support_and_offline_fallback(sample_attention_record):
    """Validates that local model is supported by default, and offline/timeout produces deterministic synthesis without paid APIs."""
    synthesizer = EvidenceGroundedSynthesizer()

    # Test synthesis with default local model (qwen3:8b)
    synthesis = await synthesizer.synthesize(
        question="Attention architecture overview",
        sources=[sample_attention_record],
        model_id="qwen3:8b",
    )

    assert synthesis.is_local_model is True
    assert synthesis.model_used in ("ollama/qwen3:8b", "local_deterministic_synthesis", "qwen3:8b")
    assert len(synthesis.grounded_response) > 50


# =============================================================================
# Feature 11: UniversalResearchEngine Facade Integration
# =============================================================================

@pytest.mark.anyio
async def test_universal_research_engine_facade_synthesis(sample_attention_record):
    """Validates that UniversalResearchEngine exposes synthesize_answer cleanly."""
    engine = UniversalResearchEngine()

    synthesis = await engine.synthesize_answer(
        question="What is the Transformer BLEU score on WMT 2014 English-to-German?",
        sources=[sample_attention_record],
    )

    assert isinstance(synthesis, GroundedAnswerSynthesis)
    assert len(synthesis.references) >= 1
    assert synthesis.overall_confidence_score > 0.0


# =============================================================================
# Feature 12: GoalVerifier Integration
# =============================================================================

@pytest.mark.anyio
async def test_goal_verifier_synthesis_grounded(sample_attention_record, sample_low_resource_record):
    """Validates GoalVerifier evaluates RESEARCH_SYNTHESIS_GROUNDED, RESEARCH_CITATION_MAPPING_VALID, and RESEARCH_CONTRADICTION_DETECTED."""
    engine = UniversalResearchEngine()

    synthesis = await engine.synthesize_answer(
        question="Compare Transformer performance between standard and low-resource regimes",
        sources=[sample_attention_record, sample_low_resource_record],
        candidate_claims=[
            "The Transformer achieves state-of-the-art results on WMT 2014.",
            "The Transformer fails to achieve acceptable BLEU scores in low-resource environments.",
        ],
    )

    verifier = GoalVerifier()

    # 1. Test RESEARCH_SYNTHESIS_GROUNDED
    req_grounded = GoalRequirement(
        requirement_id="req_synth_01",
        description="Verify synthesis is grounded in source passages",
        verification_type=VerificationType.RESEARCH_SYNTHESIS_GROUNDED,
        parameters={"synthesis": synthesis, "min_facts": 1},
    )
    res_grounded = verifier.evaluate_requirement(req_grounded)
    assert res_grounded.status == VerificationStatus.SUCCESS

    # 2. Test RESEARCH_CITATION_MAPPING_VALID
    req_cite = GoalRequirement(
        requirement_id="req_cite_01",
        description="Verify citation mapping is complete and provenance valid",
        verification_type=VerificationType.RESEARCH_CITATION_MAPPING_VALID,
        parameters={"synthesis": synthesis},
    )
    res_cite = verifier.evaluate_requirement(req_cite)
    assert res_cite.status == VerificationStatus.SUCCESS

    # 3. Test RESEARCH_CONTRADICTION_DETECTED
    req_contra = GoalRequirement(
        requirement_id="req_contra_01",
        description="Verify contradictions were detected",
        verification_type=VerificationType.RESEARCH_CONTRADICTION_DETECTED,
        parameters={"synthesis": synthesis, "min_contradictions": 1},
    )
    res_contra = verifier.evaluate_requirement(req_contra)
    assert res_contra.status == VerificationStatus.SUCCESS
