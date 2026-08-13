"""Agent Selector assigning tasks to appropriate capability registrants.
"""

import structlog
from app.ai.planner.models import Task, AgentAssignment
from app.ai.planner.capability_matcher import CapabilityMatcher

logger = structlog.get_logger("agent_selector")

class AgentSelector:
    """Evaluates registry listings score, defaulting to Software Engineer Agent."""

    def __init__(self, matcher: CapabilityMatcher) -> None:
        self.matcher = matcher

    def select_agent(self, task: Task) -> AgentAssignment:
        """Assigns optimal agent, matching capability scores."""
        matches = self.matcher.find_matches(task)

        if matches:
            best_match = max(matches, key=lambda item: item["capability_score"])
            return AgentAssignment(
                agent_id=best_match["agent_id"],
                agent_name=best_match["agent_name"],
                capability_score=best_match["capability_score"],
                confidence=0.9,
                fallback_agent_ids=["software_engineer"]
            )

        # Default fallback to Software Engineer Agent
        logger.debug("Defaulting task to Software Engineer Agent fallback", task_id=task.task_id)
        return AgentAssignment(
            agent_id="software_engineer",
            agent_name="Software Engineer Agent",
            capability_score=0.75,
            confidence=0.8,
            fallback_agent_ids=["manual_assignment"]
        )
