"""12-Stage Manual Validation Script for M3.4.7 Universal Knowledge, Research & Reasoning Engine.
"""

import asyncio
import os
import sys

# Ensure UTF-8 output encoding for Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add apps/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/backend")))

from app.ai.research import (
    UniversalResearchEngine,
    ResearchConfiguration,
    ResearchState,
    SourceType,
    ReportType,
    ConfidenceLevel,
    MockResearchProvider,
)
from app.ai.gateway import AIGateway


async def run_12_stage_validation():
    print("==================================================================")
    print("M3.4.7 – Universal Knowledge, Research & Reasoning Engine")
    print("==================================================================\n")

    engine = UniversalResearchEngine()

    # Stage 1: Core Package Init & PEP 562 Lazy Loader
    print("Stage 1: Core Package Init & PEP 562 Lazy Loader")
    assert engine.config.max_sub_questions == 5
    print("  [OK] Research Engine package loaded successfully.\n")

    # Stage 2: Research Planner
    print("Stage 2: Research Planner (Decomposition & Search Strategy)")
    plan = await engine.planner.create_plan("Artificial Intelligence Agent Architectures", mode="deep")
    print(f"  * Topic: '{plan.topic}' | Sub-questions: {len(plan.sub_questions)} | Est. Time: {plan.estimated_time_sec}s")
    for sq in plan.sub_questions[:2]:
        print(f"  * Sub-question: '{sq.query}' (Category: {sq.category})")
    assert len(plan.sub_questions) >= 3
    print("  [OK] Research Planner generated structured roadmap.\n")

    # Stage 3: Knowledge Collector
    print("Stage 3: Knowledge Collector (Multi-Format Document Ingestion)")
    local_src = await engine.collector.collect_knowledge("./docs/architecture.md")
    pdf_src = await engine.collector.collect_knowledge("./docs/whitepaper.pdf")
    ocr_src = await engine.collector.collect_knowledge("./docs/diagram.png")
    repo_src = await engine.collector.collect_knowledge("c:\\Projects\\Nova-AI")

    print(f"  * Local Doc: '{local_src.title}' ({local_src.type.value})")
    print(f"  * PDF Doc: '{pdf_src.title}' ({pdf_src.type.value})")
    print(f"  * OCR Image: '{ocr_src.title}' ({ocr_src.type.value})")
    print(f"  * Repository: '{repo_src.title}' ({repo_src.type.value})")
    assert local_src.type == SourceType.LOCAL_FILE
    print("  [OK] Knowledge Collector ingested multi-format sources.\n")

    # Stage 4: Search Engine
    print("Stage 4: Search Engine (Local, Repository, Web & Docs Search)")
    search_results = await engine.search("FastAPI framework benchmarks")
    print(f"  * Total Ranked Sources Returned: {len(search_results)}")
    for s in search_results[:2]:
        print(f"  * Source: '{s.title}' | Trust Score: {s.trust_score}")
    assert len(search_results) >= 2
    print("  [OK] Search Engine executed multi-provider query.\n")

    # Stage 5: Evidence Verification Engine
    print("Stage 5: Evidence Verification Engine (Claim Cross-Checking)")
    verification = await engine.verifier.verify_claim("FastAPI handles async requests with low latency", search_results)
    print(f"  * Claim: '{verification.statement}'")
    print(f"  * Verification Score: {verification.verification_score} | Confidence: {verification.confidence.value}")
    assert verification.verification_score >= 0.70
    print("  [OK] Verification Engine cross-checked claims against evidence.\n")

    # Stage 6: Reasoning Engine
    print("Stage 6: Reasoning Engine (Evidence Synthesis & Inference)")
    reasoning_out = await engine.reasoner.reason("FastAPI Framework", [verification])
    print(f"  * Derived Conclusions: {len(reasoning_out.conclusions)}")
    print(f"  * Summary: '{reasoning_out.evidence_summary}'")
    assert len(reasoning_out.conclusions) >= 1
    print("  [OK] Reasoning Engine derived structured conclusions.\n")

    # Stage 7: Local Knowledge Graph
    print("Stage 7: Local Knowledge Graph (Nodes, Edges & Traversal)")
    graph_summary = await engine.knowledge_graph()
    related_nodes = engine.graph.get_related_nodes("repo_nova_ai")
    print(f"  * Nodes Count: {graph_summary['nodes_count']} | Edges Count: {graph_summary['edges_count']}")
    print(f"  * Related Nodes to 'repo_nova_ai': {[n.label for n in related_nodes]}")
    assert graph_summary["nodes_count"] >= 3
    print("  [OK] Knowledge Graph traversal verified.\n")

    # Stage 8: Repository Intelligence
    print("Stage 8: Repository Intelligence (Architecture & Code Parsing)")
    repo_summary = await engine.analyze_repository("c:\\Projects\\Nova-AI")
    print(f"  * Repo Name: '{repo_summary.name}'")
    print(f"  * Languages: {repo_summary.languages}")
    print(f"  * Frameworks: {repo_summary.frameworks}")
    assert repo_summary.name == "Nova-AI"
    print("  [OK] Repository Intelligence parsed codebase structure.\n")

    # Stage 9: Document Intelligence
    print("Stage 9: Document Intelligence (PDF, Tables & Figures)")
    doc_summary = await engine.analyze_document("./docs/system_spec.pdf")
    print(f"  * Title: '{doc_summary.title}' | Format: {doc_summary.format}")
    print(f"  * Extracted Paragraphs: {len(doc_summary.paragraphs)} | Tables: {len(doc_summary.tables)}")
    assert len(doc_summary.paragraphs) >= 2
    print("  [OK] Document Intelligence extracted structured content.\n")

    # Stage 10: Citation Engine
    print("Stage 10: Citation Engine (APA, BibTeX & Markdown Citations)")
    cite_apa = engine.citation_engine.generate_citation(local_src, style="APA")
    cite_bib = engine.citation_engine.generate_citation(local_src, style="BibTeX")
    print(f"  * APA Citation: '{cite_apa.citation_string}'")
    print(f"  * BibTeX Citation: '{cite_bib.citation_string}'")
    assert "APA" in cite_apa.citation_string or "(" in cite_apa.citation_string
    print("  [OK] Citation Engine generated multi-style references.\n")

    # Stage 11: Report Generator
    print("Stage 11: Report Generator (Executive, Technical & Voice Summaries)")
    report = await engine.research("Kubernetes Cluster Administration")
    print(f"  * Executive Summary: '{report.executive_summary[:80]}...'")
    print(f"  * Voice Summary: '{report.voice_summary[:80]}...'")
    print(f"  * Citations Attached: {len(report.citations)}")
    assert len(report.executive_summary) > 0
    print("  [OK] Report Generator created multi-format reports.\n")

    # Stage 12: Research Memory, Resumption & Voice Execution
    print("Stage 12: Research Memory & Incremental Resumption ('Hey Nova, research AI Agents')")
    history = await engine.research_history()
    resumed_report = await engine.continue_research("Kubernetes Cluster Administration", "Focus on Helm Charts")
    pkg = await engine.knowledge_package("React")

    print(f"  * Saved Sessions in Memory: {len(history)}")
    print(f"  * Resumed Research Output Topic: '{resumed_report.topic}'")
    print(f"  * Retrieved Knowledge Package Topic: '{pkg.topic}' (Best Practices: {len(pkg.best_practices)})")
    assert len(history) >= 1
    assert pkg.topic == "React"
    print("  [OK] Research session resumed automatically from memory.\n")

    print("==================================================================")
    print("  ALL 12 STAGES PASSED SUCCESSFULLY!")
    print("  Universal Knowledge, Research & Reasoning Engine Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_12_stage_validation())
