import { ScheduledTask, TaskExecutionRecord } from '../types/scheduledTask';

const STORAGE_KEY = 'nova_background_tasks';
const HISTORY_KEY = 'nova_task_execution_history';

export class BackgroundTaskStore {
  private static staticTasks: Map<string, ScheduledTask> = new Map();
  private static staticHistory: TaskExecutionRecord[] = [];
  private tasks: Map<string, ScheduledTask> = BackgroundTaskStore.staticTasks;
  private history: TaskExecutionRecord[] = BackgroundTaskStore.staticHistory;

  constructor() {
    this.loadFromStorage();
  }

  saveTask(task: ScheduledTask): ScheduledTask {
    const updated = { ...task, updatedAt: new Date().toISOString() };
    this.tasks.set(updated.id, updated);
    this.persistToStorage();
    return updated;
  }

  getTask(id: string): ScheduledTask | undefined {
    return this.tasks.get(id);
  }

  getAllTasks(): ScheduledTask[] {
    return Array.from(this.tasks.values());
  }

  deleteTask(id: string): boolean {
    const deleted = this.tasks.delete(id);
    if (deleted) {
      this.persistToStorage();
    }
    return deleted;
  }

  recordExecution(record: TaskExecutionRecord): void {
    this.history.unshift(record);
    if (this.history.length > 100) {
      this.history = this.history.slice(0, 100);
    }
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem(HISTORY_KEY, JSON.stringify(this.history));
      }
    } catch {
      // Storage error ignored
    }
  }

  getHistory(taskId?: string): TaskExecutionRecord[] {
    if (taskId) {
      return this.history.filter((h) => h.taskId === taskId);
    }
    return [...this.history];
  }

  private loadFromStorage(): void {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const storedTasks = window.localStorage.getItem(STORAGE_KEY);
        if (storedTasks) {
          const arr: ScheduledTask[] = JSON.parse(storedTasks);
          for (const t of arr) {
            this.tasks.set(t.id, t);
          }
        }
        const storedHistory = window.localStorage.getItem(HISTORY_KEY);
        if (storedHistory) {
          this.history = JSON.parse(storedHistory);
        }
      }
    } catch {
      // Storage load error ignored
    }
  }

  private persistToStorage(): void {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const arr = Array.from(this.tasks.values());
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));
      }
    } catch {
      // Storage save error ignored
    }
  }
}
