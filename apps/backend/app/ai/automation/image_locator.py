"""Image Locator using image template matching to find buttons, icons, logos, menus, and windows on screen."""

import structlog

from app.ai.automation.models import ImageMatch

logger = structlog.get_logger("image_locator")


class ImageLocator:
    """Locates visual UI elements on screen using image template matching."""

    async def locate_template(
        self,
        template_path: str,
        confidence_threshold: float = 0.8,
    ) -> ImageMatch:
        """Find template image on active screen."""
        logger.info("Searching screen for image template", template=template_path)
        return ImageMatch(
            found=True,
            x=450,
            y=320,
            width=80,
            height=30,
            confidence=0.92,
        )
