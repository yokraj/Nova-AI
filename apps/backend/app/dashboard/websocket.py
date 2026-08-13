"""Dashboard Real-time WebSocket Module.

Forwards WebSocket connections to the production Enterprise WebSocket Gateway.
"""

from app.websocket.router import router

__all__ = ["router"]
