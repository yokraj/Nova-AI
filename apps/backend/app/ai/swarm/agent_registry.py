"""Agent Registry discovering and maintaining agent roles and capabilities."""

from typing import Dict, List, Optional
import structlog

from app.ai.swarm.interfaces import IAgentRegistry
from app.ai.swarm.models import AgentRole, SwarmAgentRecord

logger = structlog.get_logger("agent_registry")


class AgentRegistry(IAgentRegistry):
    """Central registry of all specialized swarm agents across Nova AI OS."""

    def __init__(self) -> None:
        self._agents: Dict[str, SwarmAgentRecord] = {}
        self._register_default_workforce()

    def _register_default_workforce(self) -> None:
        """Seed all 15 built-in agent roles."""
        defaults = [
            SwarmAgentRecord(agent_id="exec_01", name="Executive Agent", role=AgentRole.EXECUTIVE, capabilities=["orchestrate", "lead"]),
            SwarmAgentRecord(agent_id="plan_01", name="Planner Agent", role=AgentRole.PLANNER, capabilities=["decompose", "schedule"]),
            SwarmAgentRecord(agent_id="swe_01", name="Software Engineer Agent", role=AgentRole.SOFTWARE_ENGINEER, capabilities=["code", "refactor", "optimize"]),
            SwarmAgentRecord(agent_id="sec_01", name="Security Agent", role=AgentRole.SECURITY, capabilities=["audit", "scan_vulnerabilities"]),
            SwarmAgentRecord(agent_id="res_01", name="Research Agent", role=AgentRole.RESEARCH, capabilities=["search", "web_crawl"]),
            SwarmAgentRecord(agent_id="mem_01", name="Memory Agent", role=AgentRole.MEMORY, capabilities=["rag_search", "store_context"]),
            SwarmAgentRecord(agent_id="exec_rt_01", name="Execution Agent", role=AgentRole.EXECUTION, capabilities=["run_mission", "call_tools"]),
            SwarmAgentRecord(agent_id="auto_01", name="Automation Agent", role=AgentRole.AUTOMATION, capabilities=["desktop_automation", "browser_automation"]),
            SwarmAgentRecord(agent_id="browser_01", name="Browser Agent", role=AgentRole.BROWSER, capabilities=["scrape", "fill_forms"]),
            SwarmAgentRecord(agent_id="desktop_01", name="Desktop Agent", role=AgentRole.DESKTOP, capabilities=["keyboard_input", "mouse_click"]),
            SwarmAgentRecord(agent_id="service_01", name="Service Agent", role=AgentRole.SERVICE, capabilities=["irctc_booking", "checkout"]),
            SwarmAgentRecord(agent_id="learn_01", name="Learning Agent", role=AgentRole.LEARNING, capabilities=["extract_lessons", "update_strategies"]),
            SwarmAgentRecord(agent_id="ast_01", name="Personal Assistant Agent", role=AgentRole.PERSONAL_ASSISTANT, capabilities=["daily_plan", "reminders"]),
            SwarmAgentRecord(agent_id="amb_01", name="Ambient Agent", role=AgentRole.AMBIENT, capabilities=["wake_word", "proactive_alerts"]),
            SwarmAgentRecord(agent_id="vis_01", name="Vision Agent", role=AgentRole.VISION, capabilities=["ocr", "object_detection"]),
            SwarmAgentRecord(agent_id="voice_01", name="Voice Agent", role=AgentRole.VOICE, capabilities=["stt", "tts"]),
        ]
        for ag in defaults:
            self.register_agent(ag)

    def register_agent(self, agent: SwarmAgentRecord) -> None:
        """Register agent record."""
        self._agents[agent.agent_id] = agent
        logger.debug("Registered swarm agent", id=agent.agent_id, name=agent.name, role=agent.role.value)

    def find_agents_by_role(self, role: str) -> List[SwarmAgentRecord]:
        """Find agents matching role."""
        return [ag for ag in self._agents.values() if ag.role.value == role or ag.role == role]

    def list_all_agents(self) -> List[SwarmAgentRecord]:
        """List all registered agents."""
        return list(self._agents.values())
