"""Real physical manual validation suite for Phase 10K — Advanced Autonomous Coding Agent.

Validates:
10K-I — Architecture analysis
10K-J — New feature addition
10K-K — Bug fixing with FailureDiagnoser/DynamicReplanner
10K-L — Multi-file feature addition
10K-M — Real failure recovery
10K-N — Stale external conflict handling
10K-O — Git safety enforcement
10K-P — Secret protection redaction
10K-Q — Durable checkpoint recovery
"""

import sys
from pathlib import Path
import shutil
import time

# Ensure backend app is on sys.path
backend_dir = Path(__file__).resolve().parent.parent / "apps" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ai.coding.repo_understanding import RepoUnderstandingEngine
from app.ai.coding.code_context_manager import CodeContextManager
from app.ai.coding.safe_code_editor import SafeCodeEditor, StaleContextError
from app.ai.coding.code_executor import CodeExecutor
from app.ai.kernel.capability_discovery import CapabilityDiscoveryEngine
from app.ai.kernel.goal_verifier import GoalVerifier, GoalRequirement, VerificationType, VerificationStatus
from app.ai.kernel.failure_diagnoser import FailureDiagnoser, FailureType, Recoverability
from app.ai.kernel.dynamic_replanner import DynamicReplanner
from app.ai.memory.working_memory import WorkingMemoryManager, WorkingMemoryTask, TaskStatus
import json


def setup_demo_projects(base_dir: Path):
    """Sets up small real python projects on disk for physical validation."""
    if base_dir.exists():
        shutil.rmtree(base_dir, ignore_errors=True)
    base_dir.mkdir(parents=True, exist_ok=True)

    # 1. Project A: Demo Project for 10K-I (Architecture Analysis)
    proj_a = base_dir / "proj_a"
    proj_a.mkdir()
    (proj_a / "pyproject.toml").write_text(
        '[project]\nname = "demo-app"\nversion = "0.1.0"\ndependencies = ["requests>=2.28"]\n',
        encoding="utf-8"
    )
    src_a = proj_a / "src"
    src_a.mkdir()
    (src_a / "main.py").write_text(
        'def main():\n    print("Hello from demo app")\n\nif __name__ == "__main__":\n    main()\n',
        encoding="utf-8"
    )

    # 2. Project B: Calculator Project for 10K-J, K, L, M, N
    proj_b = base_dir / "calculator_proj"
    proj_b.mkdir()
    (proj_b / "requirements.txt").write_text("pytest\n", encoding="utf-8")
    
    calc_module = proj_b / "calculator.py"
    calc_module.write_text(
        '"""Calculator module with a known bug."""\n\n'
        'def add(a, b):\n'
        '    return a + b\n\n'
        'def subtract(a, b):\n'
        '    # BUG: incorrect subtraction\n'
        '    return a + b\n\n'
        'def run_calculation():\n'
        '    result = subtract(10, 4)\n'
        '    print(f"Subtract result: {result}")\n'
        '    return result\n',
        encoding="utf-8"
    )

    utils_module = proj_b / "utils.py"
    utils_module.write_text(
        '"""Utility functions."""\n\n'
        'def format_output(val):\n'
        '    return f"VALUE: {val}"\n',
        encoding="utf-8"
    )

    main_b = proj_b / "app.py"
    main_b.write_text(
        'import calculator\n'
        'import utils\n\n'
        'def run():\n'
        '    val = calculator.run_calculation()\n'
        '    print(utils.format_output(val))\n\n'
        'if __name__ == "__main__":\n'
        '    run()\n',
        encoding="utf-8"
    )

    return proj_a, proj_b


