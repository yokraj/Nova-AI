"""Memory Scoring Engine Module.

Calculates dynamic priority and relevance scores based on Importance, Recency,
Usage Frequency, Relevance, and Confidence metrics.
"""

from datetime import datetime, timezone
import math
from typing import Any, Dict, Optional
import structlog

from app.memory.config import MemoryConfig

logger = structlog.get_logger(__name__)


class MemoryScoringEngine:
    """Enterprise Memory Scoring & Dynamic Ranking Engine."""

    def __init__(self, config: Optional[MemoryConfig] = None) -> None:
        self.config = config or MemoryConfig()
        logger.info("memory_scoring_engine_initialized")

    def calculate_recency_score(self, created_at: datetime) -> float:
        """Calculates exponential decay recency score between 0.0 and 1.0."""
        now = datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        
        age_hours = max(0.0, (now - created_at).total_seconds() / 3600.0)
        half_life_hours = 72.0  # 3 days half-life
        return math.exp(-math.log(2) * age_hours / half_life_hours)

    def calculate_frequency_score(self, access_count: int) -> float:
        """Calculates log-scaled usage frequency score between 0.0 and 1.0."""
        if access_count <= 0:
            return 0.0
        return min(1.0, math.log(1 + access_count) / math.log(100))

    def calculate_priority_score(
        self,
        importance: float,
        created_at: datetime,
        access_count: int,
        relevance: float = 1.0,
        confidence: float = 1.0,
    ) -> float:
        """Calculates weighted composite priority score."""
        recency = self.calculate_recency_score(created_at)
        frequency = self.calculate_frequency_score(access_count)

        score = (
            (importance * self.config.weight_importance) +
            (recency * self.config.weight_recency) +
            (frequency * self.config.weight_frequency) +
            (relevance * self.config.weight_relevance) +
            (confidence * self.config.weight_confidence)
        )
        return round(min(1.0, max(0.0, score)), 4)
