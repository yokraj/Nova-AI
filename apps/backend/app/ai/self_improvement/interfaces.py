"""Abstract base contracts for Autonomous Self-Improvement & Adaptive Intelligence Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.self_improvement.models import (
    AgentScorecard,
    BenchmarkReport,
    ExperiencePackage,
    PerformanceMetricsSnapshot,
    QualityDiagnosticReport,
    SelfImprovementHealth,
    SelfImprovementMetrics,
    WorkflowOptimizationRecommendation,
)


class IPerformanceAnalyzer(ABC):
    """Performance Analyzer contract analyzing latency, success rate, and resource usage."""

    @abstractmethod
    def analyze_subsystem(self, subsystem_name: str) -> PerformanceMetricsSnapshot:
        """Analyzes subsystem performance metrics."""
        pass


class IWorkflowOptimizer(ABC):
    """Workflow Optimizer contract detecting duplicate steps and generating optimizations."""

    @abstractmethod
    def optimize_workflow(self, workflow_id: str, steps: List[str]) -> WorkflowOptimizationRecommendation:
        """Generates workflow optimization recommendation."""
        pass


class IExperienceDistiller(ABC):
    """Experience Distiller contract converting repeated workflows into reusable skills and templates."""

    @abstractmethod
    def distill_experience(self, workflow_name: str, steps: List[str]) -> ExperiencePackage:
        """Distills repeated workflow into ExperiencePackage."""
        pass


class IBenchmarkEngine(ABC):
    """Benchmark Engine contract running agent and subsystem benchmarks."""

    @abstractmethod
    def run_benchmark(self) -> BenchmarkReport:
        """Runs complete benchmark suite across agents and runtimes."""
        pass


class IQualityEngine(ABC):
    """Quality Engine contract detecting regressions and failure patterns."""

    @abstractmethod
    def check_quality(self) -> QualityDiagnosticReport:
        """Runs quality diagnostic check for regressions."""
        pass


class ISelfImprovementManager(ABC):
    """Subsystem Manager administrative contract."""

    @abstractmethod
    async def start(self) -> None:
        """Starts self-improvement manager."""
        pass


class IUniversalSelfImprovementEngine(ABC):
    """Central Universal Self-Improvement Engine facade contract."""

    @abstractmethod
    async def self_improve(self) -> Dict[str, Any]:
        """Runs self-improvement optimization pass."""
        pass

    @abstractmethod
    async def performance_report(self) -> Dict[str, Any]:
        """Retrieves system performance report."""
        pass

    @abstractmethod
    async def workflow_recommendations(self) -> List[Dict[str, Any]]:
        """Retrieves workflow optimization recommendations."""
        pass

    @abstractmethod
    async def agent_scorecard(self) -> List[Dict[str, Any]]:
        """Retrieves agent scorecard evaluations."""
        pass

    @abstractmethod
    async def benchmark_report(self) -> Dict[str, Any]:
        """Retrieves historical benchmark report."""
        pass

    @abstractmethod
    async def quality_report(self) -> Dict[str, Any]:
        """Retrieves quality diagnostic report."""
        pass

    @abstractmethod
    async def adaptive_settings(self) -> Dict[str, Any]:
        """Retrieves adaptive behavior settings."""
        pass

    @abstractmethod
    async def experience_summary(self) -> Dict[str, Any]:
        """Retrieves summary of distilled experience packages."""
        pass
