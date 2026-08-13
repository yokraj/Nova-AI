"""Engineering Division for Nova Autonomous AI Company.
"""

from typing import List
from app.ai.agents.models import AgentBlueprint, AgentDivision


class EngineeringDivision:
    """Engineering Division delivering architecture, backend, frontend, database, cloud, and DevOps solutions."""

    @staticmethod
    def get_agents() -> List[AgentBlueprint]:
        return [
            AgentBlueprint(agent_id="software_architect_agent", name="Software Architect Agent", division=AgentDivision.ENGINEERING, role_description="System architecture & design blueprints"),
            AgentBlueprint(agent_id="backend_engineer_agent", name="Backend Engineer Agent", division=AgentDivision.ENGINEERING, role_description="FastAPI & microservices backend development"),
            AgentBlueprint(agent_id="frontend_engineer_agent", name="Frontend Engineer Agent", division=AgentDivision.ENGINEERING, role_description="React & Next.js web application frontend"),
            AgentBlueprint(agent_id="fullstack_engineer_agent", name="FullStack Engineer Agent", division=AgentDivision.ENGINEERING, role_description="End-to-end full-stack feature engineering"),
            AgentBlueprint(agent_id="database_engineer_agent", name="Database Engineer Agent", division=AgentDivision.ENGINEERING, role_description="PostgreSQL, Alembic & Vector DB schemas"),
            AgentBlueprint(agent_id="api_engineer_agent", name="API Engineer Agent", division=AgentDivision.ENGINEERING, role_description="REST, GraphQL & WebSocket API engineering"),
            AgentBlueprint(agent_id="desktop_engineer_agent", name="Desktop Engineer Agent", division=AgentDivision.ENGINEERING, role_description="Windows native desktop automation & C++/Rust bindings"),
            AgentBlueprint(agent_id="mobile_engineer_agent", name="Mobile Engineer Agent", division=AgentDivision.ENGINEERING, role_description="Cross-platform Flutter & Android SDK modules"),
            AgentBlueprint(agent_id="cloud_engineer_agent", name="Cloud Engineer Agent", division=AgentDivision.ENGINEERING, role_description="Cloud architecture & serverless infrastructure"),
            AgentBlueprint(agent_id="devops_engineer_agent", name="DevOps Engineer Agent", division=AgentDivision.ENGINEERING, role_description="CI/CD pipelines, Docker & Kubernetes packaging"),
            AgentBlueprint(agent_id="testing_engineer_agent", name="Testing Engineer Agent", division=AgentDivision.ENGINEERING, role_description="Automated unit, integration, and e2e test suites"),
            AgentBlueprint(agent_id="performance_engineer_agent", name="Performance Engineer Agent", division=AgentDivision.ENGINEERING, role_description="Latency optimization & memory leak profiling"),
            AgentBlueprint(agent_id="security_engineer_agent", name="Security Engineer Agent", division=AgentDivision.ENGINEERING, role_description="Secure coding standards & vulnerability patching"),
            AgentBlueprint(agent_id="documentation_engineer_agent", name="Documentation Engineer Agent", division=AgentDivision.ENGINEERING, role_description="Technical specs & API documentation"),
            AgentBlueprint(agent_id="release_manager_agent", name="Release Manager Agent", division=AgentDivision.ENGINEERING, role_description="Version tagging & production deployment approval"),
        ]