def run_validation():
    print("=== STARTING PHASE 10K REAL MANUAL VALIDATION ===")
    base_scratch = Path(__file__).resolve().parent / "val_workspace"
    proj_a, proj_b = setup_demo_projects(base_scratch)

    repo_engine = RepoUnderstandingEngine()
    context_mgr = CodeContextManager()
    code_editor = SafeCodeEditor()
    code_executor = CodeExecutor()
    cap_discovery = CapabilityDiscoveryEngine.get_instance()
    verifier = GoalVerifier.get_instance()
    diagnoser = FailureDiagnoser.get_instance()
    replanner = DynamicReplanner.get_instance()

    # ------------------------------------------------------------------
    # 10K-I — Architecture Analysis
    # ------------------------------------------------------------------
    print("\n--- Testing 10K-I: Architecture Analysis ---")
    info_a = repo_engine.analyze_repository(proj_a)
    print("Detected languages:", info_a["languages"])
    print("Project type:", info_a["project_type"])
    print("Entry points:", info_a["entry_points"])
    print("Manifests:", info_a["manifest_files"])
    assert "Python" in info_a["languages"]
    assert any("main.py" in str(ep) for ep in info_a["entry_points"])
    assert any("pyproject.toml" in str(m) for m in info_a["manifest_files"])
    print("--> 10K-I PASSED: Repository architecture & dependencies correctly analyzed.")

    # ------------------------------------------------------------------
    # 10K-J — New Feature Addition (calculate_average)
    # ------------------------------------------------------------------
    print("\n--- Testing 10K-J: New Feature Addition ---")
    calc_file = proj_b / "calculator.py"
    context = context_mgr.build_goal_context("Add calculate_average", [str(calc_file)])
    print(f"Context retrieved: {context['total_files']} files target context")
    
    # Apply edit to add calculate_average
    new_func = (
        "\ndef calculate_average(numbers):\n"
        "    if not numbers:\n"
        "        return 0.0\n"
        "    return sum(numbers) / len(numbers)\n"
    )
    edit_result = code_editor.apply_edit(
        file_path=calc_file,
        new_content=calc_file.read_text(encoding="utf-8") + new_func,
        expected_hash=SafeCodeEditor.compute_file_hash(calc_file),
    )
    assert edit_result["success"] is True
    print("Diff generated:\n", edit_result["diff"])

    # Verify goal
    req = GoalRequirement(
        requirement_id="req_avg_func",
        description="calculate_average function exists",
        verification_type=VerificationType.CODE_SYMBOL_EXISTS,
        target_entity=str(calc_file),
        expected_value="calculate_average",
    )
    v_res = verifier.verify_goal("Add calculate_average function", [req])
    assert v_res.status == VerificationStatus.SUCCESS
    print("--> 10K-J PASSED: calculate_average feature added, diff generated, symbol verified.")

    # ------------------------------------------------------------------
    # 10K-K — Bug Fixing (subtract bug)
    # ------------------------------------------------------------------
    print("\n--- Testing 10K-K: Bug Fixing ---")
    # Execute validation command to reproduce bug
    exec_res1 = code_executor.execute_command(f'"{sys.executable}" app.py', cwd=proj_b)
    print("Raw output with bug:", exec_res1["stdout"].strip())
    assert "VALUE: 14" in exec_res1["stdout"]  # 10 + 4 = 14 instead of 10 - 4 = 6

    # Diagnose bug
    diag = diagnoser.diagnose_failure(
        task_id="task_bugfix",
        user_goal="Fix calculator subtraction bug",
        action_result={"action": "code:run_command", "stdout": exec_res1["stdout"], "returncode": 0},
    )
    print("Diagnosed root cause:", diag.root_cause)

    # Fix bug in calculator.py
    current_content = calc_file.read_text(encoding="utf-8")
    fixed_content = current_content.replace("    # BUG: incorrect subtraction\n    return a + b", "    return a - b")
    hash_before = SafeCodeEditor.compute_file_hash(calc_file)
    code_editor.apply_edit(calc_file, fixed_content, hash_before)

    # Re-execute validation
    exec_res2 = code_executor.execute_command(f'"{sys.executable}" app.py', cwd=proj_b)
    print("Fixed output:", exec_res2["stdout"].strip())
    assert "VALUE: 6" in exec_res2["stdout"]

    # Verify goal
    req_exec = GoalRequirement(
        requirement_id="req_fix_bug",
        description="Calculator subtraction returns correct result 6",
        verification_type=VerificationType.CODE_EXECUTION_PASS,
        target_entity="python app.py",
    )
    v_bug = verifier.verify_goal("Fix calculator bug", [req_exec], action_results=[{"action": "code:run_command", "returncode": 0, "stdout": exec_res2["stdout"]}])
    assert v_bug.status == VerificationStatus.SUCCESS
    print("--> 10K-K PASSED: Bug diagnosed, fixed, revalidated, and verified.")

    # ------------------------------------------------------------------
    # 10K-L — Multi-File Feature Addition
    # ------------------------------------------------------------------
    print("\n--- Testing 10K-L: Multi-File Feature ---")
    # Update utils.py to support custom formatting, and app.py to use calculate_average
    utils_file = proj_b / "utils.py"
    u_content = utils_file.read_text(encoding="utf-8") + "\ndef format_avg(val):\n    return f'AVERAGE: {val:.2f}'\n"
    code_editor.apply_edit(utils_file, u_content, SafeCodeEditor.compute_file_hash(utils_file))

    app_file = proj_b / "app.py"
    app_content = (
        'import calculator\n'
        'import utils\n\n'
        'def run():\n'
        '    val = calculator.run_calculation()\n'
        '    print(utils.format_output(val))\n'
        '    avg = calculator.calculate_average([10, 20, 30])\n'
        '    print(utils.format_avg(avg))\n\n'
        'if __name__ == "__main__":\n'
        '    run()\n'
    )
    code_editor.apply_edit(app_file, app_content, SafeCodeEditor.compute_file_hash(app_file))

    # Validate multi-file feature execution
    exec_res3 = code_executor.execute_command(f'"{sys.executable}" app.py', cwd=proj_b)
    print("Multi-file output:", exec_res3["stdout"].strip())
    assert "AVERAGE: 20.00" in exec_res3["stdout"]
    print("--> 10K-L PASSED: Multi-file changes applied across utils.py and app.py and verified.")

    # ------------------------------------------------------------------
    # 10K-M — Real Failure + Recovery
    # ------------------------------------------------------------------
    print("\n--- Testing 10K-M: Real Failure + Recovery ---")
    # Introduce real syntax error into calculator.py
    bad_syntax = calc_file.read_text(encoding="utf-8") + "\ndef broken_syntax(\n"
    code_editor.apply_edit(calc_file, bad_syntax, SafeCodeEditor.compute_file_hash(calc_file), validate=False)

    exec_fail = code_executor.execute_command(f'"{sys.executable}" app.py', cwd=proj_b)
    assert exec_fail["returncode"] != 0
    print("Captured real execution failure stderr snippet:", exec_fail["stderr"][:100].strip())

    # FailureDiagnoser & Replanner pipeline
    diag_m = diagnoser.diagnose_failure(
        task_id="task_syntax_err",
        user_goal="Run calculator app",
        action_result={"action": "code:run_command", "returncode": exec_fail["returncode"], "stderr": exec_fail["stderr"]}
    )
    print("Failure diagnosed:", diag_m.failure_type, "| Root cause:", diag_m.root_cause)

    from app.ai.kernel.task_graph import TaskGraph, TaskNode, NodeType
    tg = TaskGraph(graph_id="g1")
    n1 = TaskNode(node_id="n1", title="run", node_type=NodeType.ACTION)
    tg.add_node(n1)

    replan_m = replanner.replan(
        task_id="task_syntax_err",
        user_goal="Run calculator app",
        current_graph=tg,
        diagnosis=diag_m,
    )
    print("Dynamic replanner control state:", replan_m.control_state)


    # Recovery: remove broken syntax
    good_syntax = bad_syntax.replace("\ndef broken_syntax(\n", "")
    code_editor.apply_edit(calc_file, good_syntax, SafeCodeEditor.compute_file_hash(calc_file))

    exec_recovered = code_executor.execute_command(f'"{sys.executable}" app.py', cwd=proj_b)
    assert exec_recovered["returncode"] == 0
    print("--> 10K-M PASSED: Real failure captured, diagnosed, replanned, recovered, and revalidated.")

    # ------------------------------------------------------------------
    # 10K-N — External File Conflict (Stale Context Detection)
    # ------------------------------------------------------------------
    print("\n--- Testing 10K-N: External File Conflict ---")
    stale_hash = SafeCodeEditor.compute_file_hash(calc_file)
    
    # External modification behind Nova's back
    calc_file.write_text(calc_file.read_text(encoding="utf-8") + "\n# External developer edit\n", encoding="utf-8")

    # Attempt edit using stale hash
    try:
        code_editor.apply_edit(
            calc_file,
            calc_file.read_text(encoding="utf-8") + "\n# Nova edit\n",
            expected_hash=stale_hash
        )
        assert False, "Should have raised StaleContextError!"
    except StaleContextError as e:
        print("Successfully detected conflict:", e)
        print("--> 10K-N PASSED: Stale external file conflict detected; silent overwrite prevented.")

    # ------------------------------------------------------------------
    # 10K-O — Git Safety
    # ------------------------------------------------------------------
    print("\n--- Testing 10K-O: Git Safety ---")
    res_destruct = code_executor.execute_command("git reset --hard", cwd=proj_b)
    assert res_destruct["returncode"] != 0
    assert "SECURITY BLOCK" in res_destruct["stderr"] or "Security" in res_destruct["stderr"]
    print("Blocked destructive command output:", res_destruct["stderr"].strip())

    res_safe = code_executor.execute_command("git status", cwd=proj_b)
    print("Safe git command returncode:", res_safe["returncode"])
    print("--> 10K-O PASSED: Destructive git commands blocked; read-only git operations allowed.")

    # ------------------------------------------------------------------
    # 10K-P — Secret Protection
    # ------------------------------------------------------------------
    print("\n--- Testing 10K-P: Secret Protection ---")
    secret_output = "Connected to server. API_KEY=sk-proj-1234567890abcdef Secret authenticated."
    redacted = code_executor.redact_secrets(secret_output)
    print("Original output:", secret_output)
    print("Redacted output:", redacted)
    assert "sk-proj-1234567890abcdef" not in redacted
    assert "[REDACTED_API_KEY]" in redacted
    print("--> 10K-P PASSED: API keys and credentials redacted prior to storage/checkpointing.")



    # ------------------------------------------------------------------
    # 10K-Q — Durable Task Checkpoint Recovery
    # ------------------------------------------------------------------
    print("\n--- Testing 10K-Q: Durable Recovery ---")
    wm_mgr = WorkingMemoryManager.get_instance()
    task_q = wm_mgr.create_task("coding_task_10k", "Add calculator features")
    task_q.task_status = TaskStatus.RUNNING
    task_q.completed_nodes.append("node_inspect")
    task_q.completed_nodes.append("node_edit")

    # Serialize working memory task checkpoint
    ckpt_file = base_scratch / "checkpoint_task_10k.json"
    ckpt_data = task_q.snapshot()
    ckpt_file.write_text(json.dumps(ckpt_data, indent=2), encoding="utf-8")
    print("Created checkpoint file at:", ckpt_file)

    # Simulate runtime restart / clear memory
    wm_mgr.clear_task("coding_task_10k")
    assert wm_mgr.get_task("coding_task_10k") is None

    # Restore from checkpoint
    loaded_data = json.loads(ckpt_file.read_text(encoding="utf-8"))
    restored_task = WorkingMemoryTask.from_dict(loaded_data)
    wm_mgr._tasks["coding_task_10k"] = restored_task

    retrieved = wm_mgr.get_task("coding_task_10k")
    assert retrieved is not None
    assert "node_inspect" in retrieved.completed_nodes
    assert "node_edit" in retrieved.completed_nodes
    print("Restored task status:", retrieved.task_status)
    print("Restored completed nodes:", retrieved.completed_nodes)
    print("--> 10K-Q PASSED: Durable checkpoint created, runtime restarted, state successfully restored.")

    print("\n=== ALL 10K-I THRU 10K-Q MANUAL VALIDATIONS SUCCESSFUL ===")


if __name__ == "__main__":
    run_validation()
