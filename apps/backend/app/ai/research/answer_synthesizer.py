"""Evidence-Grounded Research Answer Synthesis Engine for Phase 10L-C.

Unifies question understanding, literature retrieval, evidence graphs, passage-grounded answer
generation, claim-level citation mapping, contradiction detection, epistemic claim classification,
uncertainty quantification, and local Ollama model execution without mandatory cloud APIs.
"""

import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import structlog

from app.ai.research.citation_mapper import ClaimCitationMapper
from app.ai.research.contradiction_detector import ResearchContradictionDetector
from app.ai.research.epistemic_classifier import EpistemicClassifier
from app.ai.research.evidence_graph_builder import EvidenceGraphBuilder
from app.ai.research.literature_discovery import LiteratureDiscoveryEngine
from app.ai.research.models import (
    ClaimEpistemicStatus,
    ConfidenceLevel,
    ContradictionReport,
    GroundedAnswerSynthesis,
    GroundedClaim,
    QuestionAnalysis,
    ReferenceEntry,
    ScholarlySourceRecord,
    SynthesisMode,
)
from app.ai.research.question_analyzer import ResearchQuestionAnalyzer
from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine

logger = structlog.get_logger("answer_synthesizer")


class EvidenceGroundedSynthesizer:
    """Intelligent research synthesis engine generating evidence-grounded answers with claim-level citations."""

    def __init__(
        self,
        runtime_engine: Optional[UniversalAIRuntimeEngine] = None,
        lit_discovery: Optional[LiteratureDiscoveryEngine] = None,
        question_analyzer: Optional[ResearchQuestionAnalyzer] = None,
        contradiction_detector: Optional[ResearchContradictionDetector] = None,
        citation_mapper: Optional[ClaimCitationMapper] = None,
        epistemic_classifier: Optional[EpistemicClassifier] = None,
    ) -> None:
        self.runtime = runtime_engine or UniversalAIRuntimeEngine()
        self.lit_discovery = lit_discovery or LiteratureDiscoveryEngine()
        self.citation_mapper = citation_mapper or ClaimCitationMapper()
        self.question_analyzer = question_analyzer or ResearchQuestionAnalyzer(runtime_engine=self.runtime)
        self.contradiction_detector = contradiction_detector or ResearchContradictionDetector()
        self.epistemic_classifier = epistemic_classifier or EpistemicClassifier(citation_mapper=self.citation_mapper)

    def _split_into_claim_propositions(self, text: str) -> List[str]:
        """Extracts individual assertive sentences/propositions from generated text for verification."""
        # Split on sentence boundaries
        raw_sentences = re.split(r"(?<=[.!?])\s+", text)
        cleaned: List[str] = []
        for s in raw_sentences:
            s_clean = re.sub(r"\[\d+\]", "", s).strip()  # strip inline citation tags for verification
            # Skip headers, empty lines, bullet symbols
            s_clean = re.sub(r"^[#*-]+\s*", "", s_clean).strip()
            if len(s_clean) > 20 and not s_clean.lower().startswith(("in conclusion", "to summarize", "table of contents", "references")):
                cleaned.append(s_clean)
        return cleaned

    def _compute_overall_confidence(
        self,
        verified_facts: List[GroundedClaim],
        derived_inferences: List[GroundedClaim],
        unsupported_claims: List[GroundedClaim],
        contradictions: List[ContradictionReport],
        sources_count: int,
    ) -> Tuple[ConfidenceLevel, float]:
        """Calculates quantitative and categorical confidence for the overall synthesis."""
        total_claims = len(verified_facts) + len(derived_inferences) + len(unsupported_claims)
        if total_claims == 0:
            return ConfidenceLevel.UNCERTAIN, 0.20

        # Weighted score: facts=1.0, inferences=0.7, unsupported=0.0
        score = (len(verified_facts) * 1.0 + len(derived_inferences) * 0.70) / total_claims

        # Multi-source corroboration boost
        multi_source_facts = sum(1 for f in verified_facts if f.independent_sources_count >= 2)
        if multi_source_facts >= 2:
            score = min(0.98, score + 0.08)

        # Contradiction penalty if unresolved
        if contradictions:
            penalty = min(0.20, len(contradictions) * 0.05)
            score = max(0.25, score - penalty)

        # Source diversity check
        if sources_count >= 3:
            score = min(0.99, score + 0.05)
        elif sources_count == 1:
            score = min(0.85, score)

        score = round(score, 2)

        if score >= 0.85:
            conf_level = ConfidenceLevel.HIGH
        elif score >= 0.65:
            conf_level = ConfidenceLevel.MEDIUM
        elif score >= 0.40:
            conf_level = ConfidenceLevel.LOW
        else:
            conf_level = ConfidenceLevel.UNCERTAIN

        return conf_level, score

    async def _generate_synthesis_narrative(
        self,
        question: str,
        subtopics: List[str],
        numbered_passages: List[Dict[str, Any]],
        contradictions: List[ContradictionReport],
        model_id: str = "qwen3:8b",
    ) -> Tuple[str, str, str, bool]:
        """Generates evidence-grounded narrative using local Ollama model with deterministic fallback.

        Returns:
            Tuple of (grounded_response, executive_summary, model_name, is_local)
        """
        # Format passage context for model prompting
        passage_context_lines = []
        for p in numbered_passages:
            cite_key = p["citation_key"]
            title = p["title"]
            text = p["text"]
            year = f"({p.get('year')})" if p.get("year") else ""
            passage_context_lines.append(f"{cite_key} {title} {year}:\n\"{text}\"")

        context_str = "\n\n".join(passage_context_lines)

        contradiction_context_lines = []
        for c in contradictions:
            contradiction_context_lines.append(
                f"- Conflict on '{c.topic_or_claim}': Source A ({c.source_a_citation.get('title')}) reports '{c.source_a_summary}', "
                f"whereas Source B ({c.source_b_citation.get('title')}) reports '{c.source_b_summary}'."
            )
        contradiction_str = "\n".join(contradiction_context_lines) if contradiction_context_lines else "None detected."

        prompt = (
            f"You are an expert scientific research synthesizer.\n"
            f"Answer the research inquiry based STRICTLY AND EXCLUSIVELY on the provided source passages below.\n"
            f"Attach citation markers like [1], [2] to every factual assertion.\n"
            f"Highlight any contradictions or conflicting findings.\n\n"
            f"RESEARCH INQUIRY:\n{question}\n\n"
            f"SUBTOPICS:\n" + "\n".join(f"- {st}" for st in subtopics) + "\n\n"
            f"VERIFIED EVIDENCE PASSAGES:\n{context_str}\n\n"
            f"CONTRADICTIONS IDENTIFIED:\n{contradiction_str}\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Produce a detailed, structured, evidence-grounded synthesis addressing the subtopics.\n"
            f"2. Every factual statement MUST cite the relevant passage tag (e.g. [1]).\n"
            f"3. Explicitly distinguish between confirmed facts and derived inferences or limitations.\n"
        )

        # Attempt inference via local Ollama provider through UniversalAIRuntimeEngine
        model_used = model_id
        is_local = True
        grounded_narrative = ""

        try:
            res = await self.runtime.reason(prompt=prompt, model_id=model_id)
            if res and res.text_or_data and len(res.text_or_data.strip()) > 80:
                raw_text = res.text_or_data.strip()
                # If model returned simulated/fallback header, clean it
                if not raw_text.startswith("[Ollama Engine") and not raw_text.startswith("[Reasoning -"):
                    grounded_narrative = raw_text
                    model_used = f"ollama/{model_id}"
        except Exception as e:
            logger.debug("Local Ollama synthesis runtime unavailable or timed out, using deterministic grounded synthesis", error=str(e))

        # High-fidelity deterministic grounded synthesis fallback
        if not grounded_narrative:
            model_used = "local_deterministic_synthesis"
            sections: List[str] = []

            # 1. Topic Overview & Core Mechanisms
            if numbered_passages:
                p0 = numbered_passages[0]
                sections.append(
                    f"### Overview & Core Principles\n"
                    f"Evidence from {p0['title']} {p0['citation_key']} establishes foundational principles regarding {question}. "
                    f"Specifically, {p0['text']} {p0['citation_key']}."
                )

            # 2. Detailed Findings across subtopics
            if len(numbered_passages) > 1:
                findings_lines = ["### Empirical Findings & Architectural Evaluation"]
                for i, p in enumerate(numbered_passages[1:], start=2):
                    findings_lines.append(
                        f"In {p['title']} {p['citation_key']}, researchers observe that {p['text']} {p['citation_key']}."
                    )
                sections.append("\n\n".join(findings_lines))

            # 3. Contradictions & Divergent Regimes
            if contradictions:
                contra_lines = ["### Comparative Divergence & Conflicting Findings"]
                for c in contradictions:
                    contra_lines.append(
                        f"A notable divergence occurs regarding {c.topic_or_claim} ({c.nature_of_conflict}). "
                        f"While findings in {c.source_a_citation.get('title', 'Source A')} state that '{c.source_a_summary}', "
                        f"evidence in {c.source_b_citation.get('title', 'Source B')} indicates that '{c.source_b_summary}'. "
                        f"{c.resolution_or_synthesis}"
                    )
                sections.append("\n\n".join(contra_lines))

            # 4. Synthesized Conclusions
            conclusion_lines = [
                "### Synthesis & Methodological Assessment",
                f"Overall evidence synthesizes {len(numbered_passages)} source passages across the inquiry subtopics. "
                f"Core factual assertions are corroborated by verified literature passages, while performance bounds "
                f"remain contingent on experimental conditions.",
            ]
            sections.append("\n\n".join(conclusion_lines))

            grounded_narrative = "\n\n".join(sections)

        # Executive summary generation
        exec_summary = (
            f"Evidence-grounded synthesis addressing '{question}'. "
            f"Based on {len(numbered_passages)} literature source passages, core mechanisms and empirical findings "
            f"are analyzed across {len(subtopics)} subtopics. "
            f"{'Identified ' + str(len(contradictions)) + ' key contradiction(s) across experimental regimes.' if contradictions else 'Literature exhibits broad empirical agreement.'}"
        )

        return grounded_narrative, exec_summary, model_used, is_local

    async def synthesize(
        self,
        question: str,
        sources: Optional[List[Union[ScholarlySourceRecord, Dict[str, Any]]]] = None,
        evidence_builder: Optional[EvidenceGraphBuilder] = None,
        mode: SynthesisMode = SynthesisMode.GROUNDED_STRICT,
        candidate_claims: Optional[List[str]] = None,
        max_sources: int = 8,
        model_id: str = "qwen3:8b",
    ) -> GroundedAnswerSynthesis:
        """Executes the complete Phase 10L-C evidence-grounded research synthesis workflow.

        Args:
            question: User research inquiry.
            sources: Pre-retrieved source records (optional; if None, queries LiteratureDiscoveryEngine).
            evidence_builder: Pre-built EvidenceGraphBuilder (optional; if None, instantiates fresh).
            mode: SynthesisMode (GROUNDED_STRICT, BALANCED, EXPLORATORY).
            candidate_claims: Optional explicit claims to evaluate and synthesize alongside narrative.
            max_sources: Maximum number of literature sources to ingest.
            model_id: Local Ollama model identifier (default: 'qwen3:8b').

        Returns:
            GroundedAnswerSynthesis object.
        """
        start_time = time.time()
        self.citation_mapper.reset()

        # Step 1: Understand question and identify subtopics
        analysis: QuestionAnalysis = await self.question_analyzer.analyze_question_async(question)
        logger.info("Question analyzed", subtopics=analysis.subtopics, domain=analysis.domain)

        # Step 2: Initialize or reuse EvidenceGraphBuilder
        builder = evidence_builder or EvidenceGraphBuilder()

        # Step 3: Retrieve and ingest literature if sources not already provided
        ingested_sources: List[ScholarlySourceRecord] = []
        if sources is not None:
            for s in sources[:max_sources]:
                builder.add_scholarly_source(s, extract_passages=True)
                if isinstance(s, ScholarlySourceRecord):
                    ingested_sources.append(s)
        else:
            # Multi-provider literature search using LiteratureDiscoveryEngine from Phase 10L-A
            search_query = analysis.search_queries[0] if analysis.search_queries else question
            lit_res = self.lit_discovery.search_literature(
                query=search_query,
                limit=max_sources,
            )
            for s in lit_res.sources:
                builder.add_scholarly_source(s, extract_passages=True)
                ingested_sources.append(s)

        # Step 4: Detect contradictions between sources in the evidence graph
        contradictions = self.contradiction_detector.detect_contradictions(
            builder,
            candidate_claims=candidate_claims,
        )

        # Step 5: Prepare numbered passages and register citations
        numbered_passages: List[Dict[str, Any]] = []
        for psg_id, psg in builder._passages.items():
            src_node = builder.graph.get_node(psg.source_id)
            props = src_node.properties if src_node else builder._sources.get(psg.source_id, {})
            ref = self.citation_mapper.register_source(psg.source_id, props)
            numbered_passages.append({
                "passage_id": psg_id,
                "source_id": psg.source_id,
                "text": psg.text,
                "title": props.get("title", "Untitled"),
                "year": props.get("publication_year"),
                "citation_key": ref.citation_key,
                "citation_number": ref.citation_number,
            })

        # Sort passages by citation number
        numbered_passages.sort(key=lambda p: p["citation_number"])

        # Step 6: Generate grounded answer narrative with local model / fallback
        narrative, exec_summary, model_name, is_local = await self._generate_synthesis_narrative(
            question=question,
            subtopics=analysis.subtopics,
            numbered_passages=numbered_passages,
            contradictions=contradictions,
            model_id=model_id,
        )

        # Step 7: Proposition extraction & Epistemic classification
        # Extract sentences from generated narrative to verify every statement
        extracted_propositions = self._split_into_claim_propositions(narrative)
        if candidate_claims:
            for c in candidate_claims:
                if c not in extracted_propositions:
                    extracted_propositions.append(c)

        verified_facts, derived_inferences, unsupported_claims = self.epistemic_classifier.classify_statements(
            extracted_propositions,
            builder,
        )

        # Strict Epistemic Enforcement (Feature 6):
        # Prevent unsupported claims from appearing as verified facts!
        if mode == SynthesisMode.GROUNDED_STRICT:
            # In strict mode, unsupported statements are isolated completely
            for fact in list(verified_facts):
                if fact.epistemic_status != ClaimEpistemicStatus.VERIFIED_FACT:
                    verified_facts.remove(fact)
                    unsupported_claims.append(fact)

        # Step 8: Identify uncertainties and evidence gaps
        uncertainties_and_gaps: List[str] = []
        if len(numbered_passages) == 0:
            uncertainties_and_gaps.append(f"No scholarly literature passages could be retrieved for question: '{question}'.")
        elif len(numbered_passages) < 3:
            uncertainties_and_gaps.append("Limited passage density in retrieved corpus: broader evidence is recommended.")

        if contradictions:
            for c in contradictions:
                uncertainties_and_gaps.append(
                    f"Contradictory findings regarding {c.topic_or_claim}: conclusions subject to experimental regime."
                )

        if unsupported_claims:
            uncertainties_and_gaps.append(
                f"{len(unsupported_claims)} assertion(s) lacked direct passage grounding in the retrieved corpus."
            )

        if analysis.target_conditions:
            uncertainties_and_gaps.append(
                f"Specific conditions analyzed ({', '.join(analysis.target_conditions)}) may not generalize across all environments."
            )

        # Step 9: Compute confidence scores
        conf_level, conf_score = self._compute_overall_confidence(
            verified_facts=verified_facts,
            derived_inferences=derived_inferences,
            unsupported_claims=unsupported_claims,
            contradictions=contradictions,
            sources_count=len(builder._sources),
        )

        duration = time.time() - start_time
        all_refs = self.citation_mapper.get_all_references()

        return GroundedAnswerSynthesis(
            research_question=question,
            subtopics=analysis.subtopics,
            executive_summary=exec_summary,
            grounded_response=narrative,
            verified_facts=verified_facts,
            derived_inferences=derived_inferences,
            unsupported_claims=unsupported_claims,
            contradictions=contradictions,
            uncertainties_and_gaps=uncertainties_and_gaps,
            references=all_refs,
            overall_confidence=conf_level,
            overall_confidence_score=conf_score,
            model_used=model_name,
            is_local_model=is_local,
            duration_sec=duration,
        )
