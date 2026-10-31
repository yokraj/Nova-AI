"""Claim-Level Citation Mapper for Phase 10L-C: Evidence-Grounded Research Answer Synthesis.

Maps individual claims to precise source passages and references, builds formatted citations,
and preserves complete publication provenance (DOI, URL, venue, authors, providers) without fabrication.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import structlog

from app.ai.research.evidence_graph_builder import EvidenceGraphBuilder
from app.ai.research.models import ReferenceEntry, ScholarlySourceRecord

logger = structlog.get_logger("citation_mapper")


class ClaimCitationMapper:
    """Manages claim-level citation assignment, bibliographic reference registry, and provenance preservation."""

    def __init__(self) -> None:
        self._source_to_number: Dict[str, int] = {}
        self._references: Dict[int, ReferenceEntry] = {}
        self._next_citation_idx: int = 1

    def reset(self) -> None:
        """Clears active citation state."""
        self._source_to_number.clear()
        self._references.clear()
        self._next_citation_idx = 1

    def register_source(
        self,
        source_id: str,
        source_props: Dict[str, Any],
    ) -> ReferenceEntry:
        """Registers a source into the reference bibliography and assigns a permanent citation number.

        Preserves DOI, URL, venue, authors, and provider provenance strictly without synthetic fabrication.
        """
        if source_id in self._source_to_number:
            cite_num = self._source_to_number[source_id]
            return self._references[cite_num]

        cite_num = self._next_citation_idx
        self._next_citation_idx += 1
        self._source_to_number[source_id] = cite_num

        raw_doi = source_props.get("doi")
        doi_val = str(raw_doi).strip() if raw_doi and str(raw_doi).strip().lower() not in ("none", "null", "") else None
        
        raw_url = source_props.get("canonical_url") or source_props.get("source_record_url")
        url_val = str(raw_url).strip() if raw_url and str(raw_url).strip().lower() not in ("none", "null", "") else None

        authors = source_props.get("authors") or []
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(",") if a.strip()]

        ref = ReferenceEntry(
            citation_number=cite_num,
            citation_key=f"[{cite_num}]",
            source_id=source_id,
            title=source_props.get("title", "Untitled Source"),
            authors=authors,
            publication_year=source_props.get("publication_year"),
            doi=doi_val,
            canonical_url=url_val,
            venue=source_props.get("venue"),
            provider=source_props.get("provider", "scholarly"),
            contributing_providers=source_props.get("contributing_providers") or ([source_props.get("provider")] if source_props.get("provider") else ["scholarly"]),
            retrieval_timestamp=source_props.get("retrieval_timestamp", 0.0),
        )
        self._references[cite_num] = ref
        return ref

    def get_citation_keys_for_passages(
        self,
        passages: List[Dict[str, Any]],
        evidence_builder: EvidenceGraphBuilder,
    ) -> List[str]:
        """Maps a list of supporting or relevant passages to formatted citation keys like ['[1]', '[2]']."""
        citation_keys: List[str] = []
        seen_numbers: Set[int] = set()

        for psg in passages:
            source_id = psg.get("source_id")
            if not source_id:
                continue

            # Look up source node in evidence graph
            src_node = evidence_builder.graph.get_node(source_id)
            props = src_node.properties if src_node else {}
            if not props and source_id in evidence_builder._sources:
                props = evidence_builder._sources[source_id]

            ref = self.register_source(source_id, props)
            if ref.citation_number not in seen_numbers:
                seen_numbers.add(ref.citation_number)
                citation_keys.append(ref.citation_key)

        return sorted(citation_keys, key=lambda k: int(k.strip("[]")))

    def get_all_references(self) -> List[ReferenceEntry]:
        """Returns the sorted list of all registered bibliography references."""
        return [self._references[num] for num in sorted(self._references.keys())]

    def build_reference_map(self) -> Dict[str, Dict[str, Any]]:
        """Returns map of citation key to reference details."""
        return {
            ref.citation_key: ref.model_dump()
            for ref in self.get_all_references()
        }

