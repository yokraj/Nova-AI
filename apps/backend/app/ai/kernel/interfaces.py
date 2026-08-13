"""Abstract base interfaces and contracts for AI OS Kernel components.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from app.ai.kernel.models import (
    CapabilityMatch,
    EventRecord,
    ExecutionContext,
    ExecutionPlan,
    IntentRequest,
    IntentResponse,
    KernelHealth,
    KernelMetrics,
    OSMemoryState,
    SystemSnapshot,
    VerificationResult,
)


class IIntentEngine(ABC):
    """Universal Intent Engine contract converting natural language into structured goals."""

    @abstractmethod
    async def parse_intent(self, request: IntentRequest) -> Dict[str, Any]:
        """Parses an IntentRequest into a structured goal definition."""
        pass


class ICapabilityResolver(ABC):
    """Capability Resolver contract determining system requirements."""

    @abstractmethod
    async def resolve_capabilities(self, goal_data: Dict[str, Any]) -> CapabilityMatch:
        """Determines required agents, plugins, services, actions, memory, and models."""
        pass


class IDynamicPlanner(ABC):
    """Dynamic Planner contract generating DAG execution plans."""

    @abstractmethod
    async def generate_plan(self, goal_data: Dict[str, Any], capabilities: CapabilityMatch) -> ExecutionPlan:
        """Generates an execution plan with parallel waves and dependencies."""
        pass


class IResourceManager(ABC):
    """System Resource Manager contract monitoring hardware and runtime stats."""

    @abstractmethod
    async def capture_snapshot(self) -> SystemSnapshot:
        """Captures CPU, RAM, GPU, Disk, Battery, Network, and model status snapshot."""
        pass

    @abstractmethod
    def has_sufficient_resources(self, required_ram_mb: float = 100.0) -> bool:
        """Checks if hardware resources are sufficient for task execution."""
        pass


class IContextEngine(ABC):
    """Context Engine contract managing unified OS context."""

    @abstractmethod
    async def get_unified_context(self, session_id: str = "sess_default") -> ExecutionContext:
        """Merges conversation, memory, desktop context, browser, app, clipboard, and mission into one context."""
        pass

    @abstractmethod
    async def update_context(self, updates: Dict[str, Any]) -> ExecutionContext:
        """Updates active unified context."""
        pass


class IRuntimeCoordinator(ABC):
    """Runtime Coordinator contract executing steps across all 16 AI subsystems."""

    @abstractmethod
    async def execute_plan(self, plan: ExecutionPlan, context: ExecutionContext) -> Dict[str, Any]:
        """Coordinates multi-subsystem execution of an ExecutionPlan."""
        pass


class IUniversalVerifier(ABC):
    """Universal Verifier contract ensuring post-execution condition compliance."""

    @abstractmethod
    async def verify_execution(self, step_title: str, check_spec: Optional[str], result_data: Dict[str, Any]) -> VerificationResult:
        """Verifies post-execution side effects and state."""
        pass


class IEventBus(ABC):
    """Central Event Bus contract for kernel event broadcasting."""

    @abstractmethod
    async def publish(self, event_type: str, payload: Dict[str, Any], source: str = "kernel") -> EventRecord:
        """Publishes an event to subscriber callbacks."""
        pass

    @abstractmethod
    def subscribe(self, event_type: str, callback: Callable[[EventRecord], Any]) -> None:
        """Subscribes callback to specified event_type."""
        pass


class IOSMemory(ABC):
    """OS Memory contract managing active tasks, reasoning scratchpad, and execution stack."""

    @abstractmethod
    async def record_action(self, action_type: str, details: Dict[str, Any]) -> None:
        """Records an action into audit trail memory."""
        pass

    @abstractmethod
    async def get_state(self) -> OSMemoryState:
        """Returns snapshot of current OS memory state."""
        pass


class ICopilotIntegration(ABC):
    """Software Copilot Integration contract."""

    @abstractmethod
    async def handle_code_task(self, prompt: str, project_path: Optional[str] = None) -> Dict[str, Any]:
        """Integrates software engineer agent, code memory, project memory, and developer tools."""
        pass


class IVoiceOrchestrator(ABC):
    """Voice-First Orchestrator contract."""

    @abstractmethod
    async def process_voice_workflow(self, audio_or_text: str) -> IntentResponse:
        """Runs Wake Word -> Intent -> Plan -> Execute -> Verify -> Natural Voice Response."""
        pass


class ISecurityGuard(ABC):
    """Security Guard contract enforcing approval checkpoints."""

    @abstractmethod
    def check_approval_required(self, action_type: str, parameters: Dict[str, Any]) -> bool:
        """Determines if action requires user approval (payments, file delete, install, settings, emails)."""
        pass


class IKernelManager(ABC):
    """Kernel Manager administrative contract."""

    @abstractmethod
    async def start(self) -> None:
        """Starts kernel components and event loop."""
        pass

    @abstractmethod
    async def pause(self) -> None:
        """Pauses kernel processing."""
        pass

    @abstractmethod
    async def resume(self) -> None:
        """Resumes kernel processing."""
        pass


class IKernelEngine(ABC):
    """Central AI OS Kernel Engine facade contract."""

    @abstractmethod
    async def process_intent(self, query_or_request: Any, **kwargs: Any) -> IntentResponse:
        """Main entry point processing any natural language intent."""
        pass

    @abstractmethod
    async def system_snapshot(self) -> SystemSnapshot:
        """Retrieves system resource snapshot."""
        pass

    @abstractmethod
    async def system_health(self) -> KernelHealth:
        """Retrieves overall kernel health metrics."""
        pass

    @abstractmethod
    async def active_context(self) -> ExecutionContext:
        """Retrieves current unified operating context."""
        pass

    @abstractmethod
    async def kernel_metrics(self) -> KernelMetrics:
        """Retrieves kernel telemetry metrics."""
        pass

