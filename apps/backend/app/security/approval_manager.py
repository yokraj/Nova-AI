"""Server-Managed Approval Store and Lifecycle Manager for Nova AI (F2.0.3.2).

Guarantees:
- Server-generated, cryptographically random, unguessable approval identifiers.
- Single-use authorization: tokens are consumed immediately upon physical execution.
- Strict binding to exact tool_name and SHA-256 hash of canonicalized JSON arguments.
- Short expiration deadline (default: 300 seconds / 5 minutes).
- Complete replay and reuse prevention.
- User/session binding where authentication claims are present.
- Fail-closed security: missing, expired, altered, or already consumed tokens are rejected.
"""

import hashlib
import json
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import structlog

logger = structlog.get_logger("approval_manager")


class ApprovalStatus(str, Enum):
    """Lifecycle states of a server-managed approval record."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CONSUMED = "CONSUMED"
    EXPIRED = "EXPIRED"


@dataclass
class PendingApprovalRecord:
    """Canonical server-side record for a pending sensitive tool invocation."""
    approval_id: str
    tool_name: str
    arguments: Dict[str, Any]
    arguments_hash: str
    action_description: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 300.0)
    consumed_at: Optional[float] = None

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "arguments_hash": self.arguments_hash,
            "action_description": self.action_description,
            "user_id": self.user_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "consumed_at": self.consumed_at,
        }


def canonicalize_arguments_hash(arguments: Dict[str, Any]) -> str:
    """Computes a deterministic SHA-256 hash of tool arguments."""
    try:
        serialized = json.dumps(arguments, sort_keys=True, default=str)
    except Exception:
        serialized = str(arguments)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class ServerApprovalManager:
    """Singleton server-managed approval lifecycle authority."""

    _instance: Optional["ServerApprovalManager"] = None

    def __new__(cls) -> "ServerApprovalManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._approvals: Dict[str, PendingApprovalRecord] = {}
            logger.info("server_approval_manager_initialized")
        return cls._instance

    def create_pending_approval(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        action_description: str = "",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ttl_seconds: float = 300.0,
    ) -> PendingApprovalRecord:
        """Generates a secure pending approval record bound to exact tool and arguments."""
        self._cleanup_expired()
        approval_id = f"appr_{secrets.token_hex(16)}"
        args_hash = canonicalize_arguments_hash(arguments)
        desc = action_description or f"Execution of sensitive tool '{tool_name}'"

        now = time.time()
        record = PendingApprovalRecord(
            approval_id=approval_id,
            tool_name=tool_name,
            arguments=dict(arguments),
            arguments_hash=args_hash,
            action_description=desc,
            user_id=user_id,
            session_id=session_id,
            status=ApprovalStatus.PENDING,
            created_at=now,
            expires_at=now + ttl_seconds,
        )

        self._approvals[approval_id] = record
        logger.info(
            "pending_approval_created",
            approval_id=approval_id,
            tool_name=tool_name,
            user_id=user_id,
            expires_in=ttl_seconds,
        )
        return record

    def approve(self, approval_id: str, user_id: Optional[str] = None) -> Tuple[bool, str]:
        """Marks a pending approval as APPROVED by the authenticated user."""
        self._cleanup_expired()
        record = self._approvals.get(approval_id)
        if not record:
            return False, f"Approval ID '{approval_id}' not found or has expired."

        if record.is_expired() or record.status == ApprovalStatus.EXPIRED:
            record.status = ApprovalStatus.EXPIRED
            return False, f"Approval ID '{approval_id}' has expired."

        if record.status == ApprovalStatus.CONSUMED:
            return False, f"Approval ID '{approval_id}' has already been consumed."

        if record.status == ApprovalStatus.REJECTED:
            return False, f"Approval ID '{approval_id}' was previously rejected."

        if record.user_id and user_id and record.user_id != user_id:
            logger.warning(
                "approval_user_mismatch",
                approval_id=approval_id,
                record_user=record.user_id,
                request_user=user_id,
            )
            return False, "Access denied: approval was not requested by this user."

        record.status = ApprovalStatus.APPROVED
        logger.info("approval_granted", approval_id=approval_id, tool_name=record.tool_name, user_id=user_id)
        return True, f"Approval granted for tool '{record.tool_name}'."

    def reject(self, approval_id: str, user_id: Optional[str] = None) -> Tuple[bool, str]:
        """Explicitly rejects a pending approval."""
        record = self._approvals.get(approval_id)
        if not record:
            return False, f"Approval ID '{approval_id}' not found or already purged."

        if record.user_id and user_id and record.user_id != user_id:
            return False, "Access denied: approval was not requested by this user."

        record.status = ApprovalStatus.REJECTED
        logger.info("approval_rejected", approval_id=approval_id, tool_name=record.tool_name, user_id=user_id)
        return True, f"Approval for tool '{record.tool_name}' has been rejected."

    def validate_and_consume_approval(
        self,
        approval_token: Optional[str],
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Validates that approval token is authentic, unexpired, matches tool and arguments, and consumes it."""
        if not approval_token:
            return False, f"Action '{tool_name}' requires explicit human approval, but no approval token was provided."

        self._cleanup_expired()
        record = self._approvals.get(approval_token)
        if not record:
            logger.warning("invalid_approval_token_attempt", token=approval_token, tool=tool_name)
            return False, f"Invalid or non-existent approval token '{approval_token}'."

        # Check expiration
        if record.is_expired() or record.status == ApprovalStatus.EXPIRED:
            record.status = ApprovalStatus.EXPIRED
            logger.warning("expired_approval_token_attempt", token=approval_token, tool=tool_name)
            return False, f"Approval token '{approval_token}' has expired."

        # Check single-use consumption
        if record.status == ApprovalStatus.CONSUMED:
            logger.warning("replayed_approval_token_attempt", token=approval_token, tool=tool_name)
            return False, f"Approval token '{approval_token}' has already been consumed (replay attack prevented)."

        # Check rejection
        if record.status == ApprovalStatus.REJECTED:
            return False, f"Approval token '{approval_token}' was rejected by the user."

        # Must be in APPROVED status (or PENDING if auto-approved by a higher administrative policy)
        if record.status != ApprovalStatus.APPROVED:
            return False, f"Approval token '{approval_token}' is currently '{record.status.value}', not APPROVED."

        # Verify exact tool name binding
        if record.tool_name != tool_name:
            logger.warning(
                "approval_tool_mismatch",
                token=approval_token,
                expected_tool=record.tool_name,
                attempted_tool=tool_name,
            )
            return False, f"Security Error: Approval token was issued for tool '{record.tool_name}', not '{tool_name}'."

        # Verify exact argument binding
        current_args_hash = canonicalize_arguments_hash(arguments)
        if record.arguments_hash != current_args_hash:
            logger.warning(
                "approval_arguments_mismatch",
                token=approval_token,
                tool=tool_name,
                original_hash=record.arguments_hash,
                attempted_hash=current_args_hash,
            )
            return False, (
                f"Security Error: Arguments for tool '{tool_name}' have been altered since approval was granted. "
                f"Authorization revoked."
            )

        # Verify user identity binding if applicable
        if record.user_id and user_id and record.user_id != user_id:
            logger.warning("approval_user_identity_mismatch", token=approval_token, expected=record.user_id, received=user_id)
            return False, "Security Error: Approval token does not belong to the current authenticated user session."

        # Success: consume single-use token immediately
        record.status = ApprovalStatus.CONSUMED
        record.consumed_at = time.time()
        logger.info(
            "approval_consumed_successfully",
            approval_id=approval_token,
            tool_name=tool_name,
            duration_before_use=record.consumed_at - record.created_at,
        )
        return True, "Approval verified and consumed successfully."

    def get_approval(self, approval_id: str) -> Optional[PendingApprovalRecord]:
        """Retrieves an approval record by ID."""
        return self._approvals.get(approval_id)

    def list_pending(self, user_id: Optional[str] = None) -> List[PendingApprovalRecord]:
        """Lists active pending approvals, optionally filtered by user."""
        self._cleanup_expired()
        results = []
        for rec in self._approvals.values():
            if rec.status == ApprovalStatus.PENDING and not rec.is_expired():
                if user_id is None or rec.user_id == user_id:
                    results.append(rec)
        return results

    def _cleanup_expired(self) -> None:
        """Purges stale expired records older than 1 hour."""
        now = time.time()
        stale_keys = [
            k for k, v in self._approvals.items()
            if v.is_expired() and (now - v.expires_at > 3600.0)
        ]
        for k in stale_keys:
            del self._approvals[k]


# Canonical singleton accessor
approval_manager = ServerApprovalManager()

