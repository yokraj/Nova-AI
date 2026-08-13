"""12-Stage Manual Validation Script for M3.4.1 Multi-Agent Collaboration & Swarm Intelligence Engine."""

import asyncio
import sys
import structlog

from app.ai.gateway import IAIGateway
from app.ai.swarm.agent_allocator import AgentAllocator
from app.ai.swarm.agent_registry import AgentRegistry
from app.ai.swarm.capability_matcher import CapabilityMatcher
from app.ai.swarm.configuration import SwarmConfiguration
from app.ai.swarm.conflict_resolver import ConflictResolver
from app.ai.swarm.consensus_engine import ConsensusEngine
from app.ai.swarm.leader_election import LeaderElection
from app.ai.swarm.models import AgentRole, SwarmTask, VoteRecord
from app.ai.swarm.parallel_executor import ParallelExecutor
from app.ai.swarm.shared_blackboard import SharedBlackboard
from app.ai.swarm.shared_memory import SharedMemory
from app.ai.swarm.swarm_engine import SwarmEngine
from app.ai.swarm.swarm_manager import SwarmManager
from app.ai.swarm.task_decomposer import TaskDecomposer
from app.core.dependency_container import register_ai_gateway_dependencies, resolve

logger = structlog.get_logger("test_swarm_manual")


async def run_manual_validation() -> None:
    print("=========================================")
    print("Nova AI Swarm Intelligence Engine Validation")
    print("=========================================")

    # Stage 1: Configuration & Settings
    config = SwarmConfiguration()
    assert config.enabled is True
    print("Stage 1  Swarm Configuration       PASS")

    # Stage 2: Agent Registry Workforce Discovery
    reg = AgentRegistry()
    agents = reg.list_all_agents()
    assert len(agents) >= 16
    print("Stage 2  Agent Registry Workforce  PASS")

    # Stage 3: Capability Matching & Agent Selection
    matcher = CapabilityMatcher(registry=reg)
    cands = matcher.match_task(SwarmTask(title="Code Audit", required_role=AgentRole.SOFTWARE_ENGINEER))
    assert len(cands) >= 1
    print("Stage 3  Capability Matching       PASS")

    # Stage 4: Goal Task Decomposition
    decomposer = TaskDecomposer()
    graph = await decomposer.decompose_goal("Audit backend, fix bugs, optimize, deploy")
    assert len(graph.tasks) >= 6
    print("Stage 4  Goal Task Decomposition   PASS")

    # Stage 5: Dynamic Leader Election
    election = LeaderElection()
    leader = await election.elect_leader(agents)
    assert leader.agent_id is not None
    print("Stage 5  Dynamic Leader Election    PASS")

    # Stage 6: Concurrent Parallel Executor
    allocator = AgentAllocator(registry=reg)
    executor = ParallelExecutor(allocator=allocator)
    t1 = SwarmTask(title="Scan Vulns", required_role=AgentRole.SECURITY)
    t2 = SwarmTask(title="Refactor Code", required_role=AgentRole.SOFTWARE_ENGINEER)
    res_tasks = await executor.execute_task_wave([t1, t2])
    assert len(res_tasks) == 2
    print("Stage 6  Concurrent Parallel Exec  PASS")

    # Stage 7: Shared Blackboard & Memory
    bb = SharedBlackboard()
    await bb.write("vuln_status", "clean", author_agent_id="sec_01")
    assert await bb.read("vuln_status") == "clean"
    print("Stage 7  Shared Blackboard & Memory PASS")

    # Stage 8: Voting & Consensus Engine
    consensus = ConsensusEngine()
    votes = [
        VoteRecord(agent_id="swe_01", option="pass", confidence=0.9),
        VoteRecord(agent_id="sec_01", option="pass", confidence=0.95),
    ]
    dec = await consensus.reach_consensus(votes)
    assert dec.winning_option == "pass"
    print("Stage 8  Voting & Consensus Engine PASS")

    # Stage 9: Conflict Resolver
    resolver = ConflictResolver(consensus_engine=consensus)
    c_dec = await resolver.resolve_conflict("stask_01", votes)
    assert c_dec.winning_option == "pass"
    print("Stage 9  Conflict Resolution       PASS")

    # Stage 10: Full End-to-End Swarm Execution
    manager = SwarmManager()
    e_res = await manager.execute_swarm_goal("Analyze backend security and deploy")
    assert e_res["state"] == "completed"
    print("Stage 10 Full Swarm Execution      PASS")

    # Stage 11: Swarm Engine Facade Runtime
    engine = SwarmEngine()
    s_id = await engine.create_swarm("Optimize full system")
    s_res = await engine.execute_swarm(s_id)
    assert s_res.state.value == "completed"
    print("Stage 11 Swarm Engine Facade       PASS")

    # Stage 12: Gateway Integration
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass
    gateway = resolve(IAIGateway)
    g_create = await gateway.create_swarm("Execute end-to-end swarm test")
    assert g_create["status"] == "created"
    g_exec = await gateway.execute_swarm(g_create["swarm_id"])
    assert g_exec["state"] == "completed"
    print("Stage 12 Gateway Integration        PASS")

    print("\n12/12 PASS")
    print("\nSwarm Intelligence Engine Healthy")


if __name__ == "__main__":
    asyncio.run(run_manual_validation())
