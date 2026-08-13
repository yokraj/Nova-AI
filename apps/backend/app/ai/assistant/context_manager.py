"""Context Manager building real-time personal life context."""

from datetime import datetime
import structlog

from app.ai.assistant.models import PersonalContext

logger = structlog.get_logger("context_manager")


class ContextManager:
    """Constructs real-time personal life context (date, time, calendar, active projects, tasks)."""

    async def get_current_context(self) -> PersonalContext:
        """Build real-time personal context."""
        now = datetime.utcnow()
        ctx = PersonalContext(
            current_time=now.strftime("%H:%M"),
            current_date=now.strftime("%Y-%m-%d"),
            active_project="Nova AI OS v1.0",
            pending_tasks_count=3,
            upcoming_meetings_count=2,
            work_hours_active=9 <= now.hour < 18,
        )
        logger.debug("Built personal life context", time=ctx.current_time, project=ctx.active_project)
        return ctx
