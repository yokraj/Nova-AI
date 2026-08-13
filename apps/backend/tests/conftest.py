"""Pytest conftest.py standardizing async backend for anyio.
"""

import pytest

@pytest.fixture
def anyio_backend() -> str:
    """Forces anyio tests to run only on asyncio backend."""
    return "asyncio"
