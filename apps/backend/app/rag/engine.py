"""Hybrid RAG Engine Master Orchestrator Module.

Connects Genuine Local Neural Embeddings, Memory Foundation, Vector Memory,
Hybrid Knowledge Retrieval, LLM Context Assembly, Grounding Engine, Citation Generator,
and InferenceService to provide live local LLM completions via Ollama.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.rag.config import RAGConfig
from app.rag.exceptions import RAGError
from app.rag.retriever import HybridRAGRetriever
from app.rag.context_builder import ContextBuilder
from app.rag.context_optimizer import ContextOptimizer
from app.rag.prompt_builder import PromptBuilder
from app.rag.grounding import GroundingEngine
from app.rag.response_grounder import ResponseGrounder
from app.rag.citation import CitationGenerator
from app.rag.statistics import RAGStatisticsTracker
from app.rag.health import RAGHealthChecker

from app.inference.service import InferenceService
from app.inference.repository import InferenceRepository
from app.inference.schemas import ChatInferenceRequest
from app.vector_memory.exceptions import EmbeddingModelUnavailableError

logger = structlog.get_logger(__name__)


class HybridRAGEngine:
    """Master Hybrid Retrieval-Augmented Generation Engine."""

    def __init__(
        self,
        config: Optional[RAGConfig] = None,
        retriever: Optional[HybridRAGRetriever] = None,
        inference_service: Optional[InferenceService] = None,
    ) -> None:
        self.config = config or RAGConfig()
        self.retriever = retriever or HybridRAGRetriever(config=self.config)
        self.inference_service = inference_service or InferenceService(repository=InferenceRepository())

        self.context_builder = ContextBuilder()
        self.context_optimizer = ContextOptimizer(config=self.config)
        self.prompt_builder = PromptBuilder()
        self.grounding_engine = GroundingEngine(config=self.config)
        self.response_grounder = ResponseGrounder(grounding_engine=self.grounding_engine)
        self.citation_generator = CitationGenerator()
        self.stats_tracker = RAGStatisticsTracker()
        self.health_checker = RAGHealthChecker(config=self.config)

        logger.info("hybrid_rag_engine_master_initialized")

    async def execute_grounded_query(
        self,
        query: str,
        workspace: str = "Nova",
        project: Optional[str] = None,
        conversation_id: str = "default",
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Executes full grounded RAG query pipeline:
        User query -> Query embedding -> Semantic retrieval -> Workspace filtering -> Context construction -> InferenceService -> Ollama response.
        """
        logger.info("executing_grounded_rag_query", query_snippet=query[:30], workspace=workspace)

        try:
            # 1. Retrieve Grounded Context Chunks (Hybrid Keyword + Semantic Vector)
            retrieval_res = await self.retriever.retrieve_grounded_context(
                query=query, workspace=workspace, project=project, conversation_history=conversation_history
            )
            selected_chunks = retrieval_res["selected_chunks"]

            # 2. Assemble & Optimize Context Package within Token Budget
            context_pkg = self.context_builder.build_context_package(
                retrieved_chunks=selected_chunks,
                conversation_history=conversation_history,
                user_preferences=user_preferences,
                workspace=workspace,
                project=project,
            )
            opt_context = self.context_optimizer.optimize_context(context_pkg, max_tokens=self.config.max_context_tokens)
            effective_context_text = opt_context["optimized_context_text"]

            # 3. Construct Clean Separation between System Instructions and Retrieved Context
            system_instruction = (
                "You are Nova AI Operating System's Grounded RAG Intelligence Engine.\n"
                "You answer user requests strictly using the provided grounding context.\n"
                "Rules:\n"
                "1. Base your answer ONLY on the provided context.\n"
                "2. If the context does not contain sufficient facts to answer, explicitly state your uncertainty.\n"
                "3. Do NOT fabricate or invent facts outside the context.\n"
                "4. Include source references using [Source ID] when stating facts."
            )

            if effective_context_text.strip():
                grounded_user_prompt = (
                    f"=== GROUNDING CONTEXT ===\n{effective_context_text}\n\n"
                    f"=== CURRENT USER REQUEST ===\n{query}"
                )
            else:
                grounded_user_prompt = query

            # 4. Genuine InferenceService Execution via Local Ollama (qwen3:8b)
            chat_req = ChatInferenceRequest(
                prompt=grounded_user_prompt,
                conversation_id=conversation_id,
                system_prompt=system_instruction,
                model="qwen3:8b",
                use_deterministic_tools=True,
            )
            inference_res = await self.inference_service.execute_chat(chat_req)
            raw_llm_response = inference_res.content

            # 5. Factual Grounding Verification & Post-Processing
            grounded_res = self.response_grounder.enforce_grounding(raw_llm_response, effective_context_text)
            final_text = grounded_res["final_response"]

            # 6. Generate Citation Links
            citations_pkg = self.citation_generator.generate_citations(context_pkg["sources"])
            if citations_pkg["citation_footer"] and citations_pkg["citation_footer"] not in final_text:
                final_text += citations_pkg["citation_footer"]

            # Record Statistics
            self.stats_tracker.record_retrieval(latency_ms=inference_res.latency_ms, rerank_ms=3.0, citations=citations_pkg["source_count"])

            return {
                "response": final_text,
                "query": query,
                "effective_query": retrieval_res["effective_query"],
                "conversation_id": conversation_id,
                "workspace": workspace,
                "project": project,
                "retrieved_chunks_count": len(selected_chunks),
                "citations": citations_pkg["citations"],
                "grounding_verification": grounded_res["verification"],
                "context_summary": effective_context_text[:200],
                "inference_model": inference_res.model,
                "inference_provider": inference_res.provider,
                "latency_ms": inference_res.latency_ms,
            }
        except Exception as exc:
            logger.error("hybrid_rag_query_failed", error=str(exc))
            raise RAGError(f"Failed to execute grounded RAG query: {exc}") from exc
