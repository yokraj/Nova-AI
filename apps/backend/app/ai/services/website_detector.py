"""Website Detector recognizing site domains and route endpoints from natural language requests."""

from typing import Optional, Tuple
import structlog

logger = structlog.get_logger("website_detector")


class WebsiteDetector:
    """Detects target domain and URL route for user service requests."""

    DOMAIN_MAPPINGS: dict = {
        "train": ("irctc.co.in", "https://irctc.co.in/nget/train-search"),
        "flight": ("makemytrip.com", "https://makemytrip.com/flights"),
        "passport": ("passportindia.gov.in", "https://passportindia.gov.in"),
        "tax": ("incometax.gov.in", "https://incometax.gov.in"),
        "amazon": ("amazon.in", "https://amazon.in"),
        "bank": ("netbanking.com", "https://netbanking.com"),
    }

    async def detect_website(self, utterance: str) -> Tuple[str, str]:
        """Detect (domain, start_url) from voice command."""
        text_lower = utterance.lower()
        for key, (domain, url) in self.DOMAIN_MAPPINGS.items():
            if key in text_lower:
                logger.info("Detected target website", domain=domain, url=url)
                return domain, url
        return "google.com", "https://google.com"
