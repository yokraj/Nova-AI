"""Swarm Manager unifying agent registry, task decomposer, parallel executor, consensus, and blackboard."""

from typing import Any, Dict, List, Optional
from uuid import uuid4
import structlog

from app.ai.swarm.agent_allocator import AgentAllocator
from app.ai.swarm.agent_registry import AgentRegistry
from app.ai.swarm.communication_manager import CommunicationManager
from app.ai.swarm.consensus_engine import ConsensusEngine
from app.ai.swarm.execution_coordinator import ExecutionCoordinator
from app.ai.swarm.leader_election import LeaderElection
from app.ai.swarm.load_balancer import LoadBalancer
from app.ai.swarm.parallel_executor import ParallelExecutor
from app.ai.swarm.result_aggregator import ResultAggregator
from app.ai.swarm.shared_blackboard import SharedBlackboard
from app.ai.swarm.shared_context import SharedContext
from app.ai.swarm.shared_memory import SharedMemory
from app.ai.swarm.task_decomposer import TaskDecomposer

logger = structlog.get_logger("swarm_manager")


class SwarmManager:
    """High-level Swarm Orchestrator connecting goal decomposition, agent allocation, wave execution, consensus, and result aggregation."""

    def __init__(self) -> None:
        self.registry = AgentRegistry()
        self.decomposer = TaskDecomposer()
        self.allocator = AgentAllocator(registry=self.registry)
        self.executor = ParallelExecutor(allocator=self.allocator)
        self.coordinator = ExecutionCoordinator(executor=self.executor)
        self.comm_mgr = CommunicationManager()
        self.consensus = ConsensusEngine()
        self.blackboard = SharedBlackboard()
        self.context = SharedContext()
        self.memory = SharedMemory()
        self.aggregator = ResultAggregator()
        self.leader_election = LeaderElection()
        self.load_balancer = LoadBalancer(allocator=self.allocator)

    async def execute_swarm_goal(self, goal: str) -> Dict[str, Any]:
        """Orchestrate full multi-agent swarm execution for a goal."""
        swarm_id = f"swm_{uuid4().hex[:8]}"
        logger.info("SwarmManager orchestrating goal", swarm_id=swarm_id, goal=goal)

        # 1. Elect Leader
        agents = self.registry.list_all_agents()
        leader = await self.leader_election.elect_leader(agents)
        await self.blackboard.write("leader_agent", leader.agent_id, author_agent_id="system")

        # 2. Decompose Goal into Task DAG
        graph = await self.decomposer.decompose_goal(goal)

        # 3. Wave Execution in Parallel
        executed_tasks = await self.coordinator.coordinate_execution(graph)

        # 4. Result Aggregation & Voice Summary
        res = await self.aggregator.aggregate_results(swarm_id=swarm_id, goal=goal, tasks=executed_tasks)

        # 5. Feed back outcome to Learning Engine
        try:
            from app.ai.learning.learning_engine import LearningEngine
            le = LearningEngine()
            await le.learn_from_mission(
                mission_id=f"ms_swarm_{swarm_id}",
                mission_result={
                    "goal": goal,
                    "status": "completed",
                    "agents_used": res.agents_involved,
                    "tasks_count": len(executed_tasks),
                },
            )
        except Exception as e:
            logger.debug("Learning Engine bridge fallback in SwarmManager", error=str(e))

        return res.model_dump(mode="json") if hasattr(res, "model_dump") else res
