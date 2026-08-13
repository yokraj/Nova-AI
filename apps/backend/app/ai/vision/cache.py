"""Caching helpers for visual layout structures and OCR outputs.
"""

from typing import Any, Dict, Optional
from PIL import Image
from app.ai.vision.utils import calculate_image_hash

class VisionCache:
    """Manages memory caches of visual analysis outputs keyed by image hashes."""

    def __init__(self, capacity: int = 100) -> None:
        self.capacity = capacity
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._hit_count = 0
        self._miss_count = 0

    def get(self, image: Image.Image, key: str) -> Optional[Any]:
        """Retrieves cached item by image content hash and configuration key."""
        img_hash = calculate_image_hash(image)
        if img_hash in self._cache:
            entry = self._cache[img_hash]
            if key in entry:
                self._hit_count += 1
                return entry[key]
        self._miss_count += 1
        return None

    def set(self, image: Image.Image, key: str, value: Any) -> None:
        """Saves item inside the image hash context cache registry."""
        img_hash = calculate_image_hash(image)
        if img_hash not in self._cache:
            if len(self._cache) >= self.capacity:
                # Evict oldest entry (basic FIFO eviction)
                oldest = next(iter(self._cache))
                del self._cache[oldest]
            self._cache[img_hash] = {}
        self._cache[img_hash][key] = value

    def clear(self) -> None:
        """Clears all values from the visual cache."""
        self._cache.clear()

    @property
    def metrics(self) -> Dict[str, int]:
        """Returns hits and misses observability metrics."""
        return {
            "hits": self._hit_count,
            "misses": self._miss_count,
            "size": len(self._cache),
        }
