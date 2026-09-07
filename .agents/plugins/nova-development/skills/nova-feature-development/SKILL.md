---
name: nova-feature-development
description: >-
  Standardized end-to-end development workflow for introducing or extending Nova-AI features safely, ensuring service reuse, incremental implementation, real execution, and complete verification.
---

# Nova Feature Development Skill

Use this skill whenever planning, building, or modifying any Nova-AI feature across the frontend, backend, native bridge, or AI subsystems.

## Standardized Step-by-Step Methodology

### Phase 1: Architecture & Service Discovery
1. Inspect `apps/backend/app/` to locate existing domain models, services, and security gates relevant to the feature.
2. Identify reusable backend components (e.g. `PermissionManager`, `HealthManager`, `ModelRouter`, `MemoryManager`).
3. Ensure no parallel runtime or duplicate engine is introduced.

### Phase 2: Design & API Contract Definition
1. Define Pydantic request/response schemas in `apps/backend/app/schemas/`.
2. Define TypeScript interface contracts matching backend schemas in `apps/frontend/src/types/` or `apps/frontend/src/services/`.
3. Plan API routes in FastAPI routers under `apps/backend/app/api/v1/`.

### Phase 3: Incremental Implementation
1. Write backend domain logic and service extensions in `apps/backend/app/services/` or targeted subsystem module.
2. Enforce security gates (`permission_manager.check_permission`, `security_guard`, `executable_validator`) around all operational endpoints.
3. Wire the API endpoint in FastAPI.
4. Wire frontend service call, Zustand store action, and UI component in `apps/frontend/src/`.

### Phase 4: Targeted Unit & Integration Testing
1. Run small targeted test suite:
   ```powershell
   pytest tests/unit/test_<feature>.py
   ```
2. For desktop/OS automation changes, execute the relevant manual test script:
   ```powershell
   python test_<feature>_manual.py
   ```

### Phase 5: Verification & Build Validation
1. Verify TypeScript types:
   ```powershell
   cd apps/frontend; pnpm run check
   ```
2. Verify production frontend build:
   ```powershell
   cd apps/frontend; pnpm run build
   ```

### Phase 6: Documentation & Report Update
1. Update `NOVA_FEATURE_MATRIX.md` or feature implementation report with verification evidence.
