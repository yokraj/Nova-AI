---
name: nova-release-verification
description: >-
  Comprehensive multi-stage verification suite covering TypeScript checking, Vite building, ESLint linting, pytest unit/integration tests, native tests, and production readiness checks.
---

# Nova Release Verification Skill

Use this skill before declaring any milestone, feature release, or pull request ready for production deployment in Nova-AI.

## Multi-Stage Verification Pipeline

Execute each verification stage sequentially. Report any failure immediately.

### Stage 1: Frontend Type & Code Quality Verification
Run inside `apps/frontend/`:
1. **TypeScript Typecheck**:
   ```powershell
   cd apps/frontend; npx tsc --noEmit
   ```
2. **ESLint Validation**:
   ```powershell
   cd apps/frontend; npm run lint
   ```
3. **Vite Production Build**:
   ```powershell
   cd apps/frontend; npm run build
   ```

### Stage 2: Backend Unit & Integration Tests
Run from repository root:
1. **Pytest Unit Test Suite**:
   ```powershell
   pytest tests/unit/
   ```
2. **Pytest Integration Test Suite**:
   ```powershell
   pytest tests/integration/
   ```

### Stage 3: Native & Subsystem Verification
Run native manual test harnesses:
1. `python test_desktop_automation_manual.py`
2. `python test_os_runtime_manual.py`
3. `python test_real_ai_runtime_manual.py`
4. `python test_always_on_voice_runtime_manual.py`

### Stage 4: Production Readiness Audit
- Confirm zero modified or broken production source files.
- Confirm zero hardcoded secrets.
- Confirm all new endpoints have matching security permission gates.
- Create or update `FINAL_VERIFICATION_REPORT.md` with pipeline execution results.
