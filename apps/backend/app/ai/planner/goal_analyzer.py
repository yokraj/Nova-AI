"""Intelligent goal analyzer parsing targets scope parameters and requirements.
"""

import structlog
from typing import Dict, Any
from app.ai.planner.models import Goal

logger = structlog.get_logger("goal_analyzer")

class GoalAnalyzer:
    """Classifies goal text descriptions to determine capability requirements."""

    async def analyze_goal(self, goal: Goal) -> Dict[str, Any]:
        """Classifies goal description domain and maps requirement levels."""
        desc = goal.description.lower()
        domain = "generic"
        complexity = 0.5
        capabilities = ["planning"]
        deliverables = ["execution_report"]
        risks = []

        if "erp" in desc or "crm" in desc:
            domain = "enterprise_software"
            complexity = 0.8
            capabilities.extend(["code_generation", "database_design", "authentication", "api_development"])
            deliverables.extend(["database_schema", "backend_apis", "frontend_ui"])
            risks.append("high_integration_complexity")
        elif "app" in desc or "website" in desc or "system" in desc or "build" in desc:
            domain = "software_engineering"
            complexity = 0.6
            capabilities.extend(["code_generation", "debugging", "documentation"])
            deliverables.extend(["source_code", "unit_tests", "docs"])
            risks.append("unclear_requirements")
        elif "research" in desc or "literature" in desc or "find" in desc:
            domain = "scientific_research"
            complexity = 0.4
            capabilities.extend(["literature_search", "document_analysis"])
            deliverables.extend(["research_summary", "bibliography"])
            risks.append("information_overload")

        logger.info(
            "Analyzed goal description parameters",
            domain=domain,
            complexity=complexity,
            capabilities_count=len(capabilities)
        )

        return {
            "domain": domain,
            "complexity": complexity,
            "required_capabilities": capabilities,
            "deliverables": deliverables,
            "risks": risks,
            "constraints": ["offline_first", "zero_external_api_costs"]
        }
