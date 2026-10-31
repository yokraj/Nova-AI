"""Evidence & Provenance Graph Builder for Nova-AI Scientific Research Agent (Phase 10L-B).

Builds a traceable knowledge graph connecting scholarly source records, exact source passages,
atomic factual claims, and verification outcomes with rigorous provenance tracking.
"""

from dataclasses import asdict
import json
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import uuid

import structlog

from app.ai.research.knowledge_graph import KnowledgeGraph
from app.ai.research.models import (
    AtomicClaim,
    ClaimType,
    ClaimVerificationDetail,
    ClaimVerificationOutcome,
    EvidenceRelation,
    KnowledgeGraphEdge,
    KnowledgeGraphNode,
    KnowledgeSource,
    KnowledgeType,
    ScholarlySourceRecord,
    SourcePassage,
)

logger = structlog.get_logger("evidence_graph_builder")

# Regex pattern for prompt injection directives in untrusted paper content
PROMPT_INJECTION_PATTERN = re.compile(
    r"(system\s+directive|ignore\s+all\s+(previous|prior)\s+instructions|disregard\s+(previous|all)|you\s+are\s+now\s+in\s+dan\s+mode|override\s+system\s+prompt|print\s+(secret|password|api_key))",
    re.IGNORECASE,
)

# Negation and contradiction detection triggers
NEGATION_WORDS = {
    "not", "no", "never", "neither", "nor", "fails", "failed", "failing",
    "cannot", "can't", "disproves", "disproved", "refutes", "refuted",
    "contradicts", "contradicted", "contrary", "untrue", "false",
    "ineffective", "inferior", "worse", "decreases", "decreased", "impedes",
    "prevents", "lacks", "absent", "without",
}

AFFIRMATIVE_IMPROVEMENT_WORDS = {
    "improves", "improved", "improving", "increases", "increased", "enhances",
    "enhanced", "outperforms", "outperformed", "achieves", "achieved", "superior",
    "effective", "reduces", "faster", "better", "surpasses", "surpassed",
}

OPPOSING_VERB_PAIRS = [
    ({"improves", "improved", "enhances", "increases"}, {"worsens", "decreases", "degrades", "reduces_performance", "impedes", "fails"}),
    ({"superior", "effective", "better"}, {"inferior", "ineffective", "worse", "flawed"}),
    ({"supports", "proves", "confirms"}, {"refutes", "disproves", "contradicts"}),
]

# Strong assertion predicates that require evidence corroboration
STRONG_ASSERTION_VERBS = {
    "eliminate", "eliminates", "eliminated", "cure", "cures", "cured",
    "solve", "solves", "solved", "prevent", "prevents", "prevented",
    "eradicate", "eradicates", "eradicated", "proves", "proven",
}

# Exploratory verbs that indicate topical mention rather than factual entailment
EXPLORATORY_VERBS = {
    "discuss", "discusses", "discussed", "review", "reviews", "reviewed",
    "survey", "surveys", "surveyed", "explore", "explores", "explored",
    "examine", "examines", "examined",
}

# Hedging markers indicating derived inferences rather than direct facts
HEDGING_MARKERS = [
    "suggests that", "we hypothesize", "hypothesize that", "indicates that",
    "may imply", "could indicate", "might suggest", "seems to be", "appears to",
    "posits that", "conjectures that", "speculate that", "is believed to",
]


