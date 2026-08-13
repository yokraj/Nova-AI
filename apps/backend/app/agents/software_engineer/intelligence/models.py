"""Pydantic models representing AST structures, symbols, graphs, and complexities.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ASTNodeInfo(BaseModel):
    """Details about a parsed AST node."""

    node_type: str = Field(..., description="AST node type name (e.g. FunctionDef, ClassDef).")
    name: str = Field(..., description="Node name.")
    filename: str = Field(..., description="File path relative to workspace.")
    line_number: int = Field(..., description="Starting line number (1-indexed).")
    column_number: int = Field(..., description="Starting column offset.")
    end_line: Optional[int] = Field(None, description="Ending line number.")
    end_column: Optional[int] = Field(None, description="Ending column offset.")
    scope: str = Field(..., description="Current enclosing scope path.")
    source_snippet: Optional[str] = Field(None, description="Raw source code snippet.")


class Symbol(BaseModel):
    """Represents a discovered code symbol (class, function, variable, etc.)."""

    id: str = Field(..., description="Unique symbol identifier (typically qualified name + path).")
    name: str = Field(..., description="Short symbol name.")
    fully_qualified_name: str = Field(..., description="Dot-separated name including modules and scopes.")
    symbol_type: str = Field(..., description="Type of symbol (e.g. class, function, method, variable, constant).")
    parent_scope: str = Field(..., description="Enclosing scope path.")
    module: str = Field(..., description="Python module name.")
    file_path: str = Field(..., description="Relative file path.")
    line_number: int = Field(..., description="1-indexed line number of definition.")
    column_number: int = Field(..., description="Column offset.")
    end_line: Optional[int] = Field(None, description="End line number.")
    end_column: Optional[int] = Field(None, description="End column offset.")
    visibility: str = Field("public", description="Symbol visibility ('public', 'protected', 'private').")
    signature: Optional[str] = Field(None, description="Function/Method parameters and type annotations signature.")
    annotations: Dict[str, str] = Field(default_factory=dict, description="Type annotations mapping.")
    docstring: Optional[str] = Field(None, description="Extracted docstring content.")
    references: List[str] = Field(default_factory=list, description="List of relative file paths referencing this symbol.")


class FunctionInfo(BaseModel):
    """Specific metadata for a function."""

    name: str
    fully_qualified_name: str
    is_async: bool = False
    parameters: List[str] = Field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = Field(default_factory=list)
    docstring: Optional[str] = None
    complexity: int = 1
    file_path: str
    line_number: int


class MethodInfo(BaseModel):
    """Specific metadata for a class method."""

    name: str
    class_name: str
    fully_qualified_name: str
    is_async: bool = False
    parameters: List[str] = Field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = Field(default_factory=list)
    docstring: Optional[str] = None
    complexity: int = 1
    file_path: str
    line_number: int


class ClassInfo(BaseModel):
    """Specific metadata for a class definition."""

    name: str
    fully_qualified_name: str
    bases: List[str] = Field(default_factory=list, description="Base classes inherited.")
    decorators: List[str] = Field(default_factory=list)
    docstring: Optional[str] = None
    methods: List[MethodInfo] = Field(default_factory=list)
    nested_classes: List[str] = Field(default_factory=list, description="Names of nested classes.")
    file_path: str
    line_number: int


class VariableInfo(BaseModel):
    """Specific metadata for a variable declaration."""

    name: str
    fully_qualified_name: str
    type_annotation: Optional[str] = None
    scope: str
    file_path: str
    line_number: int


class ConstantInfo(BaseModel):
    """Specific metadata for a constant declaration (uppercase variables)."""

    name: str
    fully_qualified_name: str
    value_snippet: Optional[str] = None
    file_path: str
    line_number: int


class ImportInfo(BaseModel):
    """Information about an import statement."""

    module_name: str = Field(..., description="Module path being imported.")
    imported_name: str = Field(..., description="Symbol name being imported (empty for module imports).")
    alias: Optional[str] = Field(None, description="Alias in 'as alias' clauses.")
    is_relative: bool = False
    level: int = 0
    file_path: str = Field(..., description="File where import statement occurs.")
    line_number: int = Field(..., description="Line number of statement.")


class DependencyNode(BaseModel):
    """Represents a node in the module dependency graph."""

    module_name: str
    file_path: str
    imports: List[ImportInfo] = Field(default_factory=list)


class DependencyGraph(BaseModel):
    """Represents module dependency relationships across the workspace."""

    nodes: Dict[str, DependencyNode] = Field(default_factory=dict, description="Mapping module names to nodes.")
    dependencies: Dict[str, List[str]] = Field(
        default_factory=dict, description="Mapping module name to list of modules it imports."
    )
    dependents: Dict[str, List[str]] = Field(
        default_factory=dict, description="Reverse mapping from module to modules importing it."
    )
    circular_dependencies: List[List[str]] = Field(
        default_factory=list, description="List of circular import loops detected."
    )


class CallGraph(BaseModel):
    """Represents call execution chains statically resolvable in workspace."""

    calls: Dict[str, List[str]] = Field(
        default_factory=dict, description="Maps caller fully qualified name to list of callees."
    )
    callers: Dict[str, List[str]] = Field(
        default_factory=dict, description="Maps callee fully qualified name to list of callers."
    )
    recursive_calls: List[str] = Field(
        default_factory=list, description="List of functions that make recursive calls to themselves."
    )


class ComplexityReport(BaseModel):
    """Complexity analysis statistics for a single file or entity."""

    file_path: str
    cyclomatic_complexity: int = 1
    cognitive_complexity: int = 0
    max_nesting_depth: int = 0
    function_count: int = 0
    class_count: int = 0
    total_loc: int = 0
    average_function_length: float = 0.0
    max_function_length: int = 0
    max_class_length: int = 0
    max_parameter_count: int = 0
    maintainability_index: float = 100.0


class DuplicateReport(BaseModel):
    """Contains duplicated code logic blocks detected in codebase."""

    file_path_a: str
    file_path_b: str
    line_start_a: int
    line_start_b: int
    line_end_a: int
    line_end_b: int
    similarity_score: float = 1.0
    code_snippet: Optional[str] = None


class DeadCodeReport(BaseModel):
    """Unused imports, variables, functions, and dead branches report."""

    unused_imports: List[ImportInfo] = Field(default_factory=list)
    unused_functions: List[FunctionInfo] = Field(default_factory=list)
    unused_methods: List[MethodInfo] = Field(default_factory=list)
    unused_classes: List[ClassInfo] = Field(default_factory=list)
    unused_variables: List[VariableInfo] = Field(default_factory=list)
    unused_constants: List[ConstantInfo] = Field(default_factory=list)
    unreachable_blocks: List[ASTNodeInfo] = Field(default_factory=list)


class SemanticSearchResult(BaseModel):
    """Payload of a single code semantic search result match."""

    symbol: Symbol
    score: float
    matched_by: str = Field(..., description="Matched category (e.g. 'name', 'docstring', 'filename').")


class AnalysisMetadata(BaseModel):
    """Metadata regarding code intelligence analysis operations."""

    scan_time: float
    analyzed_files: int
    python_version: str
    cache_used: bool = False


class RepositoryIntelligenceSummary(BaseModel):
    """Aggregated global counts across the analyzed workspace."""

    total_classes: int = 0
    total_functions: int = 0
    total_methods: int = 0
    total_variables: int = 0
    total_loc: int = 0
    total_complexity: int = 0


class IntelligenceReport(BaseModel):
    """Complete consolidated analysis report payload."""

    summary: RepositoryIntelligenceSummary
    symbols: Dict[str, Symbol] = Field(default_factory=dict)
    classes: List[ClassInfo] = Field(default_factory=list)
    functions: List[FunctionInfo] = Field(default_factory=list)
    dependency_graph: DependencyGraph
    call_graph: CallGraph
    complexity_reports: Dict[str, ComplexityReport] = Field(default_factory=dict)
    duplicates: List[DuplicateReport] = Field(default_factory=list)
    dead_code: DeadCodeReport
    metadata: AnalysisMetadata


class AnalysisResult(BaseModel):
    """Result of single file analysis including AST details and localized report."""

    file_path: str
    symbols: List[Symbol] = Field(default_factory=list)
    classes: List[ClassInfo] = Field(default_factory=list)
    functions: List[FunctionInfo] = Field(default_factory=list)
    imports: List[ImportInfo] = Field(default_factory=list)
    complexity: ComplexityReport
    dead_code: DeadCodeReport
