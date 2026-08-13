"""Risk Analyzer flags potential project blockers and defines mitigation plans.
"""

from typing import List
from app.agents.software_engineer.project_manager.interfaces import IRiskAnalyzer
from app.agents.software_engineer.project_manager.models import Project, Risk

class LocalRiskAnalyzer(IRiskAnalyzer):
    """Analyzes requirements and dependencies to identify and score projects risks."""

    def analyze_risks(self, project: Project) -> List[Risk]:
        """Examines the project requirements and lists potential failure areas."""
        risks = []
        req = project.requirements
        
        # 1. Check technology requirements risks
        for tech in req.technology_requirements:
            if tech.lower() in ["python", "go", "rust", "node.js", "java"]:
                risks.append(Risk(
                    id=f"risk-tech-{tech.lower()}",
                    description=f"Skill gap or local execution constraints with {tech}.",
                    level="Low",
                    impact="Medium",
                    probability="Low",
                    mitigation_strategy=f"Pre-install base images and dependencies for {tech}."
                ))

        # 2. Check service dependencies risks (like postgres/redis)
        for dep in req.dependencies:
            risks.append(Risk(
                id="risk-dependency-external",
                description=f"Availability of external dependency: {dep}.",
                level="Medium",
                impact="High",
                probability="Medium",
                mitigation_strategy="Implement offline mock interfaces for local testing."
            ))

        # 3. Default security or performance risk
        risks.append(Risk(
            id="risk-security-nonroot",
            description="Container isolation security compliance constraints.",
            level="High",
            impact="High",
            probability="Low",
            mitigation_strategy="Enforce non-root Docker configurations during build preparation stages."
        ))

        return risks
