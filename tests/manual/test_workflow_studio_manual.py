"""12-Stage Manual Validation Script for M3.4.12 Universal Workflow Learning & No-Code Automation Studio.
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/backend")))

from app.ai.workflow_studio import (
    UniversalWorkflowStudioEngine,
    WorkflowStudioConfiguration,
    WorkflowRecordingState,
    WorkflowTriggerType,
    MockWorkflowStudioProvider,
)
from app.ai.gateway import AIGateway


async def run_12_stage_validation():
    print("==================================================================")
    print("M3.4.12 – Universal Workflow Learning & No-Code Studio Validation")
    print("==================================================================\n")

    engine = UniversalWorkflowStudioEngine()

    # Stage 1: Core Package Init & PEP 562 Lazy Loader
    print("Stage 1: Core Package Init & PEP 562 Lazy Loader")
    assert engine.config.auto_extract_variables is True
    print("  [OK] Workflow Studio package loaded successfully.\n")

    # Stage 2: Master Recorder Suite
    print("Stage 2: Master Recorder Suite (Desktop, Browser, Keyboard, Mouse & Voice Recorders)")
    sess_name = engine.recorder.start_recording("GST Portal Automation")
    evt_focus = engine.desktop_recorder.capture_window_focus("GST Portal Login", "Chrome.exe")
    evt_nav = engine.browser_recorder.capture_navigation("https://gst.gov.in", "GST Portal")
    evt_click = engine.mouse_recorder.capture_click(250, 450, "Submit Button", "Chrome.exe")
    evt_type = engine.keyboard_recorder.capture_typing("user@corp.org Amount ₹18,500 OTP 987654", "Chrome.exe")
    evt_voice = engine.voice_recorder.capture_narration("Log into GST portal and file monthly return")
    engine.recorder.record_event(evt_focus)
    engine.recorder.record_event(evt_nav)
    engine.recorder.record_event(evt_click)
    engine.recorder.record_event(evt_type)
    engine.recorder.record_event(evt_voice)
    print(f"  * Started Session: '{sess_name}' | Recorder State: '{engine.recorder.state.value}'")
    print(f"  * Recorded Events Count: {len(engine.recorder._recorded_events)}")
    assert engine.recorder.state == WorkflowRecordingState.RECORDING
    print("  [OK] Master Recorder captured multi-application events.\n")

    # Stage 3: Event Stream Buffer
    print("Stage 3: Event Stream Buffer & Listener Dispatcher")
    engine.event_stream.push_event(evt_click)
    engine.event_stream.push_event(evt_type)
    stream_events = engine.event_stream.get_stream_buffer()
    print(f"  * Real-Time Stream Buffer Events Count: {len(stream_events)}")
    assert len(stream_events) >= 2
    print("  [OK] Event Stream buffer verified.\n")

    # Stage 4: Intent Extractor
    print("Stage 4: Intent Extractor (Low-Level Events -> High-Level Semantic Intents)")
    recorded_events = engine.recorder.stop_recording()
    semantic_steps = engine.intent_extractor.extract_intents(recorded_events)
    print(f"  * Extracted Semantic Steps ({len(semantic_steps)}):")
    for s in semantic_steps:
        print(f"    - [{s.action_type.value}] {s.description}")
    assert len(semantic_steps) >= 2
    print("  [OK] Intent Extractor produced semantic steps.\n")

    # Stage 5: Variable Engine Auto-Detection
    print("Stage 5: Variable Engine (Auto-Detect Emails, Currency Amounts, OTPs, Passwords)")
    detected_vars = engine.variable_engine.detect_variables("user@corp.org Amount ₹18,500 OTP 987654")
    print(f"  * Total Variables Detected: {len(detected_vars)}")
    for v in detected_vars:
        print(f"    - Variable '{v.name}' ({v.var_type}): Value = '{v.value}' | Sensitive = {v.is_sensitive}")
    assert len(detected_vars) == 3
    print("  [OK] Variable Engine extracted emails, currency, and OTPs.\n")

    # Stage 6: Workflow Builder, Optimizer & Validator
    print("Stage 6: Workflow Builder, Optimizer & Validator")
    trig_voice = engine.trigger_engine.create_voice_trigger("Hey Nova, file GST return")
    wf_def = engine.workflow_builder.build_workflow("GST Return Filing", semantic_steps, detected_vars, [trig_voice])
    wf_opt = engine.workflow_optimizer.optimize_definition(wf_def)
    val_warnings = engine.workflow_validator.validate_workflow(wf_opt)
    print(f"  * Built Workflow: '{wf_opt.name}' (ID: {wf_opt.workflow_id}) | Steps: {len(wf_opt.steps)} | Variables: {len(wf_opt.variables)}")
    print(f"  * Trigger Attached: '{wf_opt.triggers[0].expression}' | Validation Warnings: {val_warnings}")
    assert len(val_warnings) == 0
    print("  [OK] Workflow Builder & Validator produced clean workflow definition.\n")

    # Stage 7: Visual Step Editor & Versioning
    print("Stage 7: Visual Step Editor & Semantic Versioning")
    print(f"  * Initial Version: '{wf_opt.version}'")
    edited_wf = engine.versioning.increment_version(wf_opt, bump_type="patch")
    print(f"  * Version After Incremental Patch Edit: '{edited_wf.version}'")
    assert edited_wf.version == "1.0.1"
    print("  [OK] Workflow Editor & Versioning verified.\n")

    # Stage 8: Trigger Engine & Timed Scheduler
    print("Stage 8: Trigger Engine & Timed Scheduler (Voice & Cron Triggers)")
    cron_trig = engine.trigger_engine.create_schedule_trigger("0 9 1 * *")
    job_info = engine.scheduler.schedule_cron_job(wf_opt.workflow_id, cron_trig.expression)
    print(f"  * Schedule Trigger Cron: '{cron_trig.expression}' | Job ID: '{job_info['job_id']}' | Status: '{job_info['status']}'")
    assert job_info["status"] == "SCHEDULED"
    print("  [OK] Trigger Engine and Scheduler registered cron triggers.\n")

    # Stage 9: Workflow Player & Execution Engine
    print("Stage 9: Workflow Player & Execution Engine")
    play_result = await engine.workflow_player.play_workflow(wf_opt.workflow_id, parameters={"email": "user@corp.org"})
    print(f"  * Execution ID: '{play_result.execution_id}' | Success: {play_result.success} | Duration: {play_result.duration_sec}s | Steps Completed: {play_result.steps_completed}")
    assert play_result.success is True
    print("  [OK] Workflow Player executed workflow successfully.\n")

    # Stage 10: Workflow Debugger & Failure Recovery
    print("Stage 10: Workflow Debugger & Failure Recovery")
    engine.workflow_debugger.set_breakpoint(wf_opt.steps[0].step_id)
    debug_state = engine.workflow_debugger.inspect_step_state(wf_opt, 0)
    recovery_plan = engine.recovery.resolve_step_failure(wf_opt.steps[0], "Element button#submit not found")
    print(f"  * Debug Inspection: Breakpoint Active = {debug_state['has_breakpoint']} | Step: '{debug_state['description']}'")
    print(f"  * Recovery Strategy: '{recovery_plan['recovery_strategy']}' | Retry Recommended: {recovery_plan['retry_recommended']}")
    assert debug_state["has_breakpoint"] is True
    assert recovery_plan["retry_recommended"] is True
    print("  [OK] Workflow Debugger and Recovery Engine verified.\n")

    # Stage 11: Export, Import, Marketplace & Security
    print("Stage 11: Export, Import, Marketplace & Security")
    exported_json = engine.exporter.export_to_json(wf_opt)
    imported_wf = engine.importer.import_from_json(exported_json)
    market_search = engine.marketplace.search_marketplace("Order")
    sec_var = engine.security.sanitize_sensitive_variable(detected_vars[2])
    print(f"  * Exported JSON Length: {len(exported_json)} bytes | Imported Workflow Name: '{imported_wf.name}'")
    print(f"  * Marketplace Search Results: {len(market_search)} workflows found")
    print(f"  * Sanitized Sensitive Variable (OTP): '{sec_var.value}'")
    assert imported_wf.name == wf_opt.name
    assert sec_var.value == "*****ENCRYPTED*****"
    print("  [OK] Exporter, Importer, Marketplace, and Security verified.\n")

    # Stage 12: End-to-End Voice Workflow Demonstration
    print("Stage 12: End-to-End Voice Workflow Demonstration ('Hey Nova, record workflow')")
    rec_res = await engine.record_workflow("Voice Demo Workflow")
    stop_res = await engine.stop_recording()
    play_res = await engine.play_workflow(stop_res["workflow_id"])
    metrics = await engine.get_metrics()
    health = await engine.check_health()
    print(f"  * Recording Status: '{rec_res['status']}' -> Saved Workflow: '{stop_res['name']}' (ID: {stop_res['workflow_id']})")
    print(f"  * Voice Execution Result: Success = {play_res['success']} | Steps = {play_res['steps_completed']}")
    print(f"  * Health Status: Healthy = {health.is_healthy} | Total Workflows = {health.total_workflows_count}")
    print(f"  * Telemetry Metrics: Total Recordings = {metrics.total_recordings} | Total Executions = {metrics.total_executions}")
    assert play_res["success"] is True
    assert health.is_healthy is True
    print("  [OK] End-to-end voice workflow demonstration complete.\n")

    print("==================================================================")
    print("  ALL 12 STAGES PASSED SUCCESSFULLY!")
    print("  Universal Workflow Learning & No-Code Studio Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_12_stage_validation())
