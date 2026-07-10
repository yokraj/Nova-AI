"""Unit tests for the Conversation Repository Layer of Nova AI.

Verifies ConversationRepository, MessageRepository, and AttachmentRepository
queries and modification operations using mocked AsyncSessions.
"""

from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Attachment, Conversation, Message
from app.database.models.enums import ConversationStatus
from app.conversation.repositories.conversation_repository import ConversationRepository
from app.conversation.repositories.message_repository import MessageRepository
from app.conversation.repositories.attachment_repository import AttachmentRepository


@pytest.mark.anyio
async def test_conversation_repository_operations() -> None:
    """Verifies ConversationRepository CRUD, status updates, and paginate queries."""
    session = AsyncMock(spec=AsyncSession)
    repo = ConversationRepository(session)

    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()

    # 1. Create
    conv = await repo.create(user_id=user_id, title="Test Conversation")
    assert conv.user_id == user_id
    assert conv.title == "Test Conversation"
    assert conv.status == ConversationStatus.ACTIVE.value
    session.add.assert_called_with(conv)

    # 2. Get by ID
    conv.id = conv_id
    mock_exec = MagicMock()
    mock_exec.scalar_or_none.return_value = conv
    session.execute.return_value = mock_exec

    res = await repo.get_by_id(conv_id)
    assert res is conv

    # 3. Rename
    updated_conv = await repo.rename(conv_id, "New Title")
    assert updated_conv.title == "New Title"

    # 4. Archive
    archived_conv = await repo.archive(conv_id)
    assert archived_conv.status == ConversationStatus.ARCHIVED.value

    # 5. Delete (soft-delete)
    deleted_ok = await repo.delete(conv_id)
    assert deleted_ok is True
    assert conv.status == ConversationStatus.DELETED.value

    # 6. Restore
    restored_conv = await repo.restore(conv_id)
    assert restored_conv.status == ConversationStatus.ACTIVE.value

    # 7. Exists
    mock_exec.scalar.return_value = 1
    exists_ok = await repo.exists(conv_id)
    assert exists_ok is True

    # 8. Count by User
    mock_exec.scalar.return_value = 5
    count = await repo.count_by_user(user_id)
    assert count == 5

    # 9. List & Paginate
    mock_exec.scalars().all.return_value = [conv]
    list_res = await repo.list_by_user(user_id)
    assert len(list_res) == 1

    pag_res = await repo.paginate(user_id, limit=10, offset=0)
    assert len(pag_res) == 1


@pytest.mark.anyio
async def test_message_repository_operations() -> None:
    """Verifies MessageRepository CRUD, message counts, and latest messages."""
    session = AsyncMock(spec=AsyncSession)
    repo = MessageRepository(session)

    conv_id = uuid.uuid4()
    msg_id = uuid.uuid4()

    # 1. Create
    msg = await repo.create(
        conversation_id=conv_id, role="user", content="Hello", token_count=10
    )
    assert msg.conversation_id == conv_id
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.token_count == 10
    session.add.assert_called_with(msg)

    # 2. Get by ID
    msg.id = msg_id
    mock_exec = MagicMock()
    mock_exec.scalar_or_none.return_value = msg
    session.execute.return_value = mock_exec

    res = await repo.get_by_id(msg_id)
    assert res is msg

    # 3. List by Conversation & Paginate
    mock_exec.scalars().all.return_value = [msg]
    list_res = await repo.list_by_conversation(conv_id)
    assert len(list_res) == 1

    pag_res = await repo.paginate(conv_id, limit=5, offset=0)
    assert len(pag_res) == 1

    # 4. Count messages
    mock_exec.scalar.return_value = 12
    count = await repo.count_messages(conv_id)
    assert count == 12

    # 5. Latest Message
    latest = await repo.latest_message(conv_id)
    assert latest is msg

    # 6. Delete
    delete_ok = await repo.delete(msg_id)
    assert delete_ok is True
    session.delete.assert_called_with(msg)


@pytest.mark.anyio
async def test_attachment_repository_operations() -> None:
    """Verifies AttachmentRepository CRUD and bulk deletes."""
    session = AsyncMock(spec=AsyncSession)
    repo = AttachmentRepository(session)

    msg_id = uuid.uuid4()
    attach_id = uuid.uuid4()

    # 1. Create
    attach = await repo.create(
        message_id=msg_id, name="test.png", type="image", url="http://test.url", size=1024
    )
    assert attach.message_id == msg_id
    assert attach.name == "test.png"
    assert attach.type == "image"
    assert attach.url == "http://test.url"
    assert attach.size == 1024
    session.add.assert_called_with(attach)

    # 2. Get by ID
    attach.id = attach_id
    mock_exec = MagicMock()
    mock_exec.scalar_or_none.return_value = attach
    session.execute.return_value = mock_exec

    res = await repo.get_by_id(attach_id)
    assert res is attach

    # 3. List by Message
    mock_exec.scalars().all.return_value = [attach]
    list_res = await repo.list_by_message(msg_id)
    assert len(list_res) == 1

    # 4. Delete Attachment
    delete_ok = await repo.delete(attach_id)
    assert delete_ok is True
    session.delete.assert_called_with(attach)

    # 5. Delete by Message ID
    mock_exec.rowcount = 3
    session.execute.return_value = mock_exec
    deleted_count = await repo.delete_by_message(msg_id)
    assert deleted_count == 3
