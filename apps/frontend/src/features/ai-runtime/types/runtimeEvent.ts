import { AgentState } from './agentState';
import { ExecutionStep } from './executionStep';
import { ToolResult } from './toolResult';

export interface RuntimeEvent {
  eventId: string;
  timestamp: string;
  state: AgentState;
  message: string;
  step?: ExecutionStep;
  toolResult?: ToolResult;
}
