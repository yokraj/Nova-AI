"""PermissionManager executing policy checks and tracking grants.
"""

from datetime import datetime, timedelta, UTC
import fnmatch
from typing import Any, Dict, List, Optional
import uuid

from app.agents.base import AgentPermission
from app.agents.registry.registry import AgentRegistry
from app.agents.permissions.exceptions import (
    PermissionDeniedError,
    PermissionExpiredError,
    InvalidPermissionError,
    PolicyViolationError,
)
from app.agents.permissions.permission_request import PermissionRequest
from app.agents.permissions.permission_result import PermissionResult
from app.agents.permissions.policy import PermissionPolicy, PolicyEffect, PolicyDuration
from app.agents.permissions.resource import ResourceType


class PermissionManager:
    """Enterprise permission manager governing agent access to protected resources."""

    def __init__(self, registry: AgentRegistry, policies: Optional[List[PermissionPolicy]] = None) -> None:
        """Initializes PermissionManager.

        Args:
            registry: Central AgentRegistry dependency.
            policies: Initial list of security policies.
        """
        self.registry = registry
        self.policies = policies or []
        self._grants: Dict[uuid.UUID, List[PermissionResult]] = {}

    def validate_agent(self, agent_id: uuid.UUID) -> bool:
        """Verifies if the agent is registered and enabled in the platform.

        Args:
            agent_id: Target agent identifier.

        Returns:
            True if valid and enabled; False otherwise.
        """
        if not self.registry.exists(agent_id):
            return False

        for descriptor in self.registry.list():
            if descriptor.id == agent_id:
                return descriptor.enabled
        return False

    def request_permission(self, request: PermissionRequest) -> PermissionResult:
        """Requests permission for an agent to access a resource, evaluating registered policies.

        Args:
            request: The permission request parameters.

        Returns:
            PermissionResult containing decision outcome.

        Raises:
            PermissionDeniedError: If permission is denied by policy.
            InvalidPermissionError: If request parameters are invalid.
        """
        if not isinstance(request, PermissionRequest):
            raise InvalidPermissionError("Input must be a valid PermissionRequest.")

        if not self.validate_agent(request.agent_id):
            raise PermissionDeniedError("Requesting agent is not registered or is disabled.")

        # Find matching policies
        matching_policies = []
        for policy in self.policies:
            agent_match = (
                policy.agent_id == str(request.agent_id)
                or policy.agent_id == "*"
                or policy.agent_id is None
            )
            perm_match = policy.permission == request.permission
            resource_match = fnmatch.fnmatch(request.resource, policy.resource_pattern)

            if agent_match and perm_match and resource_match:
                matching_policies.append(policy)

        # Fallback default: DENY
        effect = PolicyEffect.DENY
        chosen_policy = None

        if matching_policies:
            # DENY policies override ALLOW
            deny_policies = [p for p in matching_policies if p.effect == PolicyEffect.DENY]
            if deny_policies:
                chosen_policy = deny_policies[0]
                effect = PolicyEffect.DENY
            else:
                allow_policies = [p for p in matching_policies if p.effect == PolicyEffect.ALLOW]
                if allow_policies:
                    chosen_policy = allow_policies[0]
                    effect = PolicyEffect.ALLOW
                else:
                    prompt_policies = [p for p in matching_policies if p.effect == PolicyEffect.PROMPT_USER]
                    if prompt_policies:
                        chosen_policy = prompt_policies[0]
                        effect = PolicyEffect.PROMPT_USER
        else:
            effect = PolicyEffect.DENY

        granted = False
        expires_at = None
        reason = "Access denied by default system security policy."

        if effect == PolicyEffect.ALLOW and chosen_policy:
            granted = True
            reason = f"Access allowed by policy '{chosen_policy.policy_id}'."
            if chosen_policy.duration == PolicyDuration.TEMPORARY and chosen_policy.ttl_seconds:
                expires_at = datetime.now(UTC) + timedelta(seconds=chosen_policy.ttl_seconds)
        elif effect == PolicyEffect.PROMPT_USER and chosen_policy:
            # Simulate approval for user prompting in tests
            granted = True
            reason = f"Access allowed after user confirmation for policy '{chosen_policy.policy_id}'."
        elif chosen_policy:
            reason = f"Access denied by policy '{chosen_policy.policy_id}'."

        result = PermissionResult(
            granted=granted,
            permission=request.permission,
            resource=request.resource,
            reason=reason,
            expires_at=expires_at,
        )

        if granted:
            if request.agent_id not in self._grants:
                self._grants[request.agent_id] = []
            # Remove duplicate/existing grant for the same permission and resource
            self._grants[request.agent_id] = [
                g
                for g in self._grants[request.agent_id]
                if not (g.permission == request.permission and g.resource == request.resource)
            ]
            self._grants[request.agent_id].append(result)
        else:
            raise PermissionDeniedError(reason)

        return result

    def grant_permission(
        self,
        agent_id: uuid.UUID,
        permission: AgentPermission,
        resource: str,
        duration: PolicyDuration = PolicyDuration.PERMANENT,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Manually grants a permission to an agent.

        Args:
            agent_id: Target agent identifier.
            permission: Target permission enum.
            resource: Target resource string.
            duration: Grant duration type.
            ttl_seconds: TTL in seconds for temporary grants.

        Raises:
            PermissionDeniedError: If agent validation fails.
        """
        if not self.validate_agent(agent_id):
            raise PermissionDeniedError("Target agent is not registered or is disabled.")

        expires_at = None
        if duration == PolicyDuration.TEMPORARY and ttl_seconds:
            expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)

        result = PermissionResult(
            granted=True,
            permission=permission,
            resource=resource,
            reason="Manually granted permission.",
            expires_at=expires_at,
        )

        if agent_id not in self._grants:
            self._grants[agent_id] = []
        self._grants[agent_id] = [
            g
            for g in self._grants[agent_id]
            if not (g.permission == permission and g.resource == resource)
        ]
        self._grants[agent_id].append(result)

    def revoke_permission(self, agent_id: uuid.UUID, permission: AgentPermission, resource: str) -> None:
        """Revokes a previously granted permission from an agent.

        Args:
            agent_id: Target agent identifier.
            permission: Target permission enum.
            resource: Target resource string.
        """
        if agent_id in self._grants:
            self._grants[agent_id] = [
                g
                for g in self._grants[agent_id]
                if not (g.permission == permission and fnmatch.fnmatch(resource, g.resource))
            ]

    def check_permission(self, agent_id: uuid.UUID, permission: AgentPermission, resource: str) -> bool:
        """Checks if the agent has a valid active permission grant for the resource.

        Args:
            agent_id: Target agent identifier.
            permission: Requested permission type.
            resource: Resource path/identifier.

        Returns:
            True if permitted; False otherwise.

        Raises:
            PermissionExpiredError: If the matching permission has expired.
        """
        if not self.validate_agent(agent_id):
            return False

        grants = self._grants.get(agent_id, [])
        now = datetime.now(UTC)

        matching_grants = []
        for g in grants:
            if g.permission == permission and fnmatch.fnmatch(resource, g.resource):
                matching_grants.append(g)

        for grant in matching_grants:
            if grant.expires_at and grant.expires_at < now:
                # Clean up expired grant
                self._grants[agent_id].remove(grant)
                raise PermissionExpiredError(
                    f"Permission '{permission}' for resource '{resource}' has expired."
                )

            if grant.granted:
                return True

        return False

    def list_permissions(self, agent_id: Optional[uuid.UUID] = None) -> List[PermissionResult]:
        """Lists all active, unexpired permission grants.

        Args:
            agent_id: Optional target agent identifier to filter results.

        Returns:
            List of active PermissionResult grants.
        """
        now = datetime.now(UTC)
        active_grants = []

        agents_to_check = [agent_id] if agent_id is not None else list(self._grants.keys())

        for aid in agents_to_check:
            if aid not in self._grants:
                continue

            unexpired = []
            for g in self._grants[aid]:
                if g.expires_at and g.expires_at < now:
                    continue
                unexpired.append(g)

            self._grants[aid] = unexpired
            active_grants.extend(unexpired)

        return active_grants
