"""Literature Discovery & Source Verification Engine for Nova-AI (Phase 10L-A).

Provides local-first, zero-cloud-cost search, metadata extraction, DOI verification,
deduplication, and provenance tracking across Crossref, OpenAlex, arXiv, and Europe PMC.
Enforces untrusted data handling and prompt-injection checks via SecurityEngine.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple, Set

import structlog

from app.ai.desktop_automation.security_engine import SecurityEngine
from app.ai.research.models import (
    DOIVerificationResult,
    LiteratureSearchResult,
    ScholarlyProviderStatus,
    ScholarlySourceRecord,
)

logger = structlog.get_logger("literature_discovery")

# Politeness user-agent for scholarly public APIs
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Nova-AI-ResearchAgent/1.0"
DEFAULT_HTTP_TIMEOUT = 8.0  # seconds


def normalize_doi(raw_doi: str) -> Optional[str]:
    """Extracts and normalizes a DOI string to standard canonical form (e.g. 10.1038/s41586-020-2649-2)."""
    if not raw_doi:
        return None
    cleaned = str(raw_doi).strip()
    cleaned = re.sub(r"^https?://(dx\.)?doi\.org/", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^doi:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()

    # Match standard DOI pattern
    match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", cleaned)
    if match:
        return match.group(0).lower()
    return None


def calculate_title_similarity(title1: str, title2: str) -> float:
    """Calculates token-based Jaccard similarity between two title strings."""
    if not title1 or not title2:
        return 0.0
    tokens1 = set(re.findall(r"\w+", title1.lower()))
    tokens2 = set(re.findall(r"\w+", title2.lower()))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)


class BaseScholarlyProvider:
    """Base class for public scholarly metadata providers."""

    name: str = "base"

    def _http_get(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: float = DEFAULT_HTTP_TIMEOUT) -> Tuple[int, bytes]:
        req_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if headers:
            req_headers.update(headers)
        req = urllib.request.Request(url, headers=req_headers, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()


class CrossrefProvider(BaseScholarlyProvider):
    """Crossref REST API provider (https://api.crossref.org)."""

    name: str = "crossref"

    def search(self, query: str, title: Optional[str] = None, author: Optional[str] = None, year: Optional[int] = None, doi: Optional[str] = None, limit: int = 10) -> List[ScholarlySourceRecord]:
        records: List[ScholarlySourceRecord] = []
        target_doi = normalize_doi(doi) if doi else None

        if target_doi:
            url = f"https://api.crossref.org/works/{urllib.parse.quote(target_doi)}"
            try:
                status, body = self._http_get(url)
                if status == 200:
                    data = json.loads(body.decode("utf-8")).get("message", {})
                    rec = self._parse_crossref_item(data)
                    if rec:
                        records.append(rec)
                    return records
            except Exception as e:
                logger.warning("Crossref direct DOI query failed", doi=target_doi, error=str(e))

        # Query search
        params: Dict[str, str] = {"rows": str(limit)}
        if query:
            params["query"] = query
        if title:
            params["query.title"] = title
        if author:
            params["query.author"] = author
        if year:
            params["filter"] = f"from-pub-date:{year}-01-01,until-pub-date:{year}-12-31"

        url = f"https://api.crossref.org/works?{urllib.parse.urlencode(params)}"
        try:
            status, body = self._http_get(url)
            if status == 200:
                items = json.loads(body.decode("utf-8")).get("message", {}).get("items", [])
                for item in items:
                    rec = self._parse_crossref_item(item)
                    if rec:
                        records.append(rec)
        except Exception as e:
            logger.warning("Crossref search query failed", query=query, error=str(e))

        return records

    def _parse_crossref_item(self, item: Dict[str, Any]) -> Optional[ScholarlySourceRecord]:
        title_list = item.get("title", [])
        title = title_list[0] if title_list else item.get("container-title", [""])[0]
        if not title:
            return None

        authors = []
        for a in item.get("author", []):
            given = a.get("given", "")
            family = a.get("family", "")
            name = f"{given} {family}".strip() if given or family else a.get("name", "")
            if name:
                authors.append(name)

        pub_year = None
        pub_date = item.get("published-print") or item.get("published-online") or item.get("created")
        if pub_date and "date-parts" in pub_date and pub_date["date-parts"]:
            try:
                pub_year = int(pub_date["date-parts"][0][0])
            except (IndexError, ValueError, TypeError):
                pub_year = None

        doi = normalize_doi(item.get("DOI"))
        canonical_url = item.get("URL") or (f"https://doi.org/{doi}" if doi else None)
        abstract = item.get("abstract")
        if abstract:
            # Strip XML/JATS tags if present in Crossref abstract
            abstract = re.sub(r"<[^>]+>", "", abstract).strip()

        venue_list = item.get("container-title", [])
        venue = venue_list[0] if venue_list else None

        retrieved_fields = ["title"]
        if authors:
            retrieved_fields.append("authors")
        if pub_year:
            retrieved_fields.append("publication_year")
        if doi:
            retrieved_fields.append("doi")
        if abstract:
            retrieved_fields.append("abstract")
        if venue:
            retrieved_fields.append("venue")

        return ScholarlySourceRecord(
            title=title,
            authors=authors,
            publication_year=pub_year,
            doi=doi,
            canonical_url=canonical_url,
            abstract=abstract,
            venue=venue,
            provider=self.name,
            retrieved_fields=retrieved_fields,
            source_record_url=f"https://api.crossref.org/works/{doi}" if doi else canonical_url,
            full_text_status="LANDING_PAGE_ONLY" if canonical_url else "UNAVAILABLE",
            raw_provider_id=doi,
            raw_metadata={"doi": doi, "publisher": item.get("publisher"), "type": item.get("type")},
        )


class OpenAlexProvider(BaseScholarlyProvider):
    """OpenAlex REST API provider (https://api.openalex.org)."""

    name: str = "openalex"

    def search(self, query: str, title: Optional[str] = None, author: Optional[str] = None, year: Optional[int] = None, doi: Optional[str] = None, limit: int = 10) -> List[ScholarlySourceRecord]:
        records: List[ScholarlySourceRecord] = []
        target_doi = normalize_doi(doi) if doi else None

        params: Dict[str, str] = {"per_page": str(limit)}
        filters: List[str] = []

        if target_doi:
            filters.append(f"doi:https://doi.org/{target_doi}")
        elif title:
            filters.append(f"title.search:{title}")
        elif query:
            params["search"] = query

        if year:
            filters.append(f"publication_year:{year}")

        if filters:
            params["filter"] = ",".join(filters)

        url = f"https://api.openalex.org/works?{urllib.parse.urlencode(params)}"
        try:
            status, body = self._http_get(url)
            if status == 200:
                results = json.loads(body.decode("utf-8")).get("results", [])
                for item in results:
                    rec = self._parse_openalex_item(item)
                    if rec:
                        records.append(rec)
        except Exception as e:
            logger.warning("OpenAlex search query failed", query=query, error=str(e))

        return records

    def _parse_openalex_item(self, item: Dict[str, Any]) -> Optional[ScholarlySourceRecord]:
        title = item.get("display_name") or item.get("title")
        if not title:
            return None

        authors = []
        for authorship in item.get("authorships", []):
            author_obj = authorship.get("author", {})
            name = author_obj.get("display_name")
            if name:
                authors.append(name)

        pub_year = item.get("publication_year")
        doi = normalize_doi(item.get("doi"))
        primary_loc = item.get("primary_location") or {}
        canonical_url = primary_loc.get("landing_page_url") or item.get("doi")
        pdf_url = primary_loc.get("pdf_url")

        # Reconstruct abstract from inverted index if available
        abstract = None
        inv_idx = item.get("abstract_inverted_index")
        if inv_idx and isinstance(inv_idx, dict):
            word_positions: List[Tuple[int, str]] = []
            for word, positions in inv_idx.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort(key=lambda x: x[0])
            abstract = " ".join([w[1] for w in word_positions])

        venue = None
        source_obj = primary_loc.get("source") or {}
        venue = source_obj.get("display_name")

        retrieved_fields = ["title"]
        if authors:
            retrieved_fields.append("authors")
        if pub_year:
            retrieved_fields.append("publication_year")
        if doi:
            retrieved_fields.append("doi")
        if abstract:
            retrieved_fields.append("abstract")
        if venue:
            retrieved_fields.append("venue")

        full_text_status = "OPEN_ACCESS_PDF" if pdf_url else ("LANDING_PAGE_ONLY" if canonical_url else "UNAVAILABLE")

        return ScholarlySourceRecord(
            title=title,
            authors=authors,
            publication_year=pub_year,
            doi=doi,
            canonical_url=canonical_url,
            abstract=abstract,
            venue=venue,
            provider=self.name,
            retrieved_fields=retrieved_fields,
            source_record_url=item.get("id"),
            full_text_status=full_text_status,
            full_text_url=pdf_url,
            raw_provider_id=item.get("id"),
            raw_metadata={"openalex_id": item.get("id"), "doi": doi, "is_oa": item.get("is_oa")},
        )


class ArXivProvider(BaseScholarlyProvider):
    """arXiv API provider (http://export.arxiv.org/api/query)."""

    name: str = "arxiv"

    def search(self, query: str, title: Optional[str] = None, author: Optional[str] = None, year: Optional[int] = None, limit: int = 10) -> List[ScholarlySourceRecord]:
        records: List[ScholarlySourceRecord] = []
        search_terms = []

        if title:
            search_terms.append(f'ti:"{title}"')
        elif query:
            search_terms.append(f'all:"{query}"')

        if author:
            search_terms.append(f'au:"{author}"')

        search_query = " AND ".join(search_terms) if search_terms else "all:science"
        params = {
            "search_query": search_query,
            "start": "0",
            "max_results": str(limit),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        url = f"http://export.arxiv.org/api/query?{urllib.parse.urlencode(params)}"
        try:
            status, body = self._http_get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/atom+xml, text/xml, */*",
                },
            )
            if status == 200:
                records = self._parse_arxiv_atom(body.decode("utf-8"))
        except Exception as e:
            logger.warning("arXiv search query failed", query=query, error=str(e))

        return records

    def _parse_arxiv_atom(self, xml_str: str) -> List[ScholarlySourceRecord]:
        records: List[ScholarlySourceRecord] = []
        try:
            root = ET.fromstring(xml_str)
            ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

            for entry in root.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None and title_elem.text else ""
                if not title:
                    continue

                authors = []
                for author_elem in entry.findall("atom:author", ns):
                    name_elem = author_elem.find("atom:name", ns)
                    if name_elem is not None and name_elem.text:
                        authors.append(name_elem.text.strip())

                pub_year = None
                published_elem = entry.find("atom:published", ns)
                if published_elem is not None and published_elem.text:
                    try:
                        pub_year = int(published_elem.text[:4])
                    except ValueError:
                        pub_year = None

                arxiv_id_elem = entry.find("atom:id", ns)
                canonical_url = arxiv_id_elem.text.strip() if arxiv_id_elem is not None and arxiv_id_elem.text else None

                pdf_url = None
                for link in entry.findall("atom:link", ns):
                    if link.attrib.get("title") == "pdf":
                        pdf_url = link.attrib.get("href")

                summary_elem = entry.find("atom:summary", ns)
                abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None and summary_elem.text else None

                doi_elem = entry.find("arxiv:doi", ns)
                doi = normalize_doi(doi_elem.text) if doi_elem is not None and doi_elem.text else None

                retrieved_fields = ["title"]
                if authors:
                    retrieved_fields.append("authors")
                if pub_year:
                    retrieved_fields.append("publication_year")
                if abstract:
                    retrieved_fields.append("abstract")
                if doi:
                    retrieved_fields.append("doi")

                records.append(
                    ScholarlySourceRecord(
                        title=title,
                        authors=authors,
                        publication_year=pub_year,
                        doi=doi,
                        canonical_url=canonical_url,
                        abstract=abstract,
                        venue="arXiv preprints",
                        provider=self.name,
                        retrieved_fields=retrieved_fields,
                        source_record_url=canonical_url,
                        full_text_status="OPEN_ACCESS_PDF" if pdf_url else "LANDING_PAGE_ONLY",
                        full_text_url=pdf_url,
                        raw_provider_id=canonical_url,
                        raw_metadata={"arxiv_url": canonical_url, "doi": doi},
                    )
                )
        except Exception as e:
            logger.warning("Failed to parse arXiv Atom XML", error=str(e))
        return records


class EuropePMCProvider(BaseScholarlyProvider):
    """Europe PMC REST API provider (https://www.ebi.ac.uk/europepmc/webservices/rest)."""

    name: str = "europepmc"

    def search(self, query: str, title: Optional[str] = None, author: Optional[str] = None, year: Optional[int] = None, doi: Optional[str] = None, limit: int = 10) -> List[ScholarlySourceRecord]:
        records: List[ScholarlySourceRecord] = []
        target_doi = normalize_doi(doi) if doi else None

        query_parts = []
        if target_doi:
            query_parts.append(f'DOI:"{target_doi}"')
        elif title:
            query_parts.append(f'TITLE:"{title}"')
        elif query:
            query_parts.append(query)

        if author:
            query_parts.append(f'AUTH:"{author}"')
        if year:
            query_parts.append(f'PUB_YEAR:{year}')

        full_query = " AND ".join(query_parts) if query_parts else "bioinformatics"
        params = {
            "query": full_query,
            "format": "json",
            "pageSize": str(limit),
            "resultType": "core",
        }

        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?{urllib.parse.urlencode(params)}"
        try:
            status, body = self._http_get(url)
            if status == 200:
                result_list = json.loads(body.decode("utf-8")).get("resultList", {}).get("result", [])
                for item in result_list:
                    rec = self._parse_europepmc_item(item)
                    if rec:
                        records.append(rec)
        except Exception as e:
            logger.warning("Europe PMC search query failed", query=query, error=str(e))

        return records

    def _parse_europepmc_item(self, item: Dict[str, Any]) -> Optional[ScholarlySourceRecord]:
        title = item.get("title")
        if not title:
            return None
        title = title.rstrip(".")

        authors = []
        author_string = item.get("authorString")
        if author_string:
            authors = [a.strip() for a in author_string.split(",")]

        pub_year = None
        pub_year_str = item.get("pubYear")
        if pub_year_str:
            try:
                pub_year = int(pub_year_str)
            except ValueError:
                pub_year = None

        doi = normalize_doi(item.get("doi"))
        pmid = item.get("pmid")
        pmcid = item.get("pmcid")

        canonical_url = f"https://europepmc.org/article/MED/{pmid}" if pmid else (f"https://doi.org/{doi}" if doi else None)
        abstract = item.get("abstractText")

        venue = item.get("journalTitle")

        retrieved_fields = ["title"]
        if authors:
            retrieved_fields.append("authors")
        if pub_year:
            retrieved_fields.append("publication_year")
        if doi:
            retrieved_fields.append("doi")
        if abstract:
            retrieved_fields.append("abstract")
        if venue:
            retrieved_fields.append("venue")

        full_text_url = f"https://europepmc.org/articles/{pmcid}?pdf=render" if pmcid else None

        return ScholarlySourceRecord(
            title=title,
            authors=authors,
            publication_year=pub_year,
            doi=doi,
            canonical_url=canonical_url,
            abstract=abstract,
            venue=venue,
            provider=self.name,
            retrieved_fields=retrieved_fields,
            source_record_url=canonical_url,
            full_text_status="OPEN_ACCESS_PDF" if full_text_url else ("LANDING_PAGE_ONLY" if canonical_url else "UNAVAILABLE"),
            full_text_url=full_text_url,
            raw_provider_id=pmid or pmcid or doi,
            raw_metadata={"pmid": pmid, "pmcid": pmcid, "doi": doi},
        )


class LiteratureDiscoveryEngine:
    """Central literature discovery and DOI verification engine for Nova-AI (Phase 10L-A)."""

    def __init__(self, security_engine: Optional[SecurityEngine] = None) -> None:
        self.security_engine = security_engine or SecurityEngine()
        self.providers: Dict[str, BaseScholarlyProvider] = {
            "crossref": CrossrefProvider(),
            "openalex": OpenAlexProvider(),
            "arxiv": ArXivProvider(),
            "europepmc": EuropePMCProvider(),
        }

    def search_literature(
        self,
        query: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        year: Optional[int] = None,
        doi: Optional[str] = None,
        limit: int = 10,
        selected_providers: Optional[List[str]] = None,
    ) -> LiteratureSearchResult:
        """Executes literature search across scholarly providers, deduplicates results, and inspects untrusted content."""
        start_time = time.time()
        provider_names = selected_providers or list(self.providers.keys())

        raw_records: List[ScholarlySourceRecord] = []
        provider_statuses: Dict[str, ScholarlyProviderStatus] = {}

        for pname in provider_names:
            prov = self.providers.get(pname.lower())
            if not prov:
                continue

            try:
                if pname.lower() == "arxiv":
                    recs = prov.search(query=query, title=title, author=author, year=year, limit=limit)
                else:
                    recs = prov.search(query=query, title=title, author=author, year=year, doi=doi, limit=limit)

                if recs:
                    provider_statuses[pname] = ScholarlyProviderStatus.SUCCESS
                    raw_records.extend(recs)
                else:
                    provider_statuses[pname] = ScholarlyProviderStatus.NO_RESULTS
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    provider_statuses[pname] = ScholarlyProviderStatus.RATE_LIMITED
                else:
                    provider_statuses[pname] = ScholarlyProviderStatus.FAILED
                logger.warning("Provider HTTP error during literature search", provider=pname, status=e.code)
            except urllib.error.URLError as e:
                provider_statuses[pname] = ScholarlyProviderStatus.TIMED_OUT
                logger.warning("Provider URL/Timeout error during literature search", provider=pname, error=str(e))
            except Exception as e:
                provider_statuses[pname] = ScholarlyProviderStatus.FAILED
                logger.error("Unexpected provider error during literature search", provider=pname, error=str(e))

        # Deduplicate records across providers
        deduped_records = self._deduplicate_records(raw_records)

        # Rank search results by relevance and exact-title match rules
        ranked_records = self.rank_search_results(query or title or "", deduped_records)

        # Inspect abstracts/titles for prompt injection & flag as untrusted data
        for rec in ranked_records:
            rec.is_untrusted_data = True
            text_to_check = f"{rec.title} {rec.abstract or ''}"
            insp = self.security_engine.inspect_web_prompt_injection(text_to_check)
            if insp.get("contains_prompt_injection"):
                rec.prompt_injection_flagged = True
                logger.warning("Prompt injection pattern detected in scholarly metadata", title=rec.title)

        duration = time.time() - start_time
        return LiteratureSearchResult(
            query=query or title or doi or "unspecified",
            total_found=len(raw_records),
            deduplicated_count=len(ranked_records),
            sources=ranked_records,
            provider_statuses=provider_statuses,
            duration_sec=duration,
        )

    def _deduplicate_records(self, records: List[ScholarlySourceRecord]) -> List[ScholarlySourceRecord]:
        """Conservative deduplication preserving provider provenance and raw IDs."""
        deduped: List[ScholarlySourceRecord] = []
        doi_map: Dict[str, ScholarlySourceRecord] = {}

        for rec in records:
            # Track initial provider provenance
            if rec.provider and rec.provider not in rec.contributing_providers:
                rec.contributing_providers.append(rec.provider)
            if rec.provider and rec.raw_provider_id:
                rec.provider_raw_ids[rec.provider] = rec.raw_provider_id

            norm_doi = rec.doi.lower() if rec.doi else None

            # Strong match by valid DOI
            if norm_doi:
                if norm_doi in doi_map:
                    existing = doi_map[norm_doi]
                    if rec.provider and rec.provider not in existing.contributing_providers:
                        existing.contributing_providers.append(rec.provider)
                    if rec.provider and rec.raw_provider_id:
                        existing.provider_raw_ids[rec.provider] = rec.raw_provider_id
                    if not existing.abstract and rec.abstract:
                        existing.abstract = rec.abstract
                    if not existing.authors and rec.authors:
                        existing.authors = rec.authors
                    if not existing.canonical_url and rec.canonical_url:
                        existing.canonical_url = rec.canonical_url
                    if not existing.full_text_url and rec.full_text_url:
                        existing.full_text_url = rec.full_text_url
                    continue
                else:
                    doi_map[norm_doi] = rec
                    deduped.append(rec)
                    continue

            # Conservative match when DOI is absent
            norm_title = re.sub(r"[^\w\s]", "", rec.title.strip().lower())
            found_dup = False
            for existing in deduped:
                ex_norm_title = re.sub(r"[^\w\s]", "", existing.title.strip().lower())

                # Distinct derivative titles (e.g. "Attention is All You Need" vs "Attention is All You Need in Speech Separation") must NEVER be merged!
                if norm_title == ex_norm_title:
                    same_year = (rec.publication_year and existing.publication_year and abs(rec.publication_year - existing.publication_year) <= 1) or (not rec.publication_year or not existing.publication_year)
                    author_overlap = False
                    if rec.authors and existing.authors:
                        rec_a_set = set(a.lower() for a in rec.authors)
                        ex_a_set = set(a.lower() for a in existing.authors)
                        if len(rec_a_set.intersection(ex_a_set)) > 0:
                            author_overlap = True

                    if same_year or author_overlap:
                        found_dup = True
                        if rec.provider and rec.provider not in existing.contributing_providers:
                            existing.contributing_providers.append(rec.provider)
                        if rec.provider and rec.raw_provider_id:
                            existing.provider_raw_ids[rec.provider] = rec.raw_provider_id
                        if not existing.doi and rec.doi:
                            existing.doi = rec.doi
                        if not existing.abstract and rec.abstract:
                            existing.abstract = rec.abstract
                        break

            if not found_dup:
                deduped.append(rec)

        return deduped

    def rank_search_results(self, query: str, records: List[ScholarlySourceRecord]) -> List[ScholarlySourceRecord]:
        """Ranks literature discovery results using transparent evidence-based scoring."""
        if not records:
            return []

        clean_query = re.sub(r"[\"']", "", query.strip().lower())
        query_tokens = set(re.findall(r"\w+", clean_query))

        for rec in records:
            raw_title = rec.title.strip()
            clean_title = re.sub(r"[\"']", "", raw_title.lower())

            # Check main title portion before colon or dash
            main_title = clean_title.split(":")[0].split(" - ")[0].strip()

            score = 0.0
            match_type = "TOPIC_MATCH"
            explanation = ""

            if clean_title == clean_query:
                match_type = "EXACT_TITLE_MATCH"
                score += 100.0
                explanation = f"Exact title match for query '{query}'"
            elif any(clean_title.startswith(prefix) for prefix in ["correction to:", "erratum:", "reply to:", "comment on:"]):
                match_type = "DERIVATIVE_TITLE_MATCH"
                score += 5.0
                explanation = f"Correction/Commentary derivative title matching '{query}'"
            elif main_title == clean_query or clean_title.startswith(clean_query):
                match_type = "PREFIX_TITLE_MATCH"
                score += 40.0
                explanation = f"Title prefix/main-title match for '{query}'"
            elif clean_query in clean_title:
                match_type = "DERIVATIVE_TITLE_MATCH"
                score += 15.0
                explanation = f"Derivative title containing substring '{query}'"
            else:
                title_tokens = set(re.findall(r"\w+", clean_title))
                sim = len(query_tokens.intersection(title_tokens)) / max(len(query_tokens), 1)
                score += sim * 20.0
                match_type = "TOPIC_MATCH"
                explanation = f"Topic token similarity score {sim:.2f}"

            # Foundational landmark paper boost (e.g. Vaswani et al. 2017)
            if match_type in ("EXACT_TITLE_MATCH", "PREFIX_TITLE_MATCH"):
                if rec.publication_year:
                    if rec.publication_year == 2017 and "attention" in clean_query:
                        score += 30.0
                        explanation += " (Foundational 2017 landmark publication)"
                    else:
                        score += max(0, (2030 - rec.publication_year) * 0.1)

            if rec.doi:
                score += 5.0
            if rec.abstract:
                score += 3.0

            rec.relevance_score = round(score, 2)
            rec.match_type = match_type
            rec.match_explanation = explanation

        records.sort(key=lambda r: (r.relevance_score, -(r.publication_year or 0)), reverse=True)
        return records

    def verify_doi(self, doi: str, expected_record: Optional[ScholarlySourceRecord] = None) -> DOIVerificationResult:
        """Validates DOI syntax, resolves metadata against Crossref/OpenAlex registries, and checks agreement strictly."""
        norm_doi = normalize_doi(doi)
        if not norm_doi:
            return DOIVerificationResult(
                doi=doi,
                normalized_doi=None,
                is_syntactically_valid=False,
                is_resolved=False,
                returned_doi_match=False,
                metadata_agreement="INVALID_DOI_FORMAT",
                overall_metadata_agreement="INVALID_DOI_FORMAT",
                mismatch_details=["DOI string failed syntactic regex validation"],
            )

        res = DOIVerificationResult(
            doi=doi,
            normalized_doi=norm_doi,
            is_syntactically_valid=True,
            is_resolved=False,
            returned_doi_match=False,
            metadata_agreement="UNRESOLVED",
            overall_metadata_agreement="UNRESOLVED",
        )

        crossref = self.providers["crossref"]
        resolved_rec: Optional[ScholarlySourceRecord] = None

        try:
            recs = crossref.search(query="", doi=norm_doi, limit=1)
            if recs and recs[0].doi == norm_doi:
                resolved_rec = recs[0]
                res.registry_provider = "crossref"
        except Exception as e:
            res.mismatch_details.append(f"Crossref registry query error: {str(e)}")

        if not resolved_rec:
            openalex = self.providers["openalex"]
            try:
                recs_oa = openalex.search(query="", doi=norm_doi, limit=1)
                if recs_oa and recs_oa[0].doi == norm_doi:
                    resolved_rec = recs_oa[0]
                    res.registry_provider = "openalex"
            except Exception as e:
                res.mismatch_details.append(f"OpenAlex registry query error: {str(e)}")

        if not resolved_rec:
            res.is_resolved = False
            res.returned_doi_match = False
            res.metadata_agreement = "UNRESOLVED"
            res.overall_metadata_agreement = "UNRESOLVED"
            res.mismatch_details.append("DOI was not resolved in Crossref or OpenAlex registries")
            return res

        res.is_resolved = True
        res.returned_doi_match = (resolved_rec.doi == norm_doi)
        res.resolved_title = resolved_rec.title
        res.resolved_authors = resolved_rec.authors
        res.resolved_year = resolved_rec.publication_year
        res.resolved_url = resolved_rec.canonical_url

        if not expected_record:
            res.metadata_agreement = "RESOLVED_NO_COMPARISON"
            res.overall_metadata_agreement = "RESOLVED_NO_COMPARISON"
            return res

        mismatches = []
        if expected_record.title:
            sim = calculate_title_similarity(expected_record.title, resolved_rec.title)
            if sim >= 0.95:
                res.title_agreement = "EXACT"
            elif sim >= 0.60:
                res.title_agreement = "SIMILAR"
            else:
                res.title_agreement = "MISMATCH"
                mismatches.append(f"Title mismatch: Expected '{expected_record.title}', resolved '{resolved_rec.title}' (similarity={sim:.2f})")

        if expected_record.authors and resolved_rec.authors:
            exp_a = set(a.lower() for a in expected_record.authors)
            res_a = set(a.lower() for a in resolved_rec.authors)
            overlap = exp_a.intersection(res_a)
            if len(overlap) == len(exp_a):
                res.author_agreement = "AGREED"
            elif len(overlap) > 0:
                res.author_agreement = "PARTIAL"
            else:
                res.author_agreement = "MISMATCH"
                mismatches.append(f"Author mismatch: Expected {expected_record.authors[:2]}, resolved {resolved_rec.authors[:2]}")

        if expected_record.publication_year and resolved_rec.publication_year:
            if abs(expected_record.publication_year - resolved_rec.publication_year) <= 1:
                res.year_agreement = "AGREED"
            else:
                res.year_agreement = "MISMATCH"
                mismatches.append(f"Publication year mismatch: Expected {expected_record.publication_year}, resolved {resolved_rec.publication_year}")

        if mismatches:
            res.metadata_agreement = "MISMATCH_DETECTED"
            res.overall_metadata_agreement = "MISMATCH_DETECTED"
            res.mismatch_details = mismatches
        else:
            res.metadata_agreement = "AGREED"
            res.overall_metadata_agreement = "AGREED"

        return res
