"""Dashboard Session Manager Module.

Manages active user session tokens, tracks login time, IP address, user-agent,
last activity, auto-expiration, and explicit session termination/revocation.
"""

from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
import uuid
import structlog

from app.security.exceptions import SessionExpiredException

logger = structlog.get_logger(__name__)


class DashboardSessionManager:
    """Enterprise User Session Manager tracking active dashboard logins."""

    def __init__(self, session_ttl_seconds: int = 3600) -> None:
        self.session_ttl = session_ttl_seconds
        self._sessions: Dict[str, Dict[str, Any]] = {}
        logger.info("session_manager_initialized", ttl_seconds=session_ttl_seconds)

    def create_session(self, user_id: str, role: str = "user", ip_address: str = "127.0.0.1", user_agent: str = "Unknown") -> Dict[str, Any]:
        """Creates a new active dashboard session."""
        session_id = str(uuid.uuid4())
        now = time.time()
        now_iso = datetime.now(timezone.utc).isoformat()

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "login_time": now_iso,
            "last_activity": now_iso,
            "created_at_ts": now,
            "last_activity_ts": now,
            "is_active": True,
        }

        self._sessions[session_id] = session_data
        logger.info("session_created", session_id=session_id, user_id=user_id, ip=ip_address)
        return session_data

    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validates if session is active and within TTL limits."""
        session = self._sessions.get(session_id)
        if not session or not session.get("is_active"):
            return None

        now = time.time()
        last_ts = session.get("last_activity_ts", now)

        if (now - last_ts) > self.session_ttl:
            logger.info("session_expired_ttl", session_id=session_id)
            self.expire_session(session_id)
            return None

        # Refresh last activity timestamp
        session["last_activity_ts"] = now
        session["last_activity"] = datetime.now(timezone.utc).isoformat()
        return session

    def refresh_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Refreshes active session activity timer."""
        return self.validate_session(session_id)

    def expire_session(self, session_id: str) -> None:
        """Marks session as expired."""
        if session_id in self._sessions:
            self._sessions[session_id]["is_active"] = False
            logger.info("session_expired", session_id=session_id)

    def terminate_session(self, session_id: str) -> bool:
        """Terminates and revokes an active session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info("session_terminated", session_id=session_id)
            return True
        return False

    def terminate_all_sessions(self, user_id: str) -> int:
        """Terminates all active sessions belonging to user_id."""
        to_remove = [sid for sid, s in self._sessions.items() if s.get("user_id") == user_id]
        for sid in to_remove:
            del self._sessions[sid]
        logger.info("all_sessions_terminated", user_id=user_id, count=len(to_remove))
        return len(to_remove)

    def list_active_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists active sessions filtered by user_id."""
        now = time.time()
        active = []
        for s in self._sessions.values():
            if s.get("is_active") and (now - s.get("last_activity_ts", 0)) <= self.session_ttl:
                if user_id is None or s.get("user_id") == user_id:
                    active.append(s)
        return active
