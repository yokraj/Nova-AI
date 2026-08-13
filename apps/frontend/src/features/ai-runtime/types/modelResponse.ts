import { StructuredToolCall } from './toolCall';

export interface ModelResponse {
  text: string;
  toolCalls?: StructuredToolCall[];
  isComplete: boolean;
  requiresClarification?: boolean;
}
