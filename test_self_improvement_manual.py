"""12-Stage Manual Validation Script for M3.4.11 Autonomous Self-Improvement Engine.
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

from app.ai.self_improvement import (
    UniversalSelfImprovementEngine,
    SelfImprovementConfiguration,
    EvaluationCycle,
    RegressionStatus,
    MockSelfImprovementProvider,
)
from app.ai.gateway import AIGateway


async def run_12_stage_validation():
    print("==================================================================")
    print("M3.4.11 – Autonomous Self-Improvement Engine Validation")
    print("==================================================================\n")

    engine = UniversalSelfImprovementEngine()

    # Stage 1: Core Package Init & PEP 562 Lazy Loader
    print("Stage 1: Core Package Init & PEP 562 Lazy Loader")
    assert engine.config.auto_distill_workflows is True
    print("  [OK] Self-Improvement package loaded successfully.\n")

    # Stage 2: Performance Analyzer
    print("Stage 2: Performance Analyzer (Subsystem Telemetry Snapshots)")
    perf_kernel = engine.performance_analyzer.analyze_subsystem("kernel")
    perf_copilot = engine.performance_analyzer.analyze_subsystem("copilot")
    print(f"  * Subsystem 'kernel': Latency = {perf_kernel.latency_ms}ms | Success Rate = {perf_kernel.success_rate*100}% | Memory = {perf_kernel.memory_usage_mb} MB")
    print(f"  * Subsystem 'copilot': Latency = {perf_copilot.latency_ms}ms | Success Rate = {perf_copilot.success_rate*100}% | Throughput = {perf_copilot.throughput_qps} QPS")
    assert perf_kernel.success_rate > 0.90
    print("  [OK] Performance Analyzer captured telemetry metrics.\n")

    # Stage 3: Workflow & Planner Optimizer
    print("Stage 3: Workflow & Planner Optimizer (Step Deduplication & Wave Parallelism)")
    wf_rec = engine.workflow_optimizer.optimize_workflow("wf_build", ["Requirement Analysis", "Codegen", "Codegen", "Testing"])
    plan_opt = engine.planner_optimizer.optimize_plan_decomposition("Deploy ERP", ["node_1", "node_2", "node_3"])
    print(f"  * Optimized Workflow Steps: {wf_rec.optimized_steps} (Latency Reduction: {wf_rec.latency_reduction_pct}%)")
    print(f"  * Planner Waves Parallelism Gain: {plan_opt['parallelism_gain_pct']}%")
    assert len(wf_rec.optimized_steps) == 3
    print("  [OK] Workflow & Planner Optimizers generated optimizations.\n")

    # Stage 4: Automation & Vision Optimizer
    print("Stage 4: Automation & Vision Optimizer (GUI Macro & Locator Accuracy)")
    auto_opt = engine.automation_optimizer.optimize_automation_script("macro_gst", ["click_btn", "click_btn", "enter_text"])
    vis_opt = engine.vision_optimizer.optimize_vision_locator(locator_accuracy=0.98)
    print(f"  * Automation Speedup Factor: {auto_opt['speedup_factor']}x | Optimized Actions: {auto_opt['optimized_actions']}")
    print(f"  * Vision Primary Strategy: '{vis_opt['primary_strategy']}' | Threshold: {vis_opt['ocr_confidence_threshold']}")
    assert vis_opt["primary_strategy"] == "accessibility_api"
    print("  [OK] Automation & Vision Optimizers tuned execution settings.\n")

    # Stage 5: Mission & Copilot Optimizer
    print("Stage 5: Mission & Copilot Optimizer (Pattern Extraction & Code Policies)")
    msn_opt = engine.mission_optimizer.analyze_completed_mission("msn_101", "Build E-Commerce Backend", tasks_count=4, duration_sec=120.0)
    cop_opt = engine.copilot_optimizer.optimize_copilot_pipeline(code_coverage_pct=94.5, bug_fix_rate=0.95)
    print(f"  * Mission Efficiency Score: {msn_opt['efficiency_score']} | Recommended Template: '{msn_opt['recommended_template']}'")
    print(f"  * Copilot Test Policy: '{cop_opt['test_generation_policy']}' | Refactoring: '{cop_opt['refactoring_aggressiveness']}'")
    assert msn_opt["efficiency_score"] > 0.90
    print("  [OK] Mission & Copilot Optimizers extracted reusable patterns.\n")

    # Stage 6: Conversation & Runtime Optimizer
    print("Stage 6: Conversation & Runtime Optimizer (Latency & VRAM GC Rules)")
    conv_opt = engine.conversation_optimizer.optimize_dialog_parameters(avg_turn_latency_ms=45.0, clarification_rate=0.05)
    run_opt = engine.runtime_optimizer.optimize_vram_allocation(used_vram_mb=4096, total_vram_mb=8192)
    print(f"  * Conversation Chunk Size: {conv_opt['recommended_chunk_size']} | Clarification Threshold: {conv_opt['clarification_threshold']}")
    print(f"  * Runtime VRAM Utilization: {run_opt['vram_utilization_pct']}% | Unload Policy: '{run_opt['unload_policy']}'")
    assert run_opt["unload_policy"] == "lazy_gc"
    print("  [OK] Conversation & Runtime Optimizers tuned resource rules.\n")

    # Stage 7: Experience Distillation & Skill Evolution
    print("Stage 7: Experience Distillation & Skill Evolution")
    exp_pkg = engine.experience_distiller.distill_experience("FastAPI E-Commerce Setup", ["Requirement Analysis", "Codegen", "Testing"])
    evolve_res = engine.skill_evolution.evaluate_workflow_frequency("FastAPI E-Commerce Setup", execution_count=4)
    print(f"  * Distilled Package: '{exp_pkg.name}' -> Reusable Skill ID: '{exp_pkg.reusable_skill_id}'")
    print(f"  * Skill Evolution: Should Evolve = {evolve_res['should_evolve']} | Skill ID = '{evolve_res['generated_skill_id']}'")
    assert exp_pkg.reusable_skill_id == "skill_fastapi_e-commerce_setup"
    assert evolve_res["should_evolve"] is True
    print("  [OK] Experience Distiller packaged reusable skills and templates.\n")

    # Stage 8: Agent Scorecard Evaluation
    print("Stage 8: Agent Scorecard Evaluation (Multi-Agent Workforce Scoring)")
    scorecards = engine.agent_optimizer.evaluate_agents()
    print(f"  * Total Agent Workforce Evaluated: {len(scorecards)}")
    for card in scorecards:
        print(f"  * Agent: '{card.agent_name}' ({card.role}) | Latency: {card.latency_ms}ms | Accuracy: {card.accuracy_score*100}% | Success: {card.success_rate*100}%")
    assert len(scorecards) >= 3
    print("  [OK] Agent Optimizer evaluated workforce scorecards.\n")

    # Stage 9: Benchmark & Quality Engine
    print("Stage 9: Benchmark & Quality Engine (Trend Reports & Regression Checks)")
    bench_report = engine.benchmark_engine.run_benchmark(EvaluationCycle.DAILY)
    qual_report = engine.quality_engine.check_quality()
    print(f"  * Historical Benchmark Overall Score: {bench_report.overall_score*100}% (Cycle: {bench_report.cycle.value})")
    print(f"  * Quality Diagnostic Status: '{qual_report.status.value}' | Regressions Found: {len(qual_report.regressions_found)}")
    assert bench_report.overall_score >= 0.90
    assert qual_report.status == RegressionStatus.NORMAL
    print("  [OK] Benchmark & Quality Engines generated diagnostic reports.\n")

    # Stage 10: Behavior, Goal & Feedback Engine
    print("Stage 10: Behavior, Goal & Feedback Engine (Adaptive Style & Ratings)")
    behavior_style = engine.behavior_optimizer.adapt_behavior_style(user_interaction_count=20)
    engine.feedback_engine.record_feedback("mission_101", 5.0, "Outstanding performance!")
    user_prof = engine.goal_optimizer.get_user_profile()
    print(f"  * Adaptive Speaking Style: '{behavior_style['speaking_style']}' (Safety Verified: {behavior_style['safety_lock_verified']})")
    print(f"  * User Rating Average: {engine.feedback_engine.get_average_rating()}/5.0 | User Tech Stack: {user_prof['primary_tech_stack']}")
    assert behavior_style["safety_lock_verified"] is True
    print("  [OK] Behavior & Goal Optimizers adapted system style safely.\n")

    # Stage 11: Learning Scheduler & Self Evaluator
    print("Stage 11: Learning Scheduler & Self Evaluator")
    self_eval = engine.self_evaluator.evaluate_self()
    cycle_res = engine.learning_scheduler.trigger_cycle(EvaluationCycle.DAILY)
    print(f"  * Self-Evaluation Score: {self_eval['overall_score']*100}% (Coding: {self_eval['coding_accuracy']*100}%, Reasoning: {self_eval['reasoning_quality']*100}%)")
    print(f"  * Learning Scheduler Cycle Status: '{cycle_res['status']}' (Next Run: in {cycle_res['next_run_in_hours']}h)")
    assert self_eval["overall_score"] > 0.90
    print("  [OK] Self Evaluator and Learning Scheduler executed.\n")

    # Stage 12: End-to-End System Self-Improvement Pass
    print("Stage 12: End-to-End System Self-Improvement Optimization Pass")
    pass_res = await engine.self_improve()
    metrics = await engine.get_metrics()
    health = await engine.check_health()
    print(f"  * Self-Improvement Pass Status: '{pass_res['status']}'")
    print(f"  * Experiences Distilled: {pass_res['experiences_distilled']} | Optimizations Applied: {metrics.optimizations_applied}")
    print(f"  * Health Status: Healthy = {health.is_healthy} | Total Optimizations: {health.total_optimizations_applied}")
    assert pass_res["status"] == "SUCCESS"
    assert health.is_healthy is True
    print("  [OK] End-to-end self-improvement optimization pass completed.\n")

    print("==================================================================")
    print("  ALL 12 STAGES PASSED SUCCESSFULLY!")
    print("  Autonomous Self-Improvement & Adaptive Intelligence Engine Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_12_stage_validation())
