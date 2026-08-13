"""Shopping Manager managing personal shopping lists and inventory."""

from typing import List
import structlog

logger = structlog.get_logger("shopping_manager")


class ShoppingManager:
    """Manages personal shopping lists and purchase items."""

    def __init__(self) -> None:
        self._shopping_list: List[str] = ["Wireless Earbuds", "Notebook"]

    async def add_item(self, item_name: str) -> str:
        """Add item to shopping list."""
        self._shopping_list.append(item_name)
        logger.info("Added item to shopping list", item=item_name)
        return item_name

    async def get_list(self) -> List[str]:
        """Get shopping list."""
        return list(self._shopping_list)
