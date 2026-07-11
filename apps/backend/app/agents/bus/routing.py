"""RoutingService managing synchronous request-response routing between agents.
"""

import time
import uuid
import asyncio
from typing import Any, Dict, List, Optional
from app.agents.base import BaseAgent, AgentContext
from app.agents.registry.registry import AgentRegistry
from app.agents.bus.request import AgentRequest
from app.agents.bus.response import AgentResponse
from app.agents.bus.exceptions import RoutingError, MessageValidationError


class RoutingService:
    """Resolves and routes requests between agents using the AgentRegistry."""

    def __init__(self, registry: AgentRegistry) -> None:
        """Initializes RoutingService.

        Args:
            registry: Central AgentRegistry.
        """
        self.registry = registry

    def resolve_receiver(self, receiver_name: str) -> Optional[BaseAgent]:
        """Resolves concrete agent instance by name or ID.

        Args:
            receiver_name: Agent name or UUID string representation.

        Returns:
            BaseAgent instance, or None.
        """
        # Check by name first
        for descriptor in self.registry.list():
            if descriptor.name == receiver_name:
                return self.registry.get(descriptor.id)
        # Check by ID
        try:
            receiver_uuid = uuid.UUID(receiver_name)
            return self.registry.get(receiver_uuid)
        except ValueError:
            return None

    async def route_request(self, request: AgentRequest) -> AgentResponse:
        """Routes an AgentRequest to its resolved receiver.

        Args:
            request: AgentRequest payload details.

        Returns:
            AgentResponse from receiver agent execution.

        Raises:
            RoutingError: If receiver is not found or not enabled/initialized.
            MessageValidationError: If request parameters validation fails.
        """
        if not request.sender or not request.receiver:
            raise MessageValidationError("Request sender and receiver names must be set.")

        receiver_agent = self.resolve_receiver(request.receiver)
        if not receiver_agent:
            raise RoutingError(f"Receiver agent '{request.receiver}' not found.")

        # Check if receiver is enabled
        descriptor = None
        for desc in self.registry.list():
            if desc.name == request.receiver or str(desc.id) == request.receiver:
                descriptor = desc
                break

        if descriptor and not descriptor.enabled:
            raise RoutingError(f"Receiver agent '{request.receiver}' is disabled.")

        # Extract user_id from payload, defaulting to a new UUID
        user_id_val = request.payload.get("user_id")
        if isinstance(user_id_val, str):
            try:
                user_id = uuid.UUID(user_id_val)
            except ValueError:
                user_id = uuid.uuid4()
        elif isinstance(user_id_val, uuid.UUID):
            user_id = user_id_val
        else:
            user_id = uuid.uuid4()

        context = AgentContext(
            user_id=user_id,
            conversation_id=request.conversation_id,
            request_id=request.request_id,
        )

        start_time = time.perf_counter()
        try:
            prompt = request.payload.get("prompt", "")
            result = await receiver_agent.execute(context, prompt)
            execution_time = time.perf_counter() - start_time

            return AgentResponse(
                success=result.success,
                sender=request.receiver,
                receiver=request.sender,
                payload={"response": result.response, **result.metadata},
                execution_time=execution_time,
            )
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            raise RoutingError(
                f"Error occurred during execution of receiver agent '{request.receiver}': {str(e)}"
            ) from e

    async def multicast(self, request: AgentRequest, receivers: List[str]) -> List[AgentResponse]:
        """Routes the same request payload to multiple receivers concurrently.

        Args:
            request: Reference AgentRequest template.
            receivers: List of receiver agent names.

        Returns:
            List of AgentResponse outputs.
        """
        tasks = []
        for receiver in receivers:
            req_copy = request.model_copy(update={"receiver": receiver})
            tasks.append(self.route_request(req_copy))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        responses = []
        for r, receiver in zip(results, receivers):
            if isinstance(r, Exception):
                responses.append(
                    AgentResponse(
                        success=False,
                        sender=receiver,
                        receiver=request.sender,
                        payload={"error": str(r)},
                        execution_time=0.0,
                    )
                )
            else:
                responses.append(r)
        return responses

    async def broadcast(self, request: AgentRequest) -> List[AgentResponse]:
        """Routes request to all enabled registered agents (except the sender).

        Args:
            request: Reference AgentRequest template.

        Returns:
            List of AgentResponse outputs from all enabled agents.
        """
        receivers = [
            desc.name
            for desc in self.registry.enabled_agents()
            if desc.name != request.sender
        ]
        return await self.multicast(request, receivers)
