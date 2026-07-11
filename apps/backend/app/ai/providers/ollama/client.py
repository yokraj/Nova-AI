"""HTTP client wrapping network interactions with the Ollama server API.
"""

from typing import Any, AsyncGenerator, Dict
import json
import httpx
from app.ai.providers.ollama.config import OllamaConfig
from app.ai.providers.ollama.exceptions import (
    OllamaConnectionError,
    OllamaProviderError,
    OllamaTimeoutError,
)


class OllamaClient:
    """HTTP client wrapping network interactions with the Ollama server API."""

    def __init__(self, config: OllamaConfig) -> None:
        """Initializes OllamaClient.

        Args:
            config: OllamaConfig settings.
        """
        self.config = config

    async def post(self, endpoint: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sends a POST request to Ollama server.

        Args:
            endpoint: URL path segment.
            json_data: JSON payload.

        Returns:
            Decoded JSON response dictionary.
        """
        url = f"{self.config.host.rstrip('/')}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.post(url, json=json_data)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as err:
            raise OllamaTimeoutError("Ollama request timed out.") from err
        except httpx.RequestError as err:
            raise OllamaConnectionError(f"Failed to connect to Ollama: {str(err)}") from err
        except Exception as err:
            raise OllamaProviderError(f"Ollama API request failed: {str(err)}") from err

    async def get(self, endpoint: str) -> Dict[str, Any]:
        """Sends a GET request to Ollama server.

        Args:
            endpoint: URL path segment.

        Returns:
            Decoded JSON response dictionary.
        """
        url = f"{self.config.host.rstrip('/')}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as err:
            raise OllamaTimeoutError("Ollama request timed out.") from err
        except httpx.RequestError as err:
            raise OllamaConnectionError(f"Failed to connect to Ollama: {str(err)}") from err
        except Exception as err:
            raise OllamaProviderError(f"Ollama API request failed: {str(err)}") from err

    async def post_stream(self, endpoint: str, json_data: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Sends a streaming POST request to Ollama server.

        Args:
            endpoint: URL path segment.
            json_data: JSON payload.

        Yields:
            Decoded JSON chunks.
        """
        url = f"{self.config.host.rstrip('/')}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                async with client.stream("POST", url, json=json_data) as response:
                    response.raise_for_status()
                    async for line in response.iter_lines():
                        if line:
                            yield json.loads(line)
        except httpx.TimeoutException as err:
            raise OllamaTimeoutError("Ollama request timed out.") from err
        except httpx.RequestError as err:
            raise OllamaConnectionError(f"Failed to connect to Ollama: {str(err)}") from err
        except Exception as err:
            raise OllamaProviderError(f"Ollama API request failed: {str(err)}") from err
