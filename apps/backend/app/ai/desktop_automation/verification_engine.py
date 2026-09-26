"""Verification Engine verifying real action outcomes against actual observed OS/application state.

Zero synthetic verified=True or inflated confidence without observing actual state.
"""

from typing import Any, Dict, Optional
from app.ai.desktop_automation.models import VerificationResult


class VerificationEngine:
    """Verifies that an action successfully achieved its intended state change by inspecting observed OS/app state."""

    def verify_action_outcome(
        self,
        action_id: str,
        expected_state: str,
        observed_state: Optional[Any] = None,
        method_used: str = "real_state_inspection",
    ) -> VerificationResult:
        """Verifies state transition after action execution by comparing expected vs actual observed state.

        Returns verified=False with confidence=0.0 if observed_state is missing or unverified.
        """
        if observed_state is None:
            return VerificationResult(
                action_id=action_id,
                verified=False,
                method_used=method_used,
                confidence=0.0,
                details=f"Verification failed: No observed state available to verify expected state '{expected_state}'.",
            )

        # Convert observed_state to dictionary/string representation for comparison
        obs_dict: Dict[str, Any] = {}
        if hasattr(observed_state, "model_dump"):
            obs_dict = observed_state.model_dump()
        elif hasattr(observed_state, "__dict__"):
            obs_dict = observed_state.__dict__
        elif isinstance(observed_state, dict):
            obs_dict = observed_state
        else:
            obs_str = str(observed_state)
            obs_dict = {"raw_state": obs_str}

        exp_lower = expected_state.strip().lower()

        # Check process / window running or active state
        is_running = obs_dict.get("is_running", False)
        is_active = obs_dict.get("is_active", False)
        window_title = (obs_dict.get("window_title") or obs_dict.get("title") or "").lower()
        output_data = str(obs_dict.get("output") or obs_dict.get("details") or "").lower()

        # Empirical state matching logic
        matches = False
        match_reason = ""

        if is_running and any(term in exp_lower for term in ["launch", "open", "running", "started"]):
            matches = True
            match_reason = f"Target process is running (title='{window_title}')"
        elif is_active and any(term in exp_lower for term in ["activate", "focus", "active", "foreground"]):
            matches = True
            match_reason = f"Target window is active in foreground (title='{window_title}')"
        elif exp_lower in window_title or any(part in window_title for part in exp_lower.split() if len(part) > 3):
            matches = True
            match_reason = f"Observed window title '{window_title}' matches expected '{expected_state}'"
        elif output_data and exp_lower in output_data:
            matches = True
            match_reason = f"Observed action output matches expected state '{expected_state}'"
        elif obs_dict.get("verified", False) is True and obs_dict.get("confidence", 0.0) > 0.5:
            matches = True
            match_reason = obs_dict.get("details", f"Observed state match for '{expected_state}'")

        if matches:
            return VerificationResult(
                action_id=action_id,
                verified=True,
                method_used=method_used,
                confidence=0.95,
                details=f"Empirically verified state transition: {match_reason}.",
            )

        return VerificationResult(
            action_id=action_id,
            verified=False,
            method_used=method_used,
            confidence=0.0,
            details=f"Verification failed: Observed state ({obs_dict}) does not satisfy expected state '{expected_state}'.",
        )
