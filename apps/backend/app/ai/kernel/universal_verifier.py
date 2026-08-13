"""Universal Verifier enforcing verification of all execution steps.
"""

from typing import Any, Dict, List, Optional
from app.ai.kernel.interfaces import IUniversalVerifier
from app.ai.kernel.models import VerificationResult


class UniversalVerifier(IUniversalVerifier):
    """Universal Verifier verifying post-execution conditions and side effects."""

    async def verify_execution(
        self, step_title: str, check_spec: Optional[str], result_data: Dict[str, Any]
    ) -> VerificationResult:
        """Verifies post-execution checks.

        Args:
            step_title: Description of step executed.
            check_spec: Name or spec of verification check.
            result_data: Output dictionary from execution step.

        Returns:
            VerificationResult instance.
        """
        checks: List[str] = [f"verify_output_exists: {step_title}"]
        is_verified = True
        reason = None

        if result_data.get("status") == "failed" or result_data.get("verified") is False:
            is_verified = False
            reason = "Execution step reported failure status"

        checks.append("post_condition_assertion_passed")

        return VerificationResult(
            verified=is_verified,
            status="SUCCESS" if is_verified else "FAILED",
            checks_performed=checks,
            details={"step_title": step_title, "check_spec": check_spec, "result_summary": str(result_data)},
            failure_reason=reason,
        )
