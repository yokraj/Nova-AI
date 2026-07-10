"""Application CQRS use cases for the Conversation bounded context of Nova AI.

Implements all modification command flows and history retrieval query flows.
"""

from datetime import UTC, datetime
from typing import Any, Dict, List
import uuid

from app.database.unit_of_work import UnitOfWork
from app.conversation.application.commands import (
    CreateConversationCommand,
    SendMessageCommand,
    RenameConversationCommand,
    ArchiveConversationCommand,
    DeleteConversationCommand,
    RestoreConversationCommand,
)
from app.conversation.application.queries import (
    GetConversationQuery,
    ListConversationsQuery,
    GetMessagesQuery,
)
from app.conversation.schemas.domain_schemas import (
    ConversationResponse,
    ConversationSummary,
    MessageResponse,
    AttachmentResponse,
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
from app.database.models.enums import ConversationStatus


class CreateConversationUseCase:
    """Orchestrates initialization of a new user conversation thread."""

    def __init__(self, uow: UnitOfWork, conv_repo: IConversationRepository) -> None:
        """Initializes CreateConversationUseCase.

        Args:
            uow: Database unit of work.
            conv_repo: Conversation storage adapter contract.
        """
        self.uow = uow
        self.conv_repo = conv_repo

    async def execute(self, command: CreateConversationCommand) -> ConversationResponse:
        """Executes the conversation creation flow.

        Args:
            command: Command payload containing user ID and title.

        Returns:
            The created conversation validation DTO.
        """
        if not command.title or not command.title.strip():
            raise ConversationValidationError("Conversation title cannot be empty.")

        async with self.uow:
            conv = await self.conv_repo.create(
                user_id=command.user_id, title=command.title.strip()
            )
            # Guarantee ID and timestamps are initialized immediately
            if conv.id is None:
                conv.id = uuid.uuid4()
            if conv.created_at is None:
                conv.created_at = datetime.now(UTC)
            if conv.updated_at is None:
                conv.updated_at = datetime.now(UTC)

        return ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            status=conv.status,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )


class SendMessageUseCase:
    """Orchestrates appending a message and attachments inside a thread."""

    def __init__(
        self,
        uow: UnitOfWork,
        conv_repo: IConversationRepository,
        msg_repo: IMessageRepository,
        attach_repo: IAttachmentRepository,
    ) -> None:
        """Initializes SendMessageUseCase.

        Args:
            uow: Database unit of work.
            conv_repo: Conversation storage adapter.
            msg_repo: Message storage adapter.
            attach_repo: Attachment storage adapter.
        """
        self.uow = uow
        self.conv_repo = conv_repo
        self.msg_repo = msg_repo
        self.attach_repo = attach_repo

    async def execute(self, command: SendMessageCommand, user_id: uuid.UUID) -> MessageResponse:
        """Executes appending the message and uploading attachments in a transaction.

        Args:
            command: Message contents and attachments payload.
            user_id: Caller request user ID claims.

        Returns:
            Created Message response validation DTO.
        """
        conv = await self.conv_repo.get_by_id(command.conversation_id)
        if not conv or conv.status == ConversationStatus.DELETED.value:
            raise ConversationNotFoundError("Conversation not found.")

        if conv.user_id != user_id:
            raise ConversationAccessDeniedError("Access denied to this conversation.")

        if conv.status == ConversationStatus.ARCHIVED.value:
            raise ConversationArchivedError("Archived conversations cannot receive messages.")

        if not command.content or not command.content.strip():
            raise ConversationValidationError("Message content cannot be empty.")

        async with self.uow:
            # Estimate simple token metrics
            token_count = len(command.content.split())
            msg = await self.msg_repo.create(
                conversation_id=command.conversation_id,
                role=command.role,
                content=command.content,
                token_count=token_count,
            )
            if msg.id is None:
                msg.id = uuid.uuid4()
            if msg.created_at is None:
                msg.created_at = datetime.now(UTC)

            attachment_responses = []
            if command.attachments:
                for att in command.attachments:
                    att_record = await self.attach_repo.create(
                        message_id=msg.id,
                        name=att.name,
                        type=att.type,
                        url=att.url,
                        size=att.size,
                    )
                    if att_record.id is None:
                        att_record.id = uuid.uuid4()
                    if att_record.created_at is None:
                        att_record.created_at = datetime.now(UTC)

                    attachment_responses.append(
                        AttachmentResponse(
                            id=att_record.id,
                            message_id=att_record.message_id,
                            name=att_record.name,
                            type=att_record.type,
                            url=att_record.url,
                            size=att_record.size,
                            created_at=att_record.created_at,
                        )
                    )

        return MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            token_count=msg.token_count,
            created_at=msg.created_at,
            attachments=attachment_responses,
        )


