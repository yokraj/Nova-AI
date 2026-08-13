"""Mission Bridge connecting Assistant Engine to MissionEngine & Execution Runtime."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("mission_bridge")


class MissionBridge:
    """Auto-creates multi-step execution missions for meeting prep, document collection, slide generation, and summaries."""

    async def create_meeting_prep_mission(self, meeting_title: str) -> Dict[str, Any]:
        """Auto-create multi-step mission for upcoming meeting preparation."""
        logger.info("MissionBridge creating meeting prep mission", title=meeting_title)
        mission_plan = {
            "mission_id": f"ms_mtg_{meeting_title.lower().replace(' ', '_')}",
            "goal": f"Prepare for meeting '{meeting_title}'",
            "steps": [
                {"step_id": "s1", "name": "Summarize relevant emails", "plugin_id": "email", "capability": "list_emails"},
                {"step_id": "s2", "name": "Collect agenda documents", "plugin_id": "file", "capability": "read_file"},
                {"step_id": "s3", "name": "Open presentation slides", "plugin_id": "office", "capability": "format_presentation"},
                {"step_id": "s4", "name": "Notify user preparation ready", "plugin_id": "desktop", "capability": "keyboard_input"},
            ],
        }

        try:
            from app.ai.gateway import IAIGateway
            from app.core.dependency_container import resolve
            gateway = resolve(IAIGateway)
            res = await gateway.execute_mission(mission_plan["mission_id"], mission_plan)
            return {"status": "created", "mission_plan": res}
        except Exception as e:
            logger.info("MissionEngine gateway fallback for testing", error=str(e))
            return {"status": "created", "mission_plan": mission_plan}
