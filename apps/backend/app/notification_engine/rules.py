"""Notification Rule Engine Module.

Evaluates incoming live telemetry payloads and event objects against 16 default
notification rules and custom registered rule predicates.
"""

from typing import Any, Callable, Dict, List, Optional
import structlog

from app.notification_engine.priority import NotificationPriorityLevel

logger = structlog.get_logger(__name__)

# Rule predicate function type signature: (event_name: str, payload: dict) -> Optional[dict]
RulePredicate = Callable[[str, Dict[str, Any]], Optional[Dict[str, Any]]]


class NotificationRuleEngine:
    """Evaluates telemetry and event streams against alert rules."""

    def __init__(self) -> None:
        self._rules: Dict[str, RulePredicate] = {}
        self.load_default_rules()
        logger.info("notification_rule_engine_initialized", rule_count=len(self._rules))

    def register_rule(self, rule_name: str, predicate: RulePredicate) -> None:
        """Registers a custom rule predicate."""
        self._rules[rule_name] = predicate
        logger.info("notification_rule_registered", rule_name=rule_name)

    def remove_rule(self, rule_name: str) -> bool:
        """Removes a registered rule predicate."""
        if rule_name in self._rules:
            del self._rules[rule_name]
            logger.info("notification_rule_removed", rule_name=rule_name)
            return True
        return False

    def list_rules(self) -> List[str]:
        """Returns list of registered rule names."""
        return sorted(list(self._rules.keys()))

    def evaluate(self, event_name: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluates payload against all active rules and returns generated notification dicts."""
        notifications = []
        for rule_name, predicate in self._rules.items():
            try:
                result = predicate(event_name, payload)
                if result:
                    result["rule_name"] = rule_name
                    notifications.append(result)
            except Exception as exc:
                logger.warning("rule_evaluation_failed", rule_name=rule_name, error=str(exc))
        return notifications

    def load_default_rules(self) -> None:
        """Loads 16 default notification rules."""
        # 1. CPU Threshold Rule
        def cpu_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            cpu = payload.get("cpu_percent") or payload.get("cpu", {}).get("usage_percent")
            if isinstance(cpu, (int, float)) and cpu >= 85.0:
                priority = NotificationPriorityLevel.URGENT if cpu >= 95.0 else NotificationPriorityLevel.HIGH
                return {
                    "title": "High CPU Utilization Alert",
                    "message": f"Host CPU utilization reached {cpu:.1f}%.",
                    "category": "system",
                    "priority": priority,
                    "component": "cpu",
                }
            return None

        # 2. Memory Threshold Rule
        def memory_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            mem = payload.get("memory_percent") or payload.get("memory", {}).get("percent")
            if isinstance(mem, (int, float)) and mem >= 85.0:
                priority = NotificationPriorityLevel.URGENT if mem >= 95.0 else NotificationPriorityLevel.HIGH
                return {
                    "title": "High Memory Pressure Alert",
                    "message": f"Host RAM usage reached {mem:.1f}%.",
                    "category": "system",
                    "priority": priority,
                    "component": "memory",
                }
            return None

        # 3. Disk Threshold Rule
        def disk_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            disk = payload.get("disk_percent") or payload.get("disk", {}).get("percent")
            if isinstance(disk, (int, float)) and disk >= 85.0:
                priority = NotificationPriorityLevel.URGENT if disk >= 95.0 else NotificationPriorityLevel.HIGH
                return {
                    "title": "Disk Capacity Warning",
                    "message": f"Disk space usage reached {disk:.1f}%.",
                    "category": "storage",
                    "priority": priority,
                    "component": "disk",
                }
            return None

        # 4. GPU Threshold Rule
        def gpu_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            gpus = payload.get("gpu", [])
            if isinstance(gpus, list):
                for gpu in gpus:
                    load = gpu.get("load_percent", 0.0)
                    temp = gpu.get("temperature_celsius", 0.0)
                    if temp >= 80.0 or load >= 95.0:
                        return {
                            "title": "GPU Overheating or Max Load Alert",
                            "message": f"GPU {gpu.get('name')} temp: {temp}°C, load: {load}%.",
                            "category": "hardware",
                            "priority": NotificationPriorityLevel.HIGH,
                            "component": "gpu",
                        }
            return None

        # 5. Health Degradation Rule
        def health_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            status = payload.get("status", "").lower()
            if status in ["degraded", "offline"]:
                priority = NotificationPriorityLevel.URGENT if status == "offline" else NotificationPriorityLevel.HIGH
                return {
                    "title": "System Health Degradation",
                    "message": payload.get("message", "System health report indicated degradation."),
                    "category": "health",
                    "priority": priority,
                    "component": "health",
                }
            return None

        # 6. Agent Offline Rule
        def agent_offline_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            if "agent.offline" in event_name.lower() or payload.get("status") == "agent_offline":
                return {
                    "title": "Workforce Agent Disconnected",
                    "message": f"Agent '{payload.get('agent_name', 'Unknown')}' went offline.",
                    "category": "agents",
                    "priority": NotificationPriorityLevel.HIGH,
                    "component": "agent",
                }
            return None

        # 7. Mission Failure Rule
        def mission_failure_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            if "mission.failed" in event_name.lower() or payload.get("status") == "failed":
                return {
                    "title": "Mission Execution Failure",
                    "message": f"Mission '{payload.get('mission_name', 'Mission')}' failed.",
                    "category": "missions",
                    "priority": NotificationPriorityLevel.URGENT,
                    "component": "mission",
                }
            return None

        # 8. Mission Completion Rule
        def mission_completion_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            if "mission.completed" in event_name.lower():
                return {
                    "title": "Mission Completed Successfully",
                    "message": f"Mission '{payload.get('mission_name', 'Mission')}' finished execution.",
                    "category": "missions",
                    "priority": NotificationPriorityLevel.LOW,
                    "component": "mission",
                }
            return None

        # 9. Workflow Completion Rule
        def workflow_completion_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            if "workflow.completed" in event_name.lower():
                return {
                    "title": "Workflow Completed",
                    "message": f"Workflow '{payload.get('workflow_name', 'Workflow')}' finished.",
                    "category": "workflows",
                    "priority": NotificationPriorityLevel.LOW,
                    "component": "workflow",
                }
            return None

        # 10. Voice Engine Failure Rule
        def voice_failure_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            if "voice.failed" in event_name.lower():
                return {
                    "title": "Voice Service Error",
                    "message": "Voice synthesis/recognition engine encountered an error.",
                    "category": "voice",
                    "priority": NotificationPriorityLevel.NORMAL,
                    "component": "voice",
                }
            return None

        # 11. Model Loading Rule
        def model_loading_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            if "model.loaded" in event_name.lower():
                return {
                    "title": "AI Model Loaded",
                    "message": f"Model '{payload.get('model_name', 'LLM')}' loaded into VRAM.",
                    "category": "models",
                    "priority": NotificationPriorityLevel.LOW,
                    "component": "model",
                }
            return None

        # 12. System Startup Rule
        def system_startup_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            if "system.startup" in event_name.lower():
                return {
                    "title": "Nova AI System Online",
                    "message": "Nova AI OS backend initialized successfully.",
                    "category": "system",
                    "priority": NotificationPriorityLevel.LOW,
                    "component": "system",
                }
            return None

        # 13. System Shutdown Rule
        def system_shutdown_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            if "system.shutdown" in event_name.lower():
                return {
                    "title": "System Shutdown Warning",
                    "message": "Nova AI backend service is shutting down.",
                    "category": "system",
                    "priority": NotificationPriorityLevel.HIGH,
                    "component": "system",
                }
            return None

        # 14. Configuration Changes Rule
        def config_change_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            if "configuration.updated" in event_name.lower():
                return {
                    "title": "Configuration Updated",
                    "message": "System runtime settings were modified.",
                    "category": "configuration",
                    "priority": NotificationPriorityLevel.NORMAL,
                    "component": "configuration",
                }
            return None

        # 15. Security Alerts Rule
        def security_alert_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            if "security" in event_name.lower() or payload.get("type") == "security_alert":
                return {
                    "title": "Security Access Alert",
                    "message": payload.get("message", "Unauthorized access attempt detected."),
                    "category": "security",
                    "priority": NotificationPriorityLevel.URGENT,
                    "component": "security",
                }
            return None

        # 16. Generic Error Rule
        def generic_error_rule(event_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            if "error" in event_name.lower() and not any(k in event_name.lower() for k in ["cpu", "memory", "health", "security"]):
                return {
                    "title": "System Event Error",
                    "message": payload.get("message", f"Event '{event_name}' reported an error."),
                    "category": "events",
                    "priority": NotificationPriorityLevel.NORMAL,
                    "component": "events",
                }
            return None

        self._rules = {
            "cpu_threshold": cpu_rule,
            "memory_threshold": memory_rule,
            "disk_threshold": disk_rule,
            "gpu_threshold": gpu_rule,
            "health_degradation": health_rule,
            "agent_offline": agent_offline_rule,
            "mission_failure": mission_failure_rule,
            "mission_completion": mission_completion_rule,
            "workflow_completion": workflow_completion_rule,
            "voice_failure": voice_failure_rule,
            "model_loading": model_loading_rule,
            "system_startup": system_startup_rule,
            "system_shutdown": system_shutdown_rule,
            "config_change": config_change_rule,
            "security_alert": security_alert_rule,
            "generic_error": generic_error_rule,
        }
