"""Unit tests for the Conversation Services Layer of Nova AI.

Verifies TokenCounter, ContextWindowService, ConversationValidator,
ConversationTitleGenerator, and ConversationService orchestrators.
"""

from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.core.dependency_container import container
from app.database.models import Conversation, Message
from app.database.models.enums import ConversationStatus
from app.database.unit_of_work import UnitOfWork
from app.conversation.application.commands import CreateConversationCommand, SendMessageCommand
from app.conversation.application.use_cases import (
    CreateConversationUseCase,
    SendMessageUseCase,
    RenameConversationUseCase,
    ArchiveConversationUseCase,
    DeleteConversationUseCase,
)
from app.conversation.repositories.interfaces import IConversationRepository, IMessageRepository
from app.conversation.schemas.domain_schemas import ConversationResponse, MessageResponse
from app.conversation.services.token_counter import TokenCounter
from app.conversation.services.context_window import ContextWindowService
from app.conversation.services.validator import ConversationValidator
from app.conversation.services.title_generator import ConversationTitleGenerator
from app.conversation.services.conversation_service import ConversationService
from app.conversation.domain.exceptions import (
    ConversationNotFoundError,
    ConversationAccessDeniedError,
    ConversationValidationError,
)


@pytest.fixture(autouse=True)
def clean_dependencies() -> None:
    """Ensures dependency container registry is clean for resolving mock use cases."""
    container.clear()
    yield
    container.clear()


def test_token_counter_estimation() -> None:
    """Verifies TokenCounter estimates word lengths using character limits division fallbacks."""
    counter = TokenCounter()
    assert counter.count_tokens("Hello world", "gpt-4") == 2  # Char count fallback (11 // 4)
    assert counter.count_message_tokens({"role": "user", "content": "Hello"}, "gpt-4") == 5


@pytest.mark.anyio
async def test_context_window_service_optimization() -> None:
    """Verifies ContextWindowService trims messages exceeding limits while retaining system prompts."""
    counter = TokenCounter()
    ctx_service = ContextWindowService(counter)

    m1 = Message(role="system", content="System instruction")
    m2 = Message(role="user", content="First message")
    m3 = Message(role="assistant", content="Response")
    m4 = Message(role="user", content="Newest message")

    # Limit = 20 tokens. System is 22 chars -> ~5 tokens. Each chat msg is ~3 tokens.
    # Total tokens: sys (9) + user1 (7) + assistant (6) + user2 (7) = 29.
    # Should drop m2 to fit inside limit
    opt = await ctx_service.optimize_context([m1, m2, m3, m4], "gpt-4", token_limit=20)
    assert m1 in opt
    assert m4 in opt
    assert m2 not in opt


def test_conversation_validator() -> None:
    """Verifies ConversationValidator raises correct exceptions on state boundaries."""
    conv = Conversation(user_id=uuid.uuid4(), status=ConversationStatus.ACTIVE.value)

    # Exists check
    ConversationValidator.validate_exists(conv)
    with pytest.raises(ConversationNotFoundError):
        ConversationValidator.validate_exists(None)

    # Ownership check
    ConversationValidator.validate_ownership(conv, conv.user_id)
    with pytest.raises(ConversationAccessDeniedError):
        ConversationValidator.validate_ownership(conv, uuid.uuid4())

    # Active check
    ConversationValidator.validate_active(conv)
    conv.status = ConversationStatus.ARCHIVED.value
    with pytest.raises(ConversationValidationError):
        ConversationValidator.validate_active(conv)


def test_conversation_title_generator() -> None:
    """Verifies short summary titles generate from text contents."""
    generator = ConversationTitleGenerator()
    assert generator.generate_title("Short prompt") == "Short prompt"
    assert generator.generate_title("This is a very long prompt exceeding limit") == "This is a very long prompt..."
    assert generator.generate_title("   ") == "New Conversation"


@pytest.mark.anyio
async def test_conversation_service_orchestration() -> None:
    """Verifies ConversationService facade successfully routes commands to resolved use cases."""
    uow = MagicMock(spec=UnitOfWork)
    conv_repo = AsyncMock(spec=IConversationRepository)
    msg_repo = AsyncMock(spec=IMessageRepository)
    title_gen = ConversationTitleGenerator()

    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()

    conv = Conversation(
        id=conv_id,
        user_id=user_id,
        title="Original Title",
        status=ConversationStatus.ACTIVE.value,
    )
    conv_repo.get_by_id.return_value = conv

    # Setup mocks in container for facade resolution
    mock_create_uc = AsyncMock(spec=CreateConversationUseCase)
    mock_create_uc.execute.return_value = ConversationResponse(
        id=conv_id,
        user_id=user_id,
        title="New thread",
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    container.register(CreateConversationUseCase, lambda: mock_create_uc)

    mock_send_uc = AsyncMock(spec=SendMessageUseCase)
    mock_send_uc.execute.return_value = MessageResponse(
        id=uuid.uuid4(),
        conversation_id=conv_id,
        role="user",
        content="Hi",
        token_count=1,
        created_at=datetime.now(UTC),
    )
    container.register(SendMessageUseCase, lambda: mock_send_uc)

    mock_rename_uc = AsyncMock(spec=RenameConversationUseCase)
    container.register(RenameConversationUseCase, lambda: mock_rename_uc)

    mock_archive_uc = AsyncMock(spec=ArchiveConversationUseCase)
    container.register(ArchiveConversationUseCase, lambda: mock_archive_uc)

    mock_delete_uc = AsyncMock(spec=DeleteConversationUseCase)
    container.register(DeleteConversationUseCase, lambda: mock_delete_uc)

    service = ConversationService(uow, conv_repo, msg_repo, title_gen)

    # 1. Create conversation
    res_create = await service.create_conversation(CreateConversationCommand(user_id=user_id, title="New thread"))
    assert res_create.title == "New thread"

    # 2. Send message
    res_send = await service.send_message(SendMessageCommand(conversation_id=conv_id, role="user", content="Hi"))
    assert res_send.content == "Hi"

    # 3. Rename conversation
    await service.rename_conversation(conv_id, "Renamed Title")
    mock_rename_uc.execute.assert_called_once()

    # 4. Archive conversation
    await service.archive_conversation(conv_id)
    mock_archive_uc.execute.assert_called_once()

    # 5. Delete conversation
    await service.delete_conversation(conv_id)
    mock_delete_uc.execute.assert_called_once()

    # 6. Summarize history
    msg_repo.list_by_conversation.return_value = [Message(role="user", content="Hi")]
    summary = await service.summarize_history(conv_id)
    assert "Original Title" in summary
