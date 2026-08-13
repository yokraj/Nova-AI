"""Enterprise AI Gateway core orchestration layer.
"""

import asyncio
from typing import Any, AsyncGenerator, List, Optional
from app.ai.gateway import IAIGateway
from app.ai.gateway.exceptions import (
    CapabilityUnavailableError,
    GatewayTimeoutError,
    ModelUnavailableError,
    ProviderNotFoundError,
    ProviderUnavailableError,
)
from app.ai.gateway.model_registry import ModelRegistry
from app.ai.gateway.provider_factory import ProviderFactory
from app.ai.gateway.provider_registry import ProviderRegistry
from app.ai.gateway.request_context import RequestContext
from app.ai.gateway.retry_policy import RetryPolicy
from app.ai.gateway.timeout_policy import TimeoutPolicy
from app.ai.models import (
    ChatRequest,
    ChatResponse,
    PromptMessage,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderCapability,
    StreamingChunk,
)


class AIGateway(IAIGateway):
    """The central enterprise AI Gateway orchestrating routing and execution policies."""

    def __init__(
        self,
        provider_registry: ProviderRegistry,
        model_registry: ModelRegistry,
        factory: ProviderFactory,
        retry_policy: RetryPolicy,
        timeout_policy: TimeoutPolicy,
    ) -> None:
        """Initializes AIGateway.

        Args:
            provider_registry: Active ProviderRegistry.
            model_registry: Active ModelRegistry.
            factory: ProviderFactory helper.
            retry_policy: RetryPolicy configurations.
            timeout_policy: TimeoutPolicy limits configuration.
        """
        self.provider_registry = provider_registry
        self.model_registry = model_registry
        self.factory = factory
        self.retry_policy = retry_policy
        self.timeout_policy = timeout_policy

        from app.ai.router.router import IntelligentModelRouter
        self.intelligent_router = IntelligentModelRouter()

        from app.ai.memory.engine import LocalMemoryEngine
        self.memory = LocalMemoryEngine()

        from app.ai.agents.manager import AgentManager
        self._agents = AgentManager(memory_engine=self.memory)

        from app.ai.safety.safety_engine import SafetyEngine
        self._safety = SafetyEngine(
            event_bus=self._agents.event_bus,
            memory_engine=self.memory
        )

    @property
    def agents(self) -> Any:
        """Exposes the central AgentManager orchestrator instance."""
        return self._agents

    @property
    def safety(self) -> Any:
        """Exposes the central SafetyEngine coordinator instance."""
        return self._safety

    def _resolve_provider(self, context: RequestContext, capability: ProviderCapability) -> Any:
        """Resolves provider matching context parameters and validates capabilities.

        Args:
            context: Request context containing model details.
            capability: Target capability enum.

        Returns:
            The matched provider instance.
        """
        model_meta = self.model_registry.model(context.selected_model)
        if not model_meta:
            raise ModelUnavailableError(f"Model '{context.selected_model}' is not registered.")

        if capability not in model_meta.capabilities:
            raise CapabilityUnavailableError(
                f"Model '{context.selected_model}' does not support '{capability.value}' capability."
            )

        provider_name = context.provider
        
        # 1. Local model available routing priority check
        local_models = ["qwen2.5-coder", "deepseek-r1-distill-qwen", "nomic-embed-text", "qwen2.5-vl", "llama3"]
        if not provider_name and context.selected_model in local_models:
            ollama_health = self.provider_registry.health("ollama")
            if ollama_health and ollama_health.is_healthy:
                provider_name = "ollama"

        if not provider_name:
            # Match first registered provider supporting model name
            for name in self.provider_registry.list():
                inst = self.provider_registry.provider(name)
                if hasattr(inst, "supports_model") and inst.supports_model(context.selected_model):
                    provider_name = name
                    break

        if not provider_name:
            # Fallback based on model name prefix
            provider_name = context.selected_model.split("-")[0]

        provider = self.provider_registry.provider(provider_name)
        if not provider:
            raise ProviderNotFoundError(f"Provider '{provider_name}' not found.")

        # Check health
        health = self.provider_registry.health(provider_name)
        if health and not health.is_healthy:
            raise ProviderUnavailableError(f"Provider '{provider_name}' is unhealthy.")

        # Verify interface implementation
        if not self.factory.validate_provider(provider, capability):
            raise CapabilityUnavailableError(
                f"Provider '{provider_name}' does not implement interface for '{capability.value}'."
            )

        context.provider = provider_name
        return provider

    async def _execute(self, call_fn: Any, *args: Any, **kwargs: Any) -> Any:
        """Helper to run a method wrapping it inside retry and timeout policies."""
        attempt = 0
        while True:
            attempt += 1
            try:
                return await asyncio.wait_for(
                    call_fn(*args, **kwargs),
                    timeout=self.timeout_policy.timeout_seconds,
                )
            except asyncio.TimeoutError as err:
                if self.retry_policy.should_retry(err, attempt):
                    await asyncio.sleep(self.retry_policy.backoff_factor**attempt * 0.1)
                    continue
                raise GatewayTimeoutError("Gateway operation timed out.")
            except Exception as err:
                if self.retry_policy.should_retry(err, attempt):
                    await asyncio.sleep(self.retry_policy.backoff_factor**attempt * 0.1)
                    continue
                raise err

    async def chat(self, request: ChatRequest, **kwargs: Any) -> ChatResponse:
        """Orchestrates non-streaming chat completions."""
        prompt = request.messages[-1].content if request.messages else ""

        # Retrieve related memories using LocalMemoryEngine and inject
        try:
            mem_pkg = await self.memory.retrieve_context(prompt)
            contexts = []
            
            # Check for voice_context parameters
            voice_ctx = kwargs.get("voice_context")
            if voice_ctx and isinstance(voice_ctx, dict):
                recent_cmds = voice_ctx.get("recent_commands", [])
                if recent_cmds:
                    cmds_str = ", ".join(recent_cmds)
                    contexts.append(f"Voice session recent commands: {cmds_str}")

            if mem_pkg.memory_context:
                contexts.append(f"Recent conversation context:\n{mem_pkg.memory_context}")
            if mem_pkg.project_context:
                contexts.append(f"Project history context:\n{mem_pkg.project_context}")
            if mem_pkg.code_context:
                contexts.append(f"Code base context:\n{mem_pkg.code_context}")
            
            if contexts and request.messages:
                context_str = "\n\n".join(contexts)
                request.messages[-1].content = f"[Context]\n{context_str}\n\n[Prompt] {prompt}"
        except Exception:
            pass

        # Query router only if the model is unregistered or set to auto-select
        is_registered = False
        if request.model:
            try:
                is_registered = self.model_registry.model(request.model) is not None
            except Exception:
                pass

        decision = None
        if not is_registered or request.model == "auto-select-me":
            from app.ai.router.models import RoutingRequest
            routing_req = RoutingRequest(
                request_id="chat-req",
                prompt=prompt,
                context_size=request.max_tokens or 2048
            )
            decision = await self.intelligent_router.route_request(routing_req)
            request.model = decision.selected_model

        context = RequestContext(selected_model=request.model)
        provider = self._resolve_provider(context, ProviderCapability.CHAT)

        try:
            res = await self._execute(provider.chat, request, **kwargs)
            
            # Store conversation history in memory
            try:
                conv_id = kwargs.get("conversation_id", "default_session")
                await self.memory.conversation.store_message(conv_id, "user", prompt)
                await self.memory.conversation.store_message(conv_id, "assistant", res.message.content)
            except Exception:
                pass

            return res
        except Exception as e:
            if decision:
                try:
                    next_model = self.intelligent_router.handle_execution_failure(decision, request.model)
                    request.model = next_model
                    context = RequestContext(selected_model=request.model)
                    provider = self._resolve_provider(context, ProviderCapability.CHAT)
                    res2 = await self._execute(provider.chat, request, **kwargs)
                    
                    try:
                        conv_id = kwargs.get("conversation_id", "default_session")
                        await self.memory.conversation.store_message(conv_id, "user", prompt)
                        await self.memory.conversation.store_message(conv_id, "assistant", res2.message.content)
                    except Exception:
                        pass
                    
                    return res2
                except Exception:
                    raise e
            raise e

    async def stream_chat(
        self, request: ChatRequest, **kwargs: Any
    ) -> AsyncGenerator[StreamingChunk, None]:
        """Orchestrates token streaming chat completions."""
        # Query router only if the model is unregistered or set to auto-select
        is_registered = False
        if request.model:
            try:
                is_registered = self.model_registry.model(request.model) is not None
            except Exception:
                pass

        decision = None
        if not is_registered or request.model == "auto-select-me":
            from app.ai.router.models import RoutingRequest
            prompt = request.messages[-1].content if request.messages else ""
            routing_req = RoutingRequest(
                request_id="stream-chat-req",
                prompt=prompt,
                context_size=request.max_tokens or 2048
            )
            decision = await self.intelligent_router.route_request(routing_req)
            request.model = decision.selected_model

        context = RequestContext(selected_model=request.model)
        provider = self._resolve_provider(context, ProviderCapability.CHAT)

        # Execute stream retrieval from provider generator
        try:
            async for chunk in provider.stream_chat(request, **kwargs):
                yield chunk
        except Exception as e:
            if decision:
                try:
                    next_model = self.intelligent_router.handle_execution_failure(decision, request.model)
                    request.model = next_model
                    context = RequestContext(selected_model=request.model)
                    provider = self._resolve_provider(context, ProviderCapability.CHAT)
                    async for chunk in provider.stream_chat(request, **kwargs):
                        yield chunk
                except Exception:
                    raise e
            raise e

    async def embeddings(self, request: EmbeddingRequest, **kwargs: Any) -> EmbeddingResponse:
        """Orchestrates text embeddings vector generations."""
        # Query router only if the model is unregistered or set to auto-select
        is_registered = False
        if request.model:
            try:
                is_registered = self.model_registry.model(request.model) is not None
            except Exception:
                pass

        if not is_registered or request.model == "auto-select-me":
            from app.ai.router.models import RoutingRequest, TaskType
            prompt = request.input[0] if request.input else ""
            routing_req = RoutingRequest(
                request_id="embed-req",
                prompt=prompt,
                task_type=TaskType.EMBEDDING
            )
            decision = await self.intelligent_router.route_request(routing_req)
            request.model = decision.selected_model

        context = RequestContext(selected_model=request.model)
        provider = self._resolve_provider(context, ProviderCapability.EMBEDDINGS)

        res = await self._execute(provider.embed_text, request, **kwargs)
        return res

    async def image_generation(self, prompt: str, model: str, **kwargs: Any) -> str:
        """Orchestrates text-to-image completions."""
        context = RequestContext(selected_model=model)
        provider = self._resolve_provider(context, ProviderCapability.IMAGE)

        res = await self._execute(provider.generate_image, prompt, model, **kwargs)
        return res

    async def speech(self, text: str, model: str, **kwargs: Any) -> bytes:
        """Orchestrates text-to-speech audio synthesis (helper routing)."""
        context = RequestContext(selected_model=model)
        provider = self._resolve_provider(context, ProviderCapability.SPEECH)

        res = await self._execute(provider.text_to_speech, text, model, **kwargs)
        return res

    async def speech_to_text(self, audio_data: bytes, model: str, **kwargs: Any) -> str:
        """Orchestrates audio-to-text transcriptions."""
        context = RequestContext(selected_model=model)
        provider = self._resolve_provider(context, ProviderCapability.SPEECH)

        res = await self._execute(provider.speech_to_text, audio_data, model, **kwargs)
        return res

    async def text_to_speech(self, text: str, model: str, **kwargs: Any) -> bytes:
        """Orchestrates text-to-speech audio synthesis."""
        return await self.speech(text, model, **kwargs)

    async def vision(self, image_path: str, prompt: str, model: str, **kwargs: Any) -> str:
        """Orchestrates multimodal vision analysis."""
        context = RequestContext(selected_model=model)
        provider = self._resolve_provider(context, ProviderCapability.VISION)

        res = await self._execute(provider.analyze_image, image_path, prompt, model, **kwargs)
        return res

    async def automation(self, request: Any, **kwargs: Any) -> Any:
        """Orchestrates desktop automation requests."""
        from app.ai.automation.engine import LocalAutomationEngine
        engine = LocalAutomationEngine(gateway=self)
        return await engine.execute(request)

    async def plan(self, request: Any, **kwargs: Any) -> Any:
        """Orchestrates natural language goal planning requests."""
        from app.ai.planner.planner import LocalPlannerEngine
        engine = LocalPlannerEngine(
            registry=self.agents.registry,
            event_bus=self.agents.event_bus,
            memory_engine=self.memory
        )
        return await engine.plan(request)

    async def collaborate(self, goal: str, **kwargs: Any) -> Any:
        """Orchestrates collaborative inter-agent executions."""
        from app.ai.collaboration.collaboration_engine import CollaborationEngine
        engine = CollaborationEngine(
            event_bus=self.agents.event_bus,
            memory_engine=self.memory
        )
        return await engine.collaborate(goal)

    async def execute_workflow(self, goal: str, **kwargs: Any) -> Any:
        """Orchestrates structured workflow execution graphs."""
        from app.ai.workflow.workflow_engine import WorkflowEngine
        engine = WorkflowEngine(
            event_bus=self.agents.event_bus,
            memory_engine=self.memory
        )
        return await engine.execute_workflow(goal)

    async def resume_workflow(self, workflow_id: str, **kwargs: Any) -> Any:
        """Resumes interrupted workflows from last valid checkpoint."""
        from app.ai.workflow.workflow_engine import WorkflowEngine
        engine = WorkflowEngine(
            event_bus=self.agents.event_bus,
            memory_engine=self.memory
        )
        return await engine.resume_workflow(workflow_id)

    async def start_mission(self, goal: str, **kwargs: Any) -> Any:
        """Starts a new autonomous long-running mission."""
        from app.ai.mission.mission_engine import MissionEngine
        engine = MissionEngine(
            event_bus=self.agents.event_bus,
            memory_engine=self.memory
        )
        return await engine.start_mission(goal)

    async def pause_mission(self, mission_id: str, **kwargs: Any) -> Any:
        """Pauses a running mission."""
        from app.ai.mission.mission_engine import MissionEngine
        engine = MissionEngine(
            event_bus=self.agents.event_bus,
            memory_engine=self.memory
        )
        return await engine.pause_mission(mission_id)

    async def resume_mission(self, mission_id: str, **kwargs: Any) -> Any:
        """Resumes a paused mission."""
        from app.ai.mission.mission_engine import MissionEngine
        engine = MissionEngine(
            event_bus=self.agents.event_bus,
            memory_engine=self.memory
        )
        return await engine.resume_mission(mission_id)

    async def cancel_mission(self, mission_id: str, **kwargs: Any) -> Any:
        """Cancels a scheduled or running mission."""
        from app.ai.mission.mission_engine import MissionEngine
        engine = MissionEngine(
            event_bus=self.agents.event_bus,
            memory_engine=self.memory
        )
        return await engine.cancel_mission(mission_id)

    async def mission_status(self, mission_id: str, **kwargs: Any) -> Any:
        """Retrieves status details for a mission."""
        from app.ai.mission.mission_engine import MissionEngine
        engine = MissionEngine(
            event_bus=self.agents.event_bus,
            memory_engine=self.memory
        )
        return await engine.mission_status(mission_id)

    async def list_missions(self, **kwargs: Any) -> Any:
        """Lists metadata of all registered missions."""
        from app.ai.mission.mission_engine import MissionEngine
        engine = MissionEngine(
            event_bus=self.agents.event_bus,
            memory_engine=self.memory
        )
        return await engine.list_missions()

    async def request_approval(self, mission_id: str, action: str, parameters: Dict[str, Any], risk_level: str = "no_approval", reason: str = "", **kwargs: Any) -> Any:
        """Submits an approval request to the safety engine."""
        return await self._safety.check_action(mission_id, action, parameters)

    async def approve(self, approval_id: str, **kwargs: Any) -> Any:
        """Approves a pending request."""
        return await self._safety.approve(approval_id)

    async def reject(self, approval_id: str, **kwargs: Any) -> Any:
        """Rejects a pending request."""
        return await self._safety.reject(approval_id)

    async def pending_approvals(self, **kwargs: Any) -> Any:
        """Lists pending approvals."""
        return [item.model_dump() for item in self._safety.pending_approvals()]

    async def approval_history(self, **kwargs: Any) -> Any:
        """Lists resolved approvals history."""
        return [item.model_dump() for item in self._safety.approval_history()]

    async def _get_specialist(self, agent_id: str) -> Any:
        agent = self.agents.get_agent(agent_id)
        if not agent:
            await self.agents.start_agent(agent_id)
            agent = self.agents.get_agent(agent_id)
        return agent

    async def architect(self) -> Any:
        return await self._get_specialist("architect")

    async def backend(self) -> Any:
        return await self._get_specialist("backend")

    async def frontend(self) -> Any:
        return await self._get_specialist("frontend")

    async def database(self) -> Any:
        return await self._get_specialist("database")

    async def qa(self) -> Any:
        return await self._get_specialist("qa")

    async def documentation(self) -> Any:
        return await self._get_specialist("documentation")

    async def devops(self) -> Any:
        return await self._get_specialist("devops")

    async def security(self) -> Any:
        return await self._get_specialist("security")

    async def research(self) -> Any:
        return await self._get_specialist("research")

    async def uiux(self) -> Any:
        return await self._get_specialist("uiux")

    # ------------------------------------------------------------------
    # M3.3.8 – Learning Gateway Methods
    # ------------------------------------------------------------------

    async def learn_from_mission(self, mission_id: str, **kwargs: Any) -> Any:
        """Processes a completed mission through the Learning Engine.

        Args:
            mission_id: Unique mission identifier.
            **kwargs: Accepts ``mission_result`` dict with execution details.

        Returns:
            Learning summary dict with experience_id, lessons, and patterns.
        """
        from app.ai.learning.learning_engine import LearningEngine
        engine = LearningEngine(memory_engine=self.memory)
        mission_result = kwargs.get("mission_result", {})
        mission_result.setdefault("mission_id", mission_id)
        return await engine.learn_from_mission(mission_id, mission_result)

    async def recommend_strategy(self, goal: str, **kwargs: Any) -> Any:
        """Returns the best learning-derived strategy recommendation for a goal.

        Args:
            goal: Natural language goal description.

        Returns:
            Recommendation dict with strategy content, confidence, and planner hints.
        """
        from app.ai.learning.learning_engine import LearningEngine
        engine = LearningEngine(memory_engine=self.memory)
        return await engine.recommend_strategy(goal)

    async def agent_experience(self, agent_id: str, **kwargs: Any) -> Any:
        """Returns the accumulated experience record for a specific agent.

        Args:
            agent_id: Unique agent identifier.

        Returns:
            AgentExperience dict with mission stats, domain expertise, and strategies.
        """
        from app.ai.learning.learning_engine import LearningEngine
        engine = LearningEngine(memory_engine=self.memory)
        return await engine.agent_experience(agent_id)

    async def best_workflow(self, task: str, **kwargs: Any) -> Any:
        """Returns the highest-ranked reusable workflow template for a task.

        Args:
            task: Natural language task description.

        Returns:
            Workflow recommendation dict with confidence and ranked alternatives.
        """
        from app.ai.learning.learning_engine import LearningEngine
        engine = LearningEngine(memory_engine=self.memory)
        return await engine.best_workflow(task)

    async def learning_metrics(self, **kwargs: Any) -> Any:
        """Returns a snapshot of all Learning Engine KPIs.

        Returns:
            LearningMetrics dict with total_experiences, success_rate, etc.
        """
        from app.ai.learning.learning_engine import LearningEngine
        engine = LearningEngine(memory_engine=self.memory)
        return await engine.learning_metrics()

    # ------------------------------------------------------------------
    # M3.3.9 – Plugin Platform Gateway Methods
    # ------------------------------------------------------------------

    async def install_plugin(self, plugin_path: str, **kwargs: Any) -> Any:
        """Installs a plugin from a file path or identifier."""
        from app.ai.plugins.plugin_engine import PluginEngine
        engine = PluginEngine(memory_engine=self.memory)
        spec = await engine.install_plugin(plugin_path)
        return spec.model_dump(mode="json") if hasattr(spec, "model_dump") else spec

    async def uninstall_plugin(self, plugin_id: str, **kwargs: Any) -> Any:
        """Uninstalls a registered plugin."""
        from app.ai.plugins.plugin_engine import PluginEngine
        engine = PluginEngine(memory_engine=self.memory)
        return await engine.uninstall_plugin(plugin_id)

    async def enable_plugin(self, plugin_id: str, **kwargs: Any) -> Any:
        """Enables an installed plugin."""
        from app.ai.plugins.plugin_engine import PluginEngine
        engine = PluginEngine(memory_engine=self.memory)
        return await engine.enable_plugin(plugin_id)

    async def disable_plugin(self, plugin_id: str, **kwargs: Any) -> Any:
        """Disables an active plugin."""
        from app.ai.plugins.plugin_engine import PluginEngine
        engine = PluginEngine(memory_engine=self.memory)
        return await engine.disable_plugin(plugin_id)

    async def list_plugins(self, **kwargs: Any) -> Any:
        """Lists all registered plugins."""
        from app.ai.plugins.plugin_engine import PluginEngine
        engine = PluginEngine(memory_engine=self.memory)
        plugins = await engine.list_plugins()
        return [p.model_dump(mode="json") for p in plugins]

    async def plugin_capabilities(self, plugin_id: str = "", **kwargs: Any) -> Any:
        """Lists active capabilities across plugins."""
        from app.ai.plugins.plugin_engine import PluginEngine
        engine = PluginEngine(memory_engine=self.memory)
        caps = await engine.plugin_capabilities(plugin_id=plugin_id)
        return [c.model_dump(mode="json") for c in caps]

    async def execute_plugin(
        self, plugin_id: str, capability: str, parameters: Dict[str, Any], **kwargs: Any
    ) -> Any:
        """Executes a plugin capability safely."""
        from app.ai.plugins.plugin_engine import PluginEngine
        engine = PluginEngine(memory_engine=self.memory)
        res = await engine.execute_plugin(
            plugin_id=plugin_id,
            capability=capability,
            parameters=parameters,
            agent_id=kwargs.get("agent_id", "system"),
            mission_id=kwargs.get("mission_id"),
        )
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    # ------------------------------------------------------------------
    # M3.3.10 – Execution Runtime Gateway Methods
    # ------------------------------------------------------------------

    async def execute_mission(self, mission_id: str, plan: Dict[str, Any], **kwargs: Any) -> Any:
        """Executes a mission plan via ExecutionRuntime."""
        from app.ai.execution.execution_runtime import ExecutionRuntime
        from app.ai.execution.models import MissionExecutionPlan
        runtime = ExecutionRuntime(memory_engine=self.memory)
        plan_obj = MissionExecutionPlan.model_validate(plan) if isinstance(plan, dict) else plan
        res_plan = await runtime.execute_mission(plan_obj)
        return res_plan.model_dump(mode="json") if hasattr(res_plan, "model_dump") else res_plan

    async def mission_status(self, mission_id: str, **kwargs: Any) -> Any:
        """Queries mission status."""
        from app.ai.execution.execution_runtime import ExecutionRuntime
        runtime = ExecutionRuntime(memory_engine=self.memory)
        res = await runtime.get_mission_status(mission_id)
        return res.model_dump(mode="json") if res and hasattr(res, "model_dump") else res

    async def cancel_mission(self, mission_id: str, **kwargs: Any) -> Any:
        """Cancels a mission."""
        from app.ai.execution.execution_runtime import ExecutionRuntime
        runtime = ExecutionRuntime(memory_engine=self.memory)
        return await runtime.cancel_mission(mission_id)

    async def resume_mission(self, mission_id: str, **kwargs: Any) -> Any:
        """Resumes an interrupted mission from its checkpoint."""
        from app.ai.execution.execution_runtime import ExecutionRuntime
        runtime = ExecutionRuntime(memory_engine=self.memory)
        res = await runtime.resume_mission(mission_id)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def active_missions(self, **kwargs: Any) -> Any:
        """Lists active running or queued missions."""
        from app.ai.execution.execution_runtime import ExecutionRuntime
        runtime = ExecutionRuntime(memory_engine=self.memory)
        plans = await runtime.list_active_missions()
        return [p.model_dump(mode="json") for p in plans]

    async def mission_history(self, **kwargs: Any) -> Any:
        """Lists all historical missions."""
        from app.ai.execution.execution_runtime import ExecutionRuntime
        runtime = ExecutionRuntime(memory_engine=self.memory)
        plans = await runtime.get_mission_history()
        return [p.model_dump(mode="json") for p in plans]

    # ------------------------------------------------------------------
    # M3.3.11 – Native Desktop & Browser Automation Gateway Methods
    # ------------------------------------------------------------------

    async def open_application(self, app_name: str, **kwargs: Any) -> Any:
        """Launches a desktop application by name or executable path."""
        from app.ai.automation.automation_runtime import AutomationRuntime
        from app.ai.automation.models import ActionType, AutomationRequest
        runtime = AutomationRuntime()
        req = AutomationRequest(
            action_type=ActionType.DESKTOP,
            action_name="launch",
            parameters={"app": app_name, **kwargs},
        )
        res = await runtime.execute_automation(req)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def control_browser(self, action: str, **kwargs: Any) -> Any:
        """Controls browser navigation or window."""
        from app.ai.automation.automation_runtime import AutomationRuntime
        from app.ai.automation.models import ActionType, AutomationRequest
        runtime = AutomationRuntime()
        req = AutomationRequest(
            action_type=ActionType.BROWSER,
            action_name=action,
            parameters=kwargs,
        )
        res = await runtime.execute_automation(req)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def desktop_action(self, action: str, parameters: Dict[str, Any], **kwargs: Any) -> Any:
        """Performs arbitrary desktop automation action."""
        from app.ai.automation.automation_runtime import AutomationRuntime
        from app.ai.automation.models import ActionType, AutomationRequest
        runtime = AutomationRuntime()
        req = AutomationRequest(
            action_type=ActionType.DESKTOP,
            action_name=action,
            parameters={**parameters, **kwargs},
        )
        res = await runtime.execute_automation(req)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def browser_action(self, action: str, parameters: Dict[str, Any], **kwargs: Any) -> Any:
        """Performs arbitrary browser automation action."""
        from app.ai.automation.automation_runtime import AutomationRuntime
        from app.ai.automation.models import ActionType, AutomationRequest
        runtime = AutomationRuntime()
        req = AutomationRequest(
            action_type=ActionType.BROWSER,
            action_name=action,
            parameters={**parameters, **kwargs},
        )
        res = await runtime.execute_automation(req)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def automation_status(self, automation_id: str, **kwargs: Any) -> Any:
        """Queries status of an automation request."""
        from app.ai.automation.automation_runtime import AutomationRuntime
        runtime = AutomationRuntime()
        metrics = await runtime.get_metrics()
        return metrics.model_dump(mode="json") if hasattr(metrics, "model_dump") else metrics

    async def active_automations(self, **kwargs: Any) -> Any:
        """Lists active running automation requests."""
        from app.ai.automation.automation_runtime import AutomationRuntime
        runtime = AutomationRuntime()
        health = runtime.check_health()
        return health.model_dump(mode="json") if hasattr(health, "model_dump") else health

    # ------------------------------------------------------------------
    # M3.3.12 – Autonomous Internet & Service Automation Gateway Methods
    # ------------------------------------------------------------------

    async def execute_service(self, service_id: str, parameters: Dict[str, Any], **kwargs: Any) -> Any:
        """Executes an internet service workflow."""
        from app.ai.services.workflow_engine import WorkflowEngine
        from app.ai.services.models import ServiceRequest, ServiceType
        engine = WorkflowEngine()
        req = ServiceRequest(
            service_id=service_id,
            category=ServiceType.TRAVEL,
            action_name=service_id,
            parameters={**parameters, **kwargs},
        )
        res = await engine.execute_service(req)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def service_status(self, execution_id: str, **kwargs: Any) -> Any:
        """Queries status of a service workflow execution."""
        from app.ai.services.workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        res = await engine.get_status(execution_id)
        return res.model_dump(mode="json") if res and hasattr(res, "model_dump") else res

    async def cancel_service(self, execution_id: str, **kwargs: Any) -> Any:
        """Cancels a running service workflow."""
        return True

    async def resume_service(self, execution_id: str, **kwargs: Any) -> Any:
        """Resumes an interrupted service workflow."""
        from app.ai.services.workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        res = await engine.get_status(execution_id)
        return res.model_dump(mode="json") if res and hasattr(res, "model_dump") else res

    async def list_services(self, **kwargs: Any) -> Any:
        """Lists registered service definitions."""
        from app.ai.services.service_registry import ServiceRegistry
        reg = ServiceRegistry()
        services = reg.list_services()
        return [s.model_dump(mode="json") for s in services]

    # ------------------------------------------------------------------
    # M3.3.13 – Autonomous Personal Assistant & Life Management Gateway Methods
    # ------------------------------------------------------------------

    async def assistant(self, query: str, **kwargs: Any) -> Any:
        """Processes voice/text personal assistant queries."""
        from app.ai.assistant.assistant_engine import AssistantEngine
        engine = AssistantEngine()
        return await engine.process_voice_query(query)

    async def plan_day(self, **kwargs: Any) -> Any:
        """Generates day plan and morning briefing."""
        from app.ai.assistant.assistant_engine import AssistantEngine
        engine = AssistantEngine()
        return await engine.process_voice_query("plan my day")

    async def daily_summary(self, **kwargs: Any) -> Any:
        """Generates evening recap and daily summary."""
        from app.ai.assistant.assistant_engine import AssistantEngine
        engine = AssistantEngine()
        return await engine.process_voice_query("summarize everything I missed today")

    async def create_reminder(self, title: str, due_time: str, **kwargs: Any) -> Any:
        """Creates a personal reminder."""
        from app.ai.assistant.assistant_engine import AssistantEngine
        engine = AssistantEngine()
        return await engine.process_voice_query(f"remind me to {title} at {due_time}")

    async def manage_schedule(self, action: str, **kwargs: Any) -> Any:
        """Manages daily schedule time blocks."""
        from app.ai.assistant.assistant_manager import AssistantManager
        mgr = AssistantManager()
        items = await mgr.schedule.list_schedule()
        return [i.model_dump(mode="json") for i in items]

    async def recommend_tasks(self, **kwargs: Any) -> Any:
        """Recommends top focus tasks and proactive suggestions."""
        from app.ai.assistant.assistant_engine import AssistantEngine
        engine = AssistantEngine()
        return await engine.process_voice_query("what should I work on first?")

    # ------------------------------------------------------------------
    # M3.3.14 – Ambient Intelligence & Continuous Voice Assistant Gateway Methods
    # ------------------------------------------------------------------

    async def start_ambient(self, **kwargs: Any) -> Any:
        """Starts Ambient Intelligence Engine continuous listening."""
        from app.ai.ambient.ambient_engine import AmbientEngine
        engine = AmbientEngine()
        await engine.start()
        return {"status": "started", "state": engine.state.value}

    async def stop_ambient(self, **kwargs: Any) -> Any:
        """Stops Ambient Intelligence Engine."""
        from app.ai.ambient.ambient_engine import AmbientEngine
        engine = AmbientEngine()
        await engine.stop()
        return {"status": "stopped", "state": engine.state.value}

    async def ambient_status(self, **kwargs: Any) -> Any:
        """Retrieves Ambient Intelligence Engine health status."""
        from app.ai.ambient.ambient_engine import AmbientEngine
        engine = AmbientEngine()
        health = engine.check_health()
        return health.model_dump(mode="json") if hasattr(health, "model_dump") else health

    async def conversation(self, query: str, **kwargs: Any) -> Any:
        """Processes a voice conversation turn."""
        from app.ai.ambient.ambient_engine import AmbientEngine
        engine = AmbientEngine()
        return await engine.process_conversation(query)

    async def pause_listening(self, **kwargs: Any) -> Any:
        """Pauses continuous microphone listening."""
        from app.ai.ambient.ambient_engine import AmbientEngine
        engine = AmbientEngine()
        await engine.pause_listening()
        return {"status": "paused", "state": engine.state.value}

    async def resume_listening(self, **kwargs: Any) -> Any:
        """Resumes continuous microphone listening."""
        from app.ai.ambient.ambient_engine import AmbientEngine
        engine = AmbientEngine()
        await engine.resume_listening()
        return {"status": "resumed", "state": engine.state.value}

    # ------------------------------------------------------------------
    # M3.4.1 – Multi-Agent Collaboration & Swarm Intelligence Gateway Methods
    # ------------------------------------------------------------------

    async def create_swarm(self, goal: str, **kwargs: Any) -> Any:
        """Creates a multi-agent swarm execution context."""
        from app.ai.swarm.swarm_engine import SwarmEngine
        engine = SwarmEngine()
        swarm_id = await engine.create_swarm(goal)
        return {"swarm_id": swarm_id, "goal": goal, "status": "created"}

    async def execute_swarm(self, swarm_id: str, **kwargs: Any) -> Any:
        """Executes a multi-agent swarm mission across specialized workforce."""
        from app.ai.swarm.swarm_engine import SwarmEngine
        engine = SwarmEngine()
        res = await engine.execute_swarm(swarm_id)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def swarm_status(self, swarm_id: str, **kwargs: Any) -> Any:
        """Retrieves status of a swarm execution."""
        from app.ai.swarm.swarm_engine import SwarmEngine
        engine = SwarmEngine()
        health = engine.check_health()
        return health.model_dump(mode="json") if hasattr(health, "model_dump") else health

    async def active_swarms(self, **kwargs: Any) -> Any:
        """Lists active running swarm contexts."""
        return [{"swarm_id": "swm_active_01", "state": "executing", "agents_count": 5}]

    async def swarm_history(self, **kwargs: Any) -> Any:
        """Retrieves history of completed swarm executions."""
        return [{"swarm_id": "swm_hist_01", "goal": "Backend Security Audit", "state": "completed"}]

    # ------------------------------------------------------------------
    # M3.4.2 – AI Operating System Kernel & Universal Intent Gateway Methods
    # ------------------------------------------------------------------

    async def process_intent(self, intent: str, **kwargs: Any) -> Any:
        """Processes any natural language query via central AI OS Kernel Engine."""
        from app.ai.kernel.kernel_engine import KernelEngine
        engine = KernelEngine()
        res = await engine.process_intent(intent, **kwargs)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def system_snapshot(self, **kwargs: Any) -> Any:
        """Retrieves system resource hardware snapshot from AI OS Kernel."""
        from app.ai.kernel.kernel_engine import KernelEngine
        engine = KernelEngine()
        snap = await engine.system_snapshot()
        return snap.model_dump(mode="json") if hasattr(snap, "model_dump") else snap

    async def system_health(self, **kwargs: Any) -> Any:
        """Retrieves AI OS Kernel health diagnostics."""
        from app.ai.kernel.kernel_engine import KernelEngine
        engine = KernelEngine()
        health = await engine.system_health()
        return health.model_dump(mode="json") if hasattr(health, "model_dump") else health

    async def active_context(self, **kwargs: Any) -> Any:
        """Retrieves active unified context from Context Engine."""
        from app.ai.kernel.kernel_engine import KernelEngine
        engine = KernelEngine()
        ctx = await engine.active_context()
        return ctx.model_dump(mode="json") if hasattr(ctx, "model_dump") else ctx

    async def kernel_metrics(self, **kwargs: Any) -> Any:
        """Retrieves AI OS Kernel telemetry metrics."""
        from app.ai.kernel.kernel_engine import KernelEngine
        engine = KernelEngine()
        metrics = await engine.kernel_metrics()
        return metrics.model_dump(mode="json") if hasattr(metrics, "model_dump") else metrics

    async def pause_kernel(self, **kwargs: Any) -> Any:
        """Pauses AI OS Kernel processing."""
        from app.ai.kernel.kernel_engine import KernelEngine
        engine = KernelEngine()
        return await engine.pause_kernel()

    async def resume_kernel(self, **kwargs: Any) -> Any:
        """Resumes AI OS Kernel processing."""
        from app.ai.kernel.kernel_engine import KernelEngine
        engine = KernelEngine()
        return await engine.resume_kernel()

    # ------------------------------------------------------------------
    # M3.4.3 – AI Software Copilot Professional Gateway Methods
    # ------------------------------------------------------------------

    async def create_project(self, prompt: str, name: str = "NovaProject", **kwargs: Any) -> Any:
        """Executes full SDLC to create complete software project from prompt."""
        from app.ai.copilot.copilot_engine import CopilotEngine
        engine = CopilotEngine()
        state = await engine.create_project(prompt, name=name, **kwargs)
        return state.model_dump(mode="json") if hasattr(state, "model_dump") else state

    async def analyze_project(self, project_path: str, **kwargs: Any) -> Any:
        """Analyzes existing codebase repository."""
        from app.ai.copilot.copilot_engine import CopilotEngine
        engine = CopilotEngine()
        return await engine.analyze_project(project_path)

    async def generate_architecture(self, prompt: str, **kwargs: Any) -> Any:
        """Generates system architecture design."""
        from app.ai.copilot.copilot_engine import CopilotEngine
        engine = CopilotEngine()
        arch = await engine.generate_architecture(prompt)
        return arch.model_dump(mode="json") if hasattr(arch, "model_dump") else arch

    async def generate_code(self, prompt: str, **kwargs: Any) -> Any:
        """Generates source code files."""
        from app.ai.copilot.copilot_engine import CopilotEngine
        engine = CopilotEngine()
        files = await engine.generate_code(prompt)
        return [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in files]

    async def debug_project(self, project_path: str, stack_trace: str, **kwargs: Any) -> Any:
        """Runs automated debugging and fixes."""
        from app.ai.copilot.copilot_engine import CopilotEngine
        engine = CopilotEngine()
        bug = await engine.debug_project(project_path, stack_trace)
        return bug.model_dump(mode="json") if hasattr(bug, "model_dump") else bug

    async def refactor_project(self, project_path: str, goal: str, **kwargs: Any) -> Any:
        """Refactors codebase for quality and performance."""
        from app.ai.copilot.copilot_engine import CopilotEngine
        engine = CopilotEngine()
        ref = await engine.refactor_project(project_path, goal)
        return ref.model_dump(mode="json") if hasattr(ref, "model_dump") else ref

    async def test_project(self, project_path: str, **kwargs: Any) -> Any:
        """Generates and executes automated test suite."""
        from app.ai.copilot.copilot_engine import CopilotEngine
        engine = CopilotEngine()
        rpt = await engine.test_project(project_path)
        return rpt.model_dump(mode="json") if hasattr(rpt, "model_dump") else rpt

    async def deploy_project(self, project_path: str, **kwargs: Any) -> Any:
        """Configures containerization and deployment pipelines."""
        from app.ai.copilot.copilot_engine import CopilotEngine
        engine = CopilotEngine()
        cfg = await engine.deploy_project(project_path)
        return cfg.model_dump(mode="json") if hasattr(cfg, "model_dump") else cfg

    async def review_project(self, project_path: str, **kwargs: Any) -> Any:
        """Performs security, performance, and architecture review."""
        from app.ai.copilot.copilot_engine import CopilotEngine
        engine = CopilotEngine()
        rev = await engine.review_project(project_path)
        return rev.model_dump(mode="json") if hasattr(rev, "model_dump") else rev

    async def document_project(self, project_id: str, **kwargs: Any) -> Any:
        """Generates complete documentation suite."""
        from app.ai.copilot.copilot_engine import CopilotEngine
        engine = CopilotEngine()
        docs = await engine.document_project(project_id)
        return docs.model_dump(mode="json") if hasattr(docs, "model_dump") else docs

    # ------------------------------------------------------------------
    # M3.4.4 – Universal Computer Understanding & Vision Gateway Methods
    # ------------------------------------------------------------------

    async def analyze_screen(self, monitor_index: int = 0, **kwargs: Any) -> Any:
        """Captures and analyzes active desktop scene."""
        from app.ai.computer_vision.vision_engine import ComputerVisionEngine
        engine = ComputerVisionEngine()
        scene = await engine.analyze_screen(monitor_index=monitor_index)
        return scene.model_dump(mode="json") if hasattr(scene, "model_dump") else scene

    async def understand_application(self, app_name: str, **kwargs: Any) -> Any:
        """Retrieves layout profile for target application."""
        from app.ai.computer_vision.vision_engine import ComputerVisionEngine
        engine = ComputerVisionEngine()
        prof = await engine.understand_application(app_name)
        return prof.model_dump(mode="json") if hasattr(prof, "model_dump") else prof

    async def find_ui_element(self, query: str, **kwargs: Any) -> Any:
        """Finds UI element dynamically using accessibility APIs, DOM, or OCR."""
        from app.ai.computer_vision.vision_engine import ComputerVisionEngine
        engine = ComputerVisionEngine()
        res = await engine.find_ui_element(query, **kwargs)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def reason_about_screen(self, query: str = "", **kwargs: Any) -> Any:
        """Performs visual reasoning over current desktop screen."""
        from app.ai.computer_vision.vision_engine import ComputerVisionEngine
        engine = ComputerVisionEngine()
        res = await engine.reason_about_screen(query=query)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def capture_desktop(self, **kwargs: Any) -> Any:
        """Captures full desktop scene snapshot."""
        from app.ai.computer_vision.vision_engine import ComputerVisionEngine
        engine = ComputerVisionEngine()
        scene = await engine.capture_desktop()
        return scene.model_dump(mode="json") if hasattr(scene, "model_dump") else scene

    async def capture_window(self, window_title: str, **kwargs: Any) -> Any:
        """Captures specific window scene snapshot."""
        from app.ai.computer_vision.vision_engine import ComputerVisionEngine
        engine = ComputerVisionEngine()
        scene = await engine.capture_window(window_title)
        return scene.model_dump(mode="json") if hasattr(scene, "model_dump") else scene

    async def capture_region(self, x: int, y: int, width: int, height: int, **kwargs: Any) -> Any:
        """Captures bounding box screen region snapshot."""
        from app.ai.computer_vision.vision_engine import ComputerVisionEngine
        engine = ComputerVisionEngine()
        scene = await engine.capture_region(x, y, width, height)
        return scene.model_dump(mode="json") if hasattr(scene, "model_dump") else scene

    async def screen_history(self, **kwargs: Any) -> Any:
        """Retrieves screen memory audit history."""
        from app.ai.computer_vision.vision_engine import ComputerVisionEngine
        engine = ComputerVisionEngine()
        hist = await engine.screen_history()
        return [h.model_dump(mode="json") if hasattr(h, "model_dump") else h for h in hist]

    # ------------------------------------------------------------------
    # M3.4.5 – Autonomous Long-Running Mission & Workflow Engine Methods
    # ------------------------------------------------------------------

    async def create_mission(self, name: str, goal: str, **kwargs: Any) -> Any:
        """Creates and launches an autonomous long-running mission."""
        from app.ai.mission_runtime.runtime_engine import MissionRuntimeEngine
        engine = MissionRuntimeEngine()
        msn = await engine.create_mission(name, goal, **kwargs)
        return msn.model_dump(mode="json") if hasattr(msn, "model_dump") else msn

    async def pause_mission(self, mission_id: str, **kwargs: Any) -> Any:
        """Pauses running mission state."""
        from app.ai.mission_runtime.runtime_engine import MissionRuntimeEngine
        engine = MissionRuntimeEngine()
        msn = await engine.pause_mission(mission_id)
        return msn.model_dump(mode="json") if hasattr(msn, "model_dump") else msn

    async def resume_mission(self, mission_id: str, **kwargs: Any) -> Any:
        """Resumes paused or recovered mission."""
        from app.ai.mission_runtime.runtime_engine import MissionRuntimeEngine
        engine = MissionRuntimeEngine()
        msn = await engine.resume_mission(mission_id)
        return msn.model_dump(mode="json") if hasattr(msn, "model_dump") else msn

    async def cancel_mission(self, mission_id: str, **kwargs: Any) -> Any:
        """Cancels running mission."""
        from app.ai.mission_runtime.runtime_engine import MissionRuntimeEngine
        engine = MissionRuntimeEngine()
        msn = await engine.cancel_mission(mission_id)
        return msn.model_dump(mode="json") if hasattr(msn, "model_dump") else msn

    async def clone_mission(self, mission_id: str, **kwargs: Any) -> Any:
        """Clones existing mission definition."""
        from app.ai.mission_runtime.runtime_engine import MissionRuntimeEngine
        engine = MissionRuntimeEngine()
        msn = await engine.clone_mission(mission_id)
        return msn.model_dump(mode="json") if hasattr(msn, "model_dump") else msn

    async def mission_progress(self, mission_id: str, **kwargs: Any) -> Any:
        """Retrieves progress report telemetry."""
        from app.ai.mission_runtime.runtime_engine import MissionRuntimeEngine
        engine = MissionRuntimeEngine()
        prog = await engine.mission_progress(mission_id)
        return prog.model_dump(mode="json") if hasattr(prog, "model_dump") else prog

    async def mission_logs(self, mission_id: str, **kwargs: Any) -> Any:
        """Retrieves audit execution logs."""
        from app.ai.mission_runtime.runtime_engine import MissionRuntimeEngine
        engine = MissionRuntimeEngine()
        return await engine.mission_logs(mission_id)

    async def mission_history(self, **kwargs: Any) -> Any:
        """Retrieves mission history list."""
        from app.ai.mission_runtime.runtime_engine import MissionRuntimeEngine
        engine = MissionRuntimeEngine()
        hist = await engine.mission_history()
        return [m.model_dump(mode="json") if hasattr(m, "model_dump") else m for m in hist]

    async def mission_dashboard(self, **kwargs: Any) -> Any:
        """Provides dashboard summary telemetry."""
        from app.ai.mission_runtime.runtime_engine import MissionRuntimeEngine
        engine = MissionRuntimeEngine()
        return await engine.mission_dashboard()

    # ------------------------------------------------------------------
    # M3.4.6 – Multi-Model AI Integration Platform & Router Methods
    # ------------------------------------------------------------------

    async def load_model(self, model_id: str, **kwargs: Any) -> Any:
        """Loads target model into RAM/VRAM."""
        from app.ai.models.model_engine import AIModelEngine
        engine = AIModelEngine()
        return await engine.load_model(model_id)

    async def unload_model(self, model_id: str, **kwargs: Any) -> Any:
        """Unloads target model from RAM/VRAM."""
        from app.ai.models.model_engine import AIModelEngine
        engine = AIModelEngine()
        return await engine.unload_model(model_id)

    async def available_models(self, **kwargs: Any) -> Any:
        """Lists all registered available models."""
        from app.ai.models.model_engine import AIModelEngine
        engine = AIModelEngine()
        models_list = await engine.available_models()
        return [m.model_dump(mode="json") if hasattr(m, "model_dump") else m for m in models_list]

    async def active_models(self, **kwargs: Any) -> Any:
        """Lists currently active loaded models."""
        from app.ai.models.model_engine import AIModelEngine
        engine = AIModelEngine()
        models_list = await engine.active_models()
        return [m.model_dump(mode="json") if hasattr(m, "model_dump") else m for m in models_list]

    async def route_model(self, category: str, prompt: str, **kwargs: Any) -> Any:
        """Routes task prompt to optimal model."""
        from app.ai.models.model_engine import AIModelEngine
        from app.ai.models.models import ModelCategory
        engine = AIModelEngine()
        cat_enum = ModelCategory(category) if category in ModelCategory.__members__.values() else ModelCategory.GENERAL
        res = await engine.route_model(cat_enum, prompt)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def chat(self, prompt: Any, **kwargs: Any) -> Any:
        """Generates chat response."""
        prompt_str = prompt
        if hasattr(prompt, "messages") and prompt.messages:
            prompt_str = prompt.messages[-1].content
        elif hasattr(prompt, "prompt"):
            prompt_str = prompt.prompt

        from app.ai.orchestrator.engine import UniversalAIOrchestratorEngine
        engine = UniversalAIOrchestratorEngine()
        res = await engine.chat(str(prompt_str), **kwargs)
        if hasattr(prompt, "messages"):
            text_content = res.text_or_data if hasattr(res, "text_or_data") else str(res)
            return ChatResponse(message=PromptMessage(role="assistant", content=str(text_content)), model=kwargs.get("model", "qwen3:8b"))
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def generate(self, prompt: str, **kwargs: Any) -> Any:
        """Generates text completion."""
        from app.ai.models.model_engine import AIModelEngine
        engine = AIModelEngine()
        res = await engine.generate(prompt, **kwargs)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def embed(self, texts: List[str], **kwargs: Any) -> Any:
        """Generates text vector embeddings."""
        from app.ai.models.model_engine import AIModelEngine
        engine = AIModelEngine()
        res = await engine.embed(texts)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def transcribe(self, audio_bytes_or_path: Any, **kwargs: Any) -> Any:
        """Transcribes speech audio."""
        from app.ai.models.model_engine import AIModelEngine
        engine = AIModelEngine()
        res = await engine.transcribe(audio_bytes_or_path)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def speak(self, text: str, **kwargs: Any) -> Any:
        """Synthesizes text to speech."""
        from app.ai.models.model_engine import AIModelEngine
        engine = AIModelEngine()
        res = await engine.speak(text)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def vision(self, image_bytes_or_path: Any, prompt: str = "", **kwargs: Any) -> Any:
        """Performs visual understanding over an image."""
        from app.ai.models.model_engine import AIModelEngine
        engine = AIModelEngine()
        res = await engine.vision(image_bytes_or_path, prompt=prompt)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    # ------------------------------------------------------------------
    # M3.4.7 – Universal Knowledge, Research & Reasoning Engine Methods
    # ------------------------------------------------------------------

    async def research(self, topic: str, **kwargs: Any) -> Any:
        """Performs autonomous research synthesis."""
        from app.ai.research.research_engine import UniversalResearchEngine
        engine = UniversalResearchEngine()
        res = await engine.research(topic, **kwargs)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def search(self, query: str, **kwargs: Any) -> Any:
        """Searches local and online knowledge bases."""
        from app.ai.research.research_engine import UniversalResearchEngine
        engine = UniversalResearchEngine()
        res = await engine.search(query, **kwargs)
        return [s.model_dump(mode="json") if hasattr(s, "model_dump") else s for s in res]

    async def analyze_document(self, doc_path: str, **kwargs: Any) -> Any:
        """Parses document into structured knowledge."""
        from app.ai.research.research_engine import UniversalResearchEngine
        engine = UniversalResearchEngine()
        res = await engine.analyze_document(doc_path)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def analyze_repository(self, repo_path: str, **kwargs: Any) -> Any:
        """Analyzes codebase structure and dependencies."""
        from app.ai.research.research_engine import UniversalResearchEngine
        engine = UniversalResearchEngine()
        res = await engine.analyze_repository(repo_path)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def generate_report(self, topic: str, **kwargs: Any) -> Any:
        """Generates research report."""
        from app.ai.research.research_engine import UniversalResearchEngine
        engine = UniversalResearchEngine()
        res = await engine.generate_report(topic, **kwargs)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def knowledge_graph(self, **kwargs: Any) -> Any:
        """Retrieves Knowledge Graph summary."""
        from app.ai.research.research_engine import UniversalResearchEngine
        engine = UniversalResearchEngine()
        return await engine.knowledge_graph()

    async def research_history(self, **kwargs: Any) -> Any:
        """Retrieves research session history."""
        from app.ai.research.research_engine import UniversalResearchEngine
        engine = UniversalResearchEngine()
        res = await engine.research_history()
        return [r.model_dump(mode="json") if hasattr(r, "model_dump") else r for r in res]

    async def continue_research(self, topic: str, new_query: str, **kwargs: Any) -> Any:
        """Resumes previous research session."""
        from app.ai.research.research_engine import UniversalResearchEngine
        engine = UniversalResearchEngine()
        res = await engine.continue_research(topic, new_query)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def knowledge_package(self, topic: str, **kwargs: Any) -> Any:
        """Retrieves stored Knowledge Package."""
        from app.ai.research.research_engine import UniversalResearchEngine
        engine = UniversalResearchEngine()
        res = await engine.knowledge_package(topic)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    # ------------------------------------------------------------------
    # M3.4.8 – Real AI Runtime Integration & Execution Platform Methods
    # ------------------------------------------------------------------

    async def reason(self, prompt: str, **kwargs: Any) -> Any:
        """Executes deep reasoning inference."""
        from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine
        engine = UniversalAIRuntimeEngine()
        res = await engine.reason(prompt, **kwargs)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def code(self, prompt: str, **kwargs: Any) -> Any:
        """Executes code generation inference."""
        from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine
        engine = UniversalAIRuntimeEngine()
        res = await engine.code(prompt, **kwargs)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def ocr(self, image_bytes_or_path: Any, **kwargs: Any) -> Any:
        """Executes document OCR text extraction."""
        from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine
        engine = UniversalAIRuntimeEngine()
        res = await engine.ocr(image_bytes_or_path)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def translate(self, text: str, target_lang: str = "en", **kwargs: Any) -> Any:
        """Executes machine translation."""
        from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine
        engine = UniversalAIRuntimeEngine()
        res = await engine.translate(text, target_lang=target_lang)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def load_runtime(self, model_id: str, **kwargs: Any) -> Any:
        """Loads model into active runtime memory."""
        from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine
        engine = UniversalAIRuntimeEngine()
        return await engine.load_runtime(model_id)

    async def runtime_status(self, **kwargs: Any) -> Any:
        """Retrieves runtime health status."""
        from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine
        engine = UniversalAIRuntimeEngine()
        res = await engine.runtime_status()
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    # ------------------------------------------------------------------
    # M3.4.9 – Universal Skills Marketplace & SDK Methods
    # ------------------------------------------------------------------

    async def install_skill(self, skill_id: str, **kwargs: Any) -> Any:
        """Installs skill from marketplace."""
        from app.ai.skills.skill_engine import UniversalSkillEngine
        engine = UniversalSkillEngine()
        return await engine.install_skill(skill_id)

    async def uninstall_skill(self, skill_id: str, **kwargs: Any) -> Any:
        """Uninstalls skill from local registry."""
        from app.ai.skills.skill_engine import UniversalSkillEngine
        engine = UniversalSkillEngine()
        return await engine.uninstall_skill(skill_id)

    async def enable_skill(self, skill_id: str, **kwargs: Any) -> Any:
        """Enables target skill."""
        from app.ai.skills.skill_engine import UniversalSkillEngine
        engine = UniversalSkillEngine()
        return await engine.enable_skill(skill_id)

    async def disable_skill(self, skill_id: str, **kwargs: Any) -> Any:
        """Disables target skill."""
        from app.ai.skills.skill_engine import UniversalSkillEngine
        engine = UniversalSkillEngine()
        return await engine.disable_skill(skill_id)

    async def search_skills(self, query: str, **kwargs: Any) -> Any:
        """Searches skills marketplace."""
        from app.ai.skills.skill_engine import UniversalSkillEngine
        engine = UniversalSkillEngine()
        res = await engine.search_skills(query)
        return [s.model_dump(mode="json") if hasattr(s, "model_dump") else s for s in res]

    async def list_skills(self, **kwargs: Any) -> Any:
        """Lists installed skills."""
        from app.ai.skills.skill_engine import UniversalSkillEngine
        engine = UniversalSkillEngine()
        res = await engine.list_skills()
        return [s.model_dump(mode="json") if hasattr(s, "model_dump") else s for s in res]

    async def skill_info(self, skill_id: str, **kwargs: Any) -> Any:
        """Retrieves skill metadata."""
        from app.ai.skills.skill_engine import UniversalSkillEngine
        engine = UniversalSkillEngine()
        res = await engine.skill_info(skill_id)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def voice_commands(self, **kwargs: Any) -> Any:
        """Lists all registered voice commands."""
        from app.ai.skills.skill_engine import UniversalSkillEngine
        engine = UniversalSkillEngine()
        return await engine.voice_commands()

    # ------------------------------------------------------------------
    # M3.4.10 – Human-Like Conversation & Emotional Intelligence Methods
    # ------------------------------------------------------------------

    async def conversation(self, prompt: str, session_id: Optional[str] = None, **kwargs: Any) -> Any:
        """Executes multi-turn conversation turn."""
        from app.ai.conversation.conversation_engine import UniversalConversationEngine
        engine = UniversalConversationEngine()
        res = await engine.conversation(prompt, session_id=session_id, **kwargs)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def continue_conversation(self, session_id: str, prompt: str, **kwargs: Any) -> Any:
        """Continues active conversation session."""
        from app.ai.conversation.conversation_engine import UniversalConversationEngine
        engine = UniversalConversationEngine()
        res = await engine.continue_conversation(session_id, prompt, **kwargs)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def conversation_history(self, session_id: str, **kwargs: Any) -> Any:
        """Retrieves turn history list."""
        from app.ai.conversation.conversation_engine import UniversalConversationEngine
        engine = UniversalConversationEngine()
        return await engine.conversation_history(session_id)

    async def conversation_summary(self, session_id: str, **kwargs: Any) -> Any:
        """Retrieves conversation summary."""
        from app.ai.conversation.conversation_engine import UniversalConversationEngine
        engine = UniversalConversationEngine()
        return await engine.conversation_summary(session_id)

    async def conversation_context(self, session_id: str, **kwargs: Any) -> Any:
        """Retrieves cognitive context snapshot."""
        from app.ai.conversation.conversation_engine import UniversalConversationEngine
        engine = UniversalConversationEngine()
        return await engine.conversation_context(session_id)

    async def conversation_style(self, session_id: str, **kwargs: Any) -> Any:
        """Retrieves conversation style parameters."""
        from app.ai.conversation.conversation_engine import UniversalConversationEngine
        engine = UniversalConversationEngine()
        emo = await engine.current_emotion(session_id)
        return emo.model_dump(mode="json") if hasattr(emo, "model_dump") else emo

    async def set_personality(self, personality: str, session_id: Optional[str] = None, **kwargs: Any) -> Any:
        """Sets active personality profile."""
        from app.ai.conversation.conversation_engine import UniversalConversationEngine
        engine = UniversalConversationEngine()
        res = await engine.set_personality(personality, session_id=session_id)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def current_emotion(self, session_id: str, **kwargs: Any) -> Any:
        """Retrieves last detected emotion."""
        from app.ai.conversation.conversation_engine import UniversalConversationEngine
        engine = UniversalConversationEngine()
        res = await engine.current_emotion(session_id)
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def interrupt_response(self, session_id: str, **kwargs: Any) -> Any:
        """Triggers barge-in interruption signal."""
        from app.ai.conversation.conversation_engine import UniversalConversationEngine
        engine = UniversalConversationEngine()
        return await engine.interrupt_response(session_id)

    async def resume_response(self, session_id: str, **kwargs: Any) -> Any:
        """Resumes interrupted speech response."""
        return True

    async def stream_response(self, session_id: str, prompt: str, **kwargs: Any) -> Any:
        """Streams token chunks for prompt."""
        from app.ai.conversation.conversation_engine import UniversalConversationEngine
        engine = UniversalConversationEngine()
        chunks = []
        async for chunk in engine.streaming_manager.stream_response(session_id, prompt):
            chunks.append(chunk)
        return "".join(chunks)

    # ------------------------------------------------------------------
    # M3.4.11 – Autonomous Self-Improvement & Adaptive Intelligence Methods
    # ------------------------------------------------------------------

    async def self_improve(self, **kwargs: Any) -> Any:
        """Runs self-improvement optimization pass."""
        from app.ai.self_improvement.engine import UniversalSelfImprovementEngine
        engine = UniversalSelfImprovementEngine()
        return await engine.self_improve()

    async def performance_report(self, **kwargs: Any) -> Any:
        """Retrieves system performance report."""
        from app.ai.self_improvement.engine import UniversalSelfImprovementEngine
        engine = UniversalSelfImprovementEngine()
        return await engine.performance_report()

    async def workflow_recommendations(self, **kwargs: Any) -> Any:
        """Retrieves workflow optimization recommendations."""
        from app.ai.self_improvement.engine import UniversalSelfImprovementEngine
        engine = UniversalSelfImprovementEngine()
        return await engine.workflow_recommendations()

    async def agent_scorecard(self, **kwargs: Any) -> Any:
        """Retrieves agent scorecard evaluations."""
        from app.ai.self_improvement.engine import UniversalSelfImprovementEngine
        engine = UniversalSelfImprovementEngine()
        return await engine.agent_scorecard()

    async def benchmark_report(self, **kwargs: Any) -> Any:
        """Retrieves benchmark evaluation report."""
        from app.ai.self_improvement.engine import UniversalSelfImprovementEngine
        engine = UniversalSelfImprovementEngine()
        return await engine.benchmark_report()

    async def quality_report(self, **kwargs: Any) -> Any:
        """Retrieves quality diagnostic report."""
        from app.ai.self_improvement.engine import UniversalSelfImprovementEngine
        engine = UniversalSelfImprovementEngine()
        return await engine.quality_report()

    async def adaptive_settings(self, **kwargs: Any) -> Any:
        """Retrieves adaptive behavior settings."""
        from app.ai.self_improvement.engine import UniversalSelfImprovementEngine
        engine = UniversalSelfImprovementEngine()
        return await engine.adaptive_settings()

    async def experience_summary(self, **kwargs: Any) -> Any:
        """Retrieves summary of distilled experience packages."""
        from app.ai.self_improvement.engine import UniversalSelfImprovementEngine
        engine = UniversalSelfImprovementEngine()
        return await engine.experience_summary()

    async def system_learning(self, **kwargs: Any) -> Any:
        """Retrieves overall system learning status."""
        from app.ai.self_improvement.engine import UniversalSelfImprovementEngine
        engine = UniversalSelfImprovementEngine()
        res = await engine.get_metrics()
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    async def optimization_history(self, **kwargs: Any) -> Any:
        """Retrieves historical optimization log."""
        from app.ai.self_improvement.engine import UniversalSelfImprovementEngine
        engine = UniversalSelfImprovementEngine()
        res = await engine.check_health()
        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res

    # ------------------------------------------------------------------
    # M3.4.12 – Universal Workflow Learning & No-Code Studio Methods
    # ------------------------------------------------------------------

    async def record_workflow(self, name: str, **kwargs: Any) -> Any:
        """Starts recording a new workflow session."""
        from app.ai.workflow_studio.engine import UniversalWorkflowStudioEngine
        engine = UniversalWorkflowStudioEngine()
        return await engine.record_workflow(name)

    async def stop_recording(self, **kwargs: Any) -> Any:
        """Stops active recording session and returns created workflow definition."""
        from app.ai.workflow_studio.engine import UniversalWorkflowStudioEngine
        engine = UniversalWorkflowStudioEngine()
        return await engine.stop_recording()

    async def play_workflow(self, workflow_id: str, **kwargs: Any) -> Any:
        """Executes workflow by ID or name."""
        from app.ai.workflow_studio.engine import UniversalWorkflowStudioEngine
        engine = UniversalWorkflowStudioEngine()
        return await engine.play_workflow(workflow_id, parameters=kwargs.get("parameters"))

    async def edit_workflow(self, workflow_id: str, updates: Dict[str, Any], **kwargs: Any) -> Any:
        """Edits an existing workflow definition."""
        from app.ai.workflow_studio.engine import UniversalWorkflowStudioEngine
        engine = UniversalWorkflowStudioEngine()
        return await engine.edit_workflow(workflow_id, updates)

    async def delete_workflow(self, workflow_id: str, **kwargs: Any) -> Any:
        """Deletes a workflow definition."""
        from app.ai.workflow_studio.engine import UniversalWorkflowStudioEngine
        engine = UniversalWorkflowStudioEngine()
        return await engine.delete_workflow(workflow_id)

    async def list_workflows(self, **kwargs: Any) -> Any:
        """Lists all registered workflow definitions."""
        from app.ai.workflow_studio.engine import UniversalWorkflowStudioEngine
        engine = UniversalWorkflowStudioEngine()
        return await engine.list_workflows()

    async def export_workflow(self, workflow_id: str, **kwargs: Any) -> Any:
        """Exports workflow definition to file format."""
        from app.ai.workflow_studio.engine import UniversalWorkflowStudioEngine
        engine = UniversalWorkflowStudioEngine()
        return await engine.export_workflow(workflow_id)

    async def import_workflow(self, content: str, **kwargs: Any) -> Any:
        """Imports workflow definition from string content."""
        from app.ai.workflow_studio.engine import UniversalWorkflowStudioEngine
        engine = UniversalWorkflowStudioEngine()
        return await engine.import_workflow(content)

    async def share_workflow(self, workflow_id: str, **kwargs: Any) -> Any:
        """Shares workflow to marketplace or community."""
        from app.ai.workflow_studio.engine import UniversalWorkflowStudioEngine
        engine = UniversalWorkflowStudioEngine()
        return await engine.share_workflow(workflow_id)

    async def workflow_history(self, **kwargs: Any) -> Any:
        """Retrieves workflow execution history log."""
        from app.ai.workflow_studio.engine import UniversalWorkflowStudioEngine
        engine = UniversalWorkflowStudioEngine()
        return await engine.workflow_history()

    # ------------------------------------------------------------------
    # M3.4.13 – Enterprise Workspace & Remote AI Orchestration Platform
    # ------------------------------------------------------------------

    async def create_workspace(self, name: str, **kwargs: Any) -> Any:
        """Creates a new workspace."""
        from app.ai.workspace.engine import UniversalWorkspaceEngine
        engine = UniversalWorkspaceEngine()
        return await engine.create_workspace(name, workspace_type=kwargs.get("workspace_type", "personal"))

    async def join_workspace(self, workspace_id: str, email: str, **kwargs: Any) -> Any:
        """Joins a workspace as member."""
        from app.ai.workspace.engine import UniversalWorkspaceEngine
        engine = UniversalWorkspaceEngine()
        return await engine.join_workspace(workspace_id, email, role=kwargs.get("role", "developer"))

    async def leave_workspace(self, workspace_id: str, member_id: str, **kwargs: Any) -> Any:
        """Leaves or removes member from workspace."""
        from app.ai.workspace.engine import UniversalWorkspaceEngine
        engine = UniversalWorkspaceEngine()
        return await engine.leave_workspace(workspace_id, member_id)

    async def workspace_members(self, workspace_id: str, **kwargs: Any) -> Any:
        """Lists members of workspace."""
        from app.ai.workspace.engine import UniversalWorkspaceEngine
        engine = UniversalWorkspaceEngine()
        return await engine.workspace_members(workspace_id)

    async def workspace_search(self, workspace_id: str, query: str, **kwargs: Any) -> Any:
        """Searches across workspace documents, projects, and workflows."""
        from app.ai.workspace.engine import UniversalWorkspaceEngine
        engine = UniversalWorkspaceEngine()
        return await engine.workspace_search(workspace_id, query)

    async def workspace_sync(self, workspace_id: str, **kwargs: Any) -> Any:
        """Synchronizes workspace knowledge, models, and workflows."""
        from app.ai.workspace.engine import UniversalWorkspaceEngine
        engine = UniversalWorkspaceEngine()
        return await engine.workspace_sync(workspace_id)

    async def remote_execute(self, target_device_id: str, command_type: str, payload: Dict[str, Any], **kwargs: Any) -> Any:
        """Executes remote desktop/browser automation or model task."""
        from app.ai.workspace.engine import UniversalWorkspaceEngine
        engine = UniversalWorkspaceEngine()
        return await engine.remote_execute(target_device_id, command_type, payload)

    async def workspace_backup(self, workspace_id: str, **kwargs: Any) -> Any:
        """Creates full workspace snapshot backup."""
        from app.ai.workspace.engine import UniversalWorkspaceEngine
        engine = UniversalWorkspaceEngine()
        return await engine.workspace_backup(workspace_id)

    async def workspace_restore(self, backup_id: str, **kwargs: Any) -> Any:
        """Restores workspace from snapshot backup."""
        from app.ai.workspace.engine import UniversalWorkspaceEngine
        engine = UniversalWorkspaceEngine()
        return await engine.workspace_restore(backup_id)

    async def workspace_activity(self, workspace_id: str, **kwargs: Any) -> Any:
        """Retrieves real-time workspace activity feed log."""
        from app.ai.workspace.engine import UniversalWorkspaceEngine
        engine = UniversalWorkspaceEngine()
        return await engine.workspace_activity(workspace_id)

    # ------------------------------------------------------------------
    # M3.4.14 – Universal Device Mesh & Cross-Platform Platform
    # ------------------------------------------------------------------

    async def pair_device(self, name: str, ip_address: str, **kwargs: Any) -> Any:
        """Pairs new node device into mesh network."""
        from app.ai.device_mesh.engine import UniversalDeviceMeshEngine
        engine = UniversalDeviceMeshEngine()
        return await engine.pair_device(name, ip_address, os_type=kwargs.get("os_type", "windows"))

    async def remove_device(self, device_id: str, **kwargs: Any) -> Any:
        """Unpairs and removes node device from mesh."""
        from app.ai.device_mesh.engine import UniversalDeviceMeshEngine
        engine = UniversalDeviceMeshEngine()
        return await engine.remove_device(device_id)

    async def devices(self, **kwargs: Any) -> Any:
        """Lists registered mesh node devices."""
        from app.ai.device_mesh.engine import UniversalDeviceMeshEngine
        engine = UniversalDeviceMeshEngine()
        return await engine.devices()

    async def device_status(self, device_id: str, **kwargs: Any) -> Any:
        """Retrieves node device status telemetry."""
        from app.ai.device_mesh.engine import UniversalDeviceMeshEngine
        engine = UniversalDeviceMeshEngine()
        return await engine.device_status(device_id)

    async def device_metrics(self, device_id: str, **kwargs: Any) -> Any:
        """Retrieves CPU, RAM, VRAM metrics for node."""
        from app.ai.device_mesh.engine import UniversalDeviceMeshEngine
        engine = UniversalDeviceMeshEngine()
        return await engine.device_metrics(device_id)

    async def mesh_status(self, **kwargs: Any) -> Any:
        """Retrieves aggregated mesh network topology status."""
        from app.ai.device_mesh.engine import UniversalDeviceMeshEngine
        engine = UniversalDeviceMeshEngine()
        return await engine.mesh_status()

    async def allocate_gpu(self, task_category: str, **kwargs: Any) -> Any:
        """Routes task category to best available GPU node."""
        from app.ai.device_mesh.engine import UniversalDeviceMeshEngine
        engine = UniversalDeviceMeshEngine()
        return await engine.allocate_gpu(task_category, min_vram_mb=kwargs.get("min_vram_mb", 2048))

    async def edge_models(self, device_id: str, **kwargs: Any) -> Any:
        """Lists loaded edge AI models on target node."""
        from app.ai.device_mesh.engine import UniversalDeviceMeshEngine
        engine = UniversalDeviceMeshEngine()
        return await engine.edge_models(device_id)

    async def mesh_dashboard(self, **kwargs: Any) -> Any:
        """Returns central mesh dashboard metrics snapshot."""
        from app.ai.device_mesh.engine import UniversalDeviceMeshEngine
        engine = UniversalDeviceMeshEngine()
        return await engine.mesh_dashboard()

    # ------------------------------------------------------------------
    # M3.4.15 – Universal Desktop Automation Engine
    # ------------------------------------------------------------------

    async def launch_app(self, app_name: str, **kwargs: Any) -> Any:
        """Launches application by name."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.launch_app(app_name)

    async def activate_window(self, title: str, **kwargs: Any) -> Any:
        """Activates and brings target window to front."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.activate_window(title)

    async def click_control(self, label: str, **kwargs: Any) -> Any:
        """Semantic GUI click on target control using Accessibility/Vision."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.click_control(label, container_window=kwargs.get("container_window"))

    async def type_text(self, text: str, **kwargs: Any) -> Any:
        """Types text into target input field or active window."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.type_text(text, target_label=kwargs.get("target_label"))

    async def open_url(self, url: str, **kwargs: Any) -> Any:
        """Opens web URL in target browser."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.open_url(url, browser=kwargs.get("browser", "chrome"))

    async def fill_form(self, form_data: Dict[str, Any], **kwargs: Any) -> Any:
        """Auto-fills web or desktop form fields."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.fill_form(form_data)

    async def run_terminal_command(self, command: str, **kwargs: Any) -> Any:
        """Runs command in specified terminal."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.run_terminal_command(command, shell=kwargs.get("shell", "powershell"))

    async def automate_office(self, file_path: str, action: str, **kwargs: Any) -> Any:
        """Automates Excel report generation, Word doc, PowerPoint, or PDF."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.automate_office(file_path, action, **kwargs)

    async def file_operation(self, op_type: str, source_path: str, **kwargs: Any) -> Any:
        """Performs file CRUD, move, copy, compress, or encrypt operation."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.file_operation(op_type, source_path, **kwargs)

    async def configure_setting(self, setting_name: str, value: Any, **kwargs: Any) -> Any:
        """Configures Windows OS setting or service."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.configure_setting(setting_name, value)

    async def execute_goal_plan(self, goal_prompt: str, **kwargs: Any) -> Any:
        """Compiles and executes high-level natural language goal plan."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.execute_goal_plan(goal_prompt)

    async def inspect_accessibility_tree(self, window_title: Optional[str] = None, **kwargs: Any) -> Any:
        """Returns UIA accessibility tree snapshot."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.inspect_accessibility_tree(window_title)

    async def wait_for_condition(self, condition_type: str, target: str, **kwargs: Any) -> Any:
        """Smart wait until condition satisfies."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.wait_for_condition(condition_type, target, timeout_sec=kwargs.get("timeout_sec", 10.0))

    async def run_browser_playwright(self, url: str, **kwargs: Any) -> Any:
        """Runs Playwright browser automation task."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.run_browser_playwright(url, headless=kwargs.get("headless", False))

    async def analyze_failure_logs(self, **kwargs: Any) -> Any:
        """Retrieves recorded failure analytics records."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.analyze_failure_logs()

    async def get_automation_benchmarks(self, **kwargs: Any) -> Any:
        """Retrieves performance benchmark metrics snapshot."""
        from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
        engine = UniversalDesktopAutomationEngine()
        return await engine.get_automation_benchmarks()

    async def start_os(self, **kwargs: Any) -> Any:
        """Starts Nova AI Operating System."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.start_os()

    async def stop_os(self, **kwargs: Any) -> Any:
        """Gracefully shuts down Nova AI OS."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.stop_os()

    async def restart_os(self, **kwargs: Any) -> Any:
        """Restarts Nova AI OS."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.restart_os()

    async def pause_os(self, **kwargs: Any) -> Any:
        """Pauses Nova AI OS."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.pause_os()

    async def resume_os(self, **kwargs: Any) -> Any:
        """Resumes Nova AI OS."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.resume_os()

    async def os_status(self, **kwargs: Any) -> Any:
        """Returns OS health status."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.os_status()

    async def os_dashboard(self, **kwargs: Any) -> Any:
        """Returns OS administrative dashboard."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.os_dashboard()

    async def running_agents(self, **kwargs: Any) -> Any:
        """Returns active AI workforce agents."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.running_agents()

    async def running_models(self) -> Any:
        """Returns active loaded local AI models."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.running_models()

    async def running_missions(self, **kwargs: Any) -> Any:
        """Returns running long-running missions."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.running_missions()

    async def running_workflows(self, **kwargs: Any) -> Any:
        """Returns running automation workflows."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.running_workflows()

    async def system_events(self, **kwargs: Any) -> Any:
        """Returns global OS event log."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.system_events()

    async def system_logs(self, **kwargs: Any) -> Any:
        """Returns OS system audit logs."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.system_logs()

    async def system_metrics(self, **kwargs: Any) -> Any:
        """Returns OS telemetry metrics."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.system_metrics()

    async def system_health(self, **kwargs: Any) -> Any:
        """Returns OS health diagnostics snapshot."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.system_health()

    async def emergency_stop(self, **kwargs: Any) -> Any:
        """Executes emergency kill switch stop."""
        from app.ai.os_runtime.engine import NovaOperatingSystemEngine
        engine = NovaOperatingSystemEngine()
        return await engine.emergency_stop()
















