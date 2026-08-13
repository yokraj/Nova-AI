"""Confidence Estimator calculating probability scores for diagnostics.
"""

from typing import Optional

from app.agents.software_engineer.debugging.interfaces import ConfidenceEstimator
from app.agents.software_engineer.debugging.models import (
    ConfidenceReport,
    RepairPlan,
    RootCause,
)


class DiagnosticConfidenceEstimator(ConfidenceEstimator):
    """Calculates diagnostics confidence metric scales."""

    def estimate_confidence(
        self, root_cause: RootCause, plan: Optional[RepairPlan]
    ) -> ConfidenceReport:
        """Determines success probabilities.

        Args:
            root_cause: Detected root cause details.
            plan: Estimated repair plan options.

        Returns:
            ConfidenceReport.
        """
        rc_conf = root_cause.confidence_score
        rep_conf = plan.confidence_score if plan else 0.0

        # Overall success formula
        overall = (rc_conf + rep_conf) / 2.0 if plan else rc_conf * 0.5

        return ConfidenceReport(
            root_cause_confidence=round(rc_conf, 2),
            repair_confidence=round(rep_conf, 2),
            overall_success_probability=round(overall, 2),
        )
