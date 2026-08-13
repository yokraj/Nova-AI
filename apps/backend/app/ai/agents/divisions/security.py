"""Security Division for Nova Autonomous AI Company.
"""

from typing import List
from app.ai.agents.models import AgentBlueprint, AgentDivision


class SecurityDivision:
    """Security Division enforcing permission validation, credential security, threat analysis, and privacy policies."""

    @staticmethod
    def get_agents() -> List[AgentBlueprint]:
        return [
            AgentBlueprint(agent_id="security_audit_agent", name="Security Audit Agent", division=AgentDivision.SECURITY, role_description="Security vulnerability auditing & signoff"),
            AgentBlueprint(agent_id="permission_agent", name="Permission Agent", division=AgentDivision.SECURITY, role_description="Role-based access control & permission mapping"),
            AgentBlueprint(agent_id="privacy_agent", name="Privacy Agent", division=AgentDivision.SECURITY, role_description="Local-first data privacy & telemetry masking"),
            AgentBlueprint(agent_id="credential_agent", name="Credential Agent", division=AgentDivision.SECURITY, role_description="Secure credential storage & key vault manager"),
            AgentBlueprint(agent_id="threat_analysis_agent", name="Threat Analysis Agent", division=AgentDivision.SECURITY, role_description="Real-time threat detection & malicious payload filtering"),
        ]
