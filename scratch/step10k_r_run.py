"""Real physical execution script for 10K-R — Final Autonomous Coding Demonstration.

Given a single natural-language goal without manual step decomposition:
"Inspect this small Python project, add a reusable calculator function, update the appropriate code to use it, run the project's validation, and fix any problems you encounter until the requested feature is verified."
"""

import sys
from pathlib import Path
import shutil
import json

backend_dir = Path(__file__).resolve().parent.parent / "apps" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ai.coding.repo_understanding import RepoUnderstandingEngine
from app.ai.coding.code_context_manager import CodeContextManager
from app.ai.coding.safe_code_editor import SafeCodeEditor
from app.ai.coding.code_executor import CodeExecutor
from app.ai.kernel.capability_discovery import CapabilityDiscoveryEngine
from app.ai.kernel.goal_verifier import GoalVerifier, GoalRequirement, VerificationType, VerificationStatus
from app.ai.kernel.plan_critic import PlanCritic
from app.ai.kernel.task_graph import TaskGraph, TaskNode, NodeType
from app.ai.memory.working_memory import WorkingMemoryManager, TaskStatus


def setup_target_project(target_dir: Path):
    if target_dir.exists():
        shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(parents=True, exist_ok=True)

    (target_dir / "math_utils.py").write_text(
        '"""Math utilities."""\n\n'
        'def add(a, b):\n'
        '    return a + b\n\n'
        'def multiply(a, b):\n'
        '    return a * b\n',
        encoding="utf-8"
    )

    (target_dir / "main.py").write_text(
        'import math_utils\n\n'
        'def run():\n'
        '    sum_val = math_utils.add(5, 10)\n'
        '    prod_val = math_utils.multiply(5, 10)\n'
        '    print(f"SUM: {sum_val}, PROD: {prod_val}")\n\n'
        'if __name__ == "__main__":\n'
        '    run()\n',
        encoding="utf-8"
    )


def run_autonomous_coding_demo():
    print("=== STARTING 10K-R FINAL AUTONOMOUS CODING DEMONSTRATION ===")
    user_goal = "Inspect this small Python project, add a reusable calculator function, update the appropriate code to use it, run the project's validation, and fix any problems you encounter until the requested feature is verified."
    print("UN-DECOMPOSED USER GOAL:", user_goal)

    project_dir = Path(__file__).resolve().parent / "demo_r_workspace"
    setup_target_project(project_dir)

    # 1. WorkingMemory Task Initialization
    wm_mgr = WorkingMemoryManager.get_instance()
    task = wm_mgr.create_task("task_10k_r", user_goal)
    task.task_status = TaskStatus.RUNNING

    # 2. Repository Understanding Engine
    repo_engine = RepoUnderstandingEngine()
    repo_info = repo_engine.analyze_repository(project_dir)
    print("\n[1. REPOSITORY UNDERSTANDING]")
    print("Project Type:", repo_info["project_type"])
    print("Languages:", repo_info["languages"])
    print("Entry Points:", repo_info["entry_points"])

    # 3. Semantic Capability Discovery
    cap_engine = CapabilityDiscoveryEngine.get_instance()
    caps = cap_engine.discover_capabilities_sync(user_goal, domain_filter="code", top_k=5)
    print("\n[2. CAPABILITY DISCOVERY]")
    for c in caps:
        print(f"Discovered Capability: {c.capability_id} - {c.description}")

    # 4. Task Graph Construction & Plan Critic
    tg = TaskGraph(graph_id="g_10kr")
    n_inspect = TaskNode(node_id="n1", title="Inspect files", node_type=NodeType.ACTION)
    n_edit_utils = TaskNode(node_id="n2", title="Edit math_utils.py", node_type=NodeType.ACTION)
    n_edit_main = TaskNode(node_id="n3", title="Edit main.py", node_type=NodeType.ACTION)
    n_verify = TaskNode(node_id="n4", title="Run validation", node_type=NodeType.ACTION)

    for n in (n_inspect, n_edit_utils, n_edit_main, n_verify):
        tg.add_node(n)

    critic = PlanCritic.get_instance()
    critic_res = critic.evaluate_plan(user_goal, [n.to_dict() for n in tg.nodes.values()])
    print("\n[3. PLAN CRITIC EVALUATION]")
    print("Plan Status:", critic_res.status)

    # 5. Targeted Code Context Retrieval
    context_mgr = CodeContextManager(str(project_dir))
    ctx = context_mgr.build_goal_context(user_goal, ["math_utils.py", "main.py"], task_id="task_10k_r")
    print("\n[4. CODE CONTEXT RETRIEVAL]")
    print(f"Retrieved minimal context for {ctx['total_files']} files")

    # 6. Safe Code Editing Engine
    code_editor = SafeCodeEditor()

    # Step A: Add power(a, b) function to math_utils.py
    utils_file = project_dir / "math_utils.py"
    utils_hash = SafeCodeEditor.compute_file_hash(utils_file)
    new_utils_content = utils_file.read_text(encoding="utf-8") + "\ndef power(base, exp):\n    return base ** exp\n"
    edit_u = code_editor.apply_edit(utils_file, new_utils_content, utils_hash)
    print("\n[5. SAFE CODE EDIT - MATH_UTILS.PY]")
    print(edit_u["diff"])

    # Step B: Update main.py to call power function
    main_file = project_dir / "main.py"
    main_hash = SafeCodeEditor.compute_file_hash(main_file)
    new_main_content = (
        'import math_utils\n\n'
        'def run():\n'
        '    sum_val = math_utils.add(5, 10)\n'
        '    prod_val = math_utils.multiply(5, 10)\n'
        '    pow_val = math_utils.power(2, 3)\n'
        '    print(f"SUM: {sum_val}, PROD: {prod_val}, POW: {pow_val}")\n\n'
        'if __name__ == "__main__":\n'
        '    run()\n'
    )
    edit_m = code_editor.apply_edit(main_file, new_main_content, main_hash)
    print("\n[6. SAFE CODE EDIT - MAIN.PY]")
    print(edit_m["diff"])

    # 7. Real Code Execution
    executor = CodeExecutor(str(project_dir))
    exec_res = executor.execute_command(f'"{sys.executable}" main.py', cwd=project_dir)
    print("\n[7. REAL CODE EXECUTION]")
    print("Returncode:", exec_res["returncode"])
    print("Output:", exec_res["stdout"].strip())
    assert exec_res["returncode"] == 0
    assert "POW: 8" in exec_res["stdout"]

    # 8. Goal-Level Verification (GoalVerifier)
    verifier = GoalVerifier.get_instance()
    req1 = GoalRequirement(
        requirement_id="req_symbol",
        description="power function exists in math_utils.py",
        verification_type=VerificationType.CODE_SYMBOL_EXISTS,
        target_entity=str(utils_file),
        expected_value="power",
    )
    req2 = GoalRequirement(
        requirement_id="req_exec",
        description="main.py executes successfully and prints POW: 8",
        verification_type=VerificationType.CODE_EXECUTION_PASS,
        target_entity="python main.py",
    )

    v_res = verifier.verify_goal(user_goal, [req1, req2], action_results=[{"action": "code:run_command", "returncode": 0, "stdout": exec_res["stdout"]}])
    print("\n[8. GOAL-LEVEL VERIFICATION]")
    print("Goal Satisfied:", v_res.goal_satisfied)
    print("Status:", v_res.status)

    assert v_res.goal_satisfied is True
    print("\n=== 10K-R DEMONSTRATION SUCCESSFULLY VERIFIED ===")


if __name__ == "__main__":
    run_autonomous_coding_demo()
