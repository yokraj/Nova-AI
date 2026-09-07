"""Embedding Manager coordinates local neural text embedding generation and caching.

Uses isolated ONNX fastembed runtime (.venv-stt) with local BAAI/bge-small-en-v1.5 model.
Enforces zero-cloud execution and real semantic similarity without MD5 hash vectors.
"""

from typing import List, Dict, Optional
import os
import json
import subprocess
import httpx
import structlog

from app.ai.memory.embedding_provider import IEmbeddingProvider
from app.ai.memory.exceptions import EmbeddingError

logger = structlog.get_logger("embedding_manager")


class EmbeddingManager(IEmbeddingProvider):
    """Generates real local semantic text embeddings using local ONNX fastembed runtime or Ollama."""

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
        host: str = "http://localhost:11434",
        venv_python: Optional[str] = None,
    ) -> None:
        self.model_name = model_name
        self.host = host
        self.cache: Dict[str, List[float]] = {}
        self.expected_dimension = 384  # Standard dimension for bge-small-en-v1.5 / MiniLM

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.venv_python = venv_python or os.path.join(base_dir, ".venv-stt", "Scripts", "python.exe")
        self.worker_script = os.path.join(base_dir, "app", "ai", "memory", "isolated_embedding_worker.py")

    def _embed_via_worker(self, text: str) -> List[float]:
        """Invokes isolated fastembed ONNX worker script to generate real neural vector."""
        if not os.path.exists(self.venv_python) or not os.path.exists(self.worker_script):
            raise EmbeddingError(f"Isolated embedding environment not found at '{self.venv_python}'.")

        worker_model = self.model_name
        if "nomic" in worker_model.lower() or "/" not in worker_model:
            worker_model = "BAAI/bge-small-en-v1.5"

        cmd = [
            self.venv_python,
            self.worker_script,
            "--text",
            text,
            "--model",
            worker_model,
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if proc.returncode != 0:
            err_msg = proc.stderr.strip() or proc.stdout.strip()
            raise EmbeddingError(f"Embedding worker failed: {err_msg}")

        stdout_text = proc.stdout.strip()
        json_line = None
        for line in stdout_text.splitlines():
            if line.startswith("{") and line.endswith("}"):
                json_line = line
                break

        if not json_line:
            raise EmbeddingError(f"Invalid worker stdout: {stdout_text}")

        data = json.loads(json_line)
        if "error" in data:
            raise EmbeddingError(f"Worker embedding generation error: {data['error']}")

        vec = data.get("embedding", [])
        if not vec:
            raise EmbeddingError("Empty embedding vector returned by worker.")

        self.expected_dimension = len(vec)
        return vec

    async def embed_text(self, text: str) -> List[float]:
        """Generates real local embedding vector for text segment."""
        if not text or not text.strip():
            raise EmbeddingError("Text input for embedding generation cannot be empty.")

        if text in self.cache:
            return self.cache[text]

        # 1. Try local Ollama API if host endpoint responds
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.post(
                    f"{self.host}/api/embeddings",
                    json={"model": self.model_name, "prompt": text},
                )
                if response.status_code == 200:
                    vector = response.json().get("embedding", [])
                    if vector:
                        self.cache[text] = vector
                        self.expected_dimension = len(vector)
                        return vector
        except Exception:
            pass

        # 2. Fallback to isolated fastembed ONNX neural model
        try:
            vector = self._embed_via_worker(text)
            self.cache[text] = vector
            return vector
        except Exception as err:
            logger.error("local_embedding_generation_failed", error=str(err))
            raise EmbeddingError(f"Real semantic embedding generation failed: {err}")

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for multiple texts in batch."""
        if not texts:
            raise EmbeddingError("Batch text list cannot be empty.")
        vectors = []
        for text in texts:
            vec = await self.embed_text(text)
            vectors.append(vec)
        return vectors

    def validate_dimensions(self, vector: List[float]) -> bool:
        """Confirms embedding dimensions align with expectations."""
        return len(vector) == self.expected_dimension
