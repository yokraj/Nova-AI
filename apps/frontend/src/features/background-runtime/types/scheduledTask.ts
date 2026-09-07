export type TaskStatus =
  | 'SCHEDULED'
  | 'QUEUED'
  | 'RUNNING'
  | 'WAITING_APPROVAL'
  | 'COMPLETED'
  | 'FAILED'
  | 'PAUSED'
  | 'CANCELLED'
  | 'EXPIRED';

export type ScheduleType = 'ONE_TIME' | 'INTERVAL' | 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'CRON';

export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type TriggerType =
  | 'SCHEDULE'
  | 'FILE_CREATED'
  | 'FILE_CHANGED'
  | 'FILE_DELETED'
  | 'APPLICATION_STARTED'
  | 'APPLICATION_CLOSED'
  | 'PROCESS_STARTED'
  | 'PROCESS_STOPPED'
  | 'SYSTEM_STATE_CHANGED'
  | 'SKILL_COMPLETED'
  | 'MISSION_COMPLETED'
  | 'TASK_FAILED';

export interface TaskSchedule {
  type: ScheduleType;
  cronExpression?: string;
  intervalMinutes?: number;
  timeOfDay?: string; // HH:mm format
  dayOfWeek?: number; // 0-6 (Sunday to Saturday)
  dayOfMonth?: number; // 1-31
  runAtTimestamp?: string;
  timezone?: string;
}

export interface TaskTrigger {
  type: TriggerType;
  targetPath?: string;
  processName?: string;
  skillId?: string;
  missionId?: string;
  eventFilter?: string;
}

export interface TaskExecutionRecord {
  executionId: string;
  taskId: string;
  startedAt: string;
  completedAt?: string;
  status: TaskStatus;
  stepCount: number;
  durationMs: number;
  summary: string;
  errorReason?: string;
  verified: boolean;
}

export interface ScheduledTask {
  id: string;
  name: string;
  description: string;
  goal: string;
  skillId?: string;
  missionId?: string;
  schedule?: TaskSchedule;
  trigger?: TaskTrigger;
  nextRunAt?: string;
  lastRunAt?: string;
  status: TaskStatus;
  priority: TaskPriority;
  maxRetries: number;
  retryCount: number;
  timeoutMs: number;
  maxExecutions?: number;
  executionCount: number;
  enabled: boolean;
  requiresApproval: boolean;
  trustedPolicy: boolean;
  createdAt: string;
  updatedAt: string;
  lastExecution?: TaskExecutionRecord;
}
