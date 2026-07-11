"""Tracer managing nesting trace contexts and spans.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid

from app.agent_sdk.observability.exceptions import TracingError
from app.agent_sdk.observability.span import Span


class Tracer:
    """Manages active traces hierarchies and nested spans indexes."""

    def __init__(self) -> None:
        """Initializes Tracer."""
        self._active_spans: Dict[uuid.UUID, Span] = {}
        self._completed_spans: List[Span] = []
        self._current_trace_id: Optional[uuid.UUID] = None
        self._span_stack: List[uuid.UUID] = []

    def start_trace(self) -> uuid.UUID:
        """Starts a new trace hierarchy.

        Returns:
            Trace UUID.
        """
        self._current_trace_id = uuid.uuid4()
        self._span_stack = []
        return self._current_trace_id

    def finish_trace(self) -> None:
        """Closes the current trace context."""
        self._current_trace_id = None
        self._span_stack = []

    def start_span(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> uuid.UUID:
        """Starts a span nesting it inside the active parent span if applicable.

        Args:
            name: Span identifier.
            metadata: Custom attributes.

        Returns:
            Span UUID.
        """
        if not self._current_trace_id:
            self.start_trace()

        trace_id = self._current_trace_id
        parent_id = self._span_stack[-1] if self._span_stack else None

        span = Span(
            trace_id=trace_id,
            parent_span_id=parent_id,
            name=name,
            start_time=datetime.now(timezone.utc),
            metadata=metadata or {},
        )
        self._active_spans[span.span_id] = span
        self._span_stack.append(span.span_id)
        return span.span_id

    def finish_span(self, span_id: uuid.UUID) -> None:
        """Closes the specified span and calculates duration.

        Args:
            span_id: Span UUID.

        Raises:
            TracingError: If span is not found in active list.
        """
        span = self._active_spans.pop(span_id, None)
        if not span:
            raise TracingError(f"Span '{span_id}' is not currently active.")

        span.end_time = datetime.now(timezone.utc)
        span.duration = (span.end_time - span.start_time).total_seconds()
        self._completed_spans.append(span)

        if self._span_stack and self._span_stack[-1] == span_id:
            self._span_stack.pop()

    def get_completed_spans(self) -> List[Span]:
        """Returns the list of all completed spans.

        Returns:
            List of completed Spans.
        """
        return self._completed_spans
