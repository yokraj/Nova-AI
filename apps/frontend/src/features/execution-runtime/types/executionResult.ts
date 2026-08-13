export type ExecutionStatus =
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCELLED'
  | 'DENIED'
  | 'TIMED_OUT';

export type VerificationState =
  | 'PROCESS_RUNNING'
  | 'STATE_VERIFIED'
  | 'UNVERIFIED'
  | 'VERIFICATION_FAILED';

export interface ExecutionResult {
  executionId: string;
  status: ExecutionStatus;
  capability: string;
  action: string;
  target: string;
  startedAt: string;
  completedAt: string;
  durationSeconds: number;
  verification: VerificationState;
  message: string;
  error?: string;
  metadata?: Record<string, any>;
}
