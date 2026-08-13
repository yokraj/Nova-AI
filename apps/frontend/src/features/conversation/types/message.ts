export type MessageRole = 'user' | 'assistant' | 'system' | 'tool' | 'agent' | 'mission' | 'approval' | 'error';

export type MessageStatus = 'sending' | 'thinking' | 'streaming' | 'complete' | 'error' | 'approval_required';

export type ResponseBlockType =
  | 'text'
  | 'markdown'
  | 'code'
  | 'list'
  | 'table'
  | 'quote'
  | 'image'
  | 'chart'
  | 'citation'
  | 'tool_activity'
  | 'agent_activity'
  | 'mission'
  | 'approval'
  | 'error';

export interface CodeBlockData {
  language: string;
  code: string;
  filename?: string;
}

export interface TableBlockData {
  headers: string[];
  rows: string[][];
}

export interface CitationData {
  id: string;
  title: string;
  source: string;
  url?: string;
  snippet?: string;
}

export interface ToolActivityData {
  toolName: string;
  status: 'running' | 'complete' | 'error';
  input?: string;
  output?: string;
  executionTimeMs?: number;
}

export interface AgentActivityData {
  agentName: string;
  agentAvatar: string;
  division: string;
  status: 'running' | 'complete' | 'idle';
  task: string;
  progress: number;
}

export interface MissionActivityData {
  missionId: string;
  title: string;
  category: string;
  status: 'running' | 'completed' | 'queued' | 'paused';
  subtasksCompleted: number;
  subtasksTotal: number;
  progress: number;
}

export interface ApprovalRequestData {
  id: string;
  title: string;
  actionType: string;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'pending' | 'approved' | 'rejected';
}

export interface ResponseBlock {
  id: string;
  type: ResponseBlockType;
  content?: string;
  codeData?: CodeBlockData;
  tableData?: TableBlockData;
  citationsData?: CitationData[];
  toolData?: ToolActivityData;
  agentData?: AgentActivityData;
  missionData?: MissionActivityData;
  approvalData?: ApprovalRequestData;
}

export interface AttachmentFile {
  id: string;
  name: string;
  sizeBytes: number;
  type: 'pdf' | 'txt' | 'docx' | 'csv' | 'image' | 'code';
  previewUrl?: string;
  status: 'uploading' | 'ready' | 'error';
}

export interface ConversationMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  status: MessageStatus;
  blocks?: ResponseBlock[];
  attachments?: AttachmentFile[];
  spokenText?: string;
  thinkingStage?: string;
}
