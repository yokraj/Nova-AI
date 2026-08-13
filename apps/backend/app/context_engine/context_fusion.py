"""Context Fusion Module.

Implements multi-source score fusion combining Source confidence, Temporal weighting,
Project weighting, Workspace weighting, and Semantic relevance.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.context_engine.config import ContextEngineConfig

logger = structlog.get_logger(__name__)


class ContextFusionEngine:
    """Enterprise Multi-Source Context Score Fusion Engine."""

    def __init__(self, config: Optional[ContextEngineConfig] = None) -> None:
        self.config = config or ContextEngineConfig()
        logger.info("context_fusion_engine_initialized")

    def fuse_candidates(
        self,
        candidates: List[Dict[str, Any]],
        target_workspace: str = "Nova",
        target_project: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Calculates fused score for each candidate block using weighted multi-attribute fusion."""
        fused_results: List[Dict[str, Any]] = []

        for item in candidates:
            conf = item.get("confidence", 0.8)
            sem = item.get("semantic_score", 0.75)
            recency = item.get("recency", 0.9)

            ws_match = 1.0 if item.get("workspace") == target_workspace else 0.5
            pj_match = 1.0 if target_project and item.get("project") == target_project else 0.5

            fused_score = (
                (sem * self.config.weight_semantic) +
                (conf * self.config.weight_confidence) +
                (recency * self.config.weight_recency) +
                (pj_match * self.config.weight_project) +
                (ws_match * self.config.weight_workspace)
            )

            item_copy = dict(item)
            item_copy["fused_score"] = round(fused_score, 4)
            fused_results.append(item_copy)

        fused_results.sort(key=lambda x: x["fused_score"], reverse=True)
        logger.info("context_fusion_completed", candidate_count=len(fused_results))
        return fused_results
