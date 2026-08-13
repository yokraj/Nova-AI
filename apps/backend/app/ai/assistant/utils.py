"""PEP 562 Lazy Import Utility Mapping for the Assistant package."""

import importlib
from typing import Any

_LAZY_MAP: dict = {
    # Core Config & Models
    "AssistantConfiguration": "app.ai.assistant.configuration",
    "AssistantState": "app.ai.assistant.models",
    "Timeframe": "app.ai.assistant.models",
    "ReminderPriority": "app.ai.assistant.models",
    "TaskItem": "app.ai.assistant.models",
    "ReminderItem": "app.ai.assistant.models",
    "MeetingRecord": "app.ai.assistant.models",
    "ScheduleItem": "app.ai.assistant.models",
    "DailyPlan": "app.ai.assistant.models",
    "GoalItem": "app.ai.assistant.models",
    "HabitRecord": "app.ai.assistant.models",
    "RoutineDefinition": "app.ai.assistant.models",
    "ContactRecord": "app.ai.assistant.models",
    "ExpenseRecord": "app.ai.assistant.models",
    "HealthSnapshot": "app.ai.assistant.models",
    "PersonalContext": "app.ai.assistant.models",
    "AssistantMetrics": "app.ai.assistant.models",
    "AssistantHealth": "app.ai.assistant.models",
    # Interfaces
    "IDailyPlanner": "app.ai.assistant.interfaces",
    "IScheduleManager": "app.ai.assistant.interfaces",
    "IReminderManager": "app.ai.assistant.interfaces",
    "ITaskManager": "app.ai.assistant.interfaces",
    "IGoalManager": "app.ai.assistant.interfaces",
    "IRecommendationEngine": "app.ai.assistant.interfaces",
    "IPersonalAssistantPlatform": "app.ai.assistant.interfaces",
    # Exceptions
    "AssistantEngineError": "app.ai.assistant.exceptions",
    "ScheduleConflictError": "app.ai.assistant.exceptions",
    "ReminderError": "app.ai.assistant.exceptions",
    "TaskNotFoundError": "app.ai.assistant.exceptions",
    "GoalTrackingError": "app.ai.assistant.exceptions",
    "ContextResolutionError": "app.ai.assistant.exceptions",
    # Managers & Engines
    "DailyPlanner": "app.ai.assistant.daily_planner",
    "ScheduleManager": "app.ai.assistant.schedule_manager",
    "CalendarManager": "app.ai.assistant.calendar_manager",
    "MeetingManager": "app.ai.assistant.meeting_manager",
    "ReminderManager": "app.ai.assistant.reminder_manager",
    "TaskManager": "app.ai.assistant.task_manager",
    "GoalManager": "app.ai.assistant.goal_manager",
    "HabitTracker": "app.ai.assistant.habit_tracker",
    "RoutineManager": "app.ai.assistant.routine_manager",
    "PriorityManager": "app.ai.assistant.priority_manager",
    "NotificationManager": "app.ai.assistant.notification_manager",
    "ContextManager": "app.ai.assistant.context_manager",
    "PersonalMemory": "app.ai.assistant.personal_memory",
    "PreferenceManager": "app.ai.assistant.preference_manager",
    "RelationshipManager": "app.ai.assistant.relationship_manager",
    "ContactManager": "app.ai.assistant.contact_manager",
    "TravelManager": "app.ai.assistant.travel_manager",
    "ExpenseTracker": "app.ai.assistant.expense_tracker",
    "ShoppingManager": "app.ai.assistant.shopping_manager",
    "HealthManager": "app.ai.assistant.health_manager",
    "FitnessManager": "app.ai.assistant.fitness_manager",
    "NutritionManager": "app.ai.assistant.nutrition_manager",
    "SleepManager": "app.ai.assistant.sleep_manager",
    "KnowledgeManager": "app.ai.assistant.knowledge_manager",
    "RecommendationEngine": "app.ai.assistant.recommendation_engine",
    "AssistantManager": "app.ai.assistant.assistant_manager",
    "AssistantEngine": "app.ai.assistant.assistant_engine",
    # Bridges, Telemetry & Providers
    "AutomationBridge": "app.ai.assistant.automation_bridge",
    "MissionBridge": "app.ai.assistant.mission_bridge",
    "PluginBridge": "app.ai.assistant.plugin_bridge",
    "LearningBridge": "app.ai.assistant.learning_bridge",
    "AssistantMetricsTracker": "app.ai.assistant.metrics",
    "AssistantHealthMonitor": "app.ai.assistant.health",
    "AssistantCache": "app.ai.assistant.cache",
    "MockAssistantProvider": "app.ai.assistant.mock_provider",
}


def lazy_import(name: str) -> Any:
    """Dynamically imports a mapped class or utility by name."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"Attribute '{name}' not found in assistant lazy mapping.")
