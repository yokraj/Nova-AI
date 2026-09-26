"""Test Suite for Phase 10B — WorldState & WorkingMemory Engines.

Tests real environmental observation aggregation, provenance tracking, freshness,
snapshot immutability, concurrency safety, volatile task blackboard lifecycle,
node transitions, action/observation/verification recording, recovery tracking,
budget accounting, and WorldState vs WorkingMemory separation of concerns.
"""

import time
import threading
from app.ai.desktop_automation.world_state import (
    WorldStateEngine,
    Observation,
    ProvenanceSource,
    WorldStateSnapshot,
)
from app.ai.memory.working_memory import (
    WorkingMemoryManager,
    WorkingMemoryTask,
    TaskStatus,
)
from app.ai.desktop_automation.window_tracker import WindowTracker
from app.ai.desktop_automation.application_adapter import BlenderApplicationAdapter


class TestWorldStateEngine:
    """Tests for real-time WorldState observation engine."""

    def test_world_state_construction_and_snapshot(self):
        engine = WorldStateEngine.get_instance()
        snapshot = engine.refresh()

        assert isinstance(snapshot, WorldStateSnapshot)
        assert snapshot.timestamp > 0.0
        assert snapshot.system.os_name.source == ProvenanceSource.SYSTEM_OS
        assert snapshot.system.os_name.value in ("Windows", "Linux", "Darwin")

    def test_real_window_tracker_integration(self):
        tracker = WindowTracker()
        active_window = tracker.get_active_window()

        engine = WorldStateEngine.get_instance()
        snapshot = engine.refresh()

        assert snapshot.windows.foreground_window.source == ProvenanceSource.WINDOW_TRACKER
        assert snapshot.windows.open_windows_count.value >= 0

        if active_window and getattr(active_window, "title", None):
            assert snapshot.windows.window_title.value != "UNKNOWN"
        else:
            assert snapshot.windows.window_title.value == "UNKNOWN"

    def test_application_observation_integration(self):
        adapter = BlenderApplicationAdapter()
        caps = adapter.get_capabilities()

        engine = WorldStateEngine.get_instance()
        snapshot = engine.refresh()

        assert snapshot.application.available_capabilities_count.source == ProvenanceSource.APPLICATION_ADAPTER
        assert snapshot.application.available_capabilities_count.value >= len(caps)

    def test_unknown_state_handling(self):
        obs = Observation(value="UNKNOWN", source=ProvenanceSource.UNKNOWN, confidence="UNKNOWN")
        assert obs.value == "UNKNOWN"
        assert obs.confidence == "UNKNOWN"
        assert obs.source == ProvenanceSource.UNKNOWN

    def test_observation_provenance_and_timestamps(self):
        t0 = time.time()
        obs = Observation(value="TestValue", source=ProvenanceSource.SECURITY_ENGINE, confidence="EXACT")
        assert obs.timestamp >= t0
        assert obs.source == ProvenanceSource.SECURITY_ENGINE
        assert obs.confidence == "EXACT"

    def test_freshness_and_stale_detection(self):
        obs_fresh = Observation(value="Fresh", source=ProvenanceSource.SYSTEM_OS, timestamp=time.time(), stale_threshold_sec=5.0)
        assert obs_fresh.is_stale is False

        obs_stale = Observation(value="Stale", source=ProvenanceSource.SYSTEM_OS, timestamp=time.time() - 10.0, stale_threshold_sec=5.0)
        assert obs_stale.is_stale is True

    def test_snapshot_immutability(self):
        engine = WorldStateEngine.get_instance()
        snap1 = engine.get_snapshot()
        snap_dict = snap1.to_dict()

        # Mutate dictionary copy
        snap_dict["system"]["os_name"]["value"] = "HackedOS"

        # Verify original snapshot remains unchanged
        assert snap1.system.os_name.value != "HackedOS"

    def test_concurrent_access_thread_safety(self):
        engine = WorldStateEngine.get_instance()
        errors = []

        def worker():
            try:
                for _ in range(10):
                    s = engine.refresh()
                    assert s.timestamp > 0.0
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestWorkingMemoryManager:
    """Tests for volatile WorkingMemory task blackboard."""

    def test_create_and_get_task(self):
        mgr = WorkingMemoryManager.get_instance()
        task = mgr.create_task(task_id="TASK-100", user_goal="Create procedural cube")

        assert isinstance(task, WorkingMemoryTask)
        assert task.task_id == "TASK-100"
        assert task.user_goal == "Create procedural cube"
        assert task.task_status == TaskStatus.CREATED

    def test_node_transitions(self):
        mgr = WorkingMemoryManager.get_instance()
        mgr.create_task(task_id="TASK-101", user_goal="Animate camera")

        mgr.set_current_node("TASK-101", "node_001")
        snap = mgr.get_snapshot("TASK-101")
        assert snap["current_node"] == "node_001"
        assert snap["task_status"] == TaskStatus.RUNNING.value

        mgr.complete_node("TASK-101", "node_001")
        snap2 = mgr.get_snapshot("TASK-101")
        assert "node_001" in snap2["completed_nodes"]
        assert snap2["steps_used"] == 1

    def test_record_action_observation_verification(self):
        mgr = WorkingMemoryManager.get_instance()
        mgr.create_task(task_id="TASK-102", user_goal="Add light")

        mgr.record_action("TASK-102", {"action_type": "create_light", "light_type": "POINT"})
        mgr.record_observation("TASK-102", {"light_name": "PointLight", "exists": True})
        mgr.record_verification("TASK-102", {"action_type": "create_light", "verified": True})

        snap = mgr.get_snapshot("TASK-102")
        assert len(snap["action_history"]) == 1
        assert len(snap["observations"]) == 1
        assert len(snap["verification_results"]) == 1
        assert snap["action_history"][0]["action_type"] == "create_light"

    def test_failure_and_recovery_recording(self):
        mgr = WorkingMemoryManager.get_instance()
        mgr.create_task(task_id="TASK-103", user_goal="Render frame")

        mgr.fail_node("TASK-103", "node_render", error_reason="GPU out of memory")
        mgr.record_recovery_attempt("TASK-103", {"strategy": "fallback_to_cpu", "result": "success"})

        snap = mgr.get_snapshot("TASK-103")
        assert snap["failure_count"] == 1
        assert snap["last_error"] == "GPU out of memory"
        assert snap["retry_count"] == 1
        assert len(snap["recovery_attempts"]) == 1

    def test_budget_accounting(self):
        mgr = WorkingMemoryManager.get_instance()
        task = mgr.create_task(task_id="TASK-104", user_goal="Budget test", max_steps=2, max_retries=1)

        assert task.is_budget_exceeded is False

        mgr.complete_node("TASK-104", "step1")
        mgr.complete_node("TASK-104", "step2")

        snap = mgr.get_snapshot("TASK-104")
        assert snap["steps_used"] == 2
        assert snap["is_budget_exceeded"] is True

    def test_task_isolation_and_clear(self):
        mgr = WorkingMemoryManager.get_instance()
        mgr.create_task(task_id="TASK-A", user_goal="Goal A")
        mgr.create_task(task_id="TASK-B", user_goal="Goal B")

        snap_a = mgr.get_snapshot("TASK-A")
        snap_b = mgr.get_snapshot("TASK-B")

        assert snap_a["user_goal"] == "Goal A"
        assert snap_b["user_goal"] == "Goal B"

        mgr.clear_task("TASK-A")
        assert mgr.get_snapshot("TASK-A") is None
        assert mgr.get_snapshot("TASK-B") is not None

    def test_separation_of_concerns_world_state_vs_working_memory(self):
        world_engine = WorldStateEngine.get_instance()
        world_snap = world_engine.get_snapshot()

        wm_mgr = WorkingMemoryManager.get_instance()
        wm_mgr.create_task(task_id="TASK-SEP", user_goal="Verify separation")
        wm_snap = wm_mgr.get_snapshot("TASK-SEP")

        # WorldState captures physical OS/App state
        assert "system" in world_snap.to_dict()
        assert "windows" in world_snap.to_dict()

        # WorkingMemory captures Nova's active task execution state
        assert "task_id" in wm_snap
        assert "user_goal" in wm_snap
        assert "action_history" in wm_snap
        assert "task_id" not in world_snap.to_dict()
