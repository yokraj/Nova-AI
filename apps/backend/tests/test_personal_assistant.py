"""Unit tests for Autonomous Personal Assistant & Life Management Engine."""

import pytest
from app.ai.assistant.assistant_engine import AssistantEngine
from app.ai.assistant.assistant_manager import AssistantManager
from app.ai.assistant.configuration import AssistantConfiguration
from app.ai.assistant.daily_planner import DailyPlanner
from app.ai.assistant.expense_tracker import ExpenseTracker
from app.ai.assistant.goal_manager import GoalManager
from app.ai.assistant.habit_tracker import HabitTracker
from app.ai.assistant.health_manager import HealthManager
from app.ai.assistant.meeting_manager import MeetingManager
from app.ai.assistant.personal_memory import PersonalMemory
from app.ai.assistant.recommendation_engine import RecommendationEngine
from app.ai.assistant.reminder_manager import ReminderManager
from app.ai.assistant.schedule_manager import ScheduleManager
from app.ai.assistant.task_manager import TaskManager
from app.ai.gateway import IAIGateway
from app.core.dependency_container import register_ai_gateway_dependencies, resolve


@pytest.mark.anyio
async def test_assistant_configuration():
    """Verifies default assistant configuration settings."""
    config = AssistantConfiguration()
    assert config.enabled is True
    assert config.proactive_notifications is True
    assert config.morning_briefing_time == "08:00"


@pytest.mark.anyio
async def test_daily_planner_and_briefing():
    """Verifies daily plan generation, morning briefing, and evening summary."""
    planner = DailyPlanner()
    plan = await planner.generate_morning_briefing()
    assert len(plan.schedule) >= 4
    assert len(plan.top_tasks) >= 3
    assert "Good morning!" in plan.morning_briefing

    summary = await planner.generate_evening_summary()
    assert "Evening Recap" in summary


@pytest.mark.anyio
async def test_schedule_and_calendar():
    """Verifies schedule time-blocking and calendar manager."""
    mgr = ScheduleManager()
    items = await mgr.list_schedule()
    assert len(items) >= 2


@pytest.mark.anyio
async def test_meeting_preparation():
    """Verifies meeting preparation and document collection."""
    mm = MeetingManager()
    meetings = await mm.list_meetings()
    assert len(meetings) >= 1

    prep = await mm.prepare_meeting(meetings[0].meeting_id)
    assert prep.prepared is True


@pytest.mark.anyio
async def test_reminders_tasks_and_goals():
    """Verifies reminders, tasks, and goal tracking."""
    rm = ReminderManager()
    rem = await rm.create_reminder("Pay electricity bill", "18:00")
    assert rem.title == "Pay electricity bill"

    tm = TaskManager()
    task = await tm.add_task("Review PRs", "work", 1)
    assert task.title == "Review PRs"

    gm = GoalManager()
    goal = await gm.add_goal("Learn Rust", "monthly")
    updated = await gm.update_goal_progress(goal.goal_id, 100.0)
    assert updated.completed is True


@pytest.mark.anyio
async def test_habits_and_health():
    """Verifies habit streak logging and health management."""
    ht = HabitTracker()
    habit = await ht.log_habit("Gym Workout")
    assert habit.streak_count >= 1

    hm = HealthManager()
    snap = await hm.get_health_snapshot()
    assert snap.water_intake_ml >= 1000


@pytest.mark.anyio
async def test_personal_memory_and_recommendations():
    """Verifies personal memory facts and recommendation engine."""
    mem = PersonalMemory()
    await mem.remember_fact("favorite_color", "blue")
    val = await mem.get_fact("favorite_color")
    assert val == "blue"

    recommender = RecommendationEngine()
    recs = await recommender.get_proactive_recommendations()
    assert len(recs) >= 4


@pytest.mark.anyio
async def test_assistant_engine_voice_queries():
    """Verifies voice query processing across intents."""
    engine = AssistantEngine()

    res_plan = await engine.process_voice_query("Hey Nova, plan my day.")
    assert res_plan["intent"] == "plan_day"

    res_rem = await engine.process_voice_query("Hey Nova, remind me to pay electricity tomorrow.")
    assert res_rem["intent"] == "create_reminder"

    res_mtg = await engine.process_voice_query("Hey Nova, prepare today's meetings.")
    assert res_mtg["intent"] == "prepare_meeting"

    res_rec = await engine.process_voice_query("Hey Nova, what should I work on first?")
    assert res_rec["intent"] == "recommend_tasks"


@pytest.mark.anyio
async def test_gateway_assistant_apis():
    """Verifies AI Gateway assistant methods."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    plan_res = await gateway.plan_day()
    assert plan_res["intent"] == "plan_day"

    summary_res = await gateway.daily_summary()
    assert summary_res["intent"] == "daily_summary"
