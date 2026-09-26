import py_compile
import glob
import os
import sys

phase4_files = [
    r"apps/backend/app/ai/desktop_automation/blender_executors/material_executor.py",
    r"apps/backend/app/ai/desktop_automation/blender_adapter.py",
    r"apps/backend/app/ai/desktop_automation/application_adapter.py",
    r"apps/backend/app/ai/desktop_automation/automation_router.py",
    r"apps/backend/tests/test_blender_phase4.py"
]

print("=== CHECKING PHASE 4 FILES FOR COMPILATION / SYNTAX ERRORS ===")
phase4_errors = 0
for f in phase4_files:
    full_path = os.path.join(r"c:\Projects\Nova-AI", f)
    if os.path.exists(full_path):
        try:
            py_compile.compile(full_path, doraise=True)
            print(f"[OK] {f}")
        except py_compile.PyCompileError as e:
            print(f"[ERROR] {f}: {e}")
            phase4_errors += 1
    else:
        print(f"[MISSING] {f}")

print(f"\nPhase 4 Syntax Errors: {phase4_errors}")

print("\n=== CHECKING ALL BACKEND DESKTOP AUTOMATION & TESTS ===")
backend_files = glob.glob(r"c:\Projects\Nova-AI\apps\backend\app\ai\desktop_automation\**\*.py", recursive=True) + \
                glob.glob(r"c:\Projects\Nova-AI\apps\backend\tests\**\*.py", recursive=True)

backend_errors = 0
for f in backend_files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        rel = os.path.relpath(f, r"c:\Projects\Nova-AI")
        print(f"[ERROR] {rel}: {e}")
        backend_errors += 1

print(f"Desktop Automation & Tests Total PyCompile Errors: {backend_errors} / {len(backend_files)} files")
