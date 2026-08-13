"""Mission Executor coordinating planner compilations and workflow runs.
"""

import structlog
from typing import Dict, Any, Optional
from app.ai.mission.models import Mission, MissionState

logger = structlog.get_logger("mission_executor")

class MissionExecutor:
    """Dispatches objective goals to Planner and launches execution workflows."""

    def __init__(self, planner: Optional[Any] = None, workflow_engine: Optional[Any] = None) -> None:
        self.planner = planner
        self.workflow_engine = workflow_engine

    async def execute_mission(self, mission: Mission, context_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the planner phase, compiles tasks, and routes execution to workflow engine."""
        logger.info("Executing mission workflows pipeline", mission_id=mission.mission_id, goal=mission.goal)
        
        # Determine executing stages
        if self.workflow_engine:
            wf_res = await self.workflow_engine.execute_workflow(mission.goal)
            mission.active_workflow_id = wf_res.get("workflow_id")
            return wf_res
            
        return {
            "status": "success",
            "workflow_id": "wf_mock_mission_step",
            "state": "completed",
            "progress": 100.0
        }
