"""Asset Job Manager for Nova-AI Desktop Automation.

Manages background lifecycle for long-running batch asset import/export jobs,
tracking per-file progress, state transitions, results, and controlled cancellation.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
import time
import threading
import structlog

logger = structlog.get_logger("asset_job_manager")


class AssetJobState(str, Enum):
    """Lifecycle states for Asset Jobs."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AssetJob:
    """Dataclass representing a batch asset processing job."""

    def __init__(
        self,
        job_id: str,
        operation: str,
        files: List[str],
        blender_executable: str,
    ):
        self.job_id = job_id
        self.operation = operation
        self.files = files
        self.blender_executable = blender_executable
        self.state = AssetJobState.QUEUED
        self.total_files = len(files)
        self.completed_files = 0
        self.failed_files = 0
        self.current_file: Optional[str] = None
        self.progress = 0.0
        self.per_file_results: List[Dict[str, Any]] = []
        self.error_reason: Optional[str] = None
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.cancel_requested = False

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation."""
        return {
            "job_id": self.job_id,
            "operation": self.operation,
            "state": self.state.value,
            "total_files": self.total_files,
            "completed_files": self.completed_files,
            "failed_files": self.failed_files,
            "current_file": self.current_file,
            "progress": self.progress,
            "per_file_results": self.per_file_results,
            "error_reason": self.error_reason,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "cancel_requested": self.cancel_requested,
        }


class AssetJobManager:
    """Singleton manager controlling batch asset conversion/processing jobs."""

    _instance: Optional["AssetJobManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._jobs: Dict[str, AssetJob] = {}

    @classmethod
    def get_instance(cls) -> "AssetJobManager":
        """Thread-safe singleton getter."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def submit_job(
        self,
        job_id: str,
        operation: str,
        files: List[str],
        blender_executable: str,
    ) -> AssetJob:
        """Submits a new batch asset job."""
        with self._lock:
            job = AssetJob(
                job_id=job_id,
                operation=operation,
                files=files,
                blender_executable=blender_executable,
            )
            self._jobs[job_id] = job
            logger.info("Asset job submitted", job_id=job_id, operation=operation, total_files=len(files))
            return job

    def get_job(self, job_id: str) -> Optional[AssetJob]:
        """Retrieves job by ID."""
        with self._lock:
            return self._jobs.get(job_id)

    def get_status(self, job_id: str) -> AssetJobState:
        """Gets current state of job."""
        with self._lock:
            job = self._jobs.get(job_id)
            return job.state if job else AssetJobState.FAILED

    def cancel_job(self, job_id: str) -> bool:
        """Requests cancellation of a running job."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            if job.state in (AssetJobState.COMPLETED, AssetJobState.FAILED, AssetJobState.CANCELLED):
                return False
            job.cancel_requested = True
            job.state = AssetJobState.CANCELLED
            job.end_time = time.time()
            logger.info("Asset job cancelled", job_id=job_id)
            return True

    def record_file_result(self, job_id: str, filepath: str, success: bool, details: Optional[str] = None):
        """Records progress and outcome for an individual file in batch."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            if success:
                job.completed_files += 1
            else:
                job.failed_files += 1
            job.per_file_results.append({
                "filepath": filepath,
                "success": success,
                "details": details,
                "timestamp": time.time(),
            })
            job.current_file = filepath
            if job.total_files > 0:
                job.progress = (job.completed_files + job.failed_files) / job.total_files
            if job.state == AssetJobState.QUEUED:
                job.state = AssetJobState.RUNNING

    def finalize_job(self, job_id: str, error_reason: Optional[str] = None):
        """Finalizes job outcome based on file metrics."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.end_time = time.time()
            if job.cancel_requested:
                job.state = AssetJobState.CANCELLED
            elif error_reason:
                job.state = AssetJobState.FAILED
                job.error_reason = error_reason
            elif job.failed_files == 0:
                job.state = AssetJobState.COMPLETED
            elif job.completed_files > 0:
                job.state = AssetJobState.PARTIAL_SUCCESS
            else:
                job.state = AssetJobState.FAILED
            job.progress = 1.0
            logger.info("Asset job finalized", job_id=job_id, final_state=job.state.value)

    def list_jobs(self) -> List[Dict[str, Any]]:
        """Returns summary list of all jobs."""
        with self._lock:
            return [job.to_dict() for job in self._jobs.values()]
