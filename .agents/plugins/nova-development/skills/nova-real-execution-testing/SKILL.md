---
name: nova-real-execution-testing
description: >-
  Procedures for verifying real physical execution of Windows system actions, native bridge calls, process state, and external OS side-effects without mock fallbacks.
---

# Nova Real Execution Testing Skill

Use this skill when testing native computer control, OS integration, process spawning, window manipulation, file system operations, or hardware execution in Nova-AI.

## Physical Execution Verification Guidelines

### 1. Native Bridge & Windows Verification
When testing native Windows actions, verify real physical state changes rather than trusting API return codes alone:
- **Process Launch**: Query running processes via `tasklist` or `psutil` to verify process creation and PID presence.
- **Window Management**: Query active window handles (via Win32 `GetForegroundWindow` / `EnumWindows`) to verify target window title and state.
- **File System Operations**: Verify file creation, modification timestamps, byte sizes, and content on disk.
- **Mouse & Keyboard Simulation**: Use dedicated verification scripts (`test_desktop_automation_manual.py`, `test_computer_vision_manual.py`) to confirm PyAutoGUI/Win32 input dispatch.
- **Clipboard Actions**: Verify actual system clipboard text/image buffer contents.

### 2. Manual Test Suite Execution
Run the appropriate manual verification scripts from the project root:
- Desktop Automation: `python test_desktop_automation_manual.py`
- OS Runtime: `python test_os_runtime_manual.py`
- Kernel Runtime: `python test_kernel_manual.py`
- Always On Voice Runtime: `python test_always_on_voice_runtime_manual.py`
- Computer Vision: `python test_computer_vision_manual.py`

### 3. Anti-Mock Inspection Checklist
- Ensure `NO_MOCK_MODE` or environment flag is active during testing.
- Audit test output for warning banners such as `[WARNING] Falling back to mock`.
- Any test that falls back to a mock output when testing real execution must be marked as `FAIL`.
