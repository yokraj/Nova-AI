"""Blender Async Render Job Manager.

Manages long-running render jobs via controlled subprocesses.
Provides non-blocking job submission, progress tracking, controlled cancellation,
timeout management, and output verification.
"""

from enum import Enum
from typing import Dict, List, Optional
import os
import uuid
import time
import subprocess
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger("render_job_manager")


class RenderJobState(str, Enum):
    """Render job lifecycle states."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"


class RenderJobProgress(BaseModel):
    """Progress snapshot for a render job."""

    percentage: float = 0.0
    current_frame: Optional[int] = None
    total_frames: Optional[int] = None
    status_message: str = "Initializing"


class RenderJobResult(BaseModel):
    """Execution result summary for a render job."""

    job_id: str
    state: RenderJobState
    output_files: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    duration_sec: float = 0.0


class RenderJob:
    """Dataclass holding the state and process handle of a active or historical render job."""

    def __init__(
        self,
        job_id: str,
        output_path: str,
        render_type: str = "STILL",
        scene_file: Optional[str] = None,
        start_frame: int = 1,
        end_frame: int = 1,
        step: int = 1,
        timeout_sec: float = 60.0,
    ) -> None:
        self.job_id = job_id
        self.output_path = output_path
        self.render_type = render_type
        self.scene_file = scene_file
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.step = step
        self.timeout_sec = timeout_sec

        self.state = RenderJobState.QUEUED
        self.progress = RenderJobProgress()
        self.process: Optional[subprocess.Popen] = None
        self.script_path: Optional[str] = None
        self.start_time: float = time.time()
        self.end_time: Optional[float] = None
        self.error_message: Optional[str] = None
        self.output_files: List[str] = []

    def update_status() -> None:
        pass


class RenderJobManager:
    """Manages creation, monitoring, cancellation, and retrieval of async Blender render jobs."""

    _instance: Optional["RenderJobManager"] = None

    def __init__(self) -> None:
        self._jobs: Dict[str, RenderJob] = {}

    @classmethod
    def get_instance(cls) -> "RenderJobManager":
        if cls._instance is None:
            cls._instance = RenderJobManager()
        return cls._instance

    def submit_job(
        self,
        job_id: Optional[str],
        blender_executable: str,
        script_path: str,
        output_path: str,
        render_type: str = "STILL",
        scene_file: Optional[str] = None,
        start_frame: int = 1,
        end_frame: int = 1,
        step: int = 1,
        timeout_sec: float = 60.0,
    ) -> RenderJob:
        """Submits a new async render job using controlled subprocess execution."""
        final_job_id = job_id or f"NOVA-RENDER-{uuid.uuid4().hex[:8]}"
        if final_job_id in self._jobs and self._jobs[final_job_id].state in (
            RenderJobState.RUNNING,
            RenderJobState.QUEUED,
        ):
            raise ValueError(f"Job ID '{final_job_id}' is already active.")

        job = RenderJob(
            job_id=final_job_id,
            output_path=output_path,
            render_type=render_type,
            scene_file=scene_file,
            start_frame=start_frame,
            end_frame=end_frame,
            step=step,
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
            job.state = RenderJobState.RUNNING
            job.progress = RenderJobProgress(
                percentage=0.0,
                status_message="Blender background process started",
            )
            self._jobs[final_job_id] = job
            logger.info("Render job submitted successfully", job_id=final_job_id, cmd=cmd)
            return job
        except Exception as e:
            job.state = RenderJobState.FAILED
            job.error_message = f"Subprocess creation error: {str(e)}"
            self._jobs[final_job_id] = job
            logger.error("Failed to launch render subprocess", job_id=final_job_id, error=str(e))
            return job

    def poll_job(self, job_id: str) -> RenderJob:
        """Polls active render job process state and updates progress/verification."""
        if job_id not in self._jobs:
            raise KeyError(f"Job '{job_id}' not found.")

        job = self._jobs[job_id]
        if job.state not in (RenderJobState.RUNNING, RenderJobState.CANCEL_REQUESTED):
            return job

        elapsed = time.time() - job.start_time
        if job.process is None:
            job.state = RenderJobState.FAILED
            job.error_message = "No subprocess handle associated with job."
            return job

        ret = job.process.poll()
        if ret is None:
            if elapsed > job.timeout_sec:
                logger.warning("Render job timed out", job_id=job_id, elapsed=elapsed, timeout=job.timeout_sec)
                self.cancel_job(job_id)
                job.state = RenderJobState.TIMEOUT
                job.error_message = f"Render exceeded timeout limit of {job.timeout_sec}s."
                job.end_time = time.time()
                return job

            # Calculate progress if animation
            if job.render_type == "ANIMATION" and job.end_frame >= job.start_frame:
                total = ((job.end_frame - job.start_frame) // max(1, job.step)) + 1
                found_count = self._count_rendered_frame_files(job.output_path, job.start_frame, job.end_frame, job.step)
                pct = min(99.0, round((found_count / max(1, total)) * 100.0, 1))
                job.progress = RenderJobProgress(
                    percentage=pct,
                    current_frame=job.start_frame + (found_count * job.step),
                    total_frames=total,
                    status_message=f"Rendering frame sequence ({found_count}/{total})",
                )
            else:
                job.progress = RenderJobProgress(
                    percentage=50.0,
                    status_message="Rendering in progress...",
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

        if job.state == RenderJobState.CANCEL_REQUESTED:
            job.state = RenderJobState.CANCELLED
            job.progress = RenderJobProgress(percentage=0.0, status_message="Render cancelled")
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

        out_files = self._collect_output_files(job)

        if ret == 0 and has_success and not has_error_marker and not has_exception and len(out_files) > 0:
            job.state = RenderJobState.COMPLETED
            job.output_files = out_files
            job.progress = RenderJobProgress(
                percentage=100.0,
                status_message=f"Completed successfully ({len(out_files)} files produced)",
            )
        else:
            job.state = RenderJobState.FAILED
            job.output_files = out_files
            if len(out_files) == 0 and (has_success or ret == 0):
                job.error_message = f"Render process completed but produced no valid non-empty files at {job.output_path}."
            else:
                job.error_message = f"Render process failed (ret={ret}): {stdout.strip() or stderr.strip()}"
            job.progress = RenderJobProgress(percentage=0.0, status_message="Render failed")

        return job

    def get_job(self, job_id: str) -> Optional[RenderJob]:
        """Returns poll-updated render job."""
        if job_id not in self._jobs:
            return None
        return self.poll_job(job_id)

    def get_jobs(self) -> List[RenderJob]:
        """Returns poll-updated list of all jobs."""
        results = []
        for jid in list(self._jobs.keys()):
            results.append(self.poll_job(jid))
        return results

    def get_status(self, job_id: str) -> RenderJobState:
        """Returns current state of a render job."""
        job = self.get_job(job_id)
        if not job:
            raise KeyError(f"Job '{job_id}' not found.")
        return job.state

    def get_progress(self, job_id: str) -> RenderJobProgress:
        """Returns current progress of a render job."""
        job = self.get_job(job_id)
        if not job:
            raise KeyError(f"Job '{job_id}' not found.")
        return job.progress

    def wait_for_job(self, job_id: str, timeout_sec: float = 30.0) -> RenderJobResult:
        """Blocks up to timeout_sec until job finishes or times out."""
        start = time.time()
        while time.time() - start < timeout_sec:
            job = self.poll_job(job_id)
            if job.state in (
                RenderJobState.COMPLETED,
                RenderJobState.FAILED,
                RenderJobState.CANCELLED,
                RenderJobState.TIMEOUT,
            ):
                return RenderJobResult(
                    job_id=job.job_id,
                    state=job.state,
                    output_files=job.output_files,
                    error_message=job.error_message,
                    duration_sec=(job.end_time or time.time()) - job.start_time,
                )
            time.sleep(0.2)

        job = self.poll_job(job_id)
        return RenderJobResult(
            job_id=job.job_id,
            state=job.state,
            output_files=job.output_files,
            error_message="Wait timeout reached while job is still running.",
            duration_sec=time.time() - job.start_time,
        )

    def cancel_job(self, job_id: str) -> bool:
        """Requests controlled cancellation of a running render process."""
        if job_id not in self._jobs:
            return False
        job = self._jobs[job_id]
        if job.state not in (RenderJobState.RUNNING, RenderJobState.QUEUED):
            return False

        job.state = RenderJobState.CANCEL_REQUESTED
        if job.process and job.process.poll() is None:
            try:
                job.process.terminate()
                try:
                    job.process.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    job.process.kill()
                    job.process.wait(timeout=1.0)
            except Exception as e:
                logger.error("Error terminating process", job_id=job_id, error=str(e))

        job.state = RenderJobState.CANCELLED
        job.end_time = time.time()
        job.progress = RenderJobProgress(percentage=0.0, status_message="Cancelled by user")
        return True

    def remove_job(self, job_id: str) -> bool:
        """Removes a finished job record."""
        if job_id not in self._jobs:
            return False
        job = self.poll_job(job_id)
        if job.state in (RenderJobState.RUNNING, RenderJobState.CANCEL_REQUESTED):
            return False
        del self._jobs[job_id]
        return True

    def retry_job(self, job_id: str, blender_executable: str) -> Optional[RenderJob]:
        """Retries a failed or cancelled render job."""
        if job_id not in self._jobs:
            return None
        old_job = self._jobs[job_id]
        if old_job.state in (RenderJobState.RUNNING, RenderJobState.QUEUED):
            return old_job
        if not old_job.script_path or not os.path.exists(old_job.script_path):
            raise ValueError("Cannot retry job: script artifact no longer exists on disk.")

        return self.submit_job(
            job_id=f"{old_job.job_id}-retry",
            blender_executable=blender_executable,
            script_path=old_job.script_path,
            output_path=old_job.output_path,
            render_type=old_job.render_type,
            scene_file=old_job.scene_file,
            start_frame=old_job.start_frame,
            end_frame=old_job.end_frame,
            step=old_job.step,
            timeout_sec=old_job.timeout_sec,
        )

    def _collect_output_files(self, job: RenderJob) -> List[str]:
        """Verifies existence and non-emptiness of expected render output file(s)."""
        target = job.output_path
        valid_files = []
        if os.path.isfile(target):
            if os.path.getsize(target) > 0:
                valid_files.append(target)
            return valid_files

        if os.path.isdir(target):
            for fname in os.listdir(target):
                fpath = os.path.join(target, fname)
                if os.path.isfile(fpath) and os.path.getsize(fpath) > 0:
                    valid_files.append(fpath)
            return valid_files

        # Frame pattern checks, e.g., output_path = "C:/tmp/render_" -> Blender outputs "C:/tmp/render_0001.png"
        parent_dir = os.path.dirname(target)
        base_prefix = os.path.basename(target)
        if os.path.isdir(parent_dir):
            for fname in os.listdir(parent_dir):
                if fname.startswith(base_prefix):
                    fpath = os.path.join(parent_dir, fname)
                    if os.path.isfile(fpath) and os.path.getsize(fpath) > 0:
                        valid_files.append(fpath)
        return valid_files

    def _count_rendered_frame_files(
        self, output_path: str, start_frame: int, end_frame: int, step: int
    ) -> int:
        """Counts existing rendered frame files for progress calculation."""
        parent_dir = os.path.dirname(output_path)
        base_prefix = os.path.basename(output_path)
        count = 0
        if not os.path.isdir(parent_dir):
            return 0
        for f in os.listdir(parent_dir):
            if f.startswith(base_prefix):
                fp = os.path.join(parent_dir, f)
                if os.path.isfile(fp) and os.path.getsize(fp) > 0:
                    count += 1
        return count
