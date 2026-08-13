"""WebSocket Channel Subscriptions Manager Module.

Manages 20 valid dashboard streaming channel topics, prevents duplicate client
subscriptions, and handles batch channel registration/unregistration.
"""

from typing import List, Set
import structlog

from app.websocket.connection import WebSocketConnection
from app.websocket.exceptions import ChannelNotFoundError, SubscriptionError

logger = structlog.get_logger(__name__)

SUPPORTED_CHANNELS: Set[str] = {
    "dashboard",
    "system",
    "resources",
    "cpu",
    "memory",
    "disk",
    "network",
    "gpu",
    "processes",
    "agents",
    "missions",
    "notifications",
    "events",
    "analytics",
    "health",
    "voice",
    "models",
    "workflows",
    "logs",
    "configuration",
}


class SubscriptionManager:
    """Manages channel topics and connection subscriptions."""

    def __init__(self, valid_channels: Optional[Set[str]] = None) -> None:
        self.valid_channels = valid_channels or set(SUPPORTED_CHANNELS)
        logger.info("subscription_manager_initialized", channel_count=len(self.valid_channels))

    def is_valid_channel(self, channel: str) -> bool:
        """Returns True if channel topic is supported."""
        return channel in self.valid_channels

    def subscribe(self, connection: WebSocketConnection, channel: str) -> bool:
        """Subscribes connection to a single channel topic."""
        if not self.is_valid_channel(channel):
            raise ChannelNotFoundError(channel)

        if connection.is_subscribed(channel):
            logger.debug("duplicate_subscription_skipped", connection_id=str(connection.connection_id), channel=channel)
            return False

        connection.subscribe(channel)
        logger.info("channel_subscribed", connection_id=str(connection.connection_id), channel=channel)
        return True

    def unsubscribe(self, connection: WebSocketConnection, channel: str) -> bool:
        """Unsubscribes connection from a single channel topic."""
        if not self.is_valid_channel(channel):
            raise ChannelNotFoundError(channel)

        if not connection.is_subscribed(channel):
            return False

        connection.unsubscribe(channel)
        logger.info("channel_unsubscribed", connection_id=str(connection.connection_id), channel=channel)
        return True

    def subscribe_many(self, connection: WebSocketConnection, channels: List[str]) -> List[str]:
        """Subscribes connection to multiple channel topics."""
        subscribed = []
        for channel in channels:
            try:
                if self.subscribe(connection, channel):
                    subscribed.append(channel)
            except Exception as exc:
                logger.warning("batch_subscribe_item_failed", channel=channel, error=str(exc))
        return subscribed

    def unsubscribe_many(self, connection: WebSocketConnection, channels: List[str]) -> List[str]:
        """Unsubscribes connection from multiple channel topics."""
        unsubscribed = []
        for channel in channels:
            try:
                if self.unsubscribe(connection, channel):
                    unsubscribed.append(channel)
            except Exception as exc:
                logger.warning("batch_unsubscribe_item_failed", channel=channel, error=str(exc))
        return unsubscribed

    def list_user_subscriptions(self, connection: WebSocketConnection) -> List[str]:
        """Returns list of active channel subscriptions for connection."""
        return sorted(list(connection.subscriptions))
