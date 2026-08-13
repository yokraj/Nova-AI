"""AI Gateway abstractions, policies, registries, and core orchestrator.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator

from app.ai.models import (
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderCapability,
    StreamingChunk,
)

# Legacy Service
from app.ai.gateway.service import AiGatewayService

# Interfaces
class IProviderFactory(ABC):
    """Abstract interface for constructing and validating AI providers."""

    @abstractmethod
    def create_provider(self, name: str, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def validate_provider(self, provider: Any, capability: ProviderCapability) -> bool:
        pass


class IAIGateway(ABC):
    """Abstract interface contract for central AI Gateway operations."""

    @property
    @abstractmethod
    def agents(self) -> Any:
        pass

    @abstractmethod
    async def chat(self, request: ChatRequest, **kwargs: Any) -> ChatResponse:
        pass

    @abstractmethod
    async def stream_chat(
        self, request: ChatRequest, **kwargs: Any
    ) -> AsyncGenerator[StreamingChunk, None]:
        yield StreamingChunk(content="")

    @abstractmethod
    async def embeddings(self, request: EmbeddingRequest, **kwargs: Any) -> EmbeddingResponse:
        pass

    @abstractmethod
    async def image_generation(self, prompt: str, model: str, **kwargs: Any) -> str:
        pass

    @abstractmethod
    async def speech(self, text: str, model: str, **kwargs: Any) -> bytes:
        pass

    @abstractmethod
    async def vision(self, image_path: str, prompt: str, model: str, **kwargs: Any) -> str:
        pass

    @abstractmethod
    async def automation(self, request: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def plan(self, request: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def collaborate(self, goal: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def execute_workflow(self, goal: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def resume_workflow(self, workflow_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def start_mission(self, goal: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def pause_mission(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def resume_mission(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def cancel_mission(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def mission_status(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def list_missions(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def request_approval(self, mission_id: str, action: str, parameters: Dict[str, Any], risk_level: str = "no_approval", reason: str = "", **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def approve(self, approval_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def reject(self, approval_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def pending_approvals(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def approval_history(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def architect(self) -> Any:
        pass

    @abstractmethod
    async def backend(self) -> Any:
        pass

    @abstractmethod
    async def frontend(self) -> Any:
        pass

    @abstractmethod
    async def database(self) -> Any:
        pass

    @abstractmethod
    async def qa(self) -> Any:
        pass

    @abstractmethod
    async def documentation(self) -> Any:
        pass

    @abstractmethod
    async def devops(self) -> Any:
        pass

    @abstractmethod
    async def security(self) -> Any:
        pass

    @abstractmethod
    async def research(self) -> Any:
        pass

    @abstractmethod
    async def uiux(self) -> Any:
        pass

    @abstractmethod
    async def learn_from_mission(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def recommend_strategy(self, goal: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def agent_experience(self, agent_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def best_workflow(self, task: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def learning_metrics(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def install_plugin(self, plugin_path: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def uninstall_plugin(self, plugin_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def enable_plugin(self, plugin_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def disable_plugin(self, plugin_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def list_plugins(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def plugin_capabilities(self, plugin_id: str = "", **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def execute_plugin(self, plugin_id: str, capability: str, parameters: Dict[str, Any], **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def execute_mission(self, mission_id: str, plan: Dict[str, Any], **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def mission_status(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def cancel_mission(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def resume_mission(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def active_missions(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def mission_history(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def open_application(self, app_name: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def control_browser(self, action: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def desktop_action(self, action: str, parameters: Dict[str, Any], **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def browser_action(self, action: str, parameters: Dict[str, Any], **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def automation_status(self, automation_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def active_automations(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def execute_service(self, service_id: str, parameters: Dict[str, Any], **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def service_status(self, execution_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def cancel_service(self, execution_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def resume_service(self, execution_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def list_services(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def assistant(self, query: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def plan_day(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def daily_summary(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def create_reminder(self, title: str, due_time: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def manage_schedule(self, action: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def recommend_tasks(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def start_ambient(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def stop_ambient(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def ambient_status(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def conversation(self, query: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def pause_listening(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def resume_listening(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def create_swarm(self, goal: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def execute_swarm(self, swarm_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def swarm_status(self, swarm_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def active_swarms(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def swarm_history(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def process_intent(self, intent: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def system_snapshot(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def system_health(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def active_context(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def kernel_metrics(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def pause_kernel(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def resume_kernel(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def create_project(self, prompt: str, name: str = "NovaProject", **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def analyze_project(self, project_path: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def generate_architecture(self, prompt: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def generate_code(self, prompt: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def debug_project(self, project_path: str, stack_trace: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def refactor_project(self, project_path: str, goal: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def test_project(self, project_path: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def deploy_project(self, project_path: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def review_project(self, project_path: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def document_project(self, project_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def analyze_screen(self, monitor_index: int = 0, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def understand_application(self, app_name: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def find_ui_element(self, query: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def reason_about_screen(self, query: str = "", **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def capture_desktop(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def capture_window(self, window_title: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def capture_region(self, x: int, y: int, width: int, height: int, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def screen_history(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def create_mission(self, name: str, goal: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def pause_mission(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def resume_mission(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def cancel_mission(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def clone_mission(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def mission_progress(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def mission_logs(self, mission_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def mission_history(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def mission_dashboard(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def load_model(self, model_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def unload_model(self, model_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def available_models(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def active_models(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def route_model(self, category: str, prompt: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def chat(self, prompt: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def embed(self, texts: List[str], **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def transcribe(self, audio_bytes_or_path: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def speak(self, text: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def vision(self, image_bytes_or_path: Any, prompt: str = "", **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def research(self, topic: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def search(self, query: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def analyze_document(self, doc_path: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def analyze_repository(self, repo_path: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def generate_report(self, topic: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def knowledge_graph(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def research_history(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def continue_research(self, topic: str, new_query: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def knowledge_package(self, topic: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def reason(self, prompt: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def code(self, prompt: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def ocr(self, image_bytes_or_path: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def translate(self, text: str, target_lang: str = "en", **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def load_runtime(self, model_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def runtime_status(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def install_skill(self, skill_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def uninstall_skill(self, skill_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def enable_skill(self, skill_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def disable_skill(self, skill_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def search_skills(self, query: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def list_skills(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def skill_info(self, skill_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def voice_commands(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def conversation(self, prompt: str, session_id: Optional[str] = None, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def continue_conversation(self, session_id: str, prompt: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def conversation_history(self, session_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def conversation_summary(self, session_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def conversation_context(self, session_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def conversation_style(self, session_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def set_personality(self, personality: str, session_id: Optional[str] = None, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def current_emotion(self, session_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def interrupt_response(self, session_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def resume_response(self, session_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def stream_response(self, session_id: str, prompt: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def self_improve(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def performance_report(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def workflow_recommendations(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def agent_scorecard(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def benchmark_report(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def quality_report(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def adaptive_settings(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def experience_summary(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def system_learning(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def optimization_history(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def record_workflow(self, name: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def stop_recording(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def play_workflow(self, workflow_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def edit_workflow(self, workflow_id: str, updates: Dict[str, Any], **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def delete_workflow(self, workflow_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def list_workflows(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def export_workflow(self, workflow_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def import_workflow(self, content: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def share_workflow(self, workflow_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def workflow_history(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def create_workspace(self, name: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def join_workspace(self, workspace_id: str, email: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def leave_workspace(self, workspace_id: str, member_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def workspace_members(self, workspace_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def workspace_search(self, workspace_id: str, query: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def workspace_sync(self, workspace_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def remote_execute(self, target_device_id: str, command_type: str, payload: Dict[str, Any], **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def workspace_backup(self, workspace_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def workspace_restore(self, backup_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def workspace_activity(self, workspace_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def pair_device(self, name: str, ip_address: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def remove_device(self, device_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def devices(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def device_status(self, device_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def device_metrics(self, device_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def mesh_status(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def allocate_gpu(self, task_category: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def edge_models(self, device_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def mesh_dashboard(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def launch_app(self, app_name: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def activate_window(self, title: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def click_control(self, label: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def type_text(self, text: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def open_url(self, url: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def fill_form(self, form_data: Dict[str, Any], **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def run_terminal_command(self, command: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def automate_office(self, file_path: str, action: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def file_operation(self, op_type: str, source_path: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def configure_setting(self, setting_name: str, value: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def execute_goal_plan(self, goal_prompt: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def inspect_accessibility_tree(self, window_title: Optional[str] = None, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def wait_for_condition(self, condition_type: str, target: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def run_browser_playwright(self, url: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def analyze_failure_logs(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def get_automation_benchmarks(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def start_os(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def stop_os(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def restart_os(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def pause_os(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def resume_os(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def os_status(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def os_dashboard(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def running_agents(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def running_models(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def running_missions(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def running_workflows(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def system_events(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def system_logs(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def system_metrics(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def system_health(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def emergency_stop(self, **kwargs: Any) -> Any:
        pass


















# Concrete V2 Gateway Components
from app.ai.gateway.exceptions import (
    ProviderUnavailableError,
    ProviderNotFoundError,
    ModelUnavailableError,
    CapabilityUnavailableError,
    GatewayTimeoutError,
    GatewayConfigurationError,
)
from app.ai.gateway.gateway_config import GatewayConfig
from app.ai.gateway.request_context import RequestContext
from app.ai.gateway.response import GatewayResponse
from app.ai.gateway.retry_policy import RetryPolicy
from app.ai.gateway.timeout_policy import TimeoutPolicy
from app.ai.gateway.model_registry import ModelRegistry
from app.ai.gateway.provider_registry import ProviderRegistry
from app.ai.gateway.provider_factory import ProviderFactory
from app.ai.gateway.ai_gateway import AIGateway

__all__ = [
    "IProviderFactory",
    "IAIGateway",
    "AiGatewayService",
    "ProviderUnavailableError",
    "ProviderNotFoundError",
    "ModelUnavailableError",
    "CapabilityUnavailableError",
    "GatewayTimeoutError",
    "GatewayConfigurationError",
    "GatewayConfig",
    "RequestContext",
    "GatewayResponse",
    "RetryPolicy",
    "TimeoutPolicy",
    "ModelRegistry",
    "ProviderRegistry",
    "ProviderFactory",
    "AIGateway",
]
