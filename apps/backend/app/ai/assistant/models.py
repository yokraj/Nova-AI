"""Domain models and data schemas for Autonomous Personal Assistant & Life Management."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AssistantState(str, Enum):
    """State of personal assistant engine."""

    IDLE = "idle"
    BRIEFING = "briefing"
    PLANNING = "planning"
    PREPARING_MEETING = "preparing_meeting"
    EXECUTING_MISSION = "executing_mission"
    SUMMARIZING = "summarizing"


class Timeframe(str, Enum):
    """Planning horizon timeframe."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    LONG_TERM = "long_term"


class ReminderPriority(str, Enum):
    """Priority level for reminders and notifications."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Domain Models
# ---------------------------------------------------------------------------

class TaskItem(BaseModel):
    """Personal or work task item."""

    task_id: str = Field(default_factory=lambda: f"task_{uuid4().hex[:8]}")
    title: str
    description: str = ""
    category: str = "work"
    priority: int = 1
    due_date: Optional[str] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReminderItem(BaseModel):
    """Reminder item model."""

    reminder_id: str = Field(default_factory=lambda: f"rem_{uuid4().hex[:8]}")
    title: str
    due_time: str
    priority: ReminderPriority = ReminderPriority.MEDIUM
    triggered: bool = False
    acknowledged: bool = False


class MeetingRecord(BaseModel):
    """Calendar meeting item and preparation record."""

    meeting_id: str = Field(default_factory=lambda: f"mtg_{uuid4().hex[:8]}")
    title: str
    start_time: str
    end_time: str
    attendees: List[str] = Field(default_factory=list)
    agenda: str = ""
    documents: List[str] = Field(default_factory=list)
    prepared: bool = False


class ScheduleItem(BaseModel):
    """Time block allocation on daily schedule."""

    item_id: str = Field(default_factory=lambda: f"sched_{uuid4().hex[:8]}")
    title: str
    start_time: str
    end_time: str
    activity_type: str = "work"
    is_meeting: bool = False


class DailyPlan(BaseModel):
    """Daily schedule, focus tasks, and briefing summary."""

    plan_date: str
    morning_briefing: str
    schedule: List[ScheduleItem] = Field(default_factory=list)
    top_tasks: List[TaskItem] = Field(default_factory=list)
    reminders: List[ReminderItem] = Field(default_factory=list)
    evening_summary: Optional[str] = None


class GoalItem(BaseModel):
    """Personal or professional goal model."""

    goal_id: str = Field(default_factory=lambda: f"goal_{uuid4().hex[:8]}")
    title: str
    timeframe: Timeframe = Timeframe.MONTHLY
    progress_percentage: float = 0.0
    target_date: str = ""
    completed: bool = False


class HabitRecord(BaseModel):
    """Habit streak and tracking model."""

    habit_id: str = Field(default_factory=lambda: f"habit_{uuid4().hex[:8]}")
    name: str
    frequency: str = "daily"
    streak_count: int = 0
    last_completed: Optional[str] = None


class RoutineDefinition(BaseModel):
    """Morning or evening routine definition."""

    routine_id: str
    name: str
    time_of_day: str = "morning"
    actions: List[str] = Field(default_factory=list)


class ContactRecord(BaseModel):
    """Personal contact record."""

    contact_id: str = Field(default_factory=lambda: f"cnt_{uuid4().hex[:8]}")
    name: str
    email: str = ""
    phone: str = ""
    relationship: str = "colleague"


class ExpenseRecord(BaseModel):
    """Personal expense log."""

    expense_id: str = Field(default_factory=lambda: f"exp_{uuid4().hex[:8]}")
    category: str
    amount: float
    currency: str = "INR"
    description: str = ""
    date: str = ""


class HealthSnapshot(BaseModel):
    """Personal health and wellness metrics snapshot."""

    water_intake_ml: int = 0
    sleep_hours: float = 8.0
    steps_count: int = 0
    last_break_time: str = ""


class PersonalContext(BaseModel):
    """Real-time personal life context."""

    current_time: str
    current_date: str
    active_project: str = ""
    pending_tasks_count: int = 0
    upcoming_meetings_count: int = 0
    work_hours_active: bool = True


class AssistantMetrics(BaseModel):
    """Telemetry metrics snapshot for personal assistant engine."""

    total_plans_generated: int = 0
    reminders_created: int = 0
    tasks_managed: int = 0
    meetings_prepared: int = 0
    goals_tracked: int = 0
    habits_logged: int = 0
    proactive_suggestions_count: int = 0


class AssistantHealth(BaseModel):
    """Composite health report for personal assistant engine."""

    status: str = "healthy"
    components: Dict[str, str] = Field(default_factory=dict)
    active_reminders_count: int = 0
    pending_tasks_count: int = 0
