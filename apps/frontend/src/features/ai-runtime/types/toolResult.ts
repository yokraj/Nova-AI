export interface ToolResult {
  callId: string;
  toolName: string;
  success: boolean;
  data?: any;
  errorReason?: string;
  durationMs: number;
  observationSummary?: string;
  verifiedState?: boolean;
}
