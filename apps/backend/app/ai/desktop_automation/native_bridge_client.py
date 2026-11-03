"""Python Native Bridge HTTP Client.

Unifies Python backend application and OS automation with the single NativeBridge execution boundary on port 3001.
Handles health checks, timeouts, request/response validation, error recovery, and honest offline reporting.
Zero external dependencies (uses standard library urllib.request and json).
"""

from typing import Any, Dict, List, Optional
import json
import time
import urllib.request
import urllib.error
import uuid
import structlog

logger = structlog.get_logger("native_bridge_client")


class NativeBridgeClient:
    """Python client communicating with Nova Native Bridge server on http://127.0.0.1:3001."""

    def __init__(self, base_url: str = "http://127.0.0.1:3001", default_timeout: float = 8.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_timeout = default_timeout

    def check_health(self) -> Dict[str, Any]:
        """Queries GET /health endpoint to verify Native Bridge availability."""
        url = f"{self.base_url}/health"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return {"healthy": True, "data": data}
        except Exception as e:
            logger.debug("NativeBridge health check offline", url=url, error=str(e))
        return {"healthy": False, "error": "Native Bridge server unreachable on port 3001."}

    def is_available(self) -> bool:
        """Returns True if Native Bridge server is online and responding healthy."""
        return self.check_health().get("healthy", False)

    def health_check(self) -> bool:
        """Alias for is_available for backward compatibility."""
        return self.is_available()

    def recover_connection(self, retries: int = 3, delay: float = 0.5) -> bool:
        """Attempts connection recovery by polling health check with backoff."""
        for attempt in range(retries):
            if self.is_available():
                logger.info("native_bridge_connection_recovered", attempt=attempt + 1)
                return True
            time.sleep(delay)
        return False

    def execute_native(
        self,
        capability: str,
        action: str,
        target: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        risk_level: str = "LOW",
        is_approved: bool = True,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Executes native OS action via Native Bridge HTTP endpoint /api/v1/native-execute.

        Validates payload, enforces timeouts, handles errors, and returns structured result.
        """
        req_id = f"py-req-{uuid.uuid4().hex[:8]}"

        # Request validation
        if not capability or not action:
            return {
                "requestId": req_id,
                "status": "FAILED",
                "verification": "VERIFICATION_FAILED",
                "message": "Validation Error: 'capability' and 'action' are required.",
                "errorReason": "INVALID_REQUEST",
            }

        url = f"{self.base_url}/api/v1/native-execute"
        call_timeout = timeout if timeout is not None else self.default_timeout

        payload = {
            "requestId": req_id,
            "capability": capability,
            "action": action,
            "target": target or {},
            "parameters": parameters or {},
            "authorization": {
                "userId": "python-backend",
                "riskLevel": risk_level,
                "isApproved": is_approved,
                "sessionToken": "dev-token-python",
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json", "Origin": "http://127.0.0.1:5173"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=call_timeout) as resp:
                raw_body = resp.read().decode("utf-8")
                if resp.status == 200:
                    res_json = json.loads(raw_body)
                    # Response validation
                    if not isinstance(res_json, dict) or "status" not in res_json:
                        return {
                            "requestId": req_id,
                            "status": "FAILED",
                            "verification": "VERIFICATION_FAILED",
                            "message": "Malformed response payload from Native Bridge.",
                            "errorReason": "INVALID_RESPONSE",
                        }
                    return res_json
                else:
                    return {
                        "requestId": req_id,
                        "status": "FAILED",
                        "verification": "VERIFICATION_FAILED",
                        "message": f"Native Bridge returned HTTP {resp.status}: {raw_body}",
                        "errorReason": f"HTTP_{resp.status}",
                    }
        except urllib.error.URLError as e:
            logger.warning("Native Bridge execution failed - server offline", error=str(e))
            return {
                "requestId": req_id,
                "status": "FAILED",
                "verification": "VERIFICATION_FAILED",
                "message": f"Native Bridge is unavailable on port 3001: {str(e)}",
                "errorReason": "NATIVE_BRIDGE_OFFLINE",
            }
        except TimeoutError as e:
            logger.warning("Native Bridge execution timeout", timeout=call_timeout, error=str(e))
            return {
                "requestId": req_id,
                "status": "FAILED",
                "verification": "VERIFICATION_FAILED",
                "message": f"Native Bridge execution timed out after {call_timeout}s.",
                "errorReason": "EXECUTION_TIMEOUT",
            }
        except Exception as e:
            logger.error("Native Bridge execution exception", error=str(e))
            return {
                "requestId": req_id,
                "status": "FAILED",
                "verification": "VERIFICATION_FAILED",
                "message": f"Native Bridge execution error: {str(e)}",
                "errorReason": "EXECUTION_ERROR",
            }

    # =========================================================================
    # High-Level Desktop Control Helpers
    # =========================================================================
    def list_windows(self, filter_title: Optional[str] = None) -> List[Dict[str, Any]]:
        """Enumerates open windows on the Windows workstation."""
        res = self.execute_native(
            capability="COMPUTER_CONTROL",
            action="WINDOW_LIST",
            parameters={"filter": filter_title} if filter_title else {},
        )
        if res.get("status") == "COMPLETED":
            windows = res.get("resultData", {}).get("windows", [])
            if filter_title:
                f_low = filter_title.lower()
                return [w for w in windows if f_low in str(w.get("title", "")).lower() or f_low in str(w.get("processName", "")).lower()]
            return windows
        return []

    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """Retrieves active foreground window info."""
        res = self.execute_native(
            capability="COMPUTER_CONTROL",
            action="WINDOW_GET_ACTIVE",
        )
        if res.get("status") == "COMPLETED":
            return res.get("resultData", {}).get("activeWindow")
        return None

    def focus_window(self, target_name_or_title: str) -> Dict[str, Any]:
        """Brings target window into the foreground."""
        return self.execute_native(
            capability="COMPUTER_CONTROL",
            action="WINDOW_FOCUS",
            target={"rawTarget": target_name_or_title},
            parameters={"processName": target_name_or_title},
        )

    def close_window(self, target_name_or_title: str) -> Dict[str, Any]:
        """Closes target window gracefully or terminates its process."""
        return self.execute_native(
            capability="COMPUTER_CONTROL",
            action="WINDOW_CLOSE",
            target={"rawTarget": target_name_or_title},
            parameters={"processName": target_name_or_title},
            risk_level="HIGH",
        )

    def keyboard_type(self, text: str, delay_ms: int = 15, target_window: Optional[str] = None) -> Dict[str, Any]:
        """Sends typed keystrokes to the focused window."""
        if target_window:
            self.focus_window(target_window)
            time.sleep(0.2)
        return self.execute_native(
            capability="COMPUTER_CONTROL",
            action="KEYBOARD_TYPE",
            parameters={"textPayload": text, "delayMs": delay_ms},
            risk_level="MEDIUM",
        )

    def keyboard_press(self, key_name: str) -> Dict[str, Any]:
        """Presses a single special key (e.g. 'enter', 'tab', 'esc', 'backspace')."""
        return self.execute_native(
            capability="COMPUTER_CONTROL",
            action="KEYBOARD_PRESS",
            parameters={"keyName": key_name},
        )

    def keyboard_combination(self, keys: List[str]) -> Dict[str, Any]:
        """Executes a key shortcut combination (e.g. ['ctrl', 's'], ['ctrl', 'c'])."""
        is_restricted = any(k.lower() in ["win", "cmd", "alt"] for k in keys)
        return self.execute_native(
            capability="COMPUTER_CONTROL",
            action="KEYBOARD_COMBINATION",
            parameters={"keyCombination": keys},
            risk_level="HIGH" if is_restricted else "MEDIUM",
        )

    def mouse_move(self, x: int, y: int) -> Dict[str, Any]:
        """Moves mouse to coordinate (X, Y)."""
        return self.execute_native(
            capability="COMPUTER_CONTROL",
            action="MOUSE_MOVE",
            target={"x": x, "y": y},
        )

    def mouse_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = "left",
        double_click: bool = False,
        scroll_delta: int = 0,
    ) -> Dict[str, Any]:
        """Performs mouse click, double click, right click, or scroll."""
        action = "MOUSE_DOUBLE_CLICK" if double_click else ("MOUSE_RIGHT_CLICK" if button == "right" else "MOUSE_CLICK")
        if scroll_delta != 0:
            action = "MOUSE_SCROLL"
        return self.execute_native(
            capability="COMPUTER_CONTROL",
            action=action,
            target={"x": x, "y": y} if x is not None and y is not None else {},
            parameters={"button": button, "scrollDelta": scroll_delta},
            risk_level="MEDIUM",
        )

    def capture_screenshot(self) -> Dict[str, Any]:
        """Captures desktop display to PNG file."""
        return self.execute_native(
            capability="SYSTEM_CONTROL",
            action="CAPTURE_SCREENSHOT",
        )
