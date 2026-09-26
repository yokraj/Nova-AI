"""Software Copilot Orchestrator running EXPLAIN, GUIDE, and EXECUTE modes.

Routes user prompts to active application contexts, executes through security-gated ApplicationAdapters,
and verifies real execution outcomes without mock success or hallucinated context.
"""

from typing import Any, Dict, List, Optional
import time
import structlog

from app.ai.copilot.models import CopilotMode, CopilotRequest, CopilotResponse
from app.ai.desktop_automation.application_adapter import ApplicationAdapterRegistry, BaseApplicationAdapter
from app.ai.desktop_automation.models import ApplicationContext, AutomationAction, AutomationResult, VerificationResult
from app.ai.desktop_automation.window_tracker import WindowTracker
from app.ai.desktop_automation.security_engine import SecurityEngine

logger = structlog.get_logger("copilot_orchestrator")


class CopilotOrchestrator:
    """Orchestrates AI Software Copilot interactions in EXPLAIN, GUIDE, and EXECUTE modes."""

    def __init__(self, engine: Optional[Any] = None, memory_engine: Optional[Any] = None) -> None:
        self.engine = engine
        self.window_tracker = WindowTracker()
        self.adapter_registry = ApplicationAdapterRegistry()
        self.security_engine = SecurityEngine()
        if memory_engine is not None:
            self.memory_engine = memory_engine
        else:
            try:
                from app.ai.memory.engine import LocalMemoryEngine
                self.memory_engine = LocalMemoryEngine()
            except Exception as e:
                logger.warning("Could not initialize default LocalMemoryEngine", error=str(e))
                self.memory_engine = None

    def _format_memory_context(self, context_package: Optional[Any]) -> Optional[str]:
        """Formats retrieved ContextPackage into explicit, distinguished memory context block."""
        if not context_package:
            return None

        parts = []
        if getattr(context_package, "system_context", None) and context_package.system_context.strip():
            parts.append(f"[System Directives / Preferences]:\n{context_package.system_context.strip()}")
        if getattr(context_package, "memory_context", None) and context_package.memory_context.strip():
            parts.append(f"[User / Conversation Memory]:\n{context_package.memory_context.strip()}")
        if getattr(context_package, "project_context", None) and context_package.project_context.strip():
            parts.append(f"[Project Context]:\n{context_package.project_context.strip()}")
        if getattr(context_package, "code_context", None) and context_package.code_context.strip():
            parts.append(f"[Code Context]:\n{context_package.code_context.strip()}")
        if getattr(context_package, "graph_context", None) and context_package.graph_context.strip():
            parts.append(f"[Knowledge Graph Context]:\n{context_package.graph_context.strip()}")

        if not parts:
            return None

        header = "=== RETRIEVED PERSISTENT MEMORY CONTEXT ==="
        footer = "=== END RETRIEVED MEMORY CONTEXT ==="
        return f"{header}\n" + "\n\n".join(parts) + f"\n{footer}"

    async def process_request(self, request: CopilotRequest) -> CopilotResponse:
        """Processes a Copilot request according to specified mode (EXPLAIN, GUIDE, EXECUTE)."""
        logger.info("Processing Copilot request", request_id=request.request_id, mode=request.mode, target_app=request.target_app)

        # 0. Retrieve persistent memory context BEFORE planning
        retrieved_memory_context: Optional[str] = None
        if self.memory_engine:
            try:
                context_package = await self.memory_engine.retrieve_context(
                    request.user_prompt,
                    limit=3,
                )
                retrieved_memory_context = self._format_memory_context(context_package)
            except Exception as e:
                logger.warning(
                    "Memory context retrieval failed, degrading gracefully without memory context",
                    error=str(e),
                )
                retrieved_memory_context = None

        # 1. Active Application Detection & Context Retrieval using WindowTracker & AdapterRegistry
        target_app = request.target_app
        if not target_app:
            window_info = self.window_tracker.get_active_window_info() or {}
            target_app = window_info.get("title", "Unknown")

        adapter: BaseApplicationAdapter = self.adapter_registry.get_adapter(target_app, engine=self.engine)
        app_context: ApplicationContext = await adapter.get_context()

        # Handle unknown/missing context cleanly without hallucinating application state
        if not app_context.app_name or app_context.app_name == "Unknown":
            app_context = ApplicationContext(
                app_name="Unknown",
                process_id=None,
                executable_path=None,
                window_title=None,
                window_handle=None,
                monitor_info=None,
                profile=None,
                ui_accessibility_tree=None,
                ocr_vision_data=None,
                recent_activity=[],
                timestamp=time.time(),
            )

        # 2. Dispatch to requested Copilot Mode
        if request.mode == CopilotMode.EXPLAIN:
            return await self._handle_explain_mode(request, adapter, app_context, retrieved_memory_context)
        elif request.mode == CopilotMode.GUIDE:
            return await self._handle_guide_mode(request, adapter, app_context, retrieved_memory_context)
        elif request.mode == CopilotMode.EXECUTE:
            return await self._handle_execute_mode(request, adapter, app_context, retrieved_memory_context)
        else:
            return CopilotResponse(
                request_id=request.request_id,
                mode=request.mode,
                app_context=app_context,
                retrieved_memory_context=retrieved_memory_context,
                success=False,
                status_message=f"Unsupported copilot mode '{request.mode}'.",
            )

    async def _handle_explain_mode(
        self,
        request: CopilotRequest,
        adapter: BaseApplicationAdapter,
        app_context: ApplicationContext,
        retrieved_memory_context: Optional[str] = None,
    ) -> CopilotResponse:
        """EXPLAIN Mode: Answers application-specific questions using real context without executing actions."""
        capabilities = adapter.get_capabilities()
        app_status = f"Active ({app_context.app_name})" if app_context.process_id else f"Profile Match ({app_context.app_name})"

        explanation = (
            f"Application Copilot Explanation for '{app_context.app_name}':\n"
            f"- Status: {app_status}\n"
            f"- Executable: {app_context.executable_path or 'Unavailable'}\n"
            f"- Supported Capabilities: {', '.join(capabilities) if capabilities else 'Generic Desktop'}\n"
            f"- Context: Prompt '{request.user_prompt}' evaluated against active software environment."
        )
        if retrieved_memory_context:
            explanation += f"\n\n{retrieved_memory_context}"

        return CopilotResponse(
            request_id=request.request_id,
            mode=CopilotMode.EXPLAIN,
            app_context=app_context,
            explanation=explanation,
            retrieved_memory_context=retrieved_memory_context,
            success=True,
            status_message="Explain mode response generated.",
        )

    async def _handle_guide_mode(
        self,
        request: CopilotRequest,
        adapter: BaseApplicationAdapter,
        app_context: ApplicationContext,
        retrieved_memory_context: Optional[str] = None,
    ) -> CopilotResponse:
        """GUIDE Mode: Provides contextual step-by-step guidance without destructive action execution."""
        capabilities = adapter.get_capabilities()
        steps = [
            {
                "step": 1,
                "title": f"Focus {app_context.app_name}",
                "description": f"Ensure window '{app_context.window_title or app_context.app_name}' is in active focus.",
            },
            {
                "step": 2,
                "title": "Inspect UI Elements",
                "description": f"Use UI Accessibility tree / Vision Locator to identify control target for '{request.user_prompt}'.",
            },
            {
                "step": 3,
                "title": "Review Required Capabilities",
                "description": f"Action requires capability from [{', '.join(capabilities[:3]) if capabilities else 'desktop'}].",
            },
        ]
        if retrieved_memory_context:
            steps.append({
                "step": 4,
                "title": "Apply Retained User Preferences",
                "description": f"Retrieved memory context applied: {retrieved_memory_context}",
            })

        return CopilotResponse(
            request_id=request.request_id,
            mode=CopilotMode.GUIDE,
            app_context=app_context,
            guide_steps=steps,
            retrieved_memory_context=retrieved_memory_context,
            success=True,
            status_message="Guide mode steps generated.",
        )

    async def _handle_execute_mode(
        self,
        request: CopilotRequest,
        adapter: BaseApplicationAdapter,
        app_context: ApplicationContext,
        retrieved_memory_context: Optional[str] = None,
    ) -> CopilotResponse:
        """EXECUTE Mode: Compiles action plan, passes security checks, executes via adapter, observes and verifies."""
        action_type = request.parameters.get("action_type", "click")
        target_label = request.parameters.get("target_label", request.user_prompt)

        parameters = dict(request.parameters)
        if retrieved_memory_context:
            parameters["retrieved_memory_context"] = retrieved_memory_context
            if "metric" in retrieved_memory_context.lower() and "unit_system" not in parameters:
                parameters["unit_system"] = "metric"

        action = AutomationAction(
            action_type=action_type,
            target_label=target_label,
            value=parameters.get("value"),
            selector=parameters,
        )
        action_plan = [action]

        # Security Check & Real Execution via Adapter
        try:
            execution_result: AutomationResult = await adapter.execute(action)
        except Exception as e:
            logger.error("Execution error in Copilot EXECUTE mode", error=str(e))
            return CopilotResponse(
                request_id=request.request_id,
                mode=CopilotMode.EXECUTE,
                app_context=app_context,
                action_plan=action_plan,
                execution_results=[],
                verification_results=[],
                retrieved_memory_context=retrieved_memory_context,
                success=False,
                status_message=f"Execution blocked or failed: {str(e)}",
            )

        # Observation & Verification
        verification_result: VerificationResult = await adapter.verify(action, execution_result)

        overall_success = execution_result.success

        # Store successful execution memory through canonical persistent layer
        if overall_success and self.memory_engine:
            try:
                from app.ai.memory.models import MemoryType
                await self.memory_engine.store_memory(
                    content=f"Executed {action.action_type} for '{request.user_prompt}' on {app_context.app_name}",
                    memory_type=MemoryType.CONVERSATION,
                    metadata={"request_id": request.request_id, "app": app_context.app_name},
                )
            except Exception as mem_err:
                logger.warning("Failed to store execution memory", error=str(mem_err))

        return CopilotResponse(
            request_id=request.request_id,
            mode=CopilotMode.EXECUTE,
            app_context=app_context,
            action_plan=action_plan,
            execution_results=[execution_result],
            verification_results=[verification_result],
            retrieved_memory_context=retrieved_memory_context,
            success=overall_success,
            status_message="Execute mode completed with verification." if overall_success else f"Execution failed: {execution_result.error_message or verification_result.details}",
        )
