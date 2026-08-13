"""Voice-Driven Agent Workforce Orchestrator mapping voice requests to multi-divisional execution DAGs.
"""

from typing import Any, Dict
from app.ai.agents.delegation_engine import TaskDelegationEngine
from app.ai.agents.peer_review_engine import PeerReviewEngine


class VoiceAgentOrchestrator:
    """Orchestrates complex voice requests ("Nova, build an ERP system") across the 9 Divisions."""

    def __init__(self, delegation_engine: TaskDelegationEngine, peer_review_engine: PeerReviewEngine) -> None:
        self.delegation_engine = delegation_engine
        self.peer_review_engine = peer_review_engine

    async def process_voice_mission(self, voice_prompt: str) -> Dict[str, Any]:
        """Decomposes voice prompt into multi-divisional task DAG, executes, and passes through peer review."""
        dag = await self.delegation_engine.decompose_goal(voice_prompt)
        exec_res = await self.delegation_engine.execute_mission_dag(dag)

        from app.ai.agents.models import PeerReviewRequest
        rev_req = PeerReviewRequest(
            task_id=dag.task_nodes[-1].task_id,
            author_agent_id="BackendEngineerAgent",
            content_to_review=exec_res,
        )
        rev_res = await self.peer_review_engine.evaluate_deliverable(rev_req)

        return {
            "voice_prompt": voice_prompt,
            "mission_id": dag.mission_id,
            "status": "DELIVERED",
            "task_dag_nodes_count": len(dag.task_nodes),
            "peer_review_approved": rev_res.approved,
            "quality_score": rev_res.overall_quality_score,
            "reviewer_signoffs": list(rev_res.reviewer_comments.keys()),
        }
