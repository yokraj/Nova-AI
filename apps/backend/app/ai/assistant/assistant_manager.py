"""Assistant Manager unifying life planning, scheduling, tasks, meetings, health, and memory."""

from typing import Any, Dict, List, Optional
import structlog

from app.ai.assistant.calendar_manager import CalendarManager
from app.ai.assistant.contact_manager import ContactManager
from app.ai.assistant.context_manager import ContextManager
from app.ai.assistant.daily_planner import DailyPlanner
from app.ai.assistant.expense_tracker import ExpenseTracker
from app.ai.assistant.fitness_manager import FitnessManager
from app.ai.assistant.goal_manager import GoalManager
from app.ai.assistant.habit_tracker import HabitTracker
from app.ai.assistant.health_manager import HealthManager
from app.ai.assistant.knowledge_manager import KnowledgeManager
from app.ai.assistant.meeting_manager import MeetingManager
from app.ai.assistant.notification_manager import NotificationManager
from app.ai.assistant.nutrition_manager import NutritionManager
from app.ai.assistant.personal_memory import PersonalMemory
from app.ai.assistant.preference_manager import PreferenceManager
from app.ai.assistant.priority_manager import PriorityManager
from app.ai.assistant.recommendation_engine import RecommendationEngine
from app.ai.assistant.relationship_manager import RelationshipManager
from app.ai.assistant.reminder_manager import ReminderManager
from app.ai.assistant.routine_manager import RoutineManager
from app.ai.assistant.schedule_manager import ScheduleManager
from app.ai.assistant.shopping_manager import ShoppingManager
from app.ai.assistant.sleep_manager import SleepManager
from app.ai.assistant.task_manager import TaskManager
from app.ai.assistant.travel_manager import TravelManager

logger = structlog.get_logger("assistant_manager")


class AssistantManager:
    """High-level Life Management Orchestrator unifying planner, schedule, tasks, meetings, health, memory, and habits."""

    def __init__(self) -> None:
        self.planner = DailyPlanner()
        self.schedule = ScheduleManager()
        self.calendar = CalendarManager()
        self.meetings = MeetingManager()
        self.reminders = ReminderManager()
        self.tasks = TaskManager()
        self.goals = GoalManager()
        self.habits = HabitTracker()
        self.routines = RoutineManager()
        self.priorities = PriorityManager()
        self.notifications = NotificationManager()
        self.context = ContextManager()
        self.memory = PersonalMemory()
        self.preferences = PreferenceManager()
        self.relationships = RelationshipManager()
        self.contacts = ContactManager()
        self.travel = TravelManager()
        self.expenses = ExpenseTracker()
        self.shopping = ShoppingManager()
        self.health = HealthManager()
        self.fitness = FitnessManager()
        self.nutrition = NutritionManager()
        self.sleep = SleepManager()
        self.knowledge = KnowledgeManager()
        self.recommendations = RecommendationEngine()

    async def plan_day(self) -> Dict[str, Any]:
        """Generate day plan and morning briefing."""
        plan = await self.planner.generate_morning_briefing()
        return plan.model_dump(mode="json") if hasattr(plan, "model_dump") else plan
