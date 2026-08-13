"""Notification Priority Queue Module.

Implements an asynchronous, thread-safe priority queue sorting notification payloads
by severity rank (URGENT > HIGH > NORMAL > LOW) then FIFO within equal priorities.
"""

import asyncio
import heapq
import time
from typing import Any, Dict, List, Optional
import structlog

from app.notification_engine.priority import NotificationPriorityLevel

logger = structlog.get_logger(__name__)


class NotificationQueueItem:
    """Wrapper item for Priority Queue ordering."""

    def __init__(self, payload: Dict[str, Any], counter: int) -> None:
        self.payload = payload
        self.counter = counter

        priority_val = payload.get("priority", NotificationPriorityLevel.NORMAL)
        if isinstance(priority_val, str):
            try:
                priority_val = NotificationPriorityLevel[priority_val.upper()]
            except KeyError:
                priority_val = NotificationPriorityLevel.NORMAL

        # Negate rank so higher priority comes first in min-heap (4 -> -4, 1 -> -1)
        self.priority_rank = -priority_val.rank

    def __lt__(self, other: "NotificationQueueItem") -> bool:
        if self.priority_rank != other.priority_rank:
            return self.priority_rank < other.priority_rank
        return self.counter < other.counter


class NotificationQueue:
    """Priority Queue ordering notifications by severity rank and insertion sequence."""

    def __init__(self, capacity: int = 1000) -> None:
        self.capacity = capacity
        self._heap: List[NotificationQueueItem] = []
        self._counter = 0
        self._lock = asyncio.Lock()
        logger.info("notification_queue_initialized", capacity=capacity)

    async def enqueue(self, payload: Dict[str, Any]) -> bool:
        """Pushes a notification payload into the priority queue."""
        async with self._lock:
            if len(self._heap) >= self.capacity:
                logger.warning("notification_queue_full", capacity=self.capacity)
                return False

            self._counter += 1
            item = NotificationQueueItem(payload, self._counter)
            heapq.heappush(self._heap, item)
            return True

    async def dequeue(self) -> Optional[Dict[str, Any]]:
        """Pops and returns the highest priority notification from the queue."""
        async with self._lock:
            if self._heap:
                item = heapq.heappop(self._heap)
                return item.payload
            return None

    async def peek(self) -> Optional[Dict[str, Any]]:
        """Returns the highest priority notification without popping it."""
        async with self._lock:
            if self._heap:
                return self._heap[0].payload
            return None

    async def size(self) -> int:
        """Returns current queue size."""
        async with self._lock:
            return len(self._heap)

    async def clear(self) -> None:
        """Clears all items in queue."""
        async with self._lock:
            self._heap.clear()
            logger.debug("notification_queue_cleared")

    async def flush(self) -> List[Dict[str, Any]]:
        """Flushes and returns all items ordered by priority."""
        async with self._lock:
            items = []
            while self._heap:
                items.append(heapq.heappop(self._heap).payload)
            return items
