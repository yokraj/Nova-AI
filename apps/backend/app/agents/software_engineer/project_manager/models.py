"""Pydantic data models for the Enterprise Software Project Manager Engine.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ProjectStatus(str, Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class TaskStatus(str, Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ProjectRequirement(BaseModel):
    project_name: str = Field(..., description="Name of the project/system.")
    goal: str = Field(..., description="Core business goal.")
    modules: List[str] = Field(default_factory=list, description="Extracted high-level functional modules.")
    constraints: List[str] = Field(default_factory=list, description="Technical constraints or business limits.")
    technology_requirements: List[str] = Field(default_factory=list, description="Required tech stack languages or runtimes.")
    dependencies: List[str] = Field(default_factory=list, description="External software or service dependencies.")
    risks: List[str] = Field(default_factory=list, description="Perceived technical risks.")

class UserStory(BaseModel):
    id: str
    title: str
    description: str
    acceptance_criteria: List[str] = Field(default_factory=list)

class SubTask(BaseModel):
    id: str
    title: str
    status: TaskStatus = Field(TaskStatus.PLANNED)

class Estimate(BaseModel):
    dev_hours: float = Field(0.0)
    test_hours: float = Field(0.0)
    doc_hours: float = Field(0.0)
    deploy_hours: float = Field(0.0)
    total_hours: float = Field(0.0)

class Dependency(BaseModel):
    task_id: str
    depends_on_task_id: str

class Task(BaseModel):
    id: str
    title: str
    description: str
    status: TaskStatus = Field(TaskStatus.PLANNED)
    priority: str = Field("Medium", description="Critical, High, Medium, Low")
    estimate: Estimate = Field(default_factory=Estimate)
    subtasks: List[SubTask] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs this task depends on.")

class Feature(BaseModel):
    id: str
    name: str
    description: str
    tasks: List[Task] = Field(default_factory=list)

class Epic(BaseModel):
    id: str
    name: str
    description: str
    features: List[Feature] = Field(default_factory=list)

class Milestone(BaseModel):
    id: str
    name: str
    target_date: datetime = Field(default_factory=datetime.utcnow)
    tasks: List[str] = Field(default_factory=list, description="List of task IDs in this milestone.")
    is_completed: bool = Field(False)

class Sprint(BaseModel):
    id: str
    name: str
    goal: str
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime = Field(default_factory=datetime.utcnow)
    duration_weeks: int = Field(2)
    tasks: List[Task] = Field(default_factory=list)
    is_completed: bool = Field(False)

class Risk(BaseModel):
    id: str
    description: str
    level: str = Field("Medium", description="Critical, High, Medium, Low")
    impact: str = Field("Medium", description="High, Medium, Low")
    probability: str = Field("Medium", description="High, Medium, Low")
    mitigation_strategy: str

class Progress(BaseModel):
    progress_percentage: float = Field(0.0)
    completed_tasks: int = Field(0)
    pending_tasks: int = Field(0)
    blocked_tasks: int = Field(0)
    total_tasks: int = Field(0)
    velocity: float = Field(0.0, description="Tasks completed per sprint estimation.")
    remaining_work_hours: float = Field(0.0)
    eta: datetime = Field(default_factory=datetime.utcnow)

class ResourceAllocation(BaseModel):
    agent_id: str
    assigned_tasks: List[str] = Field(default_factory=list)
    capacity_hours: float = Field(40.0)

class Project(BaseModel):
    name: str
    requirements: ProjectRequirement
    epics: List[Epic] = Field(default_factory=list)
    milestones: List[Milestone] = Field(default_factory=list)
    sprints: List[Sprint] = Field(default_factory=list)
    risks: List[Risk] = Field(default_factory=list)
    progress: Progress = Field(default_factory=Progress)
    status: ProjectStatus = Field(ProjectStatus.PLANNED)
    resource_allocations: List[ResourceAllocation] = Field(default_factory=list)

class ProjectReport(BaseModel):
    status: str = Field(..., description="success, warning, failed")
    project_name: str
    report_type: str = Field(..., description="Project progress report or Sprint report")
    format_type: str = Field("markdown", description="markdown, html, pdf")
    content_markdown: str = Field("", description="Formated report content.")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
