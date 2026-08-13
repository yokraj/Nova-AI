"""12-Stage Manual Validation Script for M3.3.13 Autonomous Personal Assistant & Life Management Engine."""

import asyncio
import sys
import structlog

from app.ai.assistant.assistant_engine import AssistantEngine
from app.ai.assistant.assistant_manager import AssistantManager
from app.ai.assistant.configuration import AssistantConfiguration
from app.ai.assistant.daily_planner import DailyPlanner
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

logger = structlog.get_logger("test_personal_assistant_manual")


async def run_manual_validation() -> None:
    print("=========================================")
    print("Nova AI Personal Assistant Engine Validation")
    print("=========================================")

    # Stage 1: Configuration
    config = AssistantConfiguration()
    assert config.enabled is True
    print("Stage 1  Assistant Configuration    PASS")

    # Stage 2: Daily Planner & Morning Briefing
    planner = DailyPlanner()
    plan = await planner.generate_morning_briefing()
    assert len(plan.schedule) >= 4
    print("Stage 2  Daily Planner & Briefing   PASS")

    # Stage 3: Schedule & Calendar
    sched = ScheduleManager()
    items = await sched.list_schedule()
    assert len(items) >= 2
    print("Stage 3  Schedule & Calendar Timeblock PASS")

    # Stage 4: Meeting Preparation
    mm = MeetingManager()
    meetings = await mm.list_meetings()
    prepared = await mm.prepare_meeting(meetings[0].meeting_id)
    assert prepared.prepared is True
    print("Stage 4  Meeting Preparation        PASS")

    # Stage 5: Reminders & Tasks
    rm = ReminderManager()
    rem = await rm.create_reminder("Pay bill", "18:00")
    tm = TaskManager()
    task = await tm.add_task("Review PRs", "work", 1)
    assert rem.title == "Pay bill"
    assert task.title == "Review PRs"
    print("Stage 5  Reminders & Task Management PASS")

    # Stage 6: Goals & Habit Tracking
    gm = GoalManager()
    goal = await gm.add_goal("Release Nova OS")
    ht = HabitTracker()
    habit = await ht.log_habit("Gym Workout")
    assert goal.title == "Release Nova OS"
    assert habit.streak_count >= 1
    print("Stage 6  Goals & Habit Tracking     PASS")

    # Stage 7: Health & Wellness
    hm = HealthManager()
    water = await hm.log_water(250)
    assert water >= 250
    print("Stage 7  Health & Wellness Tracking PASS")

    # Stage 8: Personal Memory & Preferences
    mem = PersonalMemory()
    await mem.remember_fact("work_hours", "09:00 - 18:00")
    assert await mem.get_fact("work_hours") == "09:00 - 18:00"
    print("Stage 8  Personal Memory & Facts    PASS")

    # Stage 9: Proactive Recommendations
    recommender = RecommendationEngine()
    recs = await recommender.get_proactive_recommendations()
    assert len(recs) >= 4
    print("Stage 9  Proactive Recommendations  PASS")

    # Stage 10: End-to-End Voice Command Processing
    engine = AssistantEngine()
    v_plan = await engine.process_voice_query("Hey Nova, plan my day.")
    assert v_plan["intent"] == "plan_day"
    v_rem = await engine.process_voice_query("Hey Nova, remind me to pay electricity tomorrow.")
    assert v_rem["intent"] == "create_reminder"
    print("Stage 10 Voice Command Pipeline     PASS")

    # Stage 11: Assistant Manager Orchestration
    mgr = AssistantManager()
    m_plan = await mgr.plan_day()
    assert m_plan["plan_date"] is not None
    print("Stage 11 Assistant Manager Facade   PASS")

    # Stage 12: Gateway Integration
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass
    gateway = resolve(IAIGateway)
    gw_res = await gateway.plan_day()
    assert gw_res["intent"] == "plan_day"
    print("Stage 12 Gateway Integration        PASS")

    print("\n12/12 PASS")
    print("\nPersonal Assistant Engine Healthy")


if __name__ == "__main__":
    asyncio.run(run_manual_validation())
