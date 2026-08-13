import { StructuredToolCall } from './toolCall';
import { ToolResult } from './toolResult';

export interface ModelMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  toolCalls?: StructuredToolCall[];
  toolResults?: ToolResult[];
}

export interface ModelRequest {
  messages: ModelMessage[];
  systemInstructions?: string;
  tools?: string[];
  temperature?: number;
}
