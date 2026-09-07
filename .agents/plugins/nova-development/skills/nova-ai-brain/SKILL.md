---
name: nova-ai-brain
description: >-
  Architectural guide and operational procedures for Nova's AI Gateway, local model providers, reasoning engines, tool selection, and structured execution.
---

# Nova AI Brain Skill

Use this skill when configuring, extending, or debugging Nova-AI's intelligence layer, model routing, reasoning engine, prompt management, tool selection, or structured output parsing.

## Subsystem Architecture Overview

The AI Brain subsystem lives in `apps/backend/app/ai/`, `apps/backend/app/inference/`, and `apps/backend/app/orchestrator/`:
- `inference/model_router.py`: Dynamic LLM routing (local Ollama, vLLM, LM Studio, or local GGUF model engines).
- `ai/gateway.py`: Unified API adapter handling prompt formatting, parameter tuning, and stream responses.
- `orchestrator/multi_model_orchestrator.py`: Multi-model orchestration, fallback chains, and sub-agent task distribution.
- `ai/planning.py`: Goal decomposition, plan generation, step tracking, and execution tree monitoring.

## Core Procedures

### 1. Local Model Provider Configuration
- Ensure primary routing defaults to local endpoints (e.g. Ollama `http://localhost:11434`, LM Studio `http://localhost:1234/v1`).
- Validate model availability before initiating heavy reasoning tasks:
  ```python
  from app.inference.model_router import ModelRouter
  router = ModelRouter()
  status = router.check_health()
  ```

### 2. Multi-Step Planning & Reasoning
- Inspect incoming user goals and pass them to the planning engine (`Planner`).
- Deconstruct complex tasks into atomic execution steps with explicit tool assignments.
- Enforce schema validation (Pydantic models) on all structured planner outputs.

### 3. Tool Selection & Execution Pipeline
- Tools must be registered with typed schemas (JSON Schema / OpenAPI format).
- Validate tool parameters against schema before invoking handlers.
- Route tool calls through security validation gates (`PermissionManager`, `PromptInjectionFilter`).

### 4. Verification & Testing
- Test multi-model router: `python test_model_router_manual.py`
- Test multi-model orchestrator: `python test_multi_model_orchestrator_manual.py`
- Test real AI runtime: `python test_real_ai_runtime_manual.py`
