export type ExecutionErrorType =
  | 'TARGET_NOT_FOUND'
  | 'APPLICATION_NOT_INSTALLED'
  | 'PERMISSION_DENIED'
  | 'EXECUTION_FAILED'
  | 'VERIFICATION_FAILED'
  | 'TIMEOUT'
  | 'UNSUPPORTED_CAPABILITY'
  | 'INVALID_REQUEST'
  | 'POLICY_DENIED'
  | 'SECURITY_INJECTION_DETECTED'
  | 'INVALID_TARGET';

export interface ExecutionError {
  type: ExecutionErrorType;
  message: string;
  details?: Record<string, any>;
}
