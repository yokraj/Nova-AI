"""WebSocket Handshake & Token Authentication Module.

Decodes JWT access tokens during WebSocket connection handshake using project's
security infrastructure and resolves user identity and RBAC permissions.
"""

from typing import Any, Dict, Optional, Set
from fastapi import WebSocket
from jose import JWTError
import structlog

from app.identity.infrastructure.rbac import ROLE_PERMISSIONS
from app.identity.infrastructure.security import decode_access_token
from app.websocket.exceptions import WebSocketAuthenticationError

logger = structlog.get_logger(__name__)


def extract_token_from_websocket(websocket: WebSocket, token: Optional[str] = None) -> str:
    """Extracts JWT token from query string parameter, headers, or passed parameter."""
    if token and len(token.strip()) > 0:
        return token.strip()

    # 1. Query parameter ?token=...
    query_token = websocket.query_params.get("token")
    if query_token and len(query_token.strip()) > 0:
        return query_token.strip()

    # 2. Authorization Header
    auth_header = websocket.headers.get("authorization") or websocket.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1].strip()

    raise WebSocketAuthenticationError("JWT bearer authentication token missing in WebSocket request.")


def authenticate_websocket_connection(websocket: WebSocket, token: Optional[str] = None) -> Dict[str, Any]:
    """Decodes JWT access token and resolves user identity claims and RBAC permissions."""
    jwt_token = extract_token_from_websocket(websocket, token)
    try:
        payload = decode_access_token(jwt_token)
        user_id = payload.get("sub")
        role = payload.get("role", "user")

        if not user_id:
            logger.warning("websocket_auth_failed_missing_sub")
            raise WebSocketAuthenticationError("Invalid token claims: subject (user_id) missing.")

        permissions: Set[str] = ROLE_PERMISSIONS.get(role, set())

        logger.info("websocket_auth_success", user_id=user_id, role=role)
        return {
            "user_id": str(user_id),
            "role": role,
            "permissions": permissions,
        }
    except JWTError as exc:
        logger.warning("websocket_auth_failed_jwt_error", error=str(exc))
        raise WebSocketAuthenticationError(f"Could not validate JWT credentials: {str(exc)}") from exc
    except Exception as exc:
        if isinstance(exc, WebSocketAuthenticationError):
            raise
        logger.warning("websocket_auth_failed_unhandled", error=str(exc))
        raise WebSocketAuthenticationError(str(exc)) from exc
