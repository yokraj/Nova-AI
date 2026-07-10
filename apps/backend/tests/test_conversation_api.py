"""Integration tests for the Conversation REST API router.

Verifies FastAPI HTTP responses status codes, validation payloads, JWT headers,
and OpenAPI metadata.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.dependency_container import container
from app.database.session import get_db
from app.conversation.api.conversation_router import setup_dependencies as conv_setup
from app.conversation.application.use_cases import (
    CreateConversationUseCase,
    SendMessageUseCase,
    ListConversationsUseCase,
    GetConversationUseCase,
    RenameConversationUseCase,
    DeleteConversationUseCase,
    GetMessagesUseCase,
)
from app.conversation.schemas.domain_schemas import (
    ConversationResponse,
    ConversationSummary,
    MessageResponse,
)
from app.conversation.domain.exceptions import (
    ConversationAccessDeniedError,
    ConversationNotFoundError,
)
from app.main import app


# Override database to bypass dynamic pool setups
async def mock_get_db() -> AsyncMock:
    """Mock database dependency yielding a mock session."""
    yield AsyncMock()


async def mock_setup_dependencies() -> None:
    """Mock setup to bypass container overrides in tests."""
    pass


app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[conv_setup] = mock_setup_dependencies

client = TestClient(app)

# Generate a mock token claims
MOCK_USER_ID = str(uuid.uuid4())
MOCK_HEADERS = {"Authorization": f"Bearer {MOCK_USER_ID}"}


@pytest.fixture(autouse=True)
def clear_container_fixture() -> None:
    """Clears dependency injection registries before and after execution."""
    container.clear()
    yield
    container.clear()


@pytest.fixture(autouse=True)
def mock_current_user(monkeypatch) -> None:
    """Mock get_current_user_claims dependency to return valid mock claims."""
    from app.identity.infrastructure.rbac import get_current_user_claims

    async def mock_claims() -> dict:
        return {"user_id": MOCK_USER_ID, "role": "user"}

    app.dependency_overrides[get_current_user_claims] = mock_claims
    yield
    app.dependency_overrides.pop(get_current_user_claims, None)


def test_openapi_documentation_structure() -> None:
    """Verifies that OpenAPI documentation contains conversation REST endpoints."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == status.HTTP_200_OK

    schema = response.json()
    paths = schema["paths"]

    assert "/api/v1/conversations" in paths
    assert "/api/v1/conversations/{id}" in paths
    assert "/api/v1/conversations/{id}/messages" in paths


def test_api_create_conversation_success() -> None:
    """Verifies POST /conversations success routing and response."""
    mock_uc = AsyncMock(spec=CreateConversationUseCase)
    mock_uc.execute.return_value = ConversationResponse(
        id=uuid.uuid4(),
        user_id=uuid.UUID(MOCK_USER_ID),
        title="New Chat",
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    container.register(CreateConversationUseCase, lambda: mock_uc)

    response = client.post(
        "/api/v1/conversations",
        json={"title": "New Chat"},
        headers=MOCK_HEADERS,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "New Chat"
    assert data["status"] == "active"


def test_api_list_conversations_success() -> None:
    """Verifies GET /conversations returns listing summaries."""
    mock_uc = AsyncMock(spec=ListConversationsUseCase)
    mock_uc.execute.return_value = [
        ConversationSummary(
            id=uuid.uuid4(),
            title="Summary Chat",
            status="active",
            last_message_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
        )
    ]
    container.register(ListConversationsUseCase, lambda: mock_uc)

    response = client.get("/api/v1/conversations", headers=MOCK_HEADERS)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Summary Chat"


def test_api_get_conversation_not_found() -> None:
    """Verifies GET /conversations/{id} triggers HTTP 404 when not found."""
    mock_uc = AsyncMock(spec=GetConversationUseCase)
    mock_uc.execute.side_effect = ConversationNotFoundError("Conversation not found.")
    container.register(GetConversationUseCase, lambda: mock_uc)

    response = client.get(f"/api/v1/conversations/{uuid.uuid4()}", headers=MOCK_HEADERS)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["message"].lower()


def test_api_get_conversation_access_denied() -> None:
    """Verifies GET /conversations/{id} triggers HTTP 403 when access is denied."""
    mock_uc = AsyncMock(spec=GetConversationUseCase)
    mock_uc.execute.side_effect = ConversationAccessDeniedError("Access denied.")
    container.register(GetConversationUseCase, lambda: mock_uc)

    response = client.get(f"/api/v1/conversations/{uuid.uuid4()}", headers=MOCK_HEADERS)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_api_rename_conversation_success() -> None:
    """Verifies PATCH /conversations/{id} successfully renames title."""
    mock_uc = AsyncMock(spec=RenameConversationUseCase)
    conv_id = uuid.uuid4()
    mock_uc.execute.return_value = ConversationResponse(
        id=conv_id,
        user_id=uuid.UUID(MOCK_USER_ID),
        title="Updated Chat",
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    container.register(RenameConversationUseCase, lambda: mock_uc)

    response = client.patch(
        f"/api/v1/conversations/{conv_id}",
        json={"title": "Updated Chat"},
        headers=MOCK_HEADERS,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated Chat"


def test_api_delete_conversation_success() -> None:
    """Verifies DELETE /conversations/{id} yields HTTP 204 No Content."""
    mock_uc = AsyncMock(spec=DeleteConversationUseCase)
    container.register(DeleteConversationUseCase, lambda: mock_uc)

    response = client.delete(f"/api/v1/conversations/{uuid.uuid4()}", headers=MOCK_HEADERS)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_api_send_message_success() -> None:
    """Verifies POST /conversations/{id}/messages routes correctly."""
    mock_uc = AsyncMock(spec=SendMessageUseCase)
    conv_id = uuid.uuid4()
    mock_uc.execute.return_value = MessageResponse(
        id=uuid.uuid4(),
        conversation_id=conv_id,
        role="user",
        content="Hi there!",
        token_count=2,
        created_at=datetime.now(UTC),
    )
    container.register(SendMessageUseCase, lambda: mock_uc)

    response = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={"role": "user", "content": "Hi there!"},
        headers=MOCK_HEADERS,
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["content"] == "Hi there!"


def test_api_get_messages_success() -> None:
    """Verifies GET /conversations/{id}/messages list retrieval success."""
    mock_uc = AsyncMock(spec=GetMessagesUseCase)
    conv_id = uuid.uuid4()
    mock_uc.execute.return_value = [
        MessageResponse(
            id=uuid.uuid4(),
            conversation_id=conv_id,
            role="user",
            content="Hi",
            token_count=1,
            created_at=datetime.now(UTC),
        )
    ]
    container.register(GetMessagesUseCase, lambda: mock_uc)

    response = client.get(f"/api/v1/conversations/{conv_id}/messages", headers=MOCK_HEADERS)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
