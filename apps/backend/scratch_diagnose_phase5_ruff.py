import subprocess
import json
import os

ruff_bin = r"C:\Users\YOKRAJ M S R\.local\bin\ruff.exe"

phase5_files = [
    r"apps\backend\app\ai\desktop_automation\blender_executors\camera_lighting_executor.py",
    r"apps\backend\app\ai\desktop_automation\blender_adapter.py",
    r"apps\backend\app\ai\desktop_automation\application_adapter.py",
    r"apps\backend\app\ai\desktop_automation\automation_router.py",
    r"apps\backend\tests\test_blender_phase5.py"
]

res = subprocess.run([ruff_bin, "check", "--output-format", "json"] + phase5_files, capture_output=True, text=True, cwd=r"c:\Projects\Nova-AI")
try:
    data = json.loads(res.stdout)
except Exception as e:
    print("Error parsing json:", e)
    data = []

print(f"Total Phase 5 Ruff Items: {len(data)}")
for p in data:
    print(f"[{p['code']}] {p['filename']}:{p['location']['row']} - {p['message']}")
