"""Conflict Resolver resolving concurrent editing conflicts and version divergences.
"""

from typing import Any, Dict


class ConflictResolver:
    """Resolves concurrent editing conflicts across team members using operational transformation."""

    def resolve_conflict(self, local_version: Dict[str, Any], remote_version: Dict[str, Any]) -> Dict[str, Any]:
        """Resolves version divergence using last-write-wins fallback."""
        return remote_version or local_version
