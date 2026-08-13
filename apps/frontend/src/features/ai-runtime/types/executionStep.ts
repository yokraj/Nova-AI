import { StructuredToolCall } from './toolCall';
import { ToolResult } from './toolResult';

export type StepStatus =
  | 'PENDING'
  | 'EXECUTING'
  | 'AWAITING_APPROVAL'
  | 'COMPLETED'
  | 'FAILED'
  | 'SKIPPED'
  | 'RECOVERING';

export interface ExecutionStep {
  id: string;
  stepNumber: number;
  title: string;
  description: string;
  status: StepStatus;
  dependencies?: string[];
  toolCall?: StructuredToolCall;
  toolResult?: ToolResult;
  verificationConfirmed?: boolean;
  retryCount?: number;
}
