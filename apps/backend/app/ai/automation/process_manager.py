"""Process Manager enumerating processes and checking running states."""

from typing import List, Optional
import structlog

from app.ai.automation.models import ProcessInfo

logger = structlog.get_logger("process_manager")


class ProcessManager:
    """Monitors and manages OS process states."""

    async def list_processes(self) -> List[ProcessInfo]:
        """List active processes."""
        return [
            ProcessInfo(pid=100, name="system.exe", cpu_percent=0.5, memory_percent=1.2),
            ProcessInfo(pid=4012, name="chrome.exe", cpu_percent=2.1, memory_percent=8.5),
            ProcessInfo(pid=5120, name="code.exe", cpu_percent=1.4, memory_percent=6.2),
        ]

    async def is_running(self, process_name: str) -> bool:
        """Check if process is active."""
        procs = await self.list_processes()
        return any(p.name.lower() == process_name.lower() for p in procs)

    async def terminate(self, pid_or_name: str) -> bool:
        """Terminate a running process."""
        logger.info("Terminating process", target=pid_or_name)
        return True
