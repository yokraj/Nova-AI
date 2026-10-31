"""Research Contradiction Detector for Phase 10L-C: Evidence-Grounded Research Answer Synthesis.

Detects, analyzes, and classifies contradictions, numerical conflicts, and conditional
discrepancies between scholarly sources in the evidence graph.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple
import structlog

from app.ai.research.evidence_graph_builder import (
    AFFIRMATIVE_IMPROVEMENT_WORDS,
    NEGATION_WORDS,
    OPPOSING_VERB_PAIRS,
    EvidenceGraphBuilder,
)
from app.ai.research.models import ContradictionReport

logger = structlog.get_logger("contradiction_detector")


class ResearchContradictionDetector:
    """Detects and characterizes conflicts, polarity reversals, and numerical disagreements between sources."""

    def __init__(self) -> None:
        pass

    def _extract_tokens(self, text: str) -> Set[str]:
        """Extracts normalized alphabetic tokens."""
        return set(re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()))

    def _extract_numbers(self, text: str) -> List[Tuple[float, str]]:
        """Extracts numerical values with following unit if present."""
        matches = re.findall(r"(\d+(?:\.\d+)?)\s*(%|percent|x|times|ms|seconds|bleu|folds)?", text.lower())
        results: List[Tuple[float, str]] = []
        for val_str, unit in matches:
            try:
                results.append((float(val_str), unit))
            except ValueError:
                continue
        return results

    def _detect_polarity_conflict(self, text_a: str, text_b: str) -> bool:
        """Detects if two passages assert opposing polarities about the same subject."""
        tokens_a = self._extract_tokens(text_a)
        tokens_b = self._extract_tokens(text_b)

        # Check overlapping semantic content (at least 2 substantive shared tokens)
        common = tokens_a.intersection(tokens_b) - {"the", "and", "for", "with", "that", "this", "from"}
        if len(common) < 2:
            return False

        has_neg_a = bool(tokens_a.intersection(NEGATION_WORDS))
        has_pos_a = bool(tokens_a.intersection(AFFIRMATIVE_IMPROVEMENT_WORDS))
        has_neg_b = bool(tokens_b.intersection(NEGATION_WORDS))
        has_pos_b = bool(tokens_b.intersection(AFFIRMATIVE_IMPROVEMENT_WORDS))

        if (has_pos_a and has_neg_b) or (has_neg_a and has_pos_b):
            return True

        for set_pos, set_neg in OPPOSING_VERB_PAIRS:
            if (tokens_a.intersection(set_pos) and tokens_b.intersection(set_neg)) or (tokens_a.intersection(set_neg) and tokens_b.intersection(set_pos)):
                return True

        # Divergence where one source asserts negative/failure while other is affirmative
        if (has_neg_a and not has_neg_b) or (has_neg_b and not has_neg_a):
            return True

        return False

    def _detect_numerical_discrepancy(self, text_a: str, text_b: str) -> Optional[Tuple[float, float, str]]:
        """Detects if two passages report significantly different numbers for the same metric/unit."""
        tokens_a = self._extract_tokens(text_a)
        tokens_b = self._extract_tokens(text_b)
        common = tokens_a.intersection(tokens_b) - {"the", "and", "for", "with", "that", "this"}
        if len(common) < 2:
            return None

        nums_a = self._extract_numbers(text_a)
        nums_b = self._extract_numbers(text_b)

        for val_a, unit_a in nums_a:
            for val_b, unit_b in nums_b:
                if unit_a == unit_b and unit_a != "":
                    if abs(val_a - val_b) > 0.001 and max(val_a, val_b) > 0:
                        diff_ratio = abs(val_a - val_b) / max(val_a, val_b)
                        if diff_ratio >= 0.25:  # >= 25% difference
                            return (val_a, val_b, unit_a)
        return None

    def _detect_conditional_variation(self, text_a: str, text_b: str) -> Optional[str]:
        """Detects whether findings differ due to divergent experimental conditions."""
        condition_markers = [
            ("low-resource", "high-resource"),
            ("small vocabulary", "large vocabulary"),
            ("ambient temperature", "high temperature"),
            ("mobile hardware", "server hardware"),
            ("few-shot", "fully supervised"),
            ("synthetic data", "real-world data"),
            ("short sequence", "long sequence"),
        ]
        text_a_lower = text_a.lower()
        text_b_lower = text_b.lower()

        for cond_a, cond_b in condition_markers:
            if (cond_a in text_a_lower and cond_b in text_b_lower) or (cond_b in text_a_lower and cond_a in text_b_lower):
                return f"Tested under diverging conditions: '{cond_a}' vs '{cond_b}'"

        return None

    def detect_contradictions(
        self,
        evidence_builder: EvidenceGraphBuilder,
        candidate_claims: Optional[List[str]] = None,
    ) -> List[ContradictionReport]:
        """Scans the evidence graph for cross-source contradictions and discrepancies.

        Args:
            evidence_builder: Ingested EvidenceGraphBuilder instance.
            candidate_claims: Optional list of explicit candidate claims to evaluate.

        Returns:
            List of structured ContradictionReport objects.
        """
        contradictions: List[ContradictionReport] = []

        # 1. Evaluate explicit candidate claims for contradictions if provided
        if candidate_claims:
            for c in candidate_claims:
                detail = evidence_builder.verify_claim(c)
                if detail.contradicting_passages:
                    contra_p = detail.contradicting_passages[0]
                    contra_src_id = contra_p.get("source_id")
                    contra_src_node = evidence_builder.graph.get_node(contra_src_id) if contra_src_id else None
                    contra_props = contra_src_node.properties if contra_src_node else {}

                    sup_src_props = {}
                    sup_text = c
                    if detail.supporting_passages:
                        sup_p = detail.supporting_passages[0]
                        sup_text = sup_p.get("text", c)
                        sup_src_node = evidence_builder.graph.get_node(sup_p.get("source_id"))
                        if sup_src_node:
                            sup_src_props = sup_src_node.properties

                    contradictions.append(
                        ContradictionReport(
                            topic_or_claim=c,
                            source_a_summary=sup_text,
                            source_a_citation={
                                "source_id": sup_src_props.get("source_id", "source_claim"),
                                "title": sup_src_props.get("title", "Supporting Evidence"),
                                "doi": sup_src_props.get("doi"),
                                "year": sup_src_props.get("publication_year"),
                                "authors": sup_src_props.get("authors", []),
                            },
                            source_b_summary=contra_p.get("text", ""),
                            source_b_citation={
                                "source_id": contra_src_id or "contra_source",
                                "title": contra_props.get("title", "Contradicting Source"),
                                "doi": contra_props.get("doi"),
                                "year": contra_props.get("publication_year"),
                                "authors": contra_props.get("authors", []),
                            },
                            nature_of_conflict="POLARITY_OPPOSING",
                            resolution_or_synthesis=f"Claim '{c}' is directly contested or contradicted by findings in '{contra_props.get('title', 'evidence source')}'.",
                        )
                    )

        # 2. Leverage built-in graph contradiction detection from Phase 10L-B
        raw_graph_contradictions = evidence_builder.detect_contradictory_evidence()
        for item in raw_graph_contradictions:
            claim_id = item.get("claim_id")
            claim_text = item.get("statement", f"Claim {claim_id}")
            supports = item.get("supporting_passages", [])
            contras = item.get("contradicting_passages", [])

            sup_text = supports[0].get("text") if supports else "Supported finding"
            sup_src_id = supports[0].get("source_id") if supports else None
            contra_text = contras[0].get("text") if contras else "Contradicting finding"
            contra_src_id = contras[0].get("source_id") if contras else None

            src_a_node = evidence_builder.graph.get_node(sup_src_id) if sup_src_id else None
            src_b_node = evidence_builder.graph.get_node(contra_src_id) if contra_src_id else None

            src_a_props = src_a_node.properties if src_a_node else {}
            src_b_props = src_b_node.properties if src_b_node else {}

            contradictions.append(
                ContradictionReport(
                    topic_or_claim=claim_text,
                    source_a_summary=sup_text,
                    source_a_citation={
                        "source_id": sup_src_id or "src_a",
                        "title": src_a_props.get("title", "Supporting Source"),
                        "doi": src_a_props.get("doi"),
                        "year": src_a_props.get("publication_year"),
                        "authors": src_a_props.get("authors", []),
                    },
                    source_b_summary=contra_text,
                    source_b_citation={
                        "source_id": contra_src_id or "src_b",
                        "title": src_b_props.get("title", "Contradicting Source"),
                        "doi": src_b_props.get("doi"),
                        "year": src_b_props.get("publication_year"),
                        "authors": src_b_props.get("authors", []),
                    },
                    nature_of_conflict="POLARITY_OPPOSING",
                    resolution_or_synthesis=(
                        f"Direct polarity divergence: one source confirms '{claim_text}', "
                        f"while another explicitly refutes or reports contrary outcomes."
                    ),
                )
            )

        # 2. Cross-compare passages across distinct sources in the evidence graph
        passages = list(evidence_builder._passages.values())
        seen_pairs: Set[Tuple[str, str]] = set()

        for i, psg_a in enumerate(passages):
            for j in range(i + 1, len(passages)):
                psg_b = passages[j]
                if psg_a.source_id == psg_b.source_id:
                    continue  # Same paper, skip intra-paper variations

                pair_key = tuple(sorted([psg_a.passage_id, psg_b.passage_id]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                src_a_node = evidence_builder.graph.get_node(psg_a.source_id)
                src_b_node = evidence_builder.graph.get_node(psg_b.source_id)
                src_a_props = src_a_node.properties if src_a_node else {}
                src_b_props = src_b_node.properties if src_b_node else {}

                # Check numerical discrepancies
                num_diff = self._detect_numerical_discrepancy(psg_a.text, psg_b.text)
                if num_diff:
                    val_a, val_b, unit = num_diff
                    # Check if already recorded
                    already_recorded = any(
                        c.source_a_citation.get("source_id") in (psg_a.source_id, psg_b.source_id)
                        and c.nature_of_conflict == "NUMERICAL_DISCREPANCY"
                        for c in contradictions
                    )
                    if not already_recorded:
                        contradictions.append(
                            ContradictionReport(
                                topic_or_claim=f"Quantitative measurement discrepancy ({unit})",
                                source_a_summary=psg_a.text,
                                source_a_citation={
                                    "source_id": psg_a.source_id,
                                    "title": src_a_props.get("title", "Source A"),
                                    "doi": src_a_props.get("doi"),
                                    "year": src_a_props.get("publication_year"),
                                    "authors": src_a_props.get("authors", []),
                                },
                                source_b_summary=psg_b.text,
                                source_b_citation={
                                    "source_id": psg_b.source_id,
                                    "title": src_b_props.get("title", "Source B"),
                                    "doi": src_b_props.get("doi"),
                                    "year": src_b_props.get("publication_year"),
                                    "authors": src_b_props.get("authors", []),
                                },
                                nature_of_conflict="NUMERICAL_DISCREPANCY",
                                resolution_or_synthesis=(
                                    f"Source reports {val_a}{unit} while contrasting source reports {val_b}{unit}. "
                                    f"Discrepancy may stem from differing experimental methodologies or measurement baselines."
                                ),
                            )
                        )

                # Check conditional variation
                cond_diff = self._detect_conditional_variation(psg_a.text, psg_b.text)
                if cond_diff and self._detect_polarity_conflict(psg_a.text, psg_b.text):
                    already_recorded = any(
                        c.source_a_citation.get("source_id") in (psg_a.source_id, psg_b.source_id)
                        and c.nature_of_conflict == "CONDITIONAL_VARIATION"
                        for c in contradictions
                    )
                    if not already_recorded:
                        contradictions.append(
                            ContradictionReport(
                                topic_or_claim=f"Regime-dependent variation: {cond_diff}",
                                source_a_summary=psg_a.text,
                                source_a_citation={
                                    "source_id": psg_a.source_id,
                                    "title": src_a_props.get("title", "Source A"),
                                    "doi": src_a_props.get("doi"),
                                    "year": src_a_props.get("publication_year"),
                                    "authors": src_a_props.get("authors", []),
                                },
                                source_b_summary=psg_b.text,
                                source_b_citation={
                                    "source_id": psg_b.source_id,
                                    "title": src_b_props.get("title", "Source B"),
                                    "doi": src_b_props.get("doi"),
                                    "year": src_b_props.get("publication_year"),
                                    "authors": src_b_props.get("authors", []),
                                },
                                nature_of_conflict="CONDITIONAL_VARIATION",
                                resolution_or_synthesis=(
                                    f"Empirical findings diverge under different operational regimes ({cond_diff}). "
                                    f"Performance advantages reported in one condition do not generalize unconditionally."
                                ),
                            )
                        )

                # Check general polarity conflict
                elif self._detect_polarity_conflict(psg_a.text, psg_b.text):
                    already_recorded = any(
                        (c.source_a_citation.get("source_id") == psg_a.source_id and c.source_b_citation.get("source_id") == psg_b.source_id)
                        or (c.source_a_citation.get("source_id") == psg_b.source_id and c.source_b_citation.get("source_id") == psg_a.source_id)
                        for c in contradictions
                    )
                    if not already_recorded:
                        common_words = list(self._extract_tokens(psg_a.text).intersection(self._extract_tokens(psg_b.text)) - {"the", "and", "for", "with"})
                        topic_hint = " ".join(common_words[:3]) if common_words else "Efficacy or performance"
                        contradictions.append(
                            ContradictionReport(
                                topic_or_claim=f"Contrasting findings regarding {topic_hint}",
                                source_a_summary=psg_a.text,
                                source_a_citation={
                                    "source_id": psg_a.source_id,
                                    "title": src_a_props.get("title", "Source A"),
                                    "doi": src_a_props.get("doi"),
                                    "year": src_a_props.get("publication_year"),
                                    "authors": src_a_props.get("authors", []),
                                },
                                source_b_summary=psg_b.text,
                                source_b_citation={
                                    "source_id": psg_b.source_id,
                                    "title": src_b_props.get("title", "Source B"),
                                    "doi": src_b_props.get("doi"),
                                    "year": src_b_props.get("publication_year"),
                                    "authors": src_b_props.get("authors", []),
                                },
                                nature_of_conflict="POLARITY_OPPOSING",
                                resolution_or_synthesis=(
                                    f"Sources present conflicting conclusions regarding {topic_hint}. "
                                    f"Requires careful verification of sample size, model architecture, or benchmark evaluation setup."
                                ),
                            )
                        )

        logger.info("Contradiction scan completed", total_contradictions=len(contradictions))
        return contradictions
