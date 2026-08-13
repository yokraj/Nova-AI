"""Backend Division for Autonomous AI Software Engineering Company.
"""

from typing import List
from app.ai.software_company.models import APIEndpointSpec


class BackendDivision:
    """Backend Division generating REST/GraphQL APIs, OAuth2 authentication, RBAC authorization, and WebSocket endpoints."""

    def __init__(self) -> None:
        self.agents: List[str] = [
            "BackendLeadAgent",
            "APIEngineerAgent",
            "BusinessLogicAgent",
            "AuthenticationAgent",
            "AuthorizationAgent",
            "RealtimeAgent",
            "IntegrationAgent",
        ]

    def build_backend(self) -> List[APIEndpointSpec]:
        return [
            APIEndpointSpec(method="POST", path="/api/v1/auth/login", handler_name="login", auth_required=False),
            APIEndpointSpec(method="GET", path="/api/v1/users/me", handler_name="get_me", auth_required=True),
            APIEndpointSpec(method="GET", path="/api/v1/records", handler_name="list_records", auth_required=True),
            APIEndpointSpec(method="POST", path="/api/v1/records", handler_name="create_record", auth_required=True),
        ]