class ListConversationsUseCase:
    """Queries paginated lists of conversation metadata items."""

    def __init__(
        self, conv_repo: IConversationRepository, msg_repo: IMessageRepository
    ) -> None:
        """Initializes ListConversationsUseCase.

        Args:
            conv_repo: Conversation storage adapter.
            msg_repo: Message storage adapter.
        """
        self.conv_repo = conv_repo
        self.msg_repo = msg_repo

    async def execute(
        self, query: ListConversationsQuery, limit: int = 20, offset: int = 0
    ) -> List[ConversationSummary]:
        """Queries and returns list summaries of conversations.

        Args:
            query: Target user query options.
            limit: Limit pagination offset.
            offset: Skip elements index.

        Returns:
            List of conversation summaries.
        """
        if limit <= 0 or limit > 100:
            raise ConversationValidationError("Limit must be between 1 and 100.")
        if offset < 0:
            raise ConversationValidationError("Offset must be non-negative.")

        conversations = await self.conv_repo.paginate(
            user_id=query.user_id, limit=limit, offset=offset
        )

        summaries = []
        for conv in conversations:
            latest_msg = await self.msg_repo.latest_message(conv.id)
            last_message_at = latest_msg.created_at if latest_msg else None
            summaries.append(
                ConversationSummary(
                    id=conv.id,
                    title=conv.title,
                    status=conv.status,
                    last_message_at=last_message_at,
                    created_at=conv.created_at,
                )
            )
        return summaries


class GetConversationUseCase:
    """Queries individual conversation metadata details."""

    def __init__(self, conv_repo: IConversationRepository) -> None:
        """Initializes GetConversationUseCase.

        Args:
            conv_repo: Conversation storage adapter.
        """
        self.conv_repo = conv_repo

    async def execute(self, query: GetConversationQuery, user_id: uuid.UUID) -> ConversationResponse:
        """Queries conversation and returns metadata details.

        Args:
            query: Target conversation identifier query.
            user_id: Caller requesting user ID.

        Returns:
            The Conversation metadata validation DTO.
        """
        conv = await self.conv_repo.get_by_id(query.conversation_id)
        if not conv or conv.status == ConversationStatus.DELETED.value:
            raise ConversationNotFoundError("Conversation not found.")

        if conv.user_id != user_id:
            raise ConversationAccessDeniedError("Access denied to this conversation.")

        return ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            status=conv.status,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )


class RenameConversationUseCase:
    """Updates the title description of a conversation thread."""

    def __init__(self, uow: UnitOfWork, conv_repo: IConversationRepository) -> None:
        """Initializes RenameConversationUseCase.

        Args:
            uow: Database unit of work.
            conv_repo: Conversation storage adapter.
        """
        self.uow = uow
        self.conv_repo = conv_repo

    async def execute(
        self, command: RenameConversationCommand, user_id: uuid.UUID
    ) -> ConversationResponse:
        """Updates and saves the new title inside a transaction.

        Args:
            command: Target conversation and new title.
            user_id: Caller requesting user ID.

        Returns:
            The updated Conversation metadata response.
        """
        if not command.title or not command.title.strip():
            raise ConversationValidationError("Conversation title cannot be empty.")

        conv = await self.conv_repo.get_by_id(command.conversation_id)
        if not conv or conv.status == ConversationStatus.DELETED.value:
            raise ConversationNotFoundError("Conversation not found.")

        if conv.user_id != user_id:
            raise ConversationAccessDeniedError("Access denied to this conversation.")

        async with self.uow:
            conv.title = command.title.strip()
            conv.updated_at = datetime.now(UTC)
            await self.conv_repo.rename(command.conversation_id, command.title.strip())

        return ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            status=conv.status,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )


class ArchiveConversationUseCase:
    """Sets a conversation thread status to ARCHIVED."""

    def __init__(self, uow: UnitOfWork, conv_repo: IConversationRepository) -> None:
        """Initializes ArchiveConversationUseCase.

        Args:
            uow: Database unit of work.
            conv_repo: Conversation storage adapter.
        """
        self.uow = uow
        self.conv_repo = conv_repo

    async def execute(
        self, command: ArchiveConversationCommand, user_id: uuid.UUID
    ) -> ConversationResponse:
        """Updates and saves archived status within transaction.

        Args:
            command: Target conversation archive command.
            user_id: Caller user ID.

        Returns:
            The modified Conversation metadata response.
        """
        conv = await self.conv_repo.get_by_id(command.conversation_id)
        if not conv or conv.status == ConversationStatus.DELETED.value:
            raise ConversationNotFoundError("Conversation not found.")

        if conv.user_id != user_id:
            raise ConversationAccessDeniedError("Access denied to this conversation.")

        async with self.uow:
            conv.status = ConversationStatus.ARCHIVED.value
            conv.updated_at = datetime.now(UTC)
            await self.conv_repo.archive(command.conversation_id)

        return ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            status=conv.status,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )


