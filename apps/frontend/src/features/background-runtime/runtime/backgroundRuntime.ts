import { ScheduledTask, TaskStatus, TaskExecutionRecord } from '../types/scheduledTask';
import { LocalScheduler } from '../scheduler/localScheduler';
import { TaskQueue } from '../queue/taskQueue';
import { TriggerEngine, TriggerEvent } from '../triggers/triggerEngine';
import { BackgroundTaskPolicy } from '../security/backgroundTaskPolicy';
import { ResourceBudgetGuard } from '../security/resourceBudgetGuard';
import { LocalNotificationProvider } from '../notifications/localNotificationProvider';
import { BackgroundTaskStore } from '../persistence/backgroundTaskStore';
import { AgentRuntime } from '../../ai-runtime/runtime/agentRuntime';

export type RuntimeState = 'RUNNING' | 'PAUSED' | 'OFFLINE' | 'DEGRADED';

export class BackgroundRuntime {
  private state: RuntimeState = 'RUNNING';
  private scheduler = new LocalScheduler();
  private queue = new TaskQueue();
  private triggerEngine = new TriggerEngine();
  private securityPolicy = new BackgroundTaskPolicy();
  private budgetGuard = new ResourceBudgetGuard();
  private notificationProvider = new LocalNotificationProvider();
  private taskStore = new BackgroundTaskStore();
  private agentRuntime = new AgentRuntime();
  private timerId: any = null;

  constructor() {
    this.performCrashRecovery();
    this.startHeartbeat();
  }

  startHeartbeat(intervalMs: number = 2000): void {
    if (this.timerId) return;
    this.timerId = setInterval(() => {
      this.tick();
    }, intervalMs);
  }

  stopHeartbeat(): void {
    if (this.timerId) {
      clearInterval(this.timerId);
      this.timerId = null;
    }
  }

  async tick(now: Date = new Date()): Promise<void> {
    if (this.state !== 'RUNNING') return;

    // 1. Evaluate scheduled tasks due
    const tasks = this.taskStore.getAllTasks();
    for (const task of tasks) {
      if (this.scheduler.isTaskDue(task, now)) {
        this.scheduleTaskForExecution(task);
      }
    }

    // 2. Process next queued task
    const nextTask = this.queue.dequeue();
    if (nextTask) {
      await this.executeTask(nextTask);
    }
  }

  scheduleTaskForExecution(task: ScheduledTask): boolean {
    const secResult = this.securityPolicy.evaluateTaskSecurity(task);

    if (!secResult.allowed) {
      task.status = 'CANCELLED';
      this.taskStore.saveTask(task);
      this.notificationProvider.notify(
        `Task Security Blocked: ${task.name}`,
        secResult.reason,
        'ERROR'
      );
      return false;
    }

    if (secResult.requiresApproval) {
      task.status = 'WAITING_APPROVAL';
      this.taskStore.saveTask(task);
      this.notificationProvider.notify(
        `Approval Required: ${task.name}`,
        secResult.reason,
        'APPROVAL_REQUIRED'
      );
      return false;
    }

    const queued = this.queue.enqueue(task);
    if (queued) {
      task.status = 'QUEUED';
      this.taskStore.saveTask(task);
    }
    return queued;
  }

  async executeTask(task: ScheduledTask): Promise<TaskExecutionRecord> {
    const startedAt = new Date().toISOString();
    const startTime = Date.now();

    task.status = 'RUNNING';
    task.lastRunAt = startedAt;
    task.executionCount += 1;
    this.taskStore.saveTask(task);

    let record: TaskExecutionRecord;

    try {
      // Execute via AgentRuntime
      const result = await this.agentRuntime.executeGoal(task.goal);
      const durationMs = Date.now() - startTime;
      const isSuccess = result.state === 'COMPLETED';

      record = {
        executionId: `exec-${Date.now()}`,
        taskId: task.id,
        startedAt,
        completedAt: new Date().toISOString(),
        status: isSuccess ? 'COMPLETED' : 'FAILED',
        stepCount: result.plan?.steps?.length || 1,
        durationMs,
        summary: result.summary || 'Task execution finished.',
        verified: isSuccess,
      };

      if (isSuccess) {
        task.status = 'COMPLETED';
        task.retryCount = 0;
        this.queue.markCompleted(task.id);
        this.notificationProvider.notify(
          `Task Completed: ${task.name}`,
          record.summary,
          'SUCCESS'
        );
      } else {
        this.handleTaskFailure(task, result.summary || 'Goal execution failed');
        record.status = task.status;
        record.errorReason = result.summary;
      }
    } catch (err: any) {
      const durationMs = Date.now() - startTime;
      const errorMsg = err?.message || 'Execution exception occurred';

      this.handleTaskFailure(task, errorMsg);

      record = {
        executionId: `exec-${Date.now()}`,
        taskId: task.id,
        startedAt,
        completedAt: new Date().toISOString(),
        status: task.status,
        stepCount: 1,
        durationMs,
        summary: `Execution failed: ${errorMsg}`,
        errorReason: errorMsg,
        verified: false,
      };
    }

    // Compute next run time if recurring
    const nextRun = this.scheduler.calculateNextRun(task);
    task.nextRunAt = nextRun;
    if (!nextRun && task.status === 'COMPLETED') {
      task.status = 'COMPLETED';
    } else if (nextRun && (task.status as string) !== 'PAUSED' && (task.status as string) !== 'CANCELLED') {
      task.status = 'SCHEDULED';
    }

    task.lastExecution = record;
    this.taskStore.saveTask(task);
    this.taskStore.recordExecution(record);

    return record;
  }

