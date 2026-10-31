"""Research Question Analyzer for Phase 10L-C: Evidence-Grounded Research Answer Synthesis.

Understands research questions, identifies subtopics, extracts core intent, domain, and
formulates optimized scholarly search queries.
"""

import re
from typing import Any, Dict, List, Optional
import structlog

from app.ai.research.models import QuestionAnalysis
from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine

logger = structlog.get_logger("question_analyzer")


class ResearchQuestionAnalyzer:
    """Decomposes complex research questions into structured subtopics and targeted search strategies."""

    # Common domain keyword associations
    DOMAIN_PATTERNS = {
        "computer_science": [
            "neural", "transformer", "llm", "language model", "algorithm", "deep learning",
            "reinforcement learning", "attention", "compiler", "database", "distributed",
            "gpu", "latency", "bleu", "accuracy", "model", "parameter", "inference",
        ],
        "biomedicine": [
            "protein", "gene", "crispr", "genomic", "drug", "antibody", "disease",
            "clinical", "trial", "cancer", "cellular", "pathway", "mutation", "target",
        ],
        "physics_and_materials": [
            "battery", "electrolyte", "solid-state", "lithium", "conductivity", "thermal",
            "quantum", "semiconductor", "cathode", "anode", "impedance", "nanomaterial",
        ],
        "energy_and_environment": [
            "solar", "wind", "carbon", "emission", "photovoltaic", "efficiency",
            "grid", "renewable", "capture", "storage",
        ],
    }

    # Comparative keywords
    COMPARATIVE_TERMS = [
        "compare", "versus", "vs", "difference between", "how does", "better than",
        "superior", "trade-off", "relative to", "advantages of", "disadvantages of",
    ]

    def __init__(self, runtime_engine: Optional[UniversalAIRuntimeEngine] = None) -> None:
        self.runtime = runtime_engine

    def _infer_domain(self, text: str) -> str:
        """Determines academic domain based on keyword presence."""
        text_lower = text.lower()
        for domain, keywords in self.DOMAIN_PATTERNS.items():
            if any(k in text_lower for k in keywords):
                return domain
        return "general_science"

    def _extract_entities(self, text: str) -> List[str]:
        """Extracts key scientific entities and terms."""
        # Find capitalized phrases or acronyms or quoted terms
        terms: List[str] = []
        # Quoted terms
        quoted = re.findall(r'"([^"]+)"', text)
        terms.extend(quoted)

        # Capitalized multi-word technical entities or known acronyms
        acronyms = re.findall(r"\b[A-Z]{2,}\b", text)
        terms.extend(acronyms)

        # Scientific multi-word phrases
        cleaned = re.sub(r"[^\w\s-]", " ", text)
        words = [w for w in cleaned.split() if len(w) > 3 and w.lower() not in {
            "what", "when", "where", "which", "how", "does", "compare", "versus", "their",
            "about", "with", "from", "into", "during", "between", "under", "over",
        }]
        for w in words:
            if w not in terms and len(terms) < 8:
                terms.append(w)

        return list(dict.fromkeys(terms))

    def _determine_if_comparative(self, text: str) -> bool:
        """Checks if inquiry involves direct comparison between techniques or entities."""
        text_lower = text.lower()
        return any(term in text_lower for term in self.COMPARATIVE_TERMS)

    def analyze_question(self, question: str) -> QuestionAnalysis:
        """Decomposes a research question into structured subtopics and targeted search queries.

        Args:
            question: Natural language scientific research question.

        Returns:
            QuestionAnalysis data model.
        """
        clean_q = re.sub(r"\s+", " ", question).strip()
        domain = self._infer_domain(clean_q)
        is_comparative = self._determine_if_comparative(clean_q)
        entities = self._extract_entities(clean_q)

        # Subtopic decomposition
        subtopics: List[str] = []
        search_queries: List[str] = []
        target_conditions: List[str] = []

        # If comparative question, separate comparative sides
        vs_match = re.search(r"(.+?)\s+(?:versus|vs\.?|compared to|compare with|and)\s+(.+)", clean_q, re.IGNORECASE)

        if is_comparative and vs_match:
            side_a = vs_match.group(1).strip()
            side_b = vs_match.group(2).strip()
            # Clean question prefixes
            side_a_clean = re.sub(r"^(how does|what are the differences between|compare)\s+", "", side_a, flags=re.IGNORECASE).strip()

            subtopics.append(f"Core mechanisms and principles of {side_a_clean}")
            subtopics.append(f"Core mechanisms and principles of {side_b}")
            subtopics.append(f"Comparative benchmark performance and efficiency between {side_a_clean} and {side_b}")
            subtopics.append(f"Failure modes, limitations, and edge cases under varying conditions")

            search_queries.append(f"{side_a_clean} architecture evaluation")
            search_queries.append(f"{side_b} architecture evaluation")
            search_queries.append(f"{side_a_clean} vs {side_b} comparative study")
            search_queries.append(f"{clean_q}")
        else:
            # Multi-faceted analytical decomposition
            subtopics.append(f"Fundamental concepts and theoretical background of {clean_q}")
            subtopics.append(f"Empirical methodology, experimental results, and key findings")
            subtopics.append(f"Limitations, performance trade-offs, and failure conditions")
            subtopics.append(f"Recent advancements and future research directions")

            search_queries.append(clean_q)
            if entities:
                search_queries.append(" ".join(entities[:3]))
                search_queries.append(f"{entities[0]} empirical benchmarks" if len(entities) > 0 else clean_q)

        # Extract target conditions (e.g. low-resource, high-temperature, ambient, mobile)
        cond_keywords = ["low-resource", "high-temperature", "ambient", "mobile", "edge", "zero-shot", "few-shot", "extreme"]
        for ck in cond_keywords:
            if ck in clean_q.lower():
                target_conditions.append(ck)

        core_intent = f"Investigate {clean_q} with empirical grounding across {domain}"

        return QuestionAnalysis(
            question=clean_q,
            core_intent=core_intent,
            domain=domain,
            subtopics=subtopics,
            key_entities=entities,
            search_queries=list(dict.fromkeys(search_queries)),
            requires_comparison=is_comparative,
            target_conditions=target_conditions,
        )

    async def analyze_question_async(self, question: str) -> QuestionAnalysis:
        """Asynchronous question analysis, optionally leveraging local LLM if available."""
        # Fast local deterministic decomposition is default and robust
        analysis = self.analyze_question(question)

        # If runtime engine is supplied and healthy, we can enrich with local model
        if self.runtime:
            try:
                prompt = (
                    f"Analyze this research question into subtopics and search keywords:\n"
                    f"Question: {question}\n"
                    f"Return 3-4 bullet subtopics."
                )
                res = await self.runtime.reason(prompt=prompt, model_id="qwen3:8b")
                if res and res.text_or_data:
                    lines = [line.strip("- *").strip() for line in res.text_or_data.split("\n") if line.strip().startswith(("-", "*", "1.", "2.", "3.", "4."))]
                    if lines:
                        # Append any high-quality model-suggested subtopics without duplicating
                        for l in lines:
                            if l and l not in analysis.subtopics and len(analysis.subtopics) < 6:
                                analysis.subtopics.append(l)
            except Exception as e:
                logger.debug("Local LLM question enrichment skipped, using deterministic analysis", error=str(e))

        return analysis

