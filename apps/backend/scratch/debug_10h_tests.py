import asyncio
import sys
from pathlib import Path
import tempfile

from app.ai.kernel.durable_checkpoint_store import DurableCheckpointStore
from app.ai.kernel.long_horizon_manager import LongHorizonTaskManager, DurableTaskState
from app.ai.kernel.task_graph import TaskGraph, TaskNode, TaskGraphExecutor
from app.ai.desktop_automation.models import AutomationAction
from app.ai.desktop_automation.application_adapter import ApplicationAdapterRegistry
from app.ai.kernel.goal_verifier import GoalRequirement
from tests.test_cognitive_long_horizon_task_manager import MockBlenderAdapter, test_5_resume_task, test_8_process_restart_recovery, test_26_physical_end_to_end_restart_and_recovery_chain

def run_debug():
    print("=== DEBUGGING TEST 5 ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DurableCheckpointStore(storage_dir=Path(tmpdir))
        manager = LongHorizonTaskManager(checkpoint_store=store)
        task_id = manager.create_task("Resume task test")
        graph = TaskGraph(task_id=task_id)
        graph.add_node(TaskNode(node_id="n1", title="Action node", action=AutomationAction(action_id="a1", action_type="blender:add_cube", target_label="Blender")))
        cp = store.load_checkpoint(task_id)
        cp.task_graph_dict = graph.to_dict()
        store.save_checkpoint(cp)

        manager.transition_task_state(task_id, DurableTaskState.RUNNING)
        manager.pause_task(task_id)
        res = manager.resume_task(task_id)
        print("TEST 5 RESULT:", res)

    print("\n=== DEBUGGING TEST 8 ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DurableCheckpointStore(storage_dir=Path(tmpdir))
        manager1 = LongHorizonTaskManager(checkpoint_store=store)
        task_id = manager1.create_task("Process restart recovery test")
        graph = TaskGraph(task_id=task_id)
        graph.add_node(TaskNode(node_id="n1", title="Action node", action=AutomationAction(action_id="a1", action_type="blender:add_cube", target_label="Blender")))
        cp = store.load_checkpoint(task_id)
        cp.task_graph_dict = graph.to_dict()
        store.save_checkpoint(cp)

        manager1.transition_task_state(task_id, DurableTaskState.RUNNING)

        manager2 = LongHorizonTaskManager(checkpoint_store=store)
        res = manager2.recover_on_restart(task_id)
        print("TEST 8 RESULT:", res)

    print("\n=== DEBUGGING TEST 26 ===")
    async def run_26():
        with tempfile.TemporaryDirectory() as tmpdir:
            store = DurableCheckpointStore(storage_dir=Path(tmpdir))
            task_id = "task_phys_10h_26"
            user_goal = "Create and materialize metallic Blender mesh"

            registry = ApplicationAdapterRegistry()
            adapter = MockBlenderAdapter(fail_action="blender:bad_invalid_action")
            registry.register_adapter("Blender", adapter)

            executor = TaskGraphExecutor(adapter_registry=registry)
            manager1 = LongHorizonTaskManager(checkpoint_store=store, executor=executor)

            initial_graph = TaskGraph(task_id=task_id)
            fail_node = TaskNode(
                node_id="node_initial",
                title="Execute Invalid Action",
                action=AutomationAction(action_id="act_init", action_type="blender:bad_invalid_action", target_label="Blender"),
            )
            initial_graph.add_node(fail_node)

            manager1.create_task(user_goal=user_goal, task_id=task_id)
            cp = store.load_checkpoint(task_id)
            cp.task_graph_dict = initial_graph.to_dict()
            store.save_checkpoint(cp)

            manager2 = LongHorizonTaskManager(checkpoint_store=store, executor=executor)
            req = GoalRequirement(req_id="req_metallic", description="Create metallic mesh object", target_state="Metallic")

            res = await manager2.execute_task_lifecycle(
                task_id=task_id,
                graph=initial_graph,
                requirements=[req],
                adapter_name="Blender",
            )
            print("TEST 26 RESULT:", res)

    asyncio.run(run_26())

if __name__ == "__main__":
    run_debug()
