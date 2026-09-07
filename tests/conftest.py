"""Pytest conftest.py standardizing async backend for anyio.
"""

import pytest

collect_ignore_glob = ["manual/*"]

@pytest.fixture
def anyio_backend() -> str:
    """Forces anyio tests to run only on asyncio backend."""
    return "asyncio"

