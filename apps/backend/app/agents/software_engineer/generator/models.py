"""Pydantic models representing code generation plans, context, styles and reports.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.ai.models import PromptMessage


class StyleProfile(BaseModel):
    """Naming conventions and structural styles extracted from existing project code."""

    indentation: str = Field("    ", description="Indentation style (e.g. 4 spaces, 2 spaces, tab).")
    naming_convention_class: str = Field("PascalCase", description="Style used for classes.")
    naming_convention_function: str = Field("snake_case", description="Style used for functions/methods.")
    naming_convention_variable: str = Field("snake_case", description="Style used for variables.")
    docstring_format: str = Field("google", description="Docstring style (google, sphinx, double_quotes).")
    import_organization: str = Field("grouped", description="Import ordering scheme.")
    typing_annotations: bool = Field(True, description="True if type annotations are strictly expected.")
    exception_handling: str = Field("explicit", description="Style for try-except blocks.")
    logging_style: str = Field("structlog", description="Logger preference.")


class TemplateInfo(BaseModel):
    """Metadata regarding a code template file."""

    name: str = Field(..., description="Template identifier.")
    description: str = Field(..., description="Brief summary of template purpose.")
    language: str = Field(..., description="Target programming language.")
    required_variables: List[str] = Field(default_factory=list, description="Variables needed to render this template.")


class GeneratedClass(BaseModel):
    """Details of a generated class inside source files."""

    name: str
    bases: List[str] = Field(default_factory=list)
    methods: List[str] = Field(default_factory=list)
    docstring: Optional[str] = None


class GeneratedFunction(BaseModel):
    """Details of a generated function inside source files."""

    name: str
    parameters: List[str] = Field(default_factory=list)
    return_type: Optional[str] = None
    is_async: bool = False
    docstring: Optional[str] = None


class GeneratedFile(BaseModel):
    """Contains raw source code and structural symbols of a generated file."""

    file_path: str = Field(..., description="Relative file path target location.")
    content: str = Field(..., description="Full source code contents.")
    classes: List[GeneratedClass] = Field(default_factory=list)
    functions: List[GeneratedFunction] = Field(default_factory=list)


class GenerationTask(BaseModel):
    """Single file generation subtask in a decomposition plan."""

    id: str = Field(..., description="Unique task identifier.")
    file_path: str = Field(..., description="Relative target path of file to create/modify.")
    instructions: str = Field(..., description="Step-by-step model instructions.")
    dependencies: List[str] = Field(default_factory=list, description="Task IDs that must complete first.")
    status: str = Field("pending", description="Status of task ('pending', 'running', 'completed', 'failed').")


class GenerationPlan(BaseModel):
    """Plan decomposing a request into dependencies and individual generation tasks."""

    plan_id: str
    request_summary: str
    tasks: List[GenerationTask] = Field(default_factory=list)


class ContextSummary(BaseModel):
    """Workspace context collected to guide generation."""

    repository_summary: str = Field(..., description="High-level codebase architecture.")
    related_files: List[str] = Field(default_factory=list, description="File paths added to context.")
    similar_symbols: List[str] = Field(default_factory=list, description="Symbols referenced for style imitation.")
    token_count_estimation: int = Field(0, description="Estimated prompt context tokens consumed.")


class GenerationContext(BaseModel):
    """Details regarding the workspace state gathered during generation."""

    workspace_root: str
    summary: ContextSummary
    style_profile: StyleProfile
    code_intelligence_summary: Optional[Dict[str, Any]] = None


class GenerationRequest(BaseModel):
    """Parameters sent to orchestrate a code generation run."""

    prompt: str = Field(..., description="Instructions detailing the code to write.")
    language: str = Field("python", description="Target programming language.")
    file_path: Optional[str] = Field(None, description="Optional target file path to generate/edit.")
    template_name: Optional[str] = Field(None, description="Optional template identifier to instantiate.")
    model_override: Optional[str] = Field(None, description="Optional active model name override.")
    temperature: float = Field(0.2, description="Sampling randomness (0.0 to 1.0).")
    max_tokens: int = Field(4096, description="Max generated tokens limit.")


class ValidationResult(BaseModel):
    """Validation report regarding generated code compile and syntax state."""

    is_valid: bool = Field(..., description="True if code compiles successfully.")
    errors: List[str] = Field(default_factory=list, description="Compiler or syntax error strings.")
    warnings: List[str] = Field(default_factory=list, description="Stylistic warnings.")


class FormatterResult(BaseModel):
    """Formatted code results."""

    success: bool
    content: str
    error: Optional[str] = None


class PromptPackage(BaseModel):
    """Compiled prompts sent to the local model provider."""

    messages: List[PromptMessage] = Field(default_factory=list)
    system_prompt: str


class GenerationStatistics(BaseModel):
    """Metrics compiled during model execution calls."""

    duration: float = Field(0.0, description="Execution call duration in seconds.")
    prompt_tokens: int = Field(0)
    completion_tokens: int = Field(0)
    model: str = Field("", description="Active local model name used.")
    validation_status: str = Field("untested", description="Code verification outcome.")


class GenerationResult(BaseModel):
    """Consolidated generation results."""

    success: bool
    plan: Optional[GenerationPlan] = None
    files: List[GeneratedFile] = Field(default_factory=list)
    statistics: GenerationStatistics
    cache_hit: bool = False
