export type CommandExecutionState =
  | 'IDLE'
  | 'RECEIVED'
  | 'UNDERSTANDING'
  | 'PLANNING'
  | 'CAPABILITY_SELECTED'
  | 'PERMISSION_CHECK'
  | 'AWAITING_APPROVAL'
  | 'EXECUTING'
  | 'OBSERVING'
  | 'VERIFYING'
  | 'RECOVERING'
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCELLED'
  | 'DENIED'
  | 'REQUIRES_REPLAN';


export interface CommandExecutionStep {
  id: string;
  stepNumber: number;
  title: string;
  description: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
}

export interface CommandPlan {
  steps: CommandExecutionStep[];
  estimatedDurationSeconds?: number;
}
