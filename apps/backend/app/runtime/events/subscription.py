"""Subscription definition aliases for system event subscribers.
"""

from typing import Awaitable, Callable, Union
from app.runtime.events.event import SystemEvent
from app.runtime.events.event_handler import EventHandler

# Supported subscriber types: EventHandler interface subclass or async callable listener
Subscriber = Union[EventHandler, Callable[[SystemEvent], Awaitable[None]]]
