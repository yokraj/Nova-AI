"""Mock provider simulating deterministic collaboration cycles offline.
"""

from typing import Dict, Any, List

class MockCollaborationProvider:
    """Generates structured offline simulation sequences for local testing validations."""

    def simulate_negotiation(self) -> Dict[str, Any]:
        """Simulates bidding rounds outcome where Backend Agent wins ownership."""
        return {
            "task_id": "task_auth_endpoint",
            "bidders": ["backend", "software_engineer"],
            "winning_agent": "backend",
            "winning_bid": 0.93
        }

    def simulate_handoff(self) -> Dict[str, Any]:
        """Simulates task transfer redirection from backend agent to database specialist agent."""
        return {
            "task_id": "db_optimization",
            "from_agent": "backend",
            "to_agent": "database",
            "handoff_context": {
                "source_query": "SELECT * FROM users",
                "optimization_suggested": "Add index to email column"
            },
            "status": "completed"
        }

    def simulate_consensus(self, mode: str) -> Dict[str, Any]:
        """Simulates consensus agreement voting rounds."""
        return {
            "proposal": "Use Outfit font family guidelines and glassmorphism styling parameters",
            "voting_mode": mode,
            "votes": {
                "uiux": True,
                "frontend": True,
                "architect": True
            },
            "consensus_achieved": True
        }
