export type MissionStatus =
  | 'DRAFT'
  | 'QUEUED'
  | 'PLANNING'
  | 'EXECUTING'
  | 'PAUSED'
  | 'AWAITING_APPROVAL'
  | 'RECOVERING'
  | 'REPLANNING'
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCELLED'
  | 'TIMED_OUT'
  | 'RECOVERY_REQUIRED';

export type MissionPriority = 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT';

export type AutonomyLevel = 'ASSISTED' | 'SUPERVISED' | 'AUTONOMOUS';

export type RecoveryClassification =
  | 'SAFE_TO_RESUME'
  | 'REQUIRES_REVALIDATION'
  | 'REQUIRES_USER_APPROVAL'
  | 'ABORT_REQUIRED';

export interface MissionResourceBudget {
  maxSteps: number;
  executedSteps: number;
  retriesCount: number;
  maxDurationSeconds: number;
  elapsedDurationSeconds: number;
  remainingDurationSeconds: number;
  swarmConcurrencyLimit: number;
}

export interface MissionCheckpoint {
  checkpointId: string;
  executionId: string;
  missionId: string;
  timestamp: string;
  status: MissionStatus;
  currentStep: number;
  completedSteps: string[];
  failedSteps: string[];
  pendingSteps: string[];
  executionPlanVersion: number;
  activeAgentId?: string;
  activeSwarmTasks: string[];
  toolExecutionState: Record<string, any>;
  retryCounters: Record<string, number>;
  budgetState: MissionResourceBudget;
  approvalState: {
    requiresApproval: boolean;
    stepId?: string;
    toolName?: string;
    riskLevel?: string;
    reason?: string;
  };
  recoveryState: {
    strategy?: string;
    attemptCount: number;
    errorType?: string;
  };
  verificationResults: Array<{ stepId: string; verified: boolean; summary: string }>;
  isSafeResumable: boolean;
  checkpointVersion: number;
}

export interface MissionItem {
  id: string;
  title: string;
  goal: string;
  description: string;
  status: MissionStatus;
  priority: MissionPriority;
  autonomyLevel: AutonomyLevel;
  progress: number; // 0 to 100
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  assignedAgents: string[];
  tasksCount: number;
  completedTasksCount: number;
  lastCheckpoint?: MissionCheckpoint;
  budget?: MissionResourceBudget;
  recoveryClassification?: RecoveryClassification;
}

export interface MissionProvider {
  listMissions: () => MissionItem[];
  getMissionById: (id: string) => MissionItem | undefined;
}
