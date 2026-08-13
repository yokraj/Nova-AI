export interface CommandResult {
  success: boolean;
  message: string;
  durationSeconds: number;
  outputData?: any;
  targetDomain?: string;
  targetId?: string;
  errorReason?: string;
  suggestedNextStep?: string;
}
