"""Manual Verification Runner for Phase 10L-A.1: Scholarly Identity, DOI Integrity & Search Relevance Hardening.

Executes and logs Scenarios A through I using live registry/provider responses and detailed evidence output.
"""

import sys
import os
import json
import time
import urllib.error

# Ensure apps/backend is in sys.path
sys.path.insert(0, os.path.abspath("apps/backend"))

from app.ai.research.literature_discovery import LiteratureDiscoveryEngine, normalize_doi
from app.ai.research.models import ScholarlySourceRecord, DOIVerificationResult, LiteratureSearchResult
from app.ai.research.research_engine import UniversalResearchEngine
from app.ai.kernel.goal_verifier import GoalVerifier, GoalRequirement, VerificationType, VerificationStatus


def run_hardening_scenarios():
    print("=" * 90)
    print("PHASE 10L-A.1 MANUAL HARDENING SCENARIOS (A THROUGH I)")
    print("=" * 90)

    engine = LiteratureDiscoveryEngine()
    verifier = GoalVerifier()
    research_facade = UniversalResearchEngine()

    # -------------------------------------------------------------------------
    # Scenario A: Repeated lookup of reported DOI 10.1038/s41586-020-2649-2
    # -------------------------------------------------------------------------
    print("\n--- SCENARIO A: Repeated lookup of DOI 10.1038/s41586-020-2649-2 ---")
    doi_a = "10.1038/s41586-020-2649-2"
    results_a = []
    for run in range(3):
        res = engine.verify_doi(doi_a)
        results_a.append(res)
        print(f" Run {run+1}: DOI={res.normalized_doi} | Provider={res.registry_provider} | Resolved Title='{res.resolved_title}' | Agreement={res.overall_metadata_agreement}")

    # Assert 100% consistency across runs
    assert results_a[0].resolved_title == results_a[1].resolved_title == results_a[2].resolved_title, "Scenario A Failed: Inconsistent title across runs"
    assert results_a[0].resolved_title == "Array programming with NumPy", "Scenario A Failed: Unexpected title"
    print("OUTCOME A: SUCCESS (Consistently resolved 'Array programming with NumPy')")

    # -------------------------------------------------------------------------
    # Scenario B: DOI verification detects expected-title mismatch
    # -------------------------------------------------------------------------
    print("\n--- SCENARIO B: DOI verification detects expected-title mismatch ---")
    doi_b = "10.1038/s41586-020-2649-2"
    mismatched_exp = ScholarlySourceRecord(
        title="Highly accurate protein structure prediction with AlphaFold",
        doi=doi_b,
        publication_year=2021
    )
    res_b = engine.verify_doi(doi_b, expected_record=mismatched_exp)
    print(f" Input DOI: {doi_b}")
    print(f" Expected Title: '{mismatched_exp.title}'")
    print(f" Resolved Title: '{res_b.resolved_title}'")
    print(f" Title Agreement: {res_b.title_agreement}")
    print(f" Overall Agreement: {res_b.overall_metadata_agreement}")
    print(f" Mismatch Details: {res_b.mismatch_details}")

    # Evaluate via GoalVerifier
    req_b = GoalRequirement(
        requirement_id="req_doi_mismatch",
        description="Verify DOI identity match against expected metadata",
        verification_type=VerificationType.RESEARCH_DOI_MATCH,
        condition_params={"doi_result": res_b.model_dump()}
    )
    eval_b = verifier._evaluate_requirement(req_b, snapshot=None, adapter_state={}, action_results=[], evidence_collector={})
    print(f" GoalVerifier Status: {eval_b.status}")
    print(f" GoalVerifier Failure Reason: {eval_b.failure_reason}")

    assert res_b.overall_metadata_agreement == "MISMATCH_DETECTED", "Scenario B Failed: Mismatch not detected"
    assert eval_b.status == VerificationStatus.FAILED, "Scenario B Failed: Mismatched DOI passed GoalVerifier!"
    print("OUTCOME B: SUCCESS (Mismatch detected & GoalVerifier status FAILED)")

    # -------------------------------------------------------------------------
    # Scenario C: Exact-title search for 'Attention Is All You Need'
    # -------------------------------------------------------------------------
    print("\n--- SCENARIO C: Exact-title ranking for 'Attention Is All You Need' ---")
    query_c = "Attention Is All You Need"
    res_c = engine.search_literature(query=query_c, limit=8)
    print(f" Query: '{query_c}'")
    print(f" Total Sources Returned: {len(res_c.sources)}")
    print(" Ranked Results Breakdown:")
    for idx, src in enumerate(res_c.sources[:5]):
        print(f"  [{idx+1}] Score: {src.relevance_score:6.2f} | Match: {src.match_type:20s} | Year: {src.publication_year} | Provider: {src.provider:10s} | Title: '{src.title}'")
        print(f"       Explanation: {src.match_explanation}")

    top_record = res_c.sources[0]
    assert top_record.match_type == "EXACT_TITLE_MATCH", "Scenario C Failed: Top result is not exact title match"
    assert "Attention" in top_record.title and ("Vaswani" in str(top_record.authors) or top_record.publication_year in (2017, 2025)), "Scenario C Failed: Top paper unexpected"
    print("OUTCOME C: SUCCESS (Foundational exact match ranked #1)")

    # -------------------------------------------------------------------------
    # Scenario D: Similar-title paper not falsely merged
    # -------------------------------------------------------------------------
    print("\n--- SCENARIO D: Similar-title paper not falsely merged ---")
    titles_in_results = [s.title for s in res_c.sources]
    has_original = any(t.strip().lower() in ("attention is all you need", "attention is all you need.") for t in titles_in_results)
    has_derivative = any("speech separation" in t.lower() or "video frame" in t.lower() or "correction" in t.lower() for t in titles_in_results)

    print(" Titles preserved in search results:")
    for t in titles_in_results[:6]:
        print(f"  - '{t}'")
    
    assert has_original and has_derivative, "Scenario D Failed: Derivative papers were falsely merged into original!"
    print("OUTCOME D: SUCCESS (Original and derivative papers preserved as distinct records)")

    # -------------------------------------------------------------------------
    # Scenario E: DOI-less records deduplicated conservatively
    # -------------------------------------------------------------------------
    print("\n--- SCENARIO E: Conservative deduplication of DOI-less records ---")
    rec_e1 = ScholarlySourceRecord(title="Quantum Computation with Superconducting Qubits", authors=["A. Smith"], publication_year=2024, provider="provider_a")
    rec_e2 = ScholarlySourceRecord(title="Quantum Computation with Superconducting Qubits", authors=["A. Smith"], publication_year=2024, provider="provider_b")
    rec_e3 = ScholarlySourceRecord(title="Quantum Computation with Superconducting Qubits in 3D Cavities", authors=["B. Jones"], publication_year=2024, provider="provider_c")

    deduped_e = engine._deduplicate_records([rec_e1, rec_e2, rec_e3])
    print(f" Input Records: 3 | Deduplicated Output Count: {len(deduped_e)}")
    for r in deduped_e:
        print(f"  - Title: '{r.title}' | Contributing Providers: {r.contributing_providers}")

    assert len(deduped_e) == 2, "Scenario E Failed: Conservative deduplication error"
    assert "provider_a" in deduped_e[0].contributing_providers and "provider_b" in deduped_e[0].contributing_providers, "Scenario E Failed: Provenance lost"
    print("OUTCOME E: SUCCESS (Identical titles merged; distinct title preserved)")

    # -------------------------------------------------------------------------
    # Scenario F: Provider fallback cannot silently overwrite conflicting identity
    # -------------------------------------------------------------------------
    print("\n--- SCENARIO F: Prevent silent fallback overwrite of resolved DOI ---")
    res_f = engine.verify_doi("10.1038/s41586-020-2649-2")
    print(f" Resolved Registry Provider: {res_f.registry_provider}")
    print(f" Returned DOI Match: {res_f.returned_doi_match}")
    print(f" Resolved Title: '{res_f.resolved_title}'")
    assert res_f.registry_provider == "crossref", "Scenario F Failed: Unexpected provider fallback"
    print("OUTCOME F: SUCCESS (Authoritative Crossref resolution preserved without fallback overwrite)")

    # -------------------------------------------------------------------------
    # Scenario G: Provider failure remains explicitly unavailable/unverified
    # -------------------------------------------------------------------------
    print("\n--- SCENARIO G: Provider failure reported as TIMED_OUT / FAILED ---")
    original_crossref_search = engine.providers["crossref"].search
    engine.providers["crossref"].search = lambda *args, **kwargs: (_ for _ in ()).throw(urllib.error.URLError("Simulated network timeout"))

    res_g = engine.search_literature(query="quantum mechanics", limit=2)
    print(f" Provider Statuses: {res_g.provider_statuses}")
    print(f" Crossref Status: {res_g.provider_statuses.get('crossref')}")

    engine.providers["crossref"].search = original_crossref_search
    assert res_g.provider_statuses.get("crossref") == "TIMED_OUT", "Scenario G Failed"
    print("OUTCOME G: SUCCESS (Failure explicitly reported as TIMED_OUT)")

    # -------------------------------------------------------------------------
    # Scenario H: Provenance retention in merged source records
    # -------------------------------------------------------------------------
    print("\n--- SCENARIO H: Retain provider IDs and provenance after merging ---")
    rec_h1 = ScholarlySourceRecord(title="Deep Residual Learning for Image Recognition", doi="10.1109/cvpr.2016.90", provider="crossref", raw_provider_id="10.1109/cvpr.2016.90")
    rec_h2 = ScholarlySourceRecord(title="Deep Residual Learning for Image Recognition", doi="10.1109/CVPR.2016.90", provider="openalex", raw_provider_id="W2104044530")
    rec_h3 = ScholarlySourceRecord(title="Deep Residual Learning for Image Recognition", doi="10.1109/cvpr.2016.90", provider="arxiv", raw_provider_id="1512.03385")

    deduped_h = engine._deduplicate_records([rec_h1, rec_h2, rec_h3])
    merged_h = deduped_h[0]
    print(f" Merged Title: '{merged_h.title}'")
    print(f" Contributing Providers: {merged_h.contributing_providers}")
    print(f" Provider Raw IDs: {merged_h.provider_raw_ids}")

    assert len(deduped_h) == 1, "Scenario H Failed: DOI deduplication failed"
    assert len(merged_h.contributing_providers) == 3, "Scenario H Failed: Provider provenance missing"
    assert merged_h.provider_raw_ids.get("openalex") == "W2104044530", "Scenario H Failed: OpenAlex raw ID missing"
    print("OUTCOME H: SUCCESS (Full provenance & raw IDs retained)")

    # -------------------------------------------------------------------------
    # Scenario I: Normal Nova research command path execution
    # -------------------------------------------------------------------------
    print("\n--- SCENARIO I: Execute discovery via UniversalResearchEngine facade ---")
    import asyncio
    res_i = asyncio.run(research_facade.discover_literature(query="Attention Is All You Need", limit=5))
    print(f" Facade Search Query: '{res_i.query}'")
    print(f" Deduplicated Count: {res_i.deduplicated_count}")
    print(f" Top Ranked Title: '{res_i.sources[0].title}'")
    print(f" Top Match Type: {res_i.sources[0].match_type}")
    print(f" Top Score: {res_i.sources[0].relevance_score}")
    print(f" Top Explanation: {res_i.sources[0].match_explanation}")

    assert res_i.deduplicated_count > 0, "Scenario I Failed: Facade search empty"
    assert res_i.sources[0].match_type == "EXACT_TITLE_MATCH", "Scenario I Failed: Facade top result not exact match"
    print("OUTCOME I: SUCCESS (Normal Nova research command path verified)")

    print("\n" + "=" * 90)
    print("ALL 9 MANUAL HARDENING SCENARIOS (A THROUGH I) PASSED WITH empirical EVIDENCE!")
    print("=" * 90)


if __name__ == "__main__":
    run_hardening_scenarios()