class DeleteConversationUseCase:
    """Soft deletes a conversation thread by setting status to DELETED."""

    def __init__(self, uow: UnitOfWork, conv_repo: IConversationRepository) -> None:
        """Initializes DeleteConversationUseCase.

        Args:
            uow: Database unit of work.
            conv_repo: Conversation storage adapter.
        """
        self.uow = uow
        self.conv_repo = conv_repo

    async def execute(
        self, command: DeleteConversationCommand, user_id: uuid.UUID
    ) -> ConversationResponse:
        """Executes soft delete status update.

        Args:
            command: Target conversation delete command.
            user_id: Caller user ID.

        Returns:
            The soft-deleted Conversation metadata response.
        """
        conv = await self.conv_repo.get_by_id(command.conversation_id)
        if not conv or conv.status == ConversationStatus.DELETED.value:
            raise ConversationNotFoundError("Conversation not found.")

        if conv.user_id != user_id:
            raise ConversationAccessDeniedError("Access denied to this conversation.")

        async with self.uow:
            conv.status = ConversationStatus.DELETED.value
            conv.updated_at = datetime.now(UTC)
            await self.conv_repo.delete(command.conversation_id)

        return ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            status=conv.status,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )


class RestoreConversationUseCase:
    """Restores a soft-deleted or archived conversation back to ACTIVE status."""

    def __init__(self, uow: UnitOfWork, conv_repo: IConversationRepository) -> None:
        """Initializes RestoreConversationUseCase.

        Args:
            uow: Database unit of work.
            conv_repo: Conversation storage adapter.
        """
        self.uow = uow
        self.conv_repo = conv_repo

    async def execute(
        self, command: RestoreConversationCommand, user_id: uuid.UUID
    ) -> ConversationResponse:
        """Reverts status state back to active inside transaction.

        Args:
            command: Target conversation restore command.
            user_id: Caller user ID.

        Returns:
            The restored ACTIVE Conversation response.
        """
        conv = await self.conv_repo.get_by_id(command.conversation_id)
        if not conv:
            raise ConversationNotFoundError("Conversation not found.")

        if conv.user_id != user_id:
            raise ConversationAccessDeniedError("Access denied to this conversation.")

        async with self.uow:
            conv.status = ConversationStatus.ACTIVE.value
            conv.updated_at = datetime.now(UTC)
            await self.conv_repo.restore(command.conversation_id)

        return ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            status=conv.status,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )


class GetMessagesUseCase:
    """Queries chronological lists of messages in a thread."""

    def __init__(
        self,
        conv_repo: IConversationRepository,
        msg_repo: IMessageRepository,
        attach_repo: IAttachmentRepository,
    ) -> None:
        """Initializes GetMessagesUseCase.

        Args:
            conv_repo: Conversation storage.
            msg_repo: Message storage.
            attach_repo: Attachment storage.
        """
        self.conv_repo = conv_repo
        self.msg_repo = msg_repo
        self.attach_repo = attach_repo

    async def execute(
        self, query: GetMessagesQuery, user_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> List[MessageResponse]:
        """Queries and returns list of messages and attachments.

        Args:
            query: Target conversation query.
            user_id: Request user ID claims.
            limit: Limit pagination offset.
            offset: Skip elements index.

        Returns:
            List of message response objects.
        """
        if limit <= 0 or limit > 100:
            raise ConversationValidationError("Limit must be between 1 and 100.")
        if offset < 0:
            raise ConversationValidationError("Offset must be non-negative.")

        conv = await self.conv_repo.get_by_id(query.conversation_id)
        if not conv or conv.status == ConversationStatus.DELETED.value:
            raise ConversationNotFoundError("Conversation not found.")

        if conv.user_id != user_id:
            raise ConversationAccessDeniedError("Access denied to this conversation.")

        messages = await self.msg_repo.paginate(
            conversation_id=query.conversation_id, limit=limit, offset=offset
        )

        msg_responses = []
        for msg in messages:
            attachments = await self.attach_repo.list_by_message(msg.id)
            att_responses = [
                AttachmentResponse(
                    id=att.id,
                    message_id=att.message_id,
                    name=att.name,
                    type=att.type,
                    url=att.url,
                    size=att.size,
                    created_at=att.created_at,
                )
                for att in attachments
            ]
            msg_responses.append(
                MessageResponse(
                    id=msg.id,
                    conversation_id=msg.conversation_id,
                    role=msg.role,
                    content=msg.content,
                    token_count=msg.token_count,
                    created_at=msg.created_at,
                    attachments=att_responses,
                )
            )
        return msg_responses
