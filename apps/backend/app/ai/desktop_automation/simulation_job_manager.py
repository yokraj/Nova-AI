"""Blender Simulation & Bake Job Manager.

Manages physics simulations and bake jobs via controlled background subprocesses.
Provides non-blocking simulation job submission, progress monitoring, controlled cancellation,
timeout management, and physical disk cache artifact verification.
"""

from enum import Enum
from typing import Dict, List, Optional
import os
import uuid
import time
import subprocess
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger("simulation_job_manager")


class SimulationJobState(str, Enum):
    """Simulation job lifecycle states."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"


class SimulationJobProgress(BaseModel):
    """Progress snapshot for a physics simulation bake job."""

    percentage: float = 0.0
    current_frame: Optional[int] = None
    total_frames: Optional[int] = None
    status_message: str = "Initializing simulation"


class SimulationJobResult(BaseModel):
    """Execution result summary for a simulation bake job."""

    job_id: str
    state: SimulationJobState
    cache_files: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    duration_sec: float = 0.0


class SimulationJob:
    """Holds state, configuration, and process handle for a physics simulation job."""

    def __init__(
        self,
        job_id: str,
        sim_type: str = "RIGID_BODY",
        cache_dir: Optional[str] = None,
        scene_file: Optional[str] = None,
        start_frame: int = 1,
        end_frame: int = 25,
        timeout_sec: float = 60.0,
    ) -> None:
        self.job_id = job_id
        self.sim_type = sim_type
        self.cache_dir = cache_dir
        self.scene_file = scene_file
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.timeout_sec = timeout_sec

        self.state = SimulationJobState.QUEUED
        self.progress = SimulationJobProgress()
        self.process: Optional[subprocess.Popen] = None
        self.script_path: Optional[str] = None
        self.start_time: float = time.time()
        self.end_time: Optional[float] = None
        self.error_message: Optional[str] = None
        self.cache_files: List[str] = []


class SimulationJobManager:
    """Manages creation, monitoring, cancellation, and retrieval of async Blender simulation jobs."""

    _instance: Optional["SimulationJobManager"] = None

    def __init__(self) -> None:
        self._jobs: Dict[str, SimulationJob] = {}

    @classmethod
    def get_instance(cls) -> "SimulationJobManager":
        if cls._instance is None:
            cls._instance = SimulationJobManager()
        return cls._instance

    def submit_job(
        self,
        job_id: Optional[str],
        blender_executable: str,
        script_path: str,
        sim_type: str = "RIGID_BODY",
        cache_dir: Optional[str] = None,
        scene_file: Optional[str] = None,
        start_frame: int = 1,
        end_frame: int = 25,
        timeout_sec: float = 60.0,
    ) -> SimulationJob:
        """Submits a new async simulation bake job using background subprocess execution."""
        final_job_id = job_id or f"NOVA-SIM-{uuid.uuid4().hex[:8]}"
        if final_job_id in self._jobs and self._jobs[final_job_id].state in (
            SimulationJobState.RUNNING,
            SimulationJobState.QUEUED,
        ):
            raise ValueError(f"Simulation Job ID '{final_job_id}' is already active.")

        job = SimulationJob(
            job_id=final_job_id,
            sim_type=sim_type,
            cache_dir=cache_dir,
            scene_file=scene_file,
            start_frame=start_frame,
            end_frame=end_frame,
            timeout_sec=timeout_sec,
        )
        job.script_path = script_path

        cmd = [blender_executable]
        if scene_file and os.path.exists(scene_file):
            cmd.append(scene_file)
        cmd.extend(["--background", "--python", script_path])

        try:
            job.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            job.state = SimulationJobState.RUNNING
            job.progress = SimulationJobProgress(
                percentage=0.0,
                status_message=f"Blender background {sim_type} simulation started",
            )
            self._jobs[final_job_id] = job
            logger.info("Simulation job submitted successfully", job_id=final_job_id, cmd=cmd)
            return job
        except Exception as e:
            job.state = SimulationJobState.FAILED
            job.error_message = f"Subprocess creation error: {str(e)}"
            self._jobs[final_job_id] = job
            logger.error("Failed to launch simulation subprocess", job_id=final_job_id, error=str(e))
            return job

    def poll_job(self, job_id: str) -> SimulationJob:
        """Polls active simulation job process state and updates progress/cache verification."""
        if job_id not in self._jobs:
            raise KeyError(f"Simulation job '{job_id}' not found.")

        job = self._jobs[job_id]
        if job.state not in (SimulationJobState.RUNNING, SimulationJobState.CANCEL_REQUESTED):
            return job

        elapsed = time.time() - job.start_time
        if job.process is None:
            job.state = SimulationJobState.FAILED
            job.error_message = "No subprocess handle associated with simulation job."
            return job

        ret = job.process.poll()
        if ret is None:
            if elapsed > job.timeout_sec:
                logger.warning("Simulation job timed out", job_id=job_id, elapsed=elapsed, timeout=job.timeout_sec)
                self.cancel_job(job_id)
                job.state = SimulationJobState.TIMEOUT
                job.error_message = f"Simulation bake exceeded timeout limit of {job.timeout_sec}s."
                job.end_time = time.time()
                return job

            # Calculate progress based on elapsed time or cache files
            c_files = self._collect_cache_files(job)
            total = max(1, (job.end_frame - job.start_frame) + 1)
            pct = min(99.0, round((len(c_files) / total) * 100.0, 1)) if c_files else min(90.0, round((elapsed / max(1.0, job.timeout_sec)) * 100.0, 1))
            job.progress = SimulationJobProgress(
                percentage=pct,
                current_frame=job.start_frame + int(len(c_files)),
                total_frames=total,
                status_message=f"Baking simulation frames ({len(c_files)}/{total} cache files)",
            )
            return job

        job.end_time = time.time()
        stdout, stderr = job.process.communicate()
        combined_output = (stdout or "") + "\n" + (stderr or "")

        if job.script_path and os.path.exists(job.script_path):
            try:
                os.remove(job.script_path)
            except Exception:
                pass

        if job.state == SimulationJobState.CANCEL_REQUESTED:
            job.state = SimulationJobState.CANCELLED
            job.progress = SimulationJobProgress(percentage=0.0, status_message="Simulation cancelled")
            return job

        has_success = "NOVA_ACTION_SUCCESS::" in stdout
        has_error_marker = "NOVA_ACTION_ERROR::" in stdout or "ERROR_" in stdout
        traceback_terms = [
            "Traceback (most recent call last):",
            "SyntaxError:",
            "RuntimeError:",
            "TypeError:",
            "ValueError:",
            "AttributeError:",
            "IndentationError:",
        ]
        has_exception = any(term in combined_output for term in traceback_terms)

        c_files = self._collect_cache_files(job)

        if ret == 0 and has_success and not has_error_marker and not has_exception:
            job.state = SimulationJobState.COMPLETED
            job.cache_files = c_files
            job.progress = SimulationJobProgress(
                percentage=100.0,
                status_message=f"Simulation bake completed successfully ({len(c_files)} cache artifacts)",
            )
        else:
            job.state = SimulationJobState.FAILED
            job.cache_files = c_files
            job.error_message = f"Simulation bake failed (ret={ret}): {stdout.strip() or stderr.strip()}"
            job.progress = SimulationJobProgress(percentage=0.0, status_message="Simulation failed")

        return job

    def get_job(self, job_id: str) -> Optional[SimulationJob]:
        """Returns poll-updated simulation job."""
        if job_id not in self._jobs:
            return None
        return self.poll_job(job_id)

    def get_jobs(self) -> List[SimulationJob]:
        """Returns poll-updated list of all simulation jobs."""
        results = []
        for jid in list(self._jobs.keys()):
            results.append(self.poll_job(jid))
        return results

    def get_status(self, job_id: str) -> SimulationJobState:
        """Returns current state of a simulation job."""
        job = self.get_job(job_id)
        if not job:
            raise KeyError(f"Simulation job '{job_id}' not found.")
        return job.state

    def get_progress(self, job_id: str) -> SimulationJobProgress:
        """Returns current progress of a simulation job."""
        job = self.get_job(job_id)
        if not job:
            raise KeyError(f"Simulation job '{job_id}' not found.")
        return job.progress

    def wait_for_job(self, job_id: str, timeout_sec: float = 30.0) -> SimulationJobResult:
        """Blocks up to timeout_sec until job finishes or times out."""
        start = time.time()
        while time.time() - start < timeout_sec:
            job = self.poll_job(job_id)
            if job.state in (
                SimulationJobState.COMPLETED,
                SimulationJobState.FAILED,
                SimulationJobState.CANCELLED,
                SimulationJobState.TIMEOUT,
            ):
                return SimulationJobResult(
                    job_id=job.job_id,
                    state=job.state,
                    cache_files=job.cache_files,
                    error_message=job.error_message,
                    duration_sec=(job.end_time or time.time()) - job.start_time,
                )
            time.sleep(0.2)

        job = self.poll_job(job_id)
        return SimulationJobResult(
            job_id=job.job_id,
            state=job.state,
            cache_files=job.cache_files,
            error_message="Wait timeout reached while simulation job is still running.",
            duration_sec=time.time() - job.start_time,
        )

    def cancel_job(self, job_id: str) -> bool:
        """Requests controlled cancellation of a running simulation process."""
        if job_id not in self._jobs:
            return False
        job = self._jobs[job_id]
        if job.state not in (SimulationJobState.RUNNING, SimulationJobState.QUEUED):
            return False

        job.state = SimulationJobState.CANCEL_REQUESTED
        if job.process and job.process.poll() is None:
            try:
                job.process.terminate()
                try:
                    job.process.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    job.process.kill()
                    job.process.wait(timeout=1.0)
            except Exception as e:
                logger.error("Error terminating simulation process", job_id=job_id, error=str(e))

        job.state = SimulationJobState.CANCELLED
        job.end_time = time.time()
        job.progress = SimulationJobProgress(percentage=0.0, status_message="Cancelled by user")
        return True

    def remove_job(self, job_id: str) -> bool:
        """Removes a finished simulation job record."""
        if job_id not in self._jobs:
            return False
        job = self.poll_job(job_id)
        if job.state in (SimulationJobState.RUNNING, SimulationJobState.CANCEL_REQUESTED):
            return False
        del self._jobs[job_id]
        return True

    def _collect_cache_files(self, job: SimulationJob) -> List[str]:
        """Collects existing non-empty cache files from physics cache directory."""
        if not job.cache_dir or not os.path.exists(job.cache_dir):
            return []

        c_files = []
        if os.path.isfile(job.cache_dir):
            if os.path.getsize(job.cache_dir) > 0:
                c_files.append(job.cache_dir)
            return c_files

        if os.path.isdir(job.cache_dir):
            for root, _, files in os.walk(job.cache_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    if os.path.isfile(fp) and os.path.getsize(fp) > 0:
                        c_files.append(fp)
        return c_files
