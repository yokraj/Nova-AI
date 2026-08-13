"""Assistant Engine central facade orchestrating life management, bridges, metrics, and voice commands."""

from typing import Any, Dict, List, Optional
import structlog

from app.ai.assistant.assistant_manager import AssistantManager
from app.ai.assistant.automation_bridge import AutomationBridge
from app.ai.assistant.cache import AssistantCache
from app.ai.assistant.configuration import AssistantConfiguration
from app.ai.assistant.health import AssistantHealthMonitor
from app.ai.assistant.interfaces import IPersonalAssistantPlatform
from app.ai.assistant.learning_bridge import LearningBridge
from app.ai.assistant.metrics import AssistantMetricsTracker
from app.ai.assistant.mission_bridge import MissionBridge
from app.ai.assistant.models import AssistantHealth, AssistantMetrics, DailyPlan, ReminderItem
from app.ai.assistant.plugin_bridge import PluginBridge

logger = structlog.get_logger("assistant_engine")


class AssistantEngine(IPersonalAssistantPlatform):
    """Central facade runtime orchestrating Nova's Autonomous Personal Assistant & Life Management Engine."""

    def __init__(self, config: Optional[AssistantConfiguration] = None) -> None:
        self.config = config or AssistantConfiguration()
        self.manager = AssistantManager()
        self.automation_bridge = AutomationBridge()
        self.mission_bridge = MissionBridge()
        self.plugin_bridge = PluginBridge()
        self.learning_bridge = LearningBridge()
        self.metrics = AssistantMetricsTracker()
        self.health_monitor = AssistantHealthMonitor()
        self.cache = AssistantCache()

    async def process_voice_query(self, query: str) -> Dict[str, Any]:
        """Process natural language voice query across life management sub-systems."""
        q_lower = query.lower()
        logger.info("Assistant Engine processing voice query", query=query)

        if "plan my day" in q_lower or "morning briefing" in q_lower:
            self.metrics.record_plan()
            plan: DailyPlan = await self.manager.planner.generate_morning_briefing()
            return {
                "intent": "plan_day",
                "briefing": plan.morning_briefing,
                "schedule_count": len(plan.schedule),
                "tasks_count": len(plan.top_tasks),
                "voice_response": plan.morning_briefing,
            }

        elif "remind me" in q_lower:
            self.metrics.record_reminder()
            rem: ReminderItem = await self.manager.reminders.create_reminder(
                title=query.replace("remind me to ", "").replace("remind me ", ""),
                due_time="18:00",
            )
            resp = f"I have set a reminder to '{rem.title}' for {rem.due_time}."
            return {"intent": "create_reminder", "reminder_id": rem.reminder_id, "voice_response": resp}

        elif "prepare" in q_lower and "meeting" in q_lower:
            self.metrics.record_meeting_prep()
            mission_res = await self.mission_bridge.create_meeting_prep_mission("Sprint Planning Meeting")
            resp = "I am preparing your meeting: gathering documents, summarizing emails, and opening presentation slides."
            return {"intent": "prepare_meeting", "mission": mission_res, "voice_response": resp}

        elif "summarize" in q_lower and "today" in q_lower:
            recap = await self.manager.planner.generate_evening_summary()
            return {"intent": "daily_summary", "recap": recap, "voice_response": recap}

        elif "work on first" in q_lower or "recommend" in q_lower:
            recs = await self.manager.recommendations.get_proactive_recommendations()
            resp = f"Here is what you should work on first: {recs[0]}"
            return {"intent": "recommend_tasks", "recommendations": recs, "voice_response": resp}

        else:
            resp = f"I am managing your schedule. I have recorded your query: '{query}'."
            return {"intent": "general_assistant", "query": query, "voice_response": resp}

    async def get_metrics(self) -> AssistantMetrics:
        """Retrieve telemetry metrics."""
        return self.metrics.get_metrics()

    def check_health(self) -> AssistantHealth:
        """Retrieve composite health status."""
        return self.health_monitor.check_health()
