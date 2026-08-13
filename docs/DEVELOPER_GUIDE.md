# Nova AI Enterprise Developer Guide

## Executive Overview
Welcome to the developer guide for the **Nova AI Enterprise Dashboard Backend**. This document covers architectural principles, coding conventions, repository/service design patterns, dependency injection standards, and instructions for adding new dashboard capabilities.

---

## 1. Core Architecture Principles

1. **Strict Layer Decoupling**: REST routes act strictly as presentation controllers. Routes must NEVER access SQLAlchemy models or repositories directly. All access must be routed through business services.
2. **Dependency Injection**: Use FastAPI `Depends()` for service instantiation and repository binding. Services and repositories must be easily mockable in test fixtures.
3. **Fully Asynchronous Execution**: All network I/O, database access, and cache operations must be non-blocking async functions (`async`/`await`).
4. **Structured Logging**: Use `structlog` for contextual JSON logging instead of plain `print()` statements.

---

## 2. Design Patterns

### Repository Pattern (`app/dashboard/repositories/`)
- Encapsulates database queries.
- Inherits from `BaseRepository` or `DashboardRepository`.
- Returns domain Pydantic schemas or SQLAlchemy entities to the service layer.

### Service Pattern (`app/dashboard/services/`)
- Encapsulates business rules, KPI aggregations, and caching logic.
- Interacts exclusively with repositories and in-memory caches.

---

## 3. Step-by-Step: Adding a New Dashboard Feature

1. **Define Schemas**: Add request/response DTOs in `app/dashboard/schemas/`.
2. **Implement Repository Method**: Add query method in `app/dashboard/repositories/`.
3. **Implement Service Logic**: Add async business service method in `app/dashboard/services/`.
4. **Expose REST API Endpoint**: Add route in `app/dashboard/api/` with RBAC permission check.
5. **Write Unit & Integration Tests**: Add test case in `tests/`.
