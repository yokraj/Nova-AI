# Python 3.14+ Compatibility & Deprecations Report

This report outlines the modernization modifications performed on the Nova AI codebase to resolve deprecation warnings, improve performance, and align with Python 3.14+ specifications.

---

## 1. Summary of deprecations resolved

- **`datetime.utcnow()` deprecations**:
  - **Issue**: Standard `datetime.utcnow()` has been scheduled for removal in future versions (Python 3.15+).
  - **Resolution**: Replaced with standard timezone-aware UTC datetime instances using `from datetime import UTC, datetime` and `datetime.now(UTC)`.
- **`asyncio.iscoroutinefunction()` deprecations**:
  - **Issue**: Standard `asyncio.iscoroutinefunction()` has been scheduled for removal in Python 3.16.
  - **Resolution**: Replaced with standard `inspect` introspection library check `inspect.iscoroutinefunction()`.

---

## 2. Modified Files & Changes Log

### [app/runtime/types.py](file:///C:/Projects/Nova-AI/apps/backend/app/runtime/types.py)
- Replaced `default_factory=datetime.utcnow` with `default_factory=lambda: datetime.now(UTC)`.
- Updated datetime import to fetch timezone-aware `UTC` module attribute.

### [app/automation/models.py](file:///C:/Projects/Nova-AI/apps/backend/app/automation/models.py)
- Replaced `HistoryEntry` timestamp `default_factory=datetime.utcnow` with `default_factory=lambda: datetime.now(UTC)`.

### [app/automation/engine.py](file:///C:/Projects/Nova-AI/apps/backend/app/automation/engine.py)
- Replaced `step.started_at` and `step.completed_at` timestamps assignments from `datetime.utcnow()` to `datetime.now(UTC)`.

### [app/automation/event_bus.py](file:///C:/Projects/Nova-AI/apps/backend/app/automation/event_bus.py)
- Replaced `asyncio.iscoroutinefunction(callback)` with `inspect.iscoroutinefunction(callback)`.

### [app/runtime/event_bus.py](file:///C:/Projects/Nova-AI/apps/backend/app/runtime/event_bus.py)
- Replaced `asyncio.iscoroutinefunction(callback)` with `inspect.iscoroutinefunction(callback)`.

---

## 3. Remaining Warnings

There is **1 remaining warning** raised from outside our codebase inside the third-party FastAPI testing framework itself:
```
StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.
```
This warning originates inside `fastapi/testclient.py:1` due to FastAPI's dependency bindings and cannot be resolved by modifying backend code directly without breaking FastAPI/Starlette dependencies.

---

## 4. Recommendations for Future Python Migrations

1. **Avoid `datetime.utcnow()`**: Always use standard timezone-aware `datetime.now(UTC)` for timestamps to satisfy Python 3.15+ standards.
2. **Utilize `inspect` for Coroutines**: Prefer `inspect.iscoroutinefunction()` over `asyncio` for checking callable tasks to maintain Python 3.16+ readiness.
3. **Ruff/Black Continuous Checks**: Integrate automated Ruff and Black linting hooks inside the CI/CD environment to maintain code quality.
