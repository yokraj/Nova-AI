"""REST API endpoints for managing conversations and thread messages.

Exposes CRUD resources mapped to CQRS use cases with JWT protection.
"""

from typing import Any, List
import uuid
from fastapi import APIRouter, Depends, Query, status

from app.database.session import get_db
from app.core.dependency_container import register_request_dependencies, resolve
from app.identity.infrastructure.rbac import get_current_user_claims

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
from app.conversation.schemas.domain_schemas import (
    ConversationRequest,
    ConversationResponse,
    ConversationSummary,
    MessageRequest,
    MessageResponse,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


async def setup_dependencies(session=Depends(get_db)) -> None:
    """Dependency that registers request-scoped providers inside the container."""
    register_request_dependencies(session)


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(setup_dependencies)],
)
async def create_conversation(
    payload: ConversationRequest,
    claims: dict = Depends(get_current_user_claims),
) -> Any:
    """Initializes a new chat conversation thread."""
    user_id = uuid.UUID(claims["user_id"])
    use_case = resolve(CreateConversationUseCase)
    command = CreateConversationCommand(user_id=user_id, title=payload.title)
    return await use_case.execute(command)


@router.get(
    "",
    response_model=List[ConversationSummary],
    dependencies=[Depends(setup_dependencies)],
)
async def list_conversations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    claims: dict = Depends(get_current_user_claims),
) -> Any:
    """Retrieves paginated user conversation history list."""
    user_id = uuid.UUID(claims["user_id"])
    use_case = resolve(ListConversationsUseCase)
    query = ListConversationsQuery(user_id=user_id)
    return await use_case.execute(query, limit=limit, offset=offset)


@router.get(
    "/{id}",
    response_model=ConversationResponse,
    dependencies=[Depends(setup_dependencies)],
)
async def get_conversation(
    id: uuid.UUID,
    claims: dict = Depends(get_current_user_claims),
) -> Any:
    """Retrieves metadata properties for a specific conversation thread."""
    user_id = uuid.UUID(claims["user_id"])
    use_case = resolve(GetConversationUseCase)
    query = GetConversationQuery(conversation_id=id)
    return await use_case.execute(query, user_id=user_id)


@router.patch(
    "/{id}",
    response_model=ConversationResponse,
    dependencies=[Depends(setup_dependencies)],
)
async def rename_conversation(
    id: uuid.UUID,
    payload: ConversationRequest,
    claims: dict = Depends(get_current_user_claims),
) -> Any:
    """Renames display title for a conversation thread."""
    user_id = uuid.UUID(claims["user_id"])
    use_case = resolve(RenameConversationUseCase)
    command = RenameConversationCommand(conversation_id=id, title=payload.title)
    return await use_case.execute(command, user_id=user_id)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(setup_dependencies)],
)
async def delete_conversation(
    id: uuid.UUID,
    claims: dict = Depends(get_current_user_claims),
) -> None:
    """Soft-deletes a conversation thread."""
    user_id = uuid.UUID(claims["user_id"])
    use_case = resolve(DeleteConversationUseCase)
    command = DeleteConversationCommand(conversation_id=id)
    await use_case.execute(command, user_id=user_id)


@router.post(
    "/{id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(setup_dependencies)],
)
async def send_message(
    id: uuid.UUID,
    payload: MessageRequest,
    claims: dict = Depends(get_current_user_claims),
) -> Any:
    """Appends a new chat message content inside thread."""
    user_id = uuid.UUID(claims["user_id"])
    use_case = resolve(SendMessageUseCase)
    command = SendMessageCommand(
        conversation_id=id,
        role=payload.role,
        content=payload.content,
        attachments=None,
    )
    return await use_case.execute(command, user_id=user_id)


@router.get(
    "/{id}/messages",
    response_model=List[MessageResponse],
    dependencies=[Depends(setup_dependencies)],
)
async def get_messages(
    id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    claims: dict = Depends(get_current_user_claims),
) -> Any:
    """Retrieves paginated messages lists in thread."""
    user_id = uuid.UUID(claims["user_id"])
    use_case = resolve(GetMessagesUseCase)
    query = GetMessagesQuery(conversation_id=id)
    return await use_case.execute(query, user_id=user_id, limit=limit, offset=offset)
