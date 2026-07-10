"""Orchestration service coordinating conversation business workflows.
"""

import uuid

from app.database.unit_of_work import UnitOfWork
from app.conversation.services.interfaces import IConversationService
from app.conversation.repositories.interfaces import IConversationRepository, IMessageRepository
from app.conversation.schemas.domain_schemas import ConversationResponse, MessageResponse
from app.conversation.application.commands import (
    CreateConversationCommand,
    SendMessageCommand,
    RenameConversationCommand,
    ArchiveConversationCommand,
    DeleteConversationCommand,
)
from app.conversation.services.validator import ConversationValidator
from app.conversation.services.title_generator import ConversationTitleGenerator
from app.core.dependency_container import resolve
from app.conversation.application.use_cases import (
    CreateConversationUseCase,
    SendMessageUseCase,
    RenameConversationUseCase,
    ArchiveConversationUseCase,
    DeleteConversationUseCase,
)


class ConversationService(IConversationService):
    """Facade orchestrating conversation use cases, ownership validation, and summaries."""

    def __init__(
        self,
        uow: UnitOfWork,
        conv_repo: IConversationRepository,
        msg_repo: IMessageRepository,
        title_generator: ConversationTitleGenerator,
    ) -> None:
        """Initializes ConversationService.

        Args:
            uow: Database unit of work.
            conv_repo: Conversation storage adapter.
            msg_repo: Message storage adapter.
            title_generator: ConversationTitleGenerator instance.
        """
        self.uow = uow
        self.conv_repo = conv_repo
        self.msg_repo = msg_repo
        self.title_generator = title_generator

    async def create_conversation(
        self, command: CreateConversationCommand
    ) -> ConversationResponse:
        """Initializes a new user conversation thread.

        Args:
            command: Create conversation parameters.

        Returns:
            The Conversation metadata response.
        """
        use_case = resolve(CreateConversationUseCase)
        return await use_case.execute(command)

    async def send_message(self, command: SendMessageCommand) -> MessageResponse:
        """Appends a new message within a conversation thread.

        Args:
            command: Message contents parameters.

        Returns:
            The appended message response details.
        """
        conv = await self.conv_repo.get_by_id(command.conversation_id)
        ConversationValidator.validate_exists(conv)
        use_case = resolve(SendMessageUseCase)
        return await use_case.execute(command, user_id=conv.user_id)

    async def rename_conversation(
        self, conversation_id: uuid.UUID, title: str
    ) -> ConversationResponse:
        """Modifies the display title description of a conversation.

        Args:
            conversation_id: Target Conversation UUID.
            title: New title string.

        Returns:
            The updated Conversation metadata response.
        """
        conv = await self.conv_repo.get_by_id(conversation_id)
        ConversationValidator.validate_exists(conv)
        use_case = resolve(RenameConversationUseCase)
        cmd = RenameConversationCommand(conversation_id=conversation_id, title=title)
        return await use_case.execute(cmd, user_id=conv.user_id)

    async def archive_conversation(
        self, conversation_id: uuid.UUID
    ) -> ConversationResponse:
        """Archives a conversation thread to readonly status.

        Args:
            conversation_id: Target Conversation UUID.

        Returns:
            The updated Conversation metadata response.
        """
        conv = await self.conv_repo.get_by_id(conversation_id)
        ConversationValidator.validate_exists(conv)
        use_case = resolve(ArchiveConversationUseCase)
        cmd = ArchiveConversationCommand(conversation_id=conversation_id)
        return await use_case.execute(cmd, user_id=conv.user_id)

    async def delete_conversation(self, conversation_id: uuid.UUID) -> None:
        """Soft-deletes a conversation thread.

        Args:
            conversation_id: Target Conversation UUID.
        """
        conv = await self.conv_repo.get_by_id(conversation_id)
        ConversationValidator.validate_exists(conv)
        use_case = resolve(DeleteConversationUseCase)
        cmd = DeleteConversationCommand(conversation_id=conversation_id)
        await use_case.execute(cmd, user_id=conv.user_id)

    async def summarize_history(self, conversation_id: uuid.UUID) -> str:
        """Generates a text summary details description of the thread history.

        Args:
            conversation_id: Target Conversation UUID.

        Returns:
            A summarized history details text string.
        """
        conv = await self.conv_repo.get_by_id(conversation_id)
        ConversationValidator.validate_exists(conv)
        messages = await self.msg_repo.list_by_conversation(conversation_id)
        if not messages:
            return "No messages history to summarize."
        return f"Summary of thread '{conv.title}' with {len(messages)} messages."

    async def validate_ownership(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Enforces ownership validations check constraints.

        Args:
            conversation_id: Target Conversation UUID.
            user_id: Caller requesting user ID.
        """
        conv = await self.conv_repo.get_by_id(conversation_id)
        ConversationValidator.validate_exists(conv)
        ConversationValidator.validate_ownership(conv, user_id)