  handleEvent(event: TriggerEvent): ScheduledTask[] {
    const tasks = this.taskStore.getAllTasks();
    const matched = this.triggerEngine.matchEventToTasks(event, tasks);

    for (const t of matched) {
      this.scheduleTaskForExecution(t);
    }
    return matched;
  }

  approveTask(taskId: string): boolean {
    const task = this.taskStore.getTask(taskId);
    if (!task || task.status !== 'WAITING_APPROVAL') return false;

    task.trustedPolicy = true;
    const queued = this.queue.enqueue(task);
    if (queued) {
      task.status = 'QUEUED';
      this.taskStore.saveTask(task);
      this.notificationProvider.notify(
        `Task Approved: ${task.name}`,
        'Task queued for execution.',
        'INFO'
      );
    }
    return queued;
  }

  pauseTask(taskId: string): boolean {
    const task = this.taskStore.getTask(taskId);
    if (!task) return false;

    task.status = 'PAUSED';
    task.enabled = false;
    this.queue.cancelTask(taskId);
    this.taskStore.saveTask(task);
    return true;
  }

  resumeTask(taskId: string): boolean {
    const task = this.taskStore.getTask(taskId);
    if (!task) return false;

    task.status = 'SCHEDULED';
    task.enabled = true;
    task.nextRunAt = this.scheduler.calculateNextRun(task);
    this.taskStore.saveTask(task);
    return true;
  }

  cancelTask(taskId: string): boolean {
    const task = this.taskStore.getTask(taskId);
    if (!task) return false;

    task.status = 'CANCELLED';
    task.enabled = false;
    this.queue.cancelTask(taskId);
    this.taskStore.saveTask(task);
    return true;
  }

  performCrashRecovery(): number {
    let recoveredCount = 0;
    const tasks = this.taskStore.getAllTasks();

    for (const task of tasks) {
      // 1. Detect stale RUNNING tasks from previous session crash
      if (task.status === 'RUNNING') {
        task.status = 'FAILED';
        task.retryCount = (task.retryCount || 0) + 1;
        this.taskStore.saveTask(task);
      }

      // 2. Re-calculate next run times and requeue safe tasks
      if (task.enabled && (task.status === 'SCHEDULED' || task.status === 'QUEUED' || task.status === 'FAILED')) {
        const nextRun = this.scheduler.calculateNextRun(task);
        task.nextRunAt = nextRun;

        if (task.status === 'FAILED' && !this.budgetGuard.isRetryLimitExceeded(task.retryCount)) {
          task.status = 'SCHEDULED';
        }

        this.taskStore.saveTask(task);
        recoveredCount++;
      }
    }

    return recoveredCount;
  }

  getRuntimeState(): RuntimeState {
    return this.state;
  }

  setRuntimeState(state: RuntimeState): void {
    this.state = state;
  }

  getTaskStore(): BackgroundTaskStore {
    return this.taskStore;
  }

  getQueue(): TaskQueue {
    return this.queue;
  }

  getNotifications(): LocalNotificationProvider {
    return this.notificationProvider;
  }

  private handleTaskFailure(task: ScheduledTask, errorMsg: string): void {
    task.retryCount += 1;
    this.queue.markFailed(task.id, errorMsg);

    if (this.budgetGuard.isRetryLimitExceeded(task.retryCount)) {
      task.status = 'FAILED';
      this.notificationProvider.notify(
        `Task Failed Permanently: ${task.name}`,
        `Exceeded retry limit (${task.retryCount} retries). ${errorMsg}`,
        'ERROR'
      );
    } else {
      task.status = 'SCHEDULED';
      this.notificationProvider.notify(
        `Task Failed (Will Retry): ${task.name}`,
        `Attempt ${task.retryCount} failed. ${errorMsg}`,
        'WARNING'
      );
    }
  }
}
