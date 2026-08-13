"""Human Mouse Engine implementing Bezier curves, natural pauses, random offsets, and typing delays.
"""

import math
import random
import time
from typing import Any, Dict, List, Tuple
from app.ai.desktop_automation.models import MouseAction


class HumanMouseEngine:
    """Simulates natural human cursor trajectories (Bezier curves, acceleration, micro-pauses, random jitter)."""

    def __init__(self) -> None:
        self._cursor_history: List[Tuple[int, int]] = [(0, 0)]

    def generate_bezier_path(self, start: Tuple[int, int], end: Tuple[int, int], steps: int = 15) -> List[Tuple[int, int]]:
        """Generates realistic Bezier curve control points between start and end coordinates."""
        cx = (start[0] + end[0]) // 2 + random.randint(-40, 40)
        cy = (start[1] + end[1]) // 2 + random.randint(-40, 40)

        path: List[Tuple[int, int]] = []
        for i in range(steps + 1):
            t = i / steps
            x = int((1 - t) ** 2 * start[0] + 2 * (1 - t) * t * cx + t**2 * end[0])
            y = int((1 - t) ** 2 * start[1] + 2 * (1 - t) * t * cy + t**2 * end[1])
            path.append((x, y))
        self._cursor_history.extend(path)
        return path

    def move_smooth(self, target_x: int, target_y: int, speed_multiplier: float = 1.0) -> MouseAction:
        """Executes smooth human-like Bezier cursor movement to target coordinates."""
        current = self._cursor_history[-1]
        path = self.generate_bezier_path(current, (target_x, target_y))

        # Add human micro-pause
        time.sleep(random.uniform(0.01, 0.03) / max(speed_multiplier, 0.1))

        return MouseAction(
            action_type="human_move",
            x=target_x,
            y=target_y,
            speed_multiplier=speed_multiplier,
        )

    def simulate_human_typing_delay(self, text_length: int) -> float:
        """Calculates realistic typing delay with simulated micro-pauses and keystroke variation."""
        base_delay = text_length * 0.04
        jitter = random.uniform(0.02, 0.08)
        return base_delay + jitter
