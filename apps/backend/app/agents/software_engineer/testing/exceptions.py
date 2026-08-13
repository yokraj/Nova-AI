"""Domain exceptions for the Testing & Quality Assurance Engine.
"""

from app.agents.software_engineer.exceptions import SoftwareEngineerError


class TestingError(SoftwareEngineerError):
    """Base exception for all testing-related operations."""

    pass


class TestGenerationError(TestingError):
    """Raised when generating test code fails."""

    pass


class TestExecutionError(TestingError):
    """Raised when executing test files fails."""

    pass


class CoverageError(TestingError):
    """Raised when parsing or reading coverage results fails."""

    pass


class BenchmarkError(TestingError):
    """Raised when recording performance benchmarks fails."""

    pass


class ValidationError(TestingError):
    """Raised when checking test suite syntax or imports integrity fails."""

    pass


class RepairError(TestingError):
    """Raised when formulating recommendations for failing tests fails."""

    pass


class SecurityAnalysisError(TestingError):
    """Raised when scanning code for security vulnerabilities fails."""

    pass


class StaticAnalysisError(TestingError):
    """Raised when verifying architecture guidelines alignment fails."""

    pass


class ReportGenerationError(TestingError):
    """Raised when generating reports output files fails."""

    pass


class TimeoutError(TestingError):
    """Raised when test execution exceeds maximum allocated timeout limits."""

    pass


class MockGenerationError(TestingError):
    """Raised when creating dependency mock structures fails."""

    pass
