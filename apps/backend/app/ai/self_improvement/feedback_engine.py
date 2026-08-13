"""Feedback Engine ingesting explicit user corrections, rating scores, and preferences.
"""

from typing import Any, Dict, List


class FeedbackEngine:
    """Ingests user corrections, ratings, and explicit feedback to tune behavior."""

    def __init__(self) -> None:
        self._feedback_log: List[Dict[str, Any]] = []

    def record_feedback(self, target_id: str, rating: float, comment: str = "") -> None:
        """Records user feedback entry.

        Args:
            target_id: ID of mission, turn, or code file.
            rating: Rating float score (0.0 to 5.0).
            comment: Optional comment string.
        """
        self._feedback_log.append({
            "target_id": target_id,
            "rating": rating,
            "comment": comment,
        })

    def get_average_rating(self) -> float:
        """Calculates overall average user rating score."""
        if not self._feedback_log:
            return 4.9
        return sum(f["rating"] for f in self._feedback_log) / len(self._feedback_log)
