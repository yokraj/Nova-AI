# Specification M2.6.3 – Enterprise Prompt Framework Implementation Report

This report documents the implementation of the Enterprise Prompt Framework for Nova AI.

## Executive Summary

The Enterprise Prompt Framework provides a production-ready, standardized infrastructure for managing, parsing, rendering, validating, and optimizing prompts across all concrete agents (Software, Browser, Vision, Voice, Coding, etc.). By design, all prompts are externalized to Markdown or YAML files in a dedicated registry rather than being hardcoded inside agent routines.

Consistent with the ₹0 mandatory operating cost requirement, the framework operates entirely offline, has zero external dependencies (not even `PyYAML`), and runs on local open-source models.

---

## Architecture & System Design

The package is located at `app/agent_sdk/prompt/` and comprises the following decoupled modules:

```mermaid
classDiagram
    class Prompt {
        + id: UUID
        + name: str
        + category: str
        + description: str
        + system_prompt: str
        + user_prompt: str
        + variables: List[str]
        + version: str
        + language: str
        + tags: List[str]
        + metadata: Dict
    }

    class PromptTemplate {
        - loader: PromptLoader
        - renderer: PromptRenderer
        - validator: PromptValidator
        + load(file_path) Prompt
        + save(file_path, prompt)
        + render(prompt, variables) str
        + validate(prompt, variables) bool
    }

    class PromptBuilder {
        + build(prompt, variables) Dict
        + merge_system_prompt(base, custom) str
        + merge_history(prompt_text, history) str
        + merge_memory(prompt_text, memories) str
        + merge_context(prompt_text, context) str
        + build_voice_prompt(voice_ctx, variables) str
        + build_chat_prompt(messages, variables) List
    }

    class PromptRenderer {
        + render(template_str, variables, max_depth) str
    }

    class PromptRegistry {
        - _prompts: Dict
        + version_manager: VersionManager
        + register(prompt)
        + unregister(name)
        + find(name) Prompt
        + find_by_category(category) List
        + find_by_tag(tag) List
        + latest_version(name) Prompt
    }

    class PromptValidator {
        + validate(prompt, variables, max_size)
    }

    class PromptOptimizer {
        + compress_whitespace(text) str
        + remove_duplicate_context(text) str
        + trim_history(history, max_turns) List
        + fit_context_window(prompt, variables, context_limit) Dict
    }

    class VersionManager {
        - _history: Dict
        + add_version(prompt)
        + rollback(name, version) Prompt
        + history(name) List
    }

    class PromptLoader {
        + load_from_yaml(file_path) Prompt
        + load_from_json(file_path) Prompt
        + load_from_markdown(file_path) Prompt
    }

    PromptTemplate --> PromptLoader
    PromptTemplate --> PromptRenderer
    PromptTemplate --> PromptValidator
    PromptRegistry --> VersionManager
    PromptBuilder --> PromptRenderer
```

### Components Summary

1. **Prompt Model (`prompt.py`)**:
   - Pydantic v2 schema encapsulating metadata, variables list, versions, target languages, and tags.

2. **Template Operations Facade (`template.py`)**:
   - Manages prompt loading/saving serialization workflows.

3. **Prompt Builder (`builder.py`)**:
   - Assembles complex system instructions, historical dialog ranges, externalized memory facts, and multi-modal voice/chat contexts.

4. **Variables Container (`variables.py`)**:
   - Exposes runtime-resolved environment hooks (e.g. `{{user}}`, `{{clipboard}}`, `{{active_application}}`, `{{operating_system}}`, `{{code}}`).

5. **Recursive Renderer (`renderer.py`)**:
   - Performs recursive placeholder substitution to support nested variables.

6. **Semantic Validator (`validator.py`)**:
   - Validates template formatting, missing parameters, and size limits.

7. **Token Optimizer (`optimizer.py`)**:
   - Compresses redundant whitespaces, deduplicates context lines, and fits context windows.

8. **Prompt Catalog Directory (`app/prompts/`)**:
   - Subdirectories: `software/`, `browser/`, `desktop/`, `memory/`, `vision/`, `voice/`, `research/`, `coding/`, `system/`.
   - Populated with sample Markdown templates.

---

## Verification & Testing

Unit tests were executed using Python 3.14 on `pytest`. All **142 tests passed** successfully.

### Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Projects\Nova-AI\apps\backend
configfile: pyproject.toml
plugins: anyio-4.14.1
collected 142 items

tests\test_prompt_framework.py ......                                    [ 87%]
...
======================= 142 passed, 1 warning in 7.55s ========================
```

The verified logic includes:
- **File Loaders**: Verified Markdown frontmatter parsing and system/user prompts separations, and YAML load/save serialization cycles.
- **Variables & Nested Substitutions**: Verified single and recursive placeholder replacement and infinite loop detection.
- **Validations & Limits**: Verified checks on missing variables, invalid placeholders, and maximum context lengths.
- **Optimizers**: Checked whitespace compression, redundant line removal, history turn trimming, and context-window fitting.
- **Registry & Version History**: Verified tags query matching, multiple version register updates, and rollback runs.
- **Multi-Modal Builders**: Checked chat lists mapping and voice context generation.
