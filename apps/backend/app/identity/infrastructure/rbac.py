"""Role-Based Access Control (RBAC) authorization models for Nova AI.

Defines role permissions, extracts user claims from authorization tokens,
and checks role rights using FastAPI path dependencies.
"""

from typing import Dict, Set
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.identity.infrastructure.security import decode_access_token

# Bearer token HTTP adapter configuration
security_scheme = HTTPBearer()

# Role permissions matrix
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "admin": {
        "read:users",
        "write:users",
        "admin:access",
        "read:profile",
        "write:profile",
    },
    "user": {"read:profile", "write:profile"},
}


async def get_current_user_claims(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """Decodes access token credentials and validates user session claims.

    Args:
        credentials: The HTTPAuthorizationCredentials bearer token.

    Returns:
        A dictionary containing resolved user claims (user_id, role).

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        role = payload.get("role", "user")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims: subject missing.",
            )
        return {"user_id": user_id, "role": role}
    except JWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(error)}",
        )


class PermissionChecker:
    """FastAPI path dependency checking if user claims satisfy target permissions."""

    def __init__(self, required_permission: str) -> None:
        """Initializes the permission checker.

        Args:
            required_permission: The permission string key to validate.
        """
        self.required_permission = required_permission

    def __call__(self, claims: dict = Depends(get_current_user_claims)) -> dict:
        """Runs the validation check against resolved token claims.

        Args:
            claims: The dictionary claims from get_current_user_claims.

        Returns:
            The input claims dictionary if authorization checks succeed.

        Raises:
            HTTPException: If the user role does not possess the required permission.
        """
        role = claims.get("role", "user")
        allowed_permissions = ROLE_PERMISSIONS.get(role, set())
        if self.required_permission not in allowed_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this resource.",
            )
        return claims
