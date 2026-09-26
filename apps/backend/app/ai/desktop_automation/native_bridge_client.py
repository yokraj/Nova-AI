"""Python Native Bridge HTTP Client.

Unifies Python backend application and OS automation with the single NativeBridge execution boundary on port 3001.
Zero external dependencies (uses urllib.request).
"""

from typing import Any, Dict, Optional
import json
import time
import urllib.request
import urllib.error
import uuid
import structlog

logger = structlog.get_logger("native_bridge_client")


class NativeBridgeClient:
    """Python client communicating with Nova Native Bridge server on http://127.0.0.1:3001."""

    def __init__(self, base_url: str = "http://127.0.0.1:3001") -> None:
        self.base_url = base_url.rstrip("/")

    def check_health(self) -> Dict[str, Any]:
        """Queries GET /health endpoint."""
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
        """Returns True if Native Bridge server is online."""
        return self.check_health().get("healthy", False)

    def health_check(self) -> bool:
        """Returns True if Native Bridge server is online."""
        return self.is_available()

    def execute_native(
        self,
        capability: str,
        action: str,
        target: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        risk_level: str = "LOW",
        is_approved: bool = True,
    ) -> Dict[str, Any]:
        """Executes native OS action via Native Bridge HTTP endpoint /api/v1/native-execute."""
        url = f"{self.base_url}/api/v1/native-execute"
        req_id = f"py-req-{uuid.uuid4().hex[:8]}"

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
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                if resp.status == 200:
                    res_json = json.loads(resp.read().decode("utf-8"))
                    return res_json
                else:
                    return {
                        "requestId": req_id,
                        "status": "FAILED",
                        "verification": "VERIFICATION_FAILED",
                        "message": f"Native Bridge returned HTTP {resp.status}",
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
        except Exception as e:
            logger.error("Native Bridge execution exception", error=str(e))
            return {
                "requestId": req_id,
                "status": "FAILED",
                "verification": "VERIFICATION_FAILED",
                "message": f"Native Bridge execution error: {str(e)}",
                "errorReason": "EXECUTION_ERROR",
            }
