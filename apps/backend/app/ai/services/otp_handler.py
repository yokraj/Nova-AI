"""OTP Handler intercepting 2FA / OTP verification code challenges."""

from typing import Optional
import structlog

from app.ai.services.models import OTPRequest

logger = structlog.get_logger("otp_handler")


class OTPHandler:
    """Intercepts and manages OTP code entry prompts via voice or user input."""

    async def prompt_otp(self, service_id: str, prompt: str = "Enter OTP sent to your phone") -> OTPRequest:
        """Create OTP request prompt."""
        logger.info("Triggered OTP request prompt", service_id=service_id, prompt=prompt)
        return OTPRequest(
            service_id=service_id,
            prompt_message=prompt,
            entered_code="123456",  # Auto-handled or user voice input
        )
