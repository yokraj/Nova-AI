import { ScheduledTask, TaskStatus } from '../types/scheduledTask';
import { ResourceBudgetGuard } from '../security/resourceBudgetGuard';

export class TaskQueue {
  private queue: ScheduledTask[] = [];
  private running: Map<string, ScheduledTask> = new Map();
  private budgetGuard = new ResourceBudgetGuard();

  enqueue(task: ScheduledTask): boolean {
    if (this.queue.some((t) => t.id === task.id) || this.running.has(task.id)) {
      return false; // Prevent duplicates
    }

    const updated = { ...task, status: 'QUEUED' as TaskStatus };
    this.queue.push(updated);
    this.sortQueue();
    return true;
  }

  dequeue(): ScheduledTask | undefined {
    if (this.queue.length === 0) return undefined;
    if (!this.budgetGuard.isWithinConcurrencyLimit(this.running.size)) {
      return undefined; // Concurrency limit reached
    }

    const task = this.queue.shift();
    if (task) {
      task.status = 'RUNNING';
      this.running.set(task.id, task);
    }
    return task;
  }

  markCompleted(taskId: string): void {
    const task = this.running.get(taskId);
    if (task) {
      task.status = 'COMPLETED';
      this.running.delete(taskId);
    }
  }

  markFailed(taskId: string, reason?: string): void {
    const task = this.running.get(taskId);
    if (task) {
      task.status = 'FAILED';
      this.running.delete(taskId);
    }
  }

  cancelTask(taskId: string): boolean {
    this.running.delete(taskId);
    const idx = this.queue.findIndex((t) => t.id === taskId);
    if (idx !== -1) {
      this.queue.splice(idx, 1);
      return true;
    }
    return false;
  }

  getQueueLength(): number {
    return this.queue.length;
  }

  getRunningCount(): number {
    return this.running.size;
  }

  getQueuedTasks(): ScheduledTask[] {
    return [...this.queue];
  }

  getRunningTasks(): ScheduledTask[] {
    return Array.from(this.running.values());
  }

  clear(): void {
    this.queue = [];
    this.running.clear();
  }

  private sortQueue(): void {
    const priorityWeight: Record<string, number> = {
      CRITICAL: 4,
      HIGH: 3,
      MEDIUM: 2,
      LOW: 1,
    };

    this.queue.sort((a, b) => {
      const wa = priorityWeight[a.priority] || 1;
      const wb = priorityWeight[b.priority] || 1;
      return wb - wa;
    });
  }
}
