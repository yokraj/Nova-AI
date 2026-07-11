"""SoftwareEngineerMemory tracking symbols, files, and conversation memories.
"""

from typing import List
from pydantic import BaseModel, Field

from app.agents.software_engineer.interfaces import ISimplifiedMemory


class SoftwareEngineerMemory(BaseModel, ISimplifiedMemory):
    """Tracks files, symbol names, recent searches, errors, and task histories."""

    recent_files: List[str] = Field(default_factory=list)
    recent_symbols: List[str] = Field(default_factory=list)
    recent_errors: List[str] = Field(default_factory=list)
    recent_tasks: List[str] = Field(default_factory=list)
    recent_searches: List[str] = Field(default_factory=list)
    conversation_memory: List[str] = Field(default_factory=list)

    def add_file(self, file_path: str) -> None:
        if file_path not in self.recent_files:
            self.recent_files.append(file_path)
            if len(self.recent_files) > 10:
                self.recent_files.pop(0)

    def add_symbol(self, symbol_name: str) -> None:
        if symbol_name not in self.recent_symbols:
            self.recent_symbols.append(symbol_name)
            if len(self.recent_symbols) > 10:
                self.recent_symbols.pop(0)

    def add_error(self, error_msg: str) -> None:
        self.recent_errors.append(error_msg)
        if len(self.recent_errors) > 10:
            self.recent_errors.pop(0)

    def add_task(self, task_id: str) -> None:
        if task_id not in self.recent_tasks:
            self.recent_tasks.append(task_id)

    def add_search(self, query: str) -> None:
        self.recent_searches.append(query)
        if len(self.recent_searches) > 10:
            self.recent_searches.pop(0)
