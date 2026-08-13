"""Project Planner schedules roadmaps, milestones, and phases.
"""

from datetime import datetime, timedelta
from typing import List
from app.agents.software_engineer.project_manager.interfaces import IProjectPlanner
from app.agents.software_engineer.project_manager.models import Milestone, Project, Task

class LocalProjectPlanner(IProjectPlanner):
    """Calculates development milestones, critical path, and roadmap timeline phases."""

    def create_roadmap(self, project: Project) -> List[Milestone]:
        """Arranges epics/features into successive milestone phases."""
        milestones = []
        start_time = datetime.utcnow()

        # Gather all task IDs from epics
        all_tasks: List[Task] = []
        for epic in project.epics:
            for feature in epic.features:
                all_tasks.extend(feature.tasks)

        # Split tasks into phases:
        # Phase 1: Database and Backend (First 40% of tasks)
        # Phase 2: Frontend Integration (Next 40% of tasks)
        # Phase 3: Testing, Docs, and Deployment (Remaining tasks)
        task_ids = [t.id for t in all_tasks]
        n_tasks = len(task_ids)

        if n_tasks > 0:
            p1_split = int(n_tasks * 0.4) or 1
            p2_split = int(n_tasks * 0.8) or 2

            milestones.append(Milestone(
                id="milestone-phase-1",
                name="Database & Core Services Architecture Completion",
                target_date=start_time + timedelta(days=14),
                tasks=task_ids[:p1_split]
            ))

            milestones.append(Milestone(
                id="milestone-phase-2",
                name="Frontend Layout UI Integration Ready",
                target_date=start_time + timedelta(days=28),
                tasks=task_ids[p1_split:p2_split]
            ))

            milestones.append(Milestone(
                id="milestone-phase-3",
                name="Security Hardening, Testing & Deployment Release",
                target_date=start_time + timedelta(days=42),
                tasks=task_ids[p2_split:]
            ))
        else:
            milestones.append(Milestone(
                id="milestone-general",
                name="Core Foundation Ready",
                target_date=start_time + timedelta(days=7),
                tasks=[]
            ))

        return milestones
