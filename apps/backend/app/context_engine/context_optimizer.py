"""Context Optimizer Coordinator Module.

Coordinates Context Fusion, Conflict Resolution, Deduplication, Ranking, Priority Engine,
Context Compression, and Token Budgeting into a single optimization pipeline.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.context_engine.config import ContextEngineConfig
from app.context_engine.context_fusion import ContextFusionEngine
from app.context_engine.context_conflict_resolver import ContextConflictResolver
from app.context_engine.context_deduplicator import ContextDeduplicator
from app.context_engine.context_ranker import ContextRanker
from app.context_engine.priority_engine import PriorityEngine
from app.context_engine.context_compressor import ContextCompressor
from app.context_engine.token_budget import TokenBudgetEngine

logger = structlog.get_logger(__name__)


class ContextOptimizer:
    """Enterprise Master Context Optimizer Coordinator."""

    def __init__(
        self,
        config: Optional[ContextEngineConfig] = None,
        fusion_engine: Optional[ContextFusionEngine] = None,
        conflict_resolver: Optional[ContextConflictResolver] = None,
        deduplicator: Optional[ContextDeduplicator] = None,
        ranker: Optional[ContextRanker] = None,
        priority_engine: Optional[PriorityEngine] = None,
        compressor: Optional[ContextCompressor] = None,
        budget_engine: Optional[TokenBudgetEngine] = None,
    ) -> None:
        self.config = config or ContextEngineConfig()
        self.fusion_engine = fusion_engine or ContextFusionEngine(config=self.config)
        self.conflict_resolver = conflict_resolver or ContextConflictResolver()
        self.deduplicator = deduplicator or ContextDeduplicator()
        self.ranker = ranker or ContextRanker()
        self.priority_engine = priority_engine or PriorityEngine()
        self.compressor = compressor or ContextCompressor(config=self.config)
        self.budget_engine = budget_engine or TokenBudgetEngine(config=self.config)
        logger.info("context_optimizer_coordinator_initialized")

    def optimize_candidates(
        self,
        candidates: List[Dict[str, Any]],
        token_budget: Optional[int] = None,
        workspace: str = "Nova",
        project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Runs optimization pipeline: Fuse -> Resolve Conflicts -> Deduplicate -> Rank -> Prioritize -> Fit to Budget."""
        # 1. Weighted Fusion
        fused = self.fusion_engine.fuse_candidates(candidates, target_workspace=workspace, target_project=project)

        # 2. Conflict Resolution
        resolved = self.conflict_resolver.resolve_conflicts(fused)

        # 3. Deduplication
        deduped = self.deduplicator.deduplicate(resolved)

        # 4. Multi-Attribute Ranking
        ranked = self.ranker.rank_context_blocks(deduped)

        # 5. Priority Tiering
        prioritized = self.priority_engine.assign_priorities(ranked)

        # 6. Fit to Token Budget
        fit_res = self.budget_engine.fit_to_budget(prioritized, target_budget=token_budget)

        logger.info("context_optimization_pipeline_completed", input_count=len(candidates), final_count=len(fit_res["fitted_candidates"]))
        return fit_res
