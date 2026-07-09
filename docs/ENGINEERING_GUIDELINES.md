# Nova AI - Engineering Guidelines

This document outlines the coding standards, repository rules, and architectural guidelines that must be adhered to by every developer on the **Nova AI** project.

---

## 1. Coding Standards & Style

### Python Code Style
- **Python Version**: Target Python 3.12+ (specifically Python 3.14 compatible, utilizing modern features).
- **PEP 8**: Strict adherence to standard PEP 8 coding rules.
- **Formatting**: Code formatting should align with the **Black** standard tool defaults (e.g., double quotes, 88-character maximum line lengths).
- **Linting**: **Ruff** is used for style checking and warning detection. Clean all lint issues before requesting a code review.

### Naming Conventions
- **Packages & Modules**: Must use `snake_case` (e.g. `app.core.config`).
- **Classes**: Must use `PascalCase` (e.g. `ApplicationException`, `DatabaseException`).
- **Functions, Methods & Variables**: Must use `snake_case` (e.g. `get_database_url`, `log_level`).
- **Constants**: Must use `UPPER_SNAKE_CASE` (e.g. `API_VERSION`, `PROJECT_NAME`).

### Type Hints
- Type annotations are **mandatory** on all function signatures (parameters and return types).
- Use standard library generics where possible (e.g. `list[str]`, `dict[str, Any]`, `tuple[int, ...]` instead of legacy `typing.List` / `typing.Dict`).
- Use `Union` or `|` operators for optional parameters (e.g., `str | None`).

### Documentation Rules
- Every module, class, and public function must have **Google-style docstrings**.
- Keep arguments, types, and return values detailed:
  ```python
  def configure_logging(log_level: str = "INFO", debug: bool = False) -> None:
      """Configures global structlog logging settings.

      Args:
          log_level: The minimum logging level to output.
          debug: True for colorized console output; False for JSON serialization.
      """
  ```

---

## 2. Architecture Rules

Nova AI uses a clean architecture inspired by Domain-Driven Design (DDD) principles:
- **Presentation Layer (`api/`)**: Handles HTTP routes, parameters deserialization, and client-facing exceptions rendering.
- **Domain Layer (`domain/`)**: Pure core business rules, custom exceptions, entities, value objects, and repository interface definitions.
- **Application Layer (`services/` / `schemas/`)**: Application services, use-cases execution, data contracts translation, and orchestration logic.
- **Infrastructure Layer (`database/`)**: Adapters for third-party databases, search indexes, external AI API gateways, and system devices.

### Boundary Constraints
- The Domain layer must be clean of technical framework dependencies (no FastAPI or SQLAlchemy imports inside `app/domain`).
- Entities and models must pass validation checks using Pydantic or native validators before crossing layers.

---

## 3. Dependency & Environment Configuration

### Dependency Management
- **UV Package Manager**: `uv` is the standard tool for resolving and locking Python dependencies.
- **PNPM Workspace**: `pnpm` handles the TypeScript frontend parts (desktop, browser extension) in a monorepo setup.
- Add packages only when necessary, avoiding library redundancy (e.g., use `psycopg[binary]` instead of `psycopg2-binary`).

### Environment Management
- Configure settings using `pydantic-settings` to parse values cleanly.
- Never commit active credentials, production connection strings, or API private keys into repository files.
- Document and update [.env.example](file:///C:/Projects/Nova-AI/apps/backend/.env.example) whenever adding new parameters to `core/config.py`.

---

## 4. Git & Commit Workflow

### Branching Model
- Main development target: `main` branch.
- Feature work occurs on branches named: `feature/<developer>-<short-description>` or `bugfix/<developer>-<short-description>`.

### Commit Message Conventions
Commits must conform to the **Conventional Commits** standard:
- `<type>(<scope>): <short description>`
- **Types**:
  - `feat`: A new feature implementation.
  - `fix`: A bug resolution.
  - `docs`: Documentation edits.
  - `style`: Whitespace, formatting, or missing semicolon adjustments.
  - `refactor`: Structural code edits with no functional change.
  - `test`: Adding or modifying tests.
  - `chore`: Modifying build processes, helper tools, or library dependencies.

---

## 5. Security & Logging Rules

### Security Rules
- **No Stack Disclosures**: Unhandled exception traces must never leak to API responses. Always capture internal errors and return sanitized generic maps.
- **CORS Policies**: Explicitly whitelist trusted domains in staging/production environments; disable open wildcard settings (`*`) in production.
- **Database Safety**: Enable connection pooling checking (`pool_pre_ping=True`) and query parameter sanitization (handled by SQLAlchemy engine compilation).

### Logging Rules
- Use `structlog` for all logs. Do not use standard `print()` statements.
- Ensure context tracing headers (`request_id`, `correlation_id`) are bound using context variables in HTTP middlewares, ensuring logs trace request spans across threads.
- Do not log sensitive private user information (e.g. credentials, tokens, passwords, raw health data).

---

## 6. Definition of Done (DoD)

A task is considered complete and ready to merge only when:
1. **Compilation**: All modified code compile without errors or warnings.
2. **Linting & Formatting**: Ruff checks pass and file formatting matches Black parameters.
3. **Type Checking**: Static analysis tools report no typing inconsistencies.
4. **Documentation**: Google-style docstrings and relevant files (like `README.md`, `.env.example`) are updated.
5. **Review**: The changes are approved by at least one Senior Engineer in the PR review stage.
