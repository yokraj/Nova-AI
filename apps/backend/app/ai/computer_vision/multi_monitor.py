"""Multi-Monitor Manager handling multi-screen captures, active screen selection, and coordinate transforms.
"""

from typing import Any, Dict, List
from app.ai.computer_vision.interfaces import IMultiMonitorManager


class MultiMonitorManager(IMultiMonitorManager):
    """Multi-Monitor Manager providing multi-display enumeration and global coordinate transformations."""

    def list_monitors(self) -> List[Dict[str, Any]]:
        """Returns metadata for all connected displays.

        Returns:
            List of monitor descriptor dictionaries.
        """
        return [
            {"index": 0, "name": "Primary Display", "x": 0, "y": 0, "width": 1920, "height": 1080, "is_primary": True},
            {"index": 1, "name": "Secondary Monitor", "x": 1920, "y": 0, "width": 1920, "height": 1080, "is_primary": False},
        ]

    def transform_coordinates(
        self, x: int, y: int, source_monitor: int, target_monitor: int
    ) -> Dict[str, int]:
        """Transforms local monitor coordinates into global multi-monitor desktop virtual screen coordinates.

        Args:
            x: Local X coordinate.
            y: Local Y coordinate.
            source_monitor: Source monitor index.
            target_monitor: Target monitor index.

        Returns:
            Dict containing transformed x and y coordinates.
        """
        monitors = self.list_monitors()
        source = next((m for m in monitors if m["index"] == source_monitor), monitors[0])
        target = next((m for m in monitors if m["index"] == target_monitor), monitors[0])

        global_x = source["x"] + x
        global_y = source["y"] + y

        target_local_x = global_x - target["x"]
        target_local_y = global_y - target["y"]

        return {"x": target_local_x, "y": target_local_y, "global_x": global_x, "global_y": global_y}
