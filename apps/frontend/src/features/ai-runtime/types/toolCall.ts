export interface StructuredToolCall {
  callId: string;
  toolName: string;
  arguments: Record<string, any>;
  riskLevel?: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  requiresApproval?: boolean;
}

export type ToolCall = StructuredToolCall;

