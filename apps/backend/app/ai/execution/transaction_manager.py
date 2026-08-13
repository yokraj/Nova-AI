"""Transaction Manager orchestrating multi-step atomic execution blocks."""

from typing import Dict, List, Optional
import structlog

from app.ai.execution.interfaces import ITransactionManager
from app.ai.execution.models import ExecutionStep, TransactionRecord
from app.ai.execution.rollback_manager import RollbackManager

logger = structlog.get_logger("execution_transaction_manager")


class TransactionManager(ITransactionManager):
    """Manages transactional step blocks: begin -> record -> commit or rollback."""

    def __init__(self, rollback_manager: Optional[RollbackManager] = None) -> None:
        self.rollback_mgr = rollback_manager or RollbackManager()
        self._active_transactions: Dict[str, TransactionRecord] = {}

    async def begin(self, mission_id: str) -> str:
        """Start a new transaction block for a mission."""
        tx = TransactionRecord(mission_id=mission_id)
        self._active_transactions[tx.transaction_id] = tx
        logger.info("Began transaction", tx_id=tx.transaction_id, mission_id=mission_id)
        return tx.transaction_id

    def record_step(self, tx_id: str, step: ExecutionStep) -> None:
        """Record an executed step in the active transaction block."""
        tx = self._active_transactions.get(tx_id)
        if tx:
            tx.executed_steps.append(step)

    async def commit(self, tx_id: str) -> None:
        """Commit active transaction."""
        tx = self._active_transactions.get(tx_id)
        if tx:
            tx.committed = True
            logger.info("Committed transaction", tx_id=tx_id)
            self._active_transactions.pop(tx_id, None)

    async def rollback(self, tx_id: str) -> None:
        """Rollback active transaction by executing compensating steps."""
        tx = self._active_transactions.get(tx_id)
        if tx and not tx.rolled_back:
            tx.rolled_back = True
            await self.rollback_mgr.rollback_steps(tx.executed_steps)
            logger.info("Rolled back transaction", tx_id=tx_id)
            self._active_transactions.pop(tx_id, None)
