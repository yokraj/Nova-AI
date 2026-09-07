# Testing Rules

These rules define the required testing methodology for Nova-AI code verification.

## 1. Incremental Test Hierarchy
- Always start verification by running the smallest, most specific test suite relevant to your change (e.g., `pytest tests/unit/test_specific_feature.py` or specific standalone manual test script `python test_feature_manual.py`).
- Fix any targeted unit test failures before proceeding to full subsystem or integration tests.

## 2. Frontend & Build Validation
- After modifying frontend code or shared types, run:
  - TypeScript type check: `pnpm run check` or `npx tsc --noEmit` inside `apps/frontend`
  - ESLint check: `npm run lint` inside `apps/frontend`
  - Vite production build: `npm run build` inside `apps/frontend`

## 3. Real Windows Verification
- When modifying Windows automation, process execution, screen capture, mouse/keyboard handling, or desktop bridge components:
  - Execute real verification using Windows API / process checks on the local machine.
  - Run the dedicated manual verification scripts (e.g. `python test_desktop_automation_manual.py`, `python test_os_runtime_manual.py`).

## 4. Truthful Test Reporting
- Never declare or report a test as PASS unless it was executed and returned an exit status of `0` with verified output.
- Never ignore, suppress, comment out, or mask failing test assertions to claim completion.
