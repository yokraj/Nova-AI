"""Enumerate protected system resource types.
"""

from enum import Enum


class ResourceType(str, Enum):
    """Enumeration of protected system resource types."""

    FILESYSTEM = "FILESYSTEM"
    TERMINAL = "TERMINAL"
    NETWORK = "NETWORK"
    BROWSER = "BROWSER"
    MICROPHONE = "MICROPHONE"
    CAMERA = "CAMERA"
    SCREEN = "SCREEN"
    CLIPBOARD = "CLIPBOARD"
    KEYBOARD = "KEYBOARD"
    MOUSE = "MOUSE"
    PROCESS = "PROCESS"
    DATABASE = "DATABASE"
