"""Unit tests for the Conversation Application Use Cases.

Verifies CQRS handler pipelines under mocked repositories and transactional
Unit of Work environments, checking ownership and status rules.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.database.models import Attachment, Conversation, Message
from app.database.models.enums import ConversationStatus
from app.database.unit_of_work import UnitOfWork
from app.conversation.application.commands import (
    CreateConversationCommand,
    SendMessageCommand,
    RenameConversationCommand,
    ArchiveConversationCommand,
    DeleteConversationCommand,
    RestoreConversationCommand,
    AttachmentPayload,
)
from app.conversation.application.queries import (
    GetConversationQuery,
    ListConversationsQuery,
    GetMessagesQuery,
)
from app.conversation.application.use_cases import (
    CreateConversationUseCase,
    SendMessageUseCase,
    ListConversationsUseCase,
    GetConversationUseCase,
    RenameConversationUseCase,
    ArchiveConversationUseCase,
    DeleteConversationUseCase,
    RestoreConversationUseCase,
    GetMessagesUseCase,
)
from app.conversation.repositories.interfaces import (
    IConversationRepository,
    IMessageRepository,
    IAttachmentRepository,
)
from app.conversation.domain.exceptions import (
    ConversationNotFoundError,
    ConversationAccessDeniedError,
    ConversationArchivedError,
    ConversationValidationError,
)


@pytest.fixture
def mock_uow() -> UnitOfWork:
    """Mock database transaction UnitOfWork coordinator."""
    uow = MagicMock(spec=UnitOfWork)
    uow.session = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


@pytest.mark.anyio
async def test_create_conversation_success(mock_uow: UnitOfWork) -> None:
    """Verifies CreateConversationUseCase initializes conversation correctly."""
    conv_repo = AsyncMock(spec=IConversationRepository)
    user_id = uuid.uuid4()

    conv = Conversation(
        id=uuid.uuid4(),
        user_id=user_id,
        title="Valid Title",
        status=ConversationStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    conv_repo.create.return_value = conv

    use_case = CreateConversationUseCase(mock_uow, conv_repo)
    command = CreateConversationCommand(user_id=user_id, title="Valid Title")

    res = await use_case.execute(command)
    assert res.title == "Valid Title"
    assert res.status == ConversationStatus.ACTIVE.value
    conv_repo.create.assert_called_once_with(user_id=user_id, title="Valid Title")


@pytest.mark.anyio
async def test_create_conversation_validation_error(mock_uow: UnitOfWork) -> None:
    """Verifies that empty/whitespace titles trigger ValidationError."""
    conv_repo = AsyncMock(spec=IConversationRepository)
    use_case = CreateConversationUseCase(mock_uow, conv_repo)

    command = CreateConversationCommand(user_id=uuid.uuid4(), title="   ")
    with pytest.raises(ConversationValidationError):
        await use_case.execute(command)


@pytest.mark.anyio
async def test_send_message_success(mock_uow: UnitOfWork) -> None:
    """Verifies SendMessageUseCase appends message and files inside UoW."""
    conv_repo = AsyncMock(spec=IConversationRepository)
    msg_repo = AsyncMock(spec=IMessageRepository)
    attach_repo = AsyncMock(spec=IAttachmentRepository)

    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    msg_id = uuid.uuid4()

    conv = Conversation(
        id=conv_id,
        user_id=user_id,
        title="Active Conv",
        status=ConversationStatus.ACTIVE.value,
    )
    conv_repo.get_by_id.return_value = conv

    msg = Message(
        id=msg_id,
        conversation_id=conv_id,
        role="user",
        content="Hello!",
        token_count=1,
        created_at=datetime.now(UTC),
    )
    msg_repo.create.return_value = msg

    attach = Attachment(
        id=uuid.uuid4(),
        message_id=msg_id,
        name="doc.pdf",
        type="pdf",
        url="http://test.url/doc.pdf",
        size=128,
        created_at=datetime.now(UTC),
    )
    attach_repo.create.return_value = attach

    use_case = SendMessageUseCase(mock_uow, conv_repo, msg_repo, attach_repo)
    command = SendMessageCommand(
        conversation_id=conv_id,
        role="user",
        content="Hello!",
        attachments=[
            AttachmentPayload(
                name="doc.pdf", type="pdf", url="http://test.url/doc.pdf", size=128
            )
        ],
    )

    res = await use_case.execute(command, user_id=user_id)
    assert res.content == "Hello!"
    assert len(res.attachments) == 1
    assert res.attachments[0].name == "doc.pdf"


@pytest.mark.anyio
async def test_send_message_not_found(mock_uow: UnitOfWork) -> None:
    """Verifies SendMessageUseCase raises NotFound if conversation does not exist."""
    conv_repo = AsyncMock(spec=IConversationRepository)
    msg_repo = AsyncMock(spec=IMessageRepository)
    attach_repo = AsyncMock(spec=IAttachmentRepository)

    conv_repo.get_by_id.return_value = None

    use_case = SendMessageUseCase(mock_uow, conv_repo, msg_repo, attach_repo)
    command = SendMessageCommand(
        conversation_id=uuid.uuid4(), role="user", content="Hello"
    )

    with pytest.raises(ConversationNotFoundError):
        await use_case.execute(command, user_id=uuid.uuid4())


@pytest.mark.anyio
async def test_send_message_access_denied(mock_uow: UnitOfWork) -> None:
    """Verifies SendMessageUseCase raises AccessDenied if caller does not own thread."""
    conv_repo = AsyncMock(spec=IConversationRepository)
    msg_repo = AsyncMock(spec=IMessageRepository)
    attach_repo = AsyncMock(spec=IAttachmentRepository)

    conv = Conversation(
        id=uuid.uuid4(), user_id=uuid.uuid4(), title="Other user's", status="active"
    )
    conv_repo.get_by_id.return_value = conv

    use_case = SendMessageUseCase(mock_uow, conv_repo, msg_repo, attach_repo)
    command = SendMessageCommand(
        conversation_id=conv.id, role="user", content="Hello"
    )

    with pytest.raises(ConversationAccessDeniedError):
        await use_case.execute(command, user_id=uuid.uuid4())


@pytest.mark.anyio
async def test_send_message_archived_error(mock_uow: UnitOfWork) -> None:
    """Verifies that posting messages to archived threads triggers ArchivedError."""
    conv_repo = AsyncMock(spec=IConversationRepository)
    msg_repo = AsyncMock(spec=IMessageRepository)
    attach_repo = AsyncMock(spec=IAttachmentRepository)

    user_id = uuid.uuid4()
    conv = Conversation(
        id=uuid.uuid4(),
        user_id=user_id,
        title="Archived Thread",
        status=ConversationStatus.ARCHIVED.value,
    )
    conv_repo.get_by_id.return_value = conv

    use_case = SendMessageUseCase(mock_uow, conv_repo, msg_repo, attach_repo)
    command = SendMessageCommand(
        conversation_id=conv.id, role="user", content="Hello"
    )

    with pytest.raises(ConversationArchivedError):
        await use_case.execute(command, user_id=user_id)


@pytest.mark.anyio
async def test_list_conversations_validation() -> None:
    """Verifies ListConversationsUseCase pagination rules."""
    conv_repo = AsyncMock(spec=IConversationRepository)
    msg_repo = AsyncMock(spec=IMessageRepository)
    use_case = ListConversationsUseCase(conv_repo, msg_repo)

    query = ListConversationsQuery(user_id=uuid.uuid4())

    with pytest.raises(ConversationValidationError):
        await use_case.execute(query, limit=0)

    with pytest.raises(ConversationValidationError):
        await use_case.execute(query, limit=101)

    with pytest.raises(ConversationValidationError):
        await use_case.execute(query, offset=-1)


@pytest.mark.anyio
async def test_rename_conversation_success(mock_uow: UnitOfWork) -> None:
    """Verifies renaming title success updates thread."""
    conv_repo = AsyncMock(spec=IConversationRepository)
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()

    conv = Conversation(
        id=conv_id,
        user_id=user_id,
        title="Original",
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    conv_repo.get_by_id.return_value = conv

    use_case = RenameConversationUseCase(mock_uow, conv_repo)
    command = RenameConversationCommand(conversation_id=conv_id, title="Renamed Title")

    res = await use_case.execute(command, user_id=user_id)
    assert res.title == "Renamed Title"
    conv_repo.rename.assert_called_once_with(conv_id, "Renamed Title")


@pytest.mark.anyio
async def test_archive_restore_delete_flows(mock_uow: UnitOfWork) -> None:
    """Verifies Archive, Delete, and Restore state workflow rules."""
    conv_repo = AsyncMock(spec=IConversationRepository)
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()

    conv = Conversation(
        id=conv_id,
        user_id=user_id,
        title="Thread",
        status=ConversationStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    conv_repo.get_by_id.return_value = conv

    # Archive
    archive_uc = ArchiveConversationUseCase(mock_uow, conv_repo)
    await archive_uc.execute(ArchiveConversationCommand(conversation_id=conv_id), user_id)
    conv_repo.archive.assert_called_with(conv_id)

    # Delete
    delete_uc = DeleteConversationUseCase(mock_uow, conv_repo)
    await delete_uc.execute(DeleteConversationCommand(conversation_id=conv_id), user_id)
    conv_repo.delete.assert_called_with(conv_id)

    # Restore
    restore_uc = RestoreConversationUseCase(mock_uow, conv_repo)
    await restore_uc.execute(RestoreConversationCommand(conversation_id=conv_id), user_id)
    conv_repo.restore.assert_called_with(conv_id)
