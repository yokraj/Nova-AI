"""Dashboard Constants Module.

Defines event identifiers, channel topics, and configuration defaults for the
Nova AI Enterprise Dashboard backend architecture.
"""

from typing import Final

# Dashboard Event Names
SYSTEM_UPDATED: Final[str] = "system.updated"
RESOURCE_UPDATED: Final[str] = "resource.updated"
MISSION_UPDATED: Final[str] = "mission.updated"
MODEL_UPDATED: Final[str] = "model.updated"
VOICE_UPDATED: Final[str] = "voice.updated"
WORKFLOW_UPDATED: Final[str] = "workflow.updated"
NOTIFICATION_CREATED: Final[str] = "notification.created"
LOG_RECEIVED: Final[str] = "log.received"
HEALTH_UPDATED: Final[str] = "health.updated"

