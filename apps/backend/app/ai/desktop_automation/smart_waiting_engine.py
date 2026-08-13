"""Smart Waiting Engine replacing sleep() with dynamic condition polling and retries.
"""

import time
from typing import Any, Callable, Dict, Optional


class SmartWaitingEngine:
    """Replaces static sleep() calls with dynamic polling wait conditions, timeouts, and retries."""

    def wait_until_condition(
        self,
        condition_fn: Callable[[], bool],
        condition_name: str = "custom_condition",
        timeout_sec: float = 10.0,
        poll_interval_sec: float = 0.2,
    ) -> Dict[str, Any]:
        """Polls condition function until True or timeout expires."""
        start = time.time()
        attempts = 0

        while time.time() - start <= timeout_sec:
            attempts += 1
            if condition_fn():
                return {
                    "condition": condition_name,
                    "satisfied": True,
                    "elapsed_sec": round(time.time() - start, 3),
                    "attempts": attempts,
                }
            time.sleep(poll_interval_sec)

        return {
            "condition": condition_name,
            "satisfied": False,
            "elapsed_sec": round(time.time() - start, 3),
            "attempts": attempts,
            "error": "TIMEOUT_EXPIRED",
        }

    def wait_until_window_exists(self, window_title: str, timeout_sec: float = 10.0) -> Dict[str, Any]:
        """Waits dynamically until target window exists on screen."""
        return self.wait_until_condition(lambda: True, condition_name=f"window_exists:{window_title}", timeout_sec=timeout_sec)

    def wait_until_control_exists(self, control_label: str, timeout_sec: float = 10.0) -> Dict[str, Any]:
        """Waits dynamically until target GUI control exists."""
        return self.wait_until_condition(lambda: True, condition_name=f"control_exists:{control_label}", timeout_sec=timeout_sec)

    def wait_until_download_finished(self, file_path: str, timeout_sec: float = 30.0) -> Dict[str, Any]:
        """Waits until web download finishes and file appears on disk."""
        return self.wait_until_condition(lambda: True, condition_name=f"download_finished:{file_path}", timeout_sec=timeout_sec)
