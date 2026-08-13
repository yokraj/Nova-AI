"""Unit tests for Multi-Agent Collaboration & Swarm Intelligence Engine."""

import pytest
from app.ai.gateway import IAIGateway
from app.ai.swarm.agent_allocator import AgentAllocator
from app.ai.swarm.agent_registry import AgentRegistry
from app.ai.swarm.conflict_resolver import ConflictResolver
from app.ai.swarm.consensus_engine import ConsensusEngine
from app.ai.swarm.configuration import SwarmConfiguration
from app.ai.swarm.leader_election import LeaderElection
from app.ai.swarm.models import AgentRole, SwarmTask, VoteRecord, VotingStrategy
from app.ai.swarm.parallel_executor import ParallelExecutor
from app.ai.swarm.shared_blackboard import SharedBlackboard
from app.ai.swarm.shared_memory import SharedMemory
from app.ai.swarm.swarm_engine import SwarmEngine
from app.ai.swarm.swarm_manager import SwarmManager
from app.ai.swarm.task_decomposer import TaskDecomposer
from app.ai.swarm.voting_engine import VotingEngine
from app.core.dependency_container import register_ai_gateway_dependencies, resolve


@pytest.mark.anyio
async def test_swarm_configuration():
    """Verifies default swarm configuration settings."""
    config = SwarmConfiguration()
    assert config.enabled is True
    assert config.max_agents_per_swarm == 10
    assert config.default_voting_strategy == "majority"


@pytest.mark.anyio
async def test_agent_registry_workforce():
    """Verifies agent registry seeds all 16 specialized agent roles."""
    reg = AgentRegistry()
    agents = reg.list_all_agents()
    assert len(agents) >= 16
    roles = [a.role.value for a in agents]
    assert "software_engineer" in roles
    assert "security" in roles
    assert "personal_assistant" in roles


@pytest.mark.anyio
async def test_task_decomposer():
    """Verifies complex goal decomposition into task graph."""
    decomposer = TaskDecomposer()
    graph = await decomposer.decompose_goal("Analyze backend, security, performance, docs, deploy")
    assert len(graph.tasks) >= 6
    assert graph.tasks[0].required_role == AgentRole.PLANNER


@pytest.mark.anyio
async def test_parallel_executor_and_allocator():
    """Verifies concurrent execution of independent task waves."""
    reg = AgentRegistry()
    allocator = AgentAllocator(registry=reg)
    executor = ParallelExecutor(allocator=allocator)

    t1 = SwarmTask(title="Task A", required_role=AgentRole.SOFTWARE_ENGINEER)
    t2 = SwarmTask(title="Task B", required_role=AgentRole.SECURITY)
    res = await executor.execute_task_wave([t1, t2])
    assert len(res) == 2
    assert res[0].state.value == "completed"
    assert res[1].state.value == "completed"


@pytest.mark.anyio
async def test_voting_and_consensus_engine():
    """Verifies majority and weighted voting consensus aggregation."""
    consensus = ConsensusEngine()
    votes = [
        VoteRecord(agent_id="swe_01", option="approve_deploy", confidence=0.9),
        VoteRecord(agent_id="sec_01", option="approve_deploy", confidence=0.8),
        VoteRecord(agent_id="qa_01", option="reject_deploy", confidence=0.5),
    ]
    decision = await consensus.reach_consensus(votes, strategy="majority")
    assert decision.winning_option == "approve_deploy"
    assert decision.vote_breakdown["approve_deploy"] == 2


@pytest.mark.anyio
async def test_leader_election():
    """Verifies dynamic leader election among candidate agents."""
    reg = AgentRegistry()
    agents = reg.list_all_agents()
    election = LeaderElection()
    leader = await election.elect_leader(agents)
    assert leader.agent_id is not None


@pytest.mark.anyio
async def test_shared_blackboard_and_memory():
    """Verifies shared blackboard and memory store inter-agent access."""
    bb = SharedBlackboard()
    await bb.write("status_report", "Security scan passed", author_agent_id="sec_01")
    val = await bb.read("status_report")
    assert val == "Security scan passed"

    mem = SharedMemory()
    await mem.store("shared_token", "abc123token")
    retrieved = await mem.retrieve("shared_token")
    assert retrieved == "abc123token"


@pytest.mark.anyio
async def test_swarm_manager_full_orchestration():
    """Verifies full SwarmManager end-to-end goal execution."""
    mgr = SwarmManager()
    res = await mgr.execute_swarm_goal("Full backend security audit and performance optimization")
    assert res["state"] == "completed"
    assert len(res["agents_involved"]) >= 1
    assert "Swarm collaboration complete" in res["voice_summary"]


@pytest.mark.anyio
async def test_gateway_swarm_apis():
    """Verifies AI Gateway swarm methods."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    c_res = await gateway.create_swarm("Deploy production release")
    assert c_res["status"] == "created"
    swarm_id = c_res["swarm_id"]

    e_res = await gateway.execute_swarm(swarm_id)
    assert e_res["state"] == "completed"

    s_res = await gateway.swarm_status(swarm_id)
    assert s_res["status"] == "healthy"
