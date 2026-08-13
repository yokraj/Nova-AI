"""Expense Tracker tracking personal expenses and budget analytics."""

from typing import List
import structlog

from app.ai.assistant.models import ExpenseRecord

logger = structlog.get_logger("expense_tracker")


class ExpenseTracker:
    """Logs and categorizes personal expenses."""

    def __init__(self) -> None:
        self._expenses: List[ExpenseRecord] = [
            ExpenseRecord(category="Travel", amount=320.0, description="Train ticket to Chennai"),
        ]

    async def log_expense(self, category: str, amount: float, description: str = "") -> ExpenseRecord:
        """Log new expense."""
        exp = ExpenseRecord(category=category, amount=amount, description=description)
        self._expenses.append(exp)
        logger.info("Logged personal expense", category=category, amount=amount)
        return exp

    async def list_expenses(self) -> List[ExpenseRecord]:
        """List expense records."""
        return list(self._expenses)
