"""Hooks registry managing callback execution around lifecycle transitions.
"""

from typing import Any, Callable, Coroutine, Dict, List

class LifecycleHooks:
    """Manages async subscriber callbacks triggered at hook boundaries."""

    def __init__(self) -> None:
        self._hooks: Dict[str, List[Callable[..., Coroutine[Any, Any, None]]]] = {
            "before_initialize": [],
            "after_initialize": [],
            "before_start": [],
            "after_start": [],
            "before_execute": [],
            "after_execute": [],
            "before_stop": [],
            "after_stop": []
        }

    def register(self, hook_name: str, callback: Callable[..., Coroutine[Any, Any, None]]) -> None:
        """Registers trigger callback to specified hook point."""
        if hook_name in self._hooks:
            self._hooks[hook_name].append(callback)

    async def trigger(self, hook_name: str, *args: Any, **kwargs: Any) -> None:
        """Invokes registered callbacks sequentially."""
        if hook_name in self._hooks:
            for callback in self._hooks[hook_name]:
                await callback(*args, **kwargs)
