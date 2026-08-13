"""Interfaces for the Enterprise Software Project Manager Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.agents.software_engineer.project_manager.models import (
    Project,
    ProjectRequirement,
    UserStory,
    Epic,
    Feature,
    Task,
    SubTask,
    Milestone,
    Sprint,
    Dependency,
    Risk,
    Estimate,
    Progress,
    ProjectReport,
)

class IRequirementAnalyzer(ABC):
    """Abstract interface for parsing and analyzing requirements."""

    @abstractmethod
    def analyze_requirements(self, raw_input: str) -> ProjectRequirement:
        """Analyzes text requirements and extracts goals, features, and constraints."""
        pass

class ITaskGenerator(ABC):
    """Abstract interface for task generation and hierarchical decomposition."""

    @abstractmethod
    def generate_tasks_for_feature(self, feature: Feature) -> List[Task]:
        """Generates detailed tasks for a feature including dev, test, docs, and deploy."""
        pass

    @abstractmethod
    def decompose_feature(self, name: str, description: str) -> Epic:
        """Decomposes a large feature into Epic -> Feature -> Task -> Subtask tree."""
        pass

class IProjectPlanner(ABC):
    """Abstract interface for roadmap planning and milestone scheduling."""

    @abstractmethod
    def create_roadmap(self, project: Project) -> List[Milestone]:
        """Generates roadmaps, phases, and milestone dependencies."""
        pass

class ISprintManager(ABC):
    """Abstract interface for planning and tracking sprints."""

    @abstractmethod
    def plan_sprint(self, backlog: List[Task], duration_weeks: int, goal: str) -> Sprint:
        """Creates a sprint allocation from backlog tasks."""
        pass

class IEstimationEngine(ABC):
    """Abstract interface for task estimation."""

    @abstractmethod
    def estimate_task(self, task: Task) -> Estimate:
        """Estimates dev, test, docs, and deploy durations using complexity metrics."""
        pass

class IRiskAnalyzer(ABC):
    """Abstract interface for risk assessment and mitigation planning."""

    @abstractmethod
    def analyze_risks(self, project: Project) -> List[Risk]:
        """Scans project, features, and dependencies to flag risks."""
        pass

class IProgressTracker(ABC):
    """Abstract interface for status monitoring and tracking."""

    @abstractmethod
    def calculate_progress(self, project: Project) -> Progress:
        """Calculates completed, pending, blocked metrics and velocity."""
        pass

class IReportGenerator(ABC):
    """Abstract interface for formatting project reports."""

    @abstractmethod
    def generate_report(self, project: Project, report_type: str, format_type: str) -> ProjectReport:
        """Generates markdown or HTML reports."""
        pass

class IKnowledgeManager(ABC):
    """Abstract interface for knowledge synchronization."""

    @abstractmethod
    def sync_knowledge(self, project: Project) -> bool:
        """Synchronizes architectural decisions and lessons learned with the Knowledge Base."""
        pass

class IProjectManagerEngine(ABC):
    """Abstract interface for the orchestrating Project Manager Engine."""

    @abstractmethod
    async def process_requirements(self, prompt: str) -> ProjectReport:
        """Runs the complete project management pipeline from requirements to report."""
        pass