class EvidenceGraphBuilder:
    """Constructs and navigates evidence graphs linking sources, passages, claims, and verification states."""

    def __init__(self, graph: Optional[KnowledgeGraph] = None) -> None:
        self.graph = graph or KnowledgeGraph(seed=False)
        self._sources: Dict[str, Dict[str, Any]] = {}
        self._passages: Dict[str, SourcePassage] = {}
        self._claims: Dict[str, AtomicClaim] = {}
        self._verifications: Dict[str, ClaimVerificationDetail] = {}
        # Track duplicate works by normalized DOI and normalized title to prevent artificial corroboration
        self._doi_to_source_id: Dict[str, str] = {}
        self._title_year_to_source_id: Dict[Tuple[str, Optional[int]], str] = {}

    def _clean_text(self, text: Optional[str]) -> str:
        """Normalizes whitespace and removes control characters."""
        if not text:
            return ""
        return re.sub(r"\s+", " ", str(text)).strip()

    def _normalize_title(self, title: str) -> str:
        """Normalizes a title for duplicate matching."""
        cleaned = re.sub(r"[^\w\s]", "", title.lower())
        return re.sub(r"\s+", " ", cleaned).strip()

    def add_scholarly_source(
        self,
        record: Union[ScholarlySourceRecord, KnowledgeSource, Dict[str, Any]],
        extract_passages: bool = True,
    ) -> str:
        """Ingests a scholarly source record into the knowledge graph with full provenance.

        Handles duplicate records conservatively by merging provider provenance
        without counting duplicates as independent corroborating works.

        Args:
            record: Source record or descriptor.
            extract_passages: If True, automatically extracts abstract passages.

        Returns:
            The source node ID in the graph.
        """
        # 1. Normalize input record fields
        if isinstance(record, ScholarlySourceRecord):
            rec_dict = record.model_dump()
        elif isinstance(record, KnowledgeSource):
            rec_dict = {
                "source_id": record.source_id,
                "title": record.title,
                "authors": [record.author] if record.author else [],
                "canonical_url": record.url_or_path,
                "abstract": record.extracted_text,
                "publication_year": int(record.publication_date[:4]) if (record.publication_date and record.publication_date[:4].isdigit()) else None,
                "provider": "knowledge_source",
                "retrieval_timestamp": time.time(),
                "contributing_providers": ["knowledge_source"],
                "provider_raw_ids": {},
                "is_untrusted_data": True,
            }
        elif isinstance(record, dict):
            rec_dict = dict(record)
        else:
            raise TypeError(f"Unsupported record type: {type(record)}")

        title = self._clean_text(rec_dict.get("title", "Untitled Source"))
        raw_doi = rec_dict.get("doi")
        normalized_doi = str(raw_doi).strip().lower() if raw_doi and str(raw_doi).strip() else None
        norm_title = self._normalize_title(title)
        pub_year = rec_dict.get("publication_year")

        # 2. Check for duplicate work (same DOI or matching title + year)
        existing_source_id: Optional[str] = None
        if normalized_doi and normalized_doi in self._doi_to_source_id:
            existing_source_id = self._doi_to_source_id[normalized_doi]
        elif (norm_title, pub_year) in self._title_year_to_source_id:
            cand_id = self._title_year_to_source_id[(norm_title, pub_year)]
            cand_node = self.graph.get_node(cand_id)
            cand_doi = cand_node.properties.get("doi") if cand_node else None
            # If both have explicit DOIs and they differ, they are distinct papers
            if normalized_doi and cand_doi and normalized_doi != cand_doi:
                existing_source_id = None
            else:
                existing_source_id = cand_id

        if existing_source_id:
            # Conservative deduplication: Merge provenance into existing node without duplicating
            existing_node = self.graph.get_node(existing_source_id)
            if existing_node:
                props = existing_node.properties
                prov = rec_dict.get("provider", "unknown")
                if prov not in props.get("contributing_providers", []):
                    props.setdefault("contributing_providers", []).append(prov)
                raw_pid = rec_dict.get("raw_provider_id")
                if raw_pid:
                    props.setdefault("provider_raw_ids", {})[prov] = raw_pid
                # Merge multi-provider list if passed in record
                for cp in rec_dict.get("contributing_providers", []):
                    if cp not in props["contributing_providers"]:
                        props["contributing_providers"].append(cp)
                for k, v in rec_dict.get("provider_raw_ids", {}).items():
                    props.setdefault("provider_raw_ids", {})[k] = v
                logger.debug("Merged duplicate source into existing node", source_id=existing_source_id, title=title)
                return existing_source_id

        # 3. Create fresh source node
        source_id = rec_dict.get("source_id") or f"src_{uuid.uuid4().hex[:10]}"
        # Ensure source_id is unique in graph
        while self.graph.get_node(source_id) is not None:
            source_id = f"src_{uuid.uuid4().hex[:10]}"

        # Check prompt injection on title
        title_injected = bool(PROMPT_INJECTION_PATTERN.search(title))

        contributing = rec_dict.get("contributing_providers") or ([rec_dict.get("provider")] if rec_dict.get("provider") else ["scholarly"])
        provider_ids = rec_dict.get("provider_raw_ids") or ({rec_dict.get("provider"): rec_dict.get("raw_provider_id")} if rec_dict.get("provider") and rec_dict.get("raw_provider_id") else {})

        source_props = {
            "source_id": source_id,
            "title": title,
            "doi": normalized_doi,  # Explicitly None if missing, never fabricated
            "canonical_url": rec_dict.get("canonical_url"),  # Explicitly None if missing
            "authors": rec_dict.get("authors", []),
            "publication_year": pub_year,
            "venue": rec_dict.get("venue"),
            "provider": rec_dict.get("provider", "unknown"),
            "contributing_providers": contributing,
            "provider_raw_ids": provider_ids,
            "retrieval_timestamp": rec_dict.get("retrieval_timestamp", time.time()),
            "full_text_available": bool(rec_dict.get("full_text_status") == "AVAILABLE"),
            "content_scope": "abstract" if not rec_dict.get("full_text_status") == "AVAILABLE" else "full_text",
            "is_untrusted_data": True,
            "prompt_injection_flagged": title_injected or bool(rec_dict.get("prompt_injection_flagged", False)),
        }

        node = KnowledgeGraphNode(
            node_id=source_id,
            label=title,
            type=KnowledgeType.SCHOLARLY_SOURCE,
            properties=source_props,
        )
        self.graph.add_node(node)
        self._sources[source_id] = source_props

        if normalized_doi:
            self._doi_to_source_id[normalized_doi] = source_id
        if norm_title:
            self._title_year_to_source_id[(norm_title, pub_year)] = source_id

        # 4. Extract passages from abstract / snippet
        if extract_passages:
            abstract_text = rec_dict.get("abstract") or rec_dict.get("extracted_text")
            if abstract_text and str(abstract_text).strip():
                psg_id = self.add_passage(
                    source_id=source_id,
                    text=str(abstract_text),
                    section="abstract",
                )
                self.extract_claims_from_passage(psg_id)

        return source_id

    def add_passage(
        self,
        source_id: str,
        text: str,
        section: str = "abstract",
        char_offset_start: Optional[int] = None,
        char_offset_end: Optional[int] = None,
    ) -> str:
        """Adds an exact passage snippet from a source to the graph.

        Args:
            source_id: The identifier of the parent source node.
            text: Raw excerpt text from the publication.
            section: Section label (e.g., 'abstract', 'introduction', 'results').
            char_offset_start: Character offset start in original document.
            char_offset_end: Character offset end in original document.

        Returns:
            The passage node ID in the graph.
        """
        source_node = self.graph.get_node(source_id)
        if not source_node:
            raise ValueError(f"Parent source '{source_id}' does not exist in graph.")

        cleaned = self._clean_text(text)
        passage_id = f"psg_{uuid.uuid4().hex[:10]}"

        # Prompt injection detection on passage
        injection_flagged = bool(PROMPT_INJECTION_PATTERN.search(cleaned))

        passage = SourcePassage(
            passage_id=passage_id,
            source_id=source_id,
            text=cleaned,
            section=section,
            char_offset_start=char_offset_start,
            char_offset_end=char_offset_end,
            is_untrusted_data=True,
            prompt_injection_flagged=injection_flagged,
            extracted_at=time.time(),
        )

        passage_props = passage.model_dump()
        node = KnowledgeGraphNode(
            node_id=passage_id,
            label=f"{section.capitalize()} passage ({cleaned[:40]}...)",
            type=KnowledgeType.PASSAGE,
            properties=passage_props,
        )
        self.graph.add_node(node)
        self._passages[passage_id] = passage

        # Directional edge: source -> contains_passage -> passage
        edge = KnowledgeGraphEdge(
            edge_id=f"edge_src_psg_{uuid.uuid4().hex[:8]}",
            source_id=source_id,
            target_id=passage_id,
            relation="contains_passage",
            weight=1.0,
        )
        self.graph.add_edge(edge)
        return passage_id

    def _split_into_sentences(self, text: str) -> List[str]:
        """Conservative sentence segmenter respecting common abbreviations."""
        # Protect common scientific abbreviations from splitting
        protected = text
        abbrevs = ["e.g.", "i.e.", "et al.", "Fig.", "Dr.", "Vol.", "No.", "vs.", "ca.", "approx."]
        for i, abb in enumerate(abbrevs):
            protected = protected.replace(abb, f"__ABB_{i}__")

        # Split on sentence terminals
        raw_sentences = re.split(r"(?<=[.!?])\s+", protected)

        sentences: List[str] = []
        for s in raw_sentences:
            for i, abb in enumerate(abbrevs):
                s = s.replace(f"__ABB_{i}__", abb)
            s_clean = s.strip()
            if len(s_clean) > 8:  # Ignore trivial sentence fragments
                sentences.append(s_clean)
        return sentences

    def extract_claims_from_passage(self, passage_id: str) -> List[AtomicClaim]:
        """Conservatively extracts atomic claims from an ingested passage.

        Separates direct declarative facts, numeric findings, and derived inferences.
        Strips adversarial prompt-injection commands. Never invents quotes or values.

        Args:
            passage_id: Passage node identifier.

        Returns:
            List of AtomicClaim objects added to the graph.
        """
        passage = self._passages.get(passage_id)
        if not passage:
            node = self.graph.get_node(passage_id)
            if node and node.type == KnowledgeType.PASSAGE:
                passage = SourcePassage(**node.properties)
            else:
                raise ValueError(f"Passage '{passage_id}' does not exist in graph.")

        raw_text = passage.text

        # Strip prompt injection commands from claim extraction if flagged
        if passage.prompt_injection_flagged:
            cleaned_for_claims = PROMPT_INJECTION_PATTERN.sub("[UNTRUSTED_INJECTION_REDACTED]", raw_text)
        else:
            cleaned_for_claims = raw_text

        sentences = self._split_into_sentences(cleaned_for_claims)
        extracted_claims: List[AtomicClaim] = []

        for sent in sentences:
            if "[UNTRUSTED_INJECTION_REDACTED]" in sent:
                continue  # Never convert prompt injection into claims

            # Detect derived inferences vs direct statements
            is_derived = any(marker in sent.lower() for marker in HEDGING_MARKERS)

            # Detect numerical values
            numeric_values = re.findall(r"\b\d+(?:\.\d+)?%?(?:\s*(?:BLEU|MB|GB|ms|seconds|nm|kg|M|B|K|mol|eV))?\b", sent)
            has_numeric = bool(numeric_values and any(c.isdigit() for c in sent))

            if is_derived:
                claim_type = ClaimType.DERIVED_INFERENCE
            elif has_numeric:
                claim_type = ClaimType.NUMERIC_FINDING
            else:
                claim_type = ClaimType.DIRECT_STATEMENT

            claim_id = f"clm_{uuid.uuid4().hex[:10]}"
            atomic = AtomicClaim(
                claim_id=claim_id,
                statement=sent,
                claim_type=claim_type,
                source_passage_id=passage_id,
                original_passage_text=passage.text,
                extracted_numerical_values=numeric_values,
                is_derived=is_derived,
                confidence_score=0.85 if is_derived else 1.0,
                created_at=time.time(),
            )

            claim_node = KnowledgeGraphNode(
                node_id=claim_id,
                label=sent[:60] + "..." if len(sent) > 60 else sent,
                type=KnowledgeType.CLAIM,
                properties=atomic.model_dump(),
            )
            self.graph.add_node(claim_node)
            self._claims[claim_id] = atomic
            extracted_claims.append(atomic)

            # Edge: passage -> asserts_claim -> claim
            edge = KnowledgeGraphEdge(
                edge_id=f"edge_psg_clm_{uuid.uuid4().hex[:8]}",
                source_id=passage_id,
                target_id=claim_id,
                relation="asserts_claim",
                weight=1.0,
            )
            self.graph.add_edge(edge)

        return extracted_claims

    def add_claim(
        self,
        claim: Union[AtomicClaim, str],
        source_passage_id: Optional[str] = None,
        claim_type: ClaimType = ClaimType.DIRECT_STATEMENT,
    ) -> str:
        """Explicitly adds an atomic claim to the evidence graph.

        If source_passage_id is None, the claim is treated as an ungrounded or candidate claim.

        Args:
            claim: AtomicClaim instance or natural-language statement.
            source_passage_id: Optional ID of the backing passage.
            claim_type: Classification of the claim.

        Returns:
            The claim node ID.
        """
        if isinstance(claim, str):
            claim_id = f"clm_{uuid.uuid4().hex[:10]}"
            orig_text = None
            if source_passage_id and source_passage_id in self._passages:
                orig_text = self._passages[source_passage_id].text
            atomic = AtomicClaim(
                claim_id=claim_id,
                statement=self._clean_text(claim),
                claim_type=claim_type,
                source_passage_id=source_passage_id,
                original_passage_text=orig_text,
                created_at=time.time(),
            )
        elif isinstance(claim, AtomicClaim):
            atomic = claim
            claim_id = atomic.claim_id
        else:
            raise TypeError(f"Unsupported claim type: {type(claim)}")

        node = KnowledgeGraphNode(
            node_id=claim_id,
            label=atomic.statement[:60] + "..." if len(atomic.statement) > 60 else atomic.statement,
            type=KnowledgeType.CLAIM,
            properties=atomic.model_dump(),
        )
        self.graph.add_node(node)
        self._claims[claim_id] = atomic

        if source_passage_id:
            edge = KnowledgeGraphEdge(
                edge_id=f"edge_psg_clm_{uuid.uuid4().hex[:8]}",
                source_id=source_passage_id,
                target_id=claim_id,
                relation="asserts_claim",
                weight=1.0,
            )
            self.graph.add_edge(edge)

        return claim_id

    def build_from_scholarly_records(
        self, records: List[Union[ScholarlySourceRecord, Dict[str, Any]]]
    ) -> KnowledgeGraph:
        """End-to-end pipeline: Ingests scholarly records, extracts passages and claims into graph.

        Args:
            records: List of scholarly source records.

        Returns:
            The populated KnowledgeGraph instance.
        """
        for rec in records:
            self.add_scholarly_source(rec, extract_passages=True)
        return self.graph

    def _extract_tokens(self, text: str) -> Set[str]:
        """Extracts normalized alphanumeric word tokens."""
        return set(re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", text.lower()))

    def _detect_polarity_conflict(self, claim_text: str, passage_text: str) -> bool:
        """Detects whether a passage directly contradicts or negates the claim statement."""
        claim_lower = claim_text.lower()
        passage_lower = passage_text.lower()

        # 1. Opposing verb pairs (e.g. claim has 'improves' while passage has 'degrades' or 'fails to improve')
        for positive_set, negative_set in OPPOSING_VERB_PAIRS:
            claim_has_pos = any(w in claim_lower for w in positive_set)
            passage_has_neg = any(w in passage_lower for w in negative_set)
            if claim_has_pos and passage_has_neg:
                return True

            claim_has_neg = any(w in claim_lower for w in negative_set)
            passage_has_pos = any(w in passage_lower for w in positive_set)
            if claim_has_neg and passage_has_pos:
                return True

        # 2. Negation prefix check (e.g., "does not improve", "failed to show", "cannot be")
        claim_tokens = self._extract_tokens(claim_lower)
        passage_tokens = self._extract_tokens(passage_lower)
        overlap = claim_tokens.intersection(passage_tokens)

        if len(overlap) >= 2:
            # If significant topic overlap exists, check for negation words in passage not in claim
            passage_negations = [w for w in NEGATION_WORDS if re.search(rf"\b{w}\b", passage_lower)]
            claim_negations = [w for w in NEGATION_WORDS if re.search(rf"\b{w}\b", claim_lower)]

            if passage_negations and not claim_negations:
                # Passage explicitly negates the affirmative claim
                return True
            if claim_negations and not passage_negations:
                # Claim is negative, passage is affirmative
                return True

        return False

    def _detect_numerical_conflict(self, claim_text: str, passage_text: str) -> bool:
        """Detects whether a passage presents conflicting numerical quantities for a claim."""
        claim_nums = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", claim_text))
        passage_nums = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", passage_text))
        if claim_nums and passage_nums:
            # Check if there is substantial topic overlap
            claim_tokens = self._extract_tokens(claim_text)
            psg_tokens = self._extract_tokens(passage_text)
            overlap = claim_tokens.intersection(psg_tokens)
            if len(overlap) >= 3 and not (claim_nums.intersection(passage_nums)):
                return True
        return False

    def verify_claim(self, claim_id_or_statement: str) -> ClaimVerificationDetail:
        """Evaluates an atomic claim against all source evidence in the graph.

        Produces explicit outcomes:
        - SUPPORTED: Corroborated by direct factual passage statements.
        - CONTRADICTED: Refuted or opposed by evidence passages.
        - INSUFFICIENT_EVIDENCE: Relevant topic mentioned, but lacks factual substantiation.
        - UNVERIFIED_ASSUMPTION: Orphan claim with no supporting evidence in the graph.

        A citation's existence is not proof of support.
        Duplicate copies of the same paper do not count as independent corroboration.

        Args:
            claim_id_or_statement: Target claim node ID or statement string.

        Returns:
            Structured ClaimVerificationDetail report.
        """
        # Guard against empty / malformed statements
        clean_input = self._clean_text(claim_id_or_statement)
        if not clean_input:
            return ClaimVerificationDetail(
                claim_id="clm_empty",
                statement="",
                outcome=ClaimVerificationOutcome.UNVERIFIED_ASSUMPTION,
                supporting_passages=[],
                contradicting_passages=[],
                insufficient_passages=[],
                independent_sources_count=0,
                verification_explanation="Malformed or empty claim: Statement contains no evaluable proposition.",
                is_orphan=True,
            )

        # Resolve claim node or create transient evaluation
        target_claim: Optional[AtomicClaim] = None
        claim_id: str = ""
        statement: str = ""

        if claim_id_or_statement in self._claims:
            claim_id = claim_id_or_statement
            target_claim = self._claims[claim_id]
            statement = target_claim.statement
        else:
            # Look up by statement match
            for cid, clm in self._claims.items():
                if clm.statement.strip().lower() == clean_input.lower():
                    claim_id = cid
                    target_claim = clm
                    statement = clm.statement
                    break

        if not target_claim:
            # Add as candidate claim node
            statement = clean_input
            claim_id = self.add_claim(statement)
            target_claim = self._claims[claim_id]

        claim_tokens = self._extract_tokens(statement)
        supporting: List[Dict[str, Any]] = []
        contradicting: List[Dict[str, Any]] = []
        insufficient: List[Dict[str, Any]] = []

        seen_sources: Set[str] = set()
        independent_doi_works: Set[str] = set()

        # Check all passages in graph
        for psg_id, passage in self._passages.items():
            source_id = passage.source_id
            source_props = self._sources.get(source_id, {})
            psg_tokens = self._extract_tokens(passage.text)
            overlap = claim_tokens.intersection(psg_tokens)

            # Check if this passage was the direct assertion source for the claim
            is_direct_parent = (target_claim.source_passage_id == psg_id)

            if is_direct_parent:
                # Direct origin passage is inherently supporting
                supporting.append({
                    "passage_id": psg_id,
                    "source_id": source_id,
                    "title": source_props.get("title"),
                    "doi": source_props.get("doi"),
                    "text": passage.text,
                    "rationale": "Direct source origin passage for this claim.",
                })
                seen_sources.add(source_id)
                work_key = source_props.get("doi") or source_props.get("title") or source_id
                independent_doi_works.add(work_key)
                continue

            # Check overlap threshold
            overlap_ratio = len(overlap) / max(1, len(claim_tokens))
            has_substr = bool(statement.strip()) and (statement.lower() in passage.text.lower())
            missing_claim_tokens = claim_tokens - psg_tokens
            missing_assertion_verb = bool(missing_claim_tokens.intersection(STRONG_ASSERTION_VERBS))
            passage_has_exploratory = bool(psg_tokens.intersection(EXPLORATORY_VERBS))

            if overlap_ratio >= 0.40 or has_substr:
                is_polarity_conflict = self._detect_polarity_conflict(statement, passage.text)
                is_num_conflict = self._detect_numerical_conflict(statement, passage.text)
                is_contradiction = is_polarity_conflict or is_num_conflict

                work_key = source_props.get("doi") or source_props.get("title") or source_id
                passage_evidence = {
                    "passage_id": psg_id,
                    "source_id": source_id,
                    "title": source_props.get("title"),
                    "doi": source_props.get("doi"),
                    "text": passage.text,
                }

                if is_contradiction:
                    if is_num_conflict:
                        passage_evidence["rationale"] = "Passage presents conflicting numerical quantities against claim assertion."
                    else:
                        passage_evidence["rationale"] = "Passage text exhibits polarity conflict or explicit negation against claim."
                    contradicting.append(passage_evidence)
                    seen_sources.add(source_id)
                    independent_doi_works.add(work_key)
                    # Add edge to graph
                    self.graph.add_edge(KnowledgeGraphEdge(
                        edge_id=f"edge_psg_contra_{uuid.uuid4().hex[:8]}",
                        source_id=psg_id,
                        target_id=claim_id,
                        relation="contradicts_claim",
                        weight=1.0,
                    ))
                elif (overlap_ratio >= 0.65 or has_substr) and not (missing_assertion_verb and passage_has_exploratory):
                    passage_evidence["rationale"] = "Passage directly corroborates factual claim assertion."
                    supporting.append(passage_evidence)
                    seen_sources.add(source_id)
                    independent_doi_works.add(work_key)
                    # Add edge to graph
                    self.graph.add_edge(KnowledgeGraphEdge(
                        edge_id=f"edge_psg_supp_{uuid.uuid4().hex[:8]}",
                        source_id=psg_id,
                        target_id=claim_id,
                        relation="supports_claim",
                        weight=1.0,
                    ))
                else:
                    passage_evidence["rationale"] = "Relevant topic keywords found, but factual evidence is insufficient to prove assertion."
                    insufficient.append(passage_evidence)
                    # Add edge to graph
                    self.graph.add_edge(KnowledgeGraphEdge(
                        edge_id=f"edge_psg_insuff_{uuid.uuid4().hex[:8]}",
                        source_id=psg_id,
                        target_id=claim_id,
                        relation="insufficient_evidence_for_claim",
                        weight=0.5,
                    ))

        # Determine overall outcome
        independent_count = len(independent_doi_works)

        if contradicting:
            outcome = ClaimVerificationOutcome.CONTRADICTED
            explanation = f"Contradicted by {len(contradicting)} passage(s) across {independent_count} source work(s)."
            is_orphan = False
        elif supporting:
            outcome = ClaimVerificationOutcome.SUPPORTED
            explanation = f"Supported by {len(supporting)} passage(s) across {independent_count} independent work(s)."
            is_orphan = False
        elif insufficient:
            outcome = ClaimVerificationOutcome.INSUFFICIENT_EVIDENCE
            explanation = f"Insufficient evidence: {len(insufficient)} passage(s) overlap topic keywords without proving claim."
            is_orphan = False
        else:
            outcome = ClaimVerificationOutcome.UNVERIFIED_ASSUMPTION
            explanation = "Orphan claim: No supporting or contradicting evidence found in knowledge graph."
            is_orphan = True

        detail = ClaimVerificationDetail(
            claim_id=claim_id,
            statement=statement,
            outcome=outcome,
            supporting_passages=supporting,
            contradicting_passages=contradicting,
            insufficient_passages=insufficient,
            independent_sources_count=independent_count,
            verification_explanation=explanation,
            is_orphan=is_orphan,
        )
        self._verifications[claim_id] = detail

        # Update claim node properties in graph with latest verification outcome
        claim_node = self.graph.get_node(claim_id)
        if claim_node:
            claim_node.properties["verification_outcome"] = outcome.value
            claim_node.properties["is_orphan"] = is_orphan
            claim_node.properties["independent_sources_count"] = independent_count
            claim_node.properties["verification_explanation"] = explanation

        return detail

    def find_evidence_for_claim(self, claim_id: str) -> Dict[str, Any]:
        """Retrieves all supporting, contradicting, and insufficient passages and parent sources for a claim.

        Args:
            claim_id: Claim node identifier.

        Returns:
            Dictionary containing passages, parent sources, and verification status.
        """
        detail = self.verify_claim(claim_id)
        parent_sources: List[Dict[str, Any]] = []
        for psg_info in detail.supporting_passages + detail.contradicting_passages + detail.insufficient_passages:
            src_id = psg_info.get("source_id")
            if src_id and src_id in self._sources:
                parent_sources.append(self._sources[src_id])

        return {
            "claim_id": claim_id,
            "statement": detail.statement,
            "outcome": detail.outcome.value,
            "is_orphan": detail.is_orphan,
            "supporting_passages": detail.supporting_passages,
            "contradicting_passages": detail.contradicting_passages,
            "insufficient_passages": detail.insufficient_passages,
            "independent_sources_count": detail.independent_sources_count,
            "parent_sources": parent_sources,
            "verification_explanation": detail.verification_explanation,
        }

    def traverse_claim_to_sources(self, claim_id: str) -> List[KnowledgeGraphNode]:
        """Traverses the graph backwards from a claim to all its backing scholarly source nodes.

        Traversal path: Claim <- asserts/supports/contains <- Passage <- contains_passage <- Source.

        Args:
            claim_id: Claim node identifier.

        Returns:
            List of KnowledgeGraphNode source nodes.
        """
        source_nodes: Dict[str, KnowledgeGraphNode] = {}

        # Look at incoming edges to claim
        incoming = self.graph.get_incoming_edges(claim_id)
        passage_ids = {e.source_id for e in incoming if e.relation in ("asserts_claim", "supports_claim", "contradicts_claim", "insufficient_evidence_for_claim")}

        # Check claim's direct parent passage ID if present
        claim = self._claims.get(claim_id)
        if claim and claim.source_passage_id:
            passage_ids.add(claim.source_passage_id)

        # For each passage, find incoming edge from source
        for psg_id in passage_ids:
            psg_incoming = self.graph.get_incoming_edges(psg_id)
            for e in psg_incoming:
                if e.relation == "contains_passage":
                    src_node = self.graph.get_node(e.source_id)
                    if src_node and src_node.type == KnowledgeType.SCHOLARLY_SOURCE:
                        source_nodes[src_node.node_id] = src_node

            # Also check direct passage object source_id
            if psg_id in self._passages:
                src_id = self._passages[psg_id].source_id
                src_node = self.graph.get_node(src_id)
                if src_node and src_node.type == KnowledgeType.SCHOLARLY_SOURCE:
                    source_nodes[src_node.node_id] = src_node

        return list(source_nodes.values())

    def traverse_source_to_claims(self, source_id: str) -> List[KnowledgeGraphNode]:
        """Traverses the graph forwards from a source to all claims asserted or derived from it.

        Traversal path: Source -> contains_passage -> Passage -> asserts_claim -> Claim.

        Args:
            source_id: Source node identifier.

        Returns:
            List of KnowledgeGraphNode claim nodes.
        """
        claim_nodes: Dict[str, KnowledgeGraphNode] = {}

        # Find passages belonging to source
        outgoing = self.graph.get_outgoing_edges(source_id)
        passage_ids = {e.target_id for e in outgoing if e.relation == "contains_passage"}

        for psg_id in passage_ids:
            psg_outgoing = self.graph.get_outgoing_edges(psg_id)
            for e in psg_outgoing:
                if e.relation in ("asserts_claim", "supports_claim"):
                    clm_node = self.graph.get_node(e.target_id)
                    if clm_node and clm_node.type == KnowledgeType.CLAIM:
                        claim_nodes[clm_node.node_id] = clm_node

        return list(claim_nodes.values())

    def find_unsupported_claims(self) -> List[KnowledgeGraphNode]:
        """Finds all claims in the graph that are orphans, contradicted, or lack sufficient evidence.

        Returns:
            List of unverified / unsupported claim KnowledgeGraphNode items.
        """
        unsupported: List[KnowledgeGraphNode] = []
        for nid, node in self.graph.get_nodes().items():
            if node.type == KnowledgeType.CLAIM:
                detail = self.verify_claim(nid)
                if detail.outcome in (
                    ClaimVerificationOutcome.UNVERIFIED_ASSUMPTION,
                    ClaimVerificationOutcome.INSUFFICIENT_EVIDENCE,
                    ClaimVerificationOutcome.CONTRADICTED,
                ):
                    unsupported.append(node)
        return unsupported

    def detect_contradictory_evidence(self) -> List[Dict[str, Any]]:
        """Finds all claims in the graph that have detected contradictory evidence or polarity conflicts.

        Returns:
            List of contradiction evaluation records.
        """
        contradictions: List[Dict[str, Any]] = []
        for nid, node in self.graph.get_nodes().items():
            if node.type == KnowledgeType.CLAIM:
                detail = self.verify_claim(nid)
                if detail.outcome == ClaimVerificationOutcome.CONTRADICTED or bool(detail.contradicting_passages):
                    contradictions.append({
                        "claim_id": nid,
                        "statement": detail.statement,
                        "contradicting_passages": detail.contradicting_passages,
                        "supporting_passages": detail.supporting_passages,
                        "explanation": detail.verification_explanation,
                    })
        return contradictions

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the complete evidence graph state, nodes, passages, claims, and relations."""
        return {
            "graph": self.graph.to_dict(),
            "sources": self._sources,
            "passages": {pid: psg.model_dump() for pid, psg in self._passages.items()},
            "claims": {cid: clm.model_dump() for cid, clm in self._claims.items()},
            "verifications": {vid: ver.model_dump() for vid, ver in self._verifications.items()},
            "doi_to_source_id": self._doi_to_source_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceGraphBuilder":
        """Reconstructs an EvidenceGraphBuilder from serialized dictionary."""
        kg = KnowledgeGraph.from_dict(data.get("graph", {}))
        builder = cls(graph=kg)
        builder._sources = data.get("sources", {})
        builder._doi_to_source_id = data.get("doi_to_source_id", {})

        for pid, psg_data in data.get("passages", {}).items():
            builder._passages[pid] = SourcePassage(**psg_data)

        for cid, clm_data in data.get("claims", {}).items():
            builder._claims[cid] = AtomicClaim(**clm_data)

        for vid, ver_data in data.get("verifications", {}).items():
            builder._verifications[vid] = ClaimVerificationDetail(**ver_data)

        # Rebuild title_year index
        for s_id, s_props in builder._sources.items():
            t = s_props.get("title", "")
            y = s_props.get("publication_year")
            if t:
                builder._title_year_to_source_id[(builder._normalize_title(t), y)] = s_id

        return builder

    def save_to_json(self, file_path: Union[str, Path]) -> None:
        """Persists the complete evidence graph to a JSON file."""
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_from_json(cls, file_path: Union[str, Path]) -> "EvidenceGraphBuilder":
        """Loads and restores the evidence graph from a JSON file."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Evidence graph file not found: {file_path}")
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls.from_dict(data)
