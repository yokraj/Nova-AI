"""Unit tests for the Agent SDK Prompt Framework.

Verifies Markdown and YAML loading, recursive variable replacements, validations,
context window optimizations, rollbacks, and voice prompts builders.
"""

import os
import uuid
import pytest

from app.agent_sdk.prompt import (
    Prompt,
    PromptTemplate,
    PromptBuilder,
    PromptRegistry,
    PromptValidator,
    PromptOptimizer,
    VersionManager,
    PromptLoader,
    PromptVariables,
    PromptValidationError,
    PromptRenderingError,
)


@pytest.fixture
def prompts_dir() -> str:
    """Helper locating prompts base folder."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../app/prompts"))


def test_prompt_loading_markdown_and_yaml(prompts_dir: str) -> None:
    """Verifies that PromptLoader parses YAML frontmatter and system/user prompts from Markdown files."""
    template = PromptTemplate()

    # 1. Markdown loading
    md_path = os.path.join(prompts_dir, "software/code_review.md")
    assert os.path.exists(md_path)

    prompt = template.load(md_path)
    assert prompt.name == "code_review"
    assert prompt.category == "software"
    assert "best practices" in prompt.description
    assert "Review the code" in prompt.system_prompt
    assert "review this {{language}} code" in prompt.user_prompt

    # 2. YAML saving & loading
    temp_yaml = os.path.join(os.path.dirname(md_path), "temp_code_review.yaml")
    try:
        template.save(temp_yaml, prompt)
        assert os.path.exists(temp_yaml)

        prompt_yaml = template.load(temp_yaml)
        assert prompt_yaml.name == prompt.name
        assert prompt_yaml.system_prompt == prompt.system_prompt
        assert prompt_yaml.user_prompt == prompt.user_prompt
    finally:
        if os.path.exists(temp_yaml):
            os.remove(temp_yaml)


def test_variable_replacement_and_nested() -> None:
    """Verifies recursive variable expansion and error boundaries on infinite loops."""
    template = PromptTemplate()

    # Basic rendering
    prompt = Prompt(
        name="test",
        category="test",
        user_prompt="Hello {{user_name}} in {{timezone}}.",
        variables=["user_name", "timezone"],
    )
    rendered = template.render(prompt, {"user_name": "Nova", "timezone": "UTC"})
    assert rendered == "Hello Nova in UTC."

    # Nested rendering
    prompt_nested = Prompt(
        name="test_nested",
        category="test",
        user_prompt="Say {{welcome}}.",
        variables=["welcome"],
    )
    variables = {
        "welcome": "hello {{name}}",
        "name": "developer of {{project}}",
        "project": "Nova AI",
    }
    rendered_nested = template.render(prompt_nested, variables)
    assert rendered_nested == "Say hello developer of Nova AI."

    # Max depth recursion error
    prompt_loop = Prompt(name="test_loop", category="test", user_prompt="{{loop}}", variables=["loop"])
    with pytest.raises(PromptRenderingError):
        template.render(prompt_loop, {"loop": "nested {{loop}}"})


def test_prompt_validation() -> None:
    """Verifies that PromptValidator checks for missing variables and malformed templates."""
    validator = PromptValidator()
    prompt = Prompt(
        name="val",
        category="val",
        user_prompt="Process {{data}}",
        variables=["data", "extra"],  # Declared 'extra' as required
    )

    # 1. Missing variable check
    with pytest.raises(PromptValidationError):
        validator.validate(prompt, {"data": "my-payload"})

    # 2. Malformed template check (missing closing brace)
    prompt_malformed = Prompt(
        name="val_malformed",
        category="val",
        user_prompt="Process {{data",
        variables=["data"],
    )
    with pytest.raises(PromptValidationError):
        validator.validate(prompt_malformed, {"data": "my-payload"})


def test_prompt_optimization() -> None:
    """Verifies whitespace compression, duplicate removals, and context fitting."""
    optimizer = PromptOptimizer()

    # Whitespace compression
    raw_text = "Hello    world!\n\n\nHow  are  you?"
    assert optimizer.compress_whitespace(raw_text) == "Hello world!\nHow are you?"

    # Duplicate lines removal
    dup_text = "line 1\nline 1\nline 2"
    assert optimizer.remove_duplicate_context(dup_text) == "line 1\nline 2"

    # History trimming
    history = [
        {"role": "system", "content": "sys-prompt"},
        {"role": "user", "content": "turn 1"},
        {"role": "assistant", "content": "turn 2"},
        {"role": "user", "content": "turn 3"},
        {"role": "assistant", "content": "turn 4"},
        {"role": "user", "content": "turn 5"},
    ]
    # Trim to max 3 turns: oldest system prompt + 2 latest turns
    trimmed = optimizer.trim_history(history, max_turns=3)
    assert len(trimmed) == 3
    assert trimmed[0]["content"] == "sys-prompt"
    assert trimmed[1]["content"] == "turn 4"
    assert trimmed[2]["content"] == "turn 5"

    # Fitting context window
    prompt = Prompt(
        name="code_prompt",
        category="coding",
        system_prompt="Review",
        user_prompt="Evaluate {{code}}",
        variables=["code"],
    )
    # Budget = 10 tokens = 40 characters limit
    # system_len (6) + user_len (9) = 15 chars. Available budget = 25 chars.
    long_code = "print('this code block is extremely long and will overflow context window limit')"
    optimized_vars = optimizer.fit_context_window(prompt, {"code": long_code}, context_limit=10)
    assert len(optimized_vars["code"]) <= 50  # includes truncated suffix
    assert "TRUNCATED" in optimized_vars["code"]


def test_prompt_registry_and_versions() -> None:
    """Verifies indexing, queries, and rollbacks in PromptRegistry."""
    registry = PromptRegistry()

    p_v1 = Prompt(
        name="test_prompt",
        category="system",
        description="description",
        user_prompt="old prompt",
        version="v1",
        tags=["sys"],
    )
    p_v2 = Prompt(
        name="test_prompt",
        category="system",
        description="description",
        user_prompt="new prompt",
        version="v2",
        tags=["sys"],
    )

    registry.register(p_v1)
    registry.register(p_v2)

    # Queries
    assert len(registry.find_by_category("system")) == 1
    assert len(registry.find_by_tag("sys")) == 1
    assert registry.latest_version("test_prompt").version == "v2"

    # Rollback checks
    rolled = registry.version_manager.rollback("test_prompt", "v1")
    assert rolled.user_prompt == "old prompt"


def test_voice_prompt_and_chat_builders() -> None:
    """Verifies that PromptBuilder builds voice context blocks and resolves chat lists."""
    builder = PromptBuilder()

    # Voice context
    voice_ctx = {
        "wake_word": "Nova",
        "speech_speed": "1.2",
        "active_application": "Terminal",
        "conversation_summary": "Discussed code review",
    }
    rendered_voice = builder.build_voice_prompt(voice_ctx, {"target": "user"})
    assert "Nova" in rendered_voice
    assert "1.2" in rendered_voice
    assert " डिस्कस " not in rendered_voice  # should be english

    # Chat prompt injection
    msgs = [
        {"role": "system", "content": "You are assisting {{name}}."},
        {"role": "user", "content": "Execute {{task}}."},
    ]
    resolved = builder.build_chat_prompt(msgs, {"name": "Alice", "task": "refactor"})
    assert resolved[0]["content"] == "You are assisting Alice."
    assert resolved[1]["content"] == "Execute refactor."
