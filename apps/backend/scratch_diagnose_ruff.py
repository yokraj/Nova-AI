import subprocess
import json
import os

ruff_bin = r"C:\Users\YOKRAJ M S R\.local\bin\ruff.exe"

# Run ruff on entire workspace with JSON output
res = subprocess.run([ruff_bin, "check", "--output-format", "json", "."], capture_output=True, text=True, cwd=r"c:\Projects\Nova-AI")
try:
    data = json.loads(res.stdout)
except Exception as e:
    print("Error parsing json:", e)
    data = []

print(f"Total Ruff Items Found across repo: {len(data)}")

phase4_files = [
    r"apps\backend\app\ai\desktop_automation\blender_executors\material_executor.py",
    r"apps\backend\app\ai/desktop_automation\blender_adapter.py",
    r"apps\backend\app\ai\desktop_automation\application_adapter.py",
    r"apps\backend\app\ai\desktop_automation\automation_router.py",
    r"apps\backend\tests\test_blender_phase4.py"
]
phase4_files_norm = [os.path.normpath(f) for f in phase4_files]

phase4_problems = []
desktop_automation_problems = []
tests_problems = []
other_nova_problems = []
external_problems = []

for item in data:
    filepath = item.get("filename", "")
    rel_path = os.path.relpath(filepath, r"c:\Projects\Nova-AI")
    norm_path = os.path.normpath(rel_path)

    # Check phase 4
    if any(norm_path.endswith(f) or f.endswith(norm_path) for f in phase4_files_norm):
        phase4_problems.append(item)

    if norm_path.startswith(os.path.normpath("apps/backend/app/ai/desktop_automation")):
        desktop_automation_problems.append(item)
    elif norm_path.startswith(os.path.normpath("apps/backend/tests")):
        tests_problems.append(item)
    elif norm_path.startswith("apps") or norm_path.startswith("config"):
        other_nova_problems.append(item)
    else:
        external_problems.append(item)

print(f"\n--- RUFF DIAGNOSTIC BREAKDOWN ---")
print(f"Phase 4 files problems: {len(phase4_problems)}")
print(f"Desktop Automation directory problems: {len(desktop_automation_problems)}")
print(f"Backend Tests directory problems: {len(tests_problems)}")
print(f"Other Nova-AI source problems: {len(other_nova_problems)}")
print(f"External / Root / Temp problems: {len(external_problems)}")

print("\n--- PHASE 4 FILE DETAILS ---")
if not phase4_problems:
    print("Zero problems in Phase 4 files!")
else:
    for p in phase4_problems:
        print(f"[{p['code']}] {p['filename']}:{p['location']['row']} - {p['message']}")
