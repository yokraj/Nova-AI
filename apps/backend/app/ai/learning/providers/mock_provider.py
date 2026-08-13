"""Mock Learning Provider — deterministic offline simulations for testing and development."""

from datetime import datetime
from typing import Any, Dict, List


class MockLearningProvider:
    """Provides deterministic, offline simulations of all Learning Engine operations.

    No cloud services, no paid APIs.  All results are pre-computed and stable
    across runs so that tests remain deterministic and reproducible.
    """

    # ------------------------------------------------------------------
    # Experience simulations
    # ------------------------------------------------------------------

    def simulate_experience(
        self,
        goal: str = "Build React dashboard",
        success: bool = True,
    ) -> Dict[str, Any]:
        """Return a pre-built experience result dict."""
        return {
            "mission_id": "mock_ms_001",
            "goal": goal,
            "status": "success" if success else "failed",
            "duration_seconds": 42.0,
            "agents_used": ["backend", "frontend", "qa"],
            "workflow_id": "wf_mock_001",
            "recovery_count": 0,
            "approval_count": 0,
            "user_satisfaction": 0.95,
            "metadata": {"environment": "mock"},
        }

    def simulate_failed_experience(self, goal: str = "Deploy microservice") -> Dict[str, Any]:
        """Return a pre-built failure result dict."""
        return {
            "mission_id": "mock_ms_002",
            "goal": goal,
            "status": "failed",
            "duration_seconds": 15.0,
            "agents_used": ["devops"],
            "workflow_id": None,
            "recovery_count": 1,
            "approval_count": 2,
            "user_satisfaction": 0.4,
            "metadata": {"environment": "mock"},
        }

    # ------------------------------------------------------------------
    # Pattern simulations
    # ------------------------------------------------------------------

    def simulate_patterns(self) -> List[Dict[str, Any]]:
        """Return a deterministic list of detected pattern dicts."""
        return [
            {
                "pattern_id": "ptn_mock_001",
                "name": "Successful React Workflow",
                "description": "Recurring successful pattern for React dashboard goals.",
                "occurrences": 5,
                "success_rate": 0.90,
                "agent_ids": ["frontend", "backend"],
                "domain_keywords": ["react", "dashboard"],
            },
            {
                "pattern_id": "ptn_mock_002",
                "name": "Efficient Backend+QA Combo",
                "description": "backend+qa agent combination shows 95% success.",
                "occurrences": 3,
                "success_rate": 0.95,
                "agent_ids": ["backend", "qa"],
                "domain_keywords": ["backend", "qa"],
            },
        ]

    # ------------------------------------------------------------------
    # Strategy simulations
    # ------------------------------------------------------------------

    def simulate_strategy(self, domain: str = "coding") -> Dict[str, Any]:
        """Return a pre-built strategy dict for the given domain."""
        strategy_map = {
            "coding": {
                "strategy_id": "str_mock_coding",
                "name": "Incremental Coding Strategy",
                "domain": "coding",
                "version": 1,
                "success_rate": 0.88,
                "steps": [
                    "Scaffold project",
                    "Implement core logic",
                    "Write tests",
                    "Document",
                ],
            },
            "debugging": {
                "strategy_id": "str_mock_debug",
                "name": "Root Cause Debugging Strategy",
                "domain": "debugging",
                "version": 1,
                "success_rate": 0.82,
                "steps": [
                    "Reproduce issue",
                    "Isolate scope",
                    "Identify root cause",
                    "Apply fix",
                ],
            },
        }
        return strategy_map.get(
            domain,
            {
                "strategy_id": "str_mock_generic",
                "name": "Generic Strategy",
                "domain": domain,
                "version": 1,
                "success_rate": 0.75,
                "steps": ["Analyse", "Plan", "Execute", "Review"],
            },
        )

    # ------------------------------------------------------------------
    # Lesson simulations
    # ------------------------------------------------------------------

    def simulate_lessons(self) -> List[str]:
        """Return pre-built lesson strings."""
        return [
            "✓ Reusable layout components improved speed.",
            "✓ Parallel frontend/backend agents reduced completion time.",
            "✓ Authentication should be implemented before dashboard pages.",
            "⚡ Consider parallelising independent subtasks.",
        ]

    # ------------------------------------------------------------------
    # Recommendation simulations
    # ------------------------------------------------------------------

    def simulate_recommendation(self, goal: str = "") -> Dict[str, Any]:
        """Return a deterministic recommendation dict."""
        return {
            "recommendation_id": "rec_mock_001",
            "target": "planner",
            "content": (
                "Use 'Incremental Coding Strategy' — "
                "success rate 88%. Steps: Scaffold → Implement → Test → Document."
            ),
            "strategy_id": "str_mock_coding",
            "confidence": 0.88,
            "goal_context": goal,
            "created_at": datetime.utcnow().isoformat(),
        }

    # ------------------------------------------------------------------
    # Metrics simulation
    # ------------------------------------------------------------------

    def simulate_metrics(self) -> Dict[str, Any]:
        """Return a complete learning metrics snapshot."""
        return {
            "total_experiences": 10,
            "success_rate": 0.80,
            "failure_rate": 0.20,
            "learned_strategies": 6,
            "pattern_matches": 3,
            "recommendations_generated": 8,
            "knowledge_reuse_pct": 0.50,
            "agent_learning_score": 0.75,
        }

    # ------------------------------------------------------------------
    # Health simulation
    # ------------------------------------------------------------------

    def simulate_health(self) -> Dict[str, Any]:
        """Return a healthy status for all sub-systems."""
        return {
            "status": "healthy",
            "components": {
                "experience_store": "online",
                "pattern_detector": "online",
                "strategy_repository": "online",
                "recommendation_engine": "online",
            },
            "total_experiences": 10,
            "total_strategies": 6,
            "pattern_matches": 3,
        }
