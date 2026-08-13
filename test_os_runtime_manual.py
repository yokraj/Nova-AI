"""20-Stage Manual Validation Script for M3.4.16 AI Operating System Core & Always-On Voice Runtime.
"""

import asyncio
import os
import sys

# Ensure UTF-8 output encoding for Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add apps/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "apps/backend")))

from app.ai.os_runtime import (
    NovaOperatingSystemEngine,
    OSRuntimeConfiguration,
    OSState,
    MockOSRuntimeProvider,
)


async def run_20_stage_validation():
    print("==================================================================")
    print("M3.4.16 – AI Operating System Core & Always-On Voice Runtime")
    print("==================================================================\n")

    engine = NovaOperatingSystemEngine()

    # Stage 1: Core Package Init & PEP 562 Lazy Loader
    print("Stage 1: Core OS Runtime Package Init & PEP 562 Lazy Loader")
    assert engine.config.always_on_voice_enabled is True
    print(f"  * OS Name: '{engine.config.os_name}' v{engine.config.os_version} | Environment: '{engine.config.environment}'")
    print("  [OK] OS Runtime package loaded successfully.\n")

    # Stage 2: Dependency-Aware Boot Manager Sequence (25 Subsystems)
    print("Stage 2: Dependency-Aware Boot Manager Sequence (25 Subsystems)")
    boot_diag = await engine.start_os()
    print(f"  * Boot Duration: {boot_diag.duration_sec}s | Success = {boot_diag.success}")
    print(f"  * Loaded Subsystems Count: {len(boot_diag.subsystems_loaded)} (First 5: {boot_diag.subsystems_loaded[:5]})")
    assert boot_diag.success is True and len(boot_diag.subsystems_loaded) >= 20
    print("  [OK] Boot Manager sequence executed successfully.\n")

    # Stage 3: Windows Service Manager, Task Scheduler & Startup Daemon
    print("Stage 3: Windows Service Manager, Task Scheduler & System Tray Daemon")
    win_svc = engine.service_manager.register_windows_startup()
    print(f"  * Windows Service: '{win_svc['service_name']}' | Type: '{win_svc['startup_type']}' | System Tray = {win_svc['system_tray_enabled']}")
    assert win_svc["status"] == "REGISTERED_WINDOWS_SERVICE"
    print("  [OK] Windows Service Manager registered startup daemon.\n")

    # Stage 4: User Login Detection & Session Restoration Manager
    print("Stage 4: User Login Detection & Session Restoration Manager")
    restore_res = await engine.startup_manager.restore_session_state()
    print(f"  * Restored Workspace: '{restore_res['restored_workspace']}' | Resumed Missions: {restore_res['resumed_missions_count']}")
    assert restore_res["status"] == "SESSION_RESTORED"
    print("  [OK] Startup Manager restored user session state.\n")

    # Stage 5: Always-On Voice Runtime (Wake Word -> STT -> LLM -> TTS Stream)
    print("Stage 5: Always-On Voice Runtime (Wake Word -> STT -> LLM -> TTS Stream)")
    voice_turn = await engine.voice_runtime.process_voice_turn()
    print(f"  * Configured Wake Word: '{engine.voice_runtime.wake_word}' | Detected = {voice_turn['wake_word_detected']}")
    print(f"  * STT Transcript: '{voice_turn['transcript']}'")
    print(f"  * LLM Response: '{voice_turn['model_response']}'")
    assert voice_turn["tts_audio_generated"] is True
    print("  [OK] Always-On Voice Runtime processed voice turn pipeline.\n")

    # Stage 6: Context Runtime (Background Window, Browser, Clipboard & Telemetry Monitor)
    print("Stage 6: Context Runtime (Background Desktop, Window, Browser & Hardware Monitor)")
    ctx = await engine.context_runtime.get_unified_context_snapshot()
    print(f"  * Active Window: '{ctx['active_window']}' | Browser Tab: '{ctx['browser_tab']}'")
    print(f"  * Hardware Telemetry: CPU = {ctx['hardware_telemetry']['cpu_percent']}% | RAM = {ctx['hardware_telemetry']['ram_used_mb']} MB | VRAM = {ctx['hardware_telemetry']['vram_used_mb']} MB")
    assert ctx["user_presence"] == "ACTIVE"
    print("  [OK] Context Runtime captured unified environment snapshot.\n")

    # Stage 7: Global Event Runtime (Central Pub-Sub Event Bus Across All 25 Subsystems)
    print("Stage 7: Global Event Runtime (Central Pub-Sub Event Bus Across 25 Subsystems)")
    event_log = []
    engine.event_runtime.subscribe("MISSION_COMPLETED", lambda e: event_log.append(e))
    pub_evt = await engine.event_runtime.publish_event("MISSION_COMPLETED", {"mission_id": "msn_001", "name": "Monthly GST Filing"})
    print(f"  * Published Event ID: '{pub_evt.event_id}' | Type = '{pub_evt.event_type}' | Source = '{pub_evt.source}'")
    print(f"  * Event Bus Subscribers Triggered: {len(event_log)} callback(s) executed")
    assert len(event_log) == 1 and pub_evt.event_type == "MISSION_COMPLETED"
    print("  [OK] Global Event Runtime pub-sub bus verified.\n")

    # Stage 8: Unified Scheduler Runtime (Consolidated Priority Cron/Timer Queue)
    print("Stage 8: Unified Scheduler Runtime (Consolidated Priority Cron/Timer Queue)")
    sched_job = await engine.scheduler_runtime.schedule_job("Hourly Log Backup", category="backup", interval_seconds=3600)
    all_jobs = engine.scheduler_runtime.list_jobs()
    print(f"  * Scheduled Job: Name = '{sched_job.name}' | Category = '{sched_job.category}' | Job ID = '{sched_job.job_id}'")
    print(f"  * Total Active Jobs in Unified Queue: {len(all_jobs)}")
    assert len(all_jobs) >= 1 and sched_job.category == "backup"
    print("  [OK] Unified Scheduler Runtime registered cron/timer job.\n")

    # Stage 9: Continuous Decision Loop Runtime (Observe -> Reason -> Plan -> Execute)
    print("Stage 9: Continuous Decision Loop Runtime (Observe -> Understand -> Reason -> Plan -> Execute)")
    decision = await engine.decision_runtime.execute_cycle()
    print(f"  * Decision Phase: '{decision['phase']}'")
    print(f"  * Observation: '{decision['observation']}'")
    print(f"  * Reasoning & Intent: '{decision['reasoning']}'")
    assert decision["phase"] == "DECISION_CYCLE_COMPLETED"
    print("  [OK] Continuous Decision Loop Runtime executed reasoning iteration.\n")

    # Stage 10: Interrupt Runtime (Speech Barge-In & TTS/Task Pausing)
    print("Stage 10: Interrupt Runtime (Speech Barge-In & TTS/Task Pausing)")
    barge_in = await engine.interrupt_runtime.handle_user_barge_in()
    resume = await engine.interrupt_runtime.resume_after_interrupt()
    print(f"  * Barge-In Interruption Handled: TTS Paused = {barge_in['tts_paused']} | Listening Active = {barge_in['listening_active']}")
    print(f"  * Resumed Execution: Automation Resumed = {resume['automation_resumed']}")
    assert barge_in["tts_paused"] is True and resume["automation_resumed"] is True
    print("  [OK] Interrupt Runtime handled speech barge-in.\n")

    # Stage 11: Background Idle Runtime (Memory Compression, Model Pre-load & Indexing)
    print("Stage 11: Background Idle Runtime (Memory Compression, Model Pre-load & Indexing)")
    idle_opt = await engine.idle_runtime.run_idle_optimization()
    print(f"  * Idle Optimizations Executed: Conversations Compressed = {idle_opt['conversations_compressed']} | Models Preloaded = {idle_opt['models_preloaded']} | Files Indexed = {idle_opt['files_indexed']}")
    assert idle_opt["status"] == "IDLE_OPTIMIZATION_COMPLETED"
    print("  [OK] Background Idle Runtime completed optimizations.\n")

    # Stage 12: Proactive Recommendation Runtime (Deadlines, Security Alerts & Automation Opportunities)
    print("Stage 12: Proactive Recommendation Runtime (Deadlines, Security Alerts & Automation)")
    recs = await engine.proactive_runtime.generate_recommendations()
    print(f"  * Total Active Recommendations: {len(recs)}")
    for rec in recs:
        print(f"    - [{rec['category'].upper()}] {rec['title']}: '{rec['message']}'")
    assert len(recs) >= 2 and recs[0]["category"] == "security"
    print("  [OK] Proactive Recommendation Runtime generated suggestions.\n")

    # Stage 13: Multi-Workspace Session Runtime & Context Switching
    print("Stage 13: Multi-Workspace Session Runtime & Context Switching")
    sess = await engine.session_runtime.get_active_session()
    switched_sess = await engine.session_runtime.switch_workspace("Nova AI Developer Workspace")
    print(f"  * Active User Session: User = '{sess.user_id}' | Session ID = '{sess.session_id}'")
    print(f"  * Switched Active Workspace: '{switched_sess.active_workspace}'")
    assert switched_sess.active_workspace == "Nova AI Developer Workspace"
    print("  [OK] Session Runtime managed multi-workspace switching.\n")

    # Stage 14: Self-Healing Recovery Runtime (Crashed Subsystem Auto-Restoration)
    print("Stage 14: Self-Healing Recovery Runtime (Crashed Subsystem Auto-Restoration)")
    recovery = await engine.recovery_runtime.recover_subsystem("Desktop Automation Engine", "Display driver timeout")
    print(f"  * Subsystem Recovery: Target = '{recovery['subsystem']}' | Action = '{recovery['action']}'")
    print(f"  * Self-Healing Status: Recovered = {recovery['recovered']} -> Status: {recovery['status']}")
    assert recovery["recovered"] is True and recovery["status"] == "SELF_HEALED"
    print("  [OK] Self-Healing Recovery Runtime restored subsystem.\n")

    # Stage 15: Unified Administrative Dashboard & Telemetry APIs
    print("Stage 15: Unified Administrative Dashboard & Telemetry APIs")
    dash = await engine.os_dashboard()
    print(f"  * OS State: '{dash.os_state}' | Uptime: {dash.uptime_seconds}s | Health Score = {dash.health_score}/100")
    print(f"  * Active Workforce Agents ({len(dash.active_agents)}): {dash.active_agents}")
    print(f"  * Loaded Local AI Models ({len(dash.active_models)}): {dash.active_models}")
    print(f"  * Running Missions: {dash.running_missions_count} | Running Workflows: {dash.running_workflows_count}")
    assert dash.health_score == 100.0 and len(dash.active_agents) >= 3
    print("  [OK] Dashboard Runtime API snapshot verified.\n")

    # Stage 16: Multi-Channel Notification Runtime (Voice, Toast, System Tray & Email)
    print("Stage 16: Multi-Channel Notification Runtime (Voice, Toast, System Tray & Email)")
    notif = await engine.notification_runtime.notify("GST Filing", "Monthly GST Return filed successfully.", channel="voice_and_toast")
    print(f"  * Notification Dispatched: ID = '{notif.notification_id}' | Title = '{notif.title}' | Channel = '{notif.channel}'")
    assert notif.title == "GST Filing" and notif.channel == "voice_and_toast"
    print("  [OK] Multi-Channel Notification Runtime dispatched alert.\n")

    # Stage 17: Resource Allocation & Dynamic VRAM/RAM Garbage Collection
    print("Stage 17: Resource Allocation & Dynamic VRAM/RAM Garbage Collection")
    res_opt = await engine.resource_runtime.optimize_resources()
    print(f"  * Resource GC Results: Freed VRAM = {res_opt['vram_freed_mb']} MB | Freed RAM = {res_opt['ram_freed_mb']} MB | Models Unloaded = {res_opt['models_unloaded']}")
    assert res_opt["status"] == "RESOURCES_OPTIMIZED"
    print("  [OK] Resource Runtime executed dynamic GC.\n")

    # Stage 18: Central Security Policy Engine & Emergency Stop Kill Switch
    print("Stage 18: Central Security Policy Engine & Emergency Stop Kill Switch")
    sec_policy = await engine.security_runtime.get_policy()
    print(f"  * Central Security Policy: Enforce Approvals = {sec_policy.enforce_approval_holds} | Encrypted Storage = {sec_policy.encrypted_storage_active}")

    kill_res = await engine.emergency_stop()
    print(f"  * Emergency Kill Switch Action: State = '{kill_res['state']}' | Activated = {kill_res['kill_switch_activated']}")
    assert kill_res["kill_switch_activated"] is True and kill_res["state"] == OSState.EMERGENCY_STOP
    print("  [OK] Central Security Policy Engine and Emergency Kill Switch verified.\n")

    # Stage 19: Dynamic Plugin Hot Reload Runtime (Zero-Restart Skill Updates)
    print("Stage 19: Dynamic Plugin Hot Reload Runtime (Zero-Restart Skill Updates)")
    plugin_reload = await engine.plugin_runtime.hot_reload_plugin("skill_vscode")
    print(f"  * Hot Reload Plugin: '{plugin_reload['plugin_name']}' | Status = {plugin_reload['status']} | Zero-Restart = {plugin_reload['no_restart_required']}")
    assert plugin_reload["no_restart_required"] is True
    print("  [OK] Plugin Runtime hot reloaded skill module without restarting OS.\n")

    # Stage 20: Cross-Platform Distributed Runtime Interface Preparation
    print("Stage 20: Cross-Platform Distributed Runtime Interface Preparation")
    dist_res = await engine.distributed_runtime.orchestrate_node("node_linux_rtx4090", "check_gpu_temperature")
    print(f"  * Distributed Node Task: Target Node = '{dist_res['target_node']}' | Command = '{dist_res['command']}' | Orchestrated = {dist_res['orchestrated']}")
    assert dist_res["orchestrated"] is True
    print("  [OK] Distributed Runtime interface preparation verified.\n")

    print("==================================================================")
    print("  ALL 20 STAGES PASSED SUCCESSFULLY!")
    print("  Nova AI Operating System Core & Always-On Voice Runtime Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_20_stage_validation())
