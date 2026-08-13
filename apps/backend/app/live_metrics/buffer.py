"""Metrics Buffer Module.

Provides a thread-safe and async bounded buffer queue for storing pending
telemetry broadcast payloads with configurable capacity limits.
"""

from collections import deque
import threading
from typing import Any, Dict, List, Optional
import structlog

from app.live_metrics.exceptions import BufferOverflow

logger = structlog.get_logger(__name__)


class MetricsBuffer:
    """Thread-safe bounded queue for buffering telemetry update payloads."""

    def __init__(self, capacity: int = 100) -> None:
        self.capacity = capacity
        self._buffer: deque = deque(maxlen=capacity)
        self._lock = threading.Lock()
        logger.info("metrics_buffer_initialized", capacity=capacity)

    def push(self, item: Dict[str, Any]) -> None:
        """Pushes a metric item into the buffer. Evicts oldest item if capacity is exceeded."""
        with self._lock:
            if len(self._buffer) >= self.capacity:
                logger.warning("buffer_capacity_reached_evicting_oldest", capacity=self.capacity)
            self._buffer.append(item)

    def pop(self) -> Optional[Dict[str, Any]]:
        """Pops and returns the oldest metric item from the buffer."""
        with self._lock:
            if self._buffer:
                return self._buffer.popleft()
            return None

    def peek(self) -> Optional[Dict[str, Any]]:
        """Returns the oldest metric item without removing it from buffer."""
        with self._lock:
            if self._buffer:
                return self._buffer[0]
            return None

    def clear(self) -> None:
        """Empties all items from the buffer."""
        with self._lock:
            self._buffer.clear()
            logger.debug("metrics_buffer_cleared")

    def size(self) -> int:
        """Returns current item count in buffer."""
        with self._lock:
            return len(self._buffer)

    def flush(self) -> List[Dict[str, Any]]:
        """Flushes and returns all items currently queued in buffer."""
        with self._lock:
            items = list(self._buffer)
            self._buffer.clear()
            return items
