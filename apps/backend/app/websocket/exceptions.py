"""WebSocket Gateway Exception Hierarchy Module.

Defines custom exception classes for authentication failures, channel errors,
subscription conflicts, heartbeat timeouts, and broadcast issues.
"""


class WebSocketGatewayError(Exception):
    """Base exception for all WebSocket Gateway failures."""

    def __init__(self, message: str = "WebSocket gateway error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class WebSocketAuthenticationError(WebSocketGatewayError):
    """Raised when JWT token decoding or handshake authentication fails."""

    def __init__(self, detail: str = "WebSocket authentication failed.") -> None:
        super().__init__(detail)


class SubscriptionError(WebSocketGatewayError):
    """Raised when subscribing or unsubscribing to a channel fails."""

    def __init__(self, detail: str = "Channel subscription error.") -> None:
        super().__init__(detail)


class ChannelNotFoundError(WebSocketGatewayError):
    """Raised when attempting to access an invalid or unregistered channel."""

    def __init__(self, channel: str) -> None:
        super().__init__(f"WebSocket channel '{channel}' not found or invalid.")


class ConnectionClosedError(WebSocketGatewayError):
    """Raised when attempting I/O operations on a closed connection."""

    def __init__(self, connection_id: str) -> None:
        super().__init__(f"WebSocket connection '{connection_id}' is closed.")


class HeartbeatTimeoutError(WebSocketGatewayError):
    """Raised when a client fails to respond to ping frames within timeout limits."""

    def __init__(self, connection_id: str) -> None:
        super().__init__(f"Heartbeat timeout for connection '{connection_id}'.")


class BroadcastError(WebSocketGatewayError):
    """Raised when payload distribution to connections encounters unhandled failure."""

    def __init__(self, detail: str = "Failed to broadcast message.") -> None:
        super().__init__(detail)
