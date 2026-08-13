export type ExecutionErrorType =
  | 'TOOL_NOT_FOUND'
  | 'TOOL_ARGUMENTS_INVALID'
  | 'TOOL_EXECUTION_FAILED'
  | 'PERMISSION_DENIED'
  | 'BUDGET_EXCEEDED'
  | 'VERIFICATION_FAILED'
  | 'PROMPT_INJECTION_DETECTED'
  | 'MAX_RETRIES_EXCEEDED';

export interface ExecutionError {
  type: ExecutionErrorType;
  message: string;
  stepId?: string;
  toolName?: string;
  recoverable: boolean;
}
