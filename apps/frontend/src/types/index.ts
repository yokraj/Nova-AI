export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  avatarUrl?: string;
}

export interface MetricCardData {
  title: string;
  value: string | number;
  change: string;
  isPositive: boolean;
  iconName: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  model?: string;
  provider?: string;
  tokens?: number;
}

export interface MemoryItem {
  id: string;
  type: string;
  content: string;
  workspace: string;
  confidence: number;
  createdAt: string;
}

export interface AgentInfo {
  id: string;
  name: string;
  role: string;
  status: 'active' | 'idle' | 'busy' | 'offline';
  tasksCompleted: number;
  avatar: string;
}

export interface RepositoryInfo {
  id: string;
  name: string;
  language: string;
  filesCount: number;
  loc: number;
  status: 'indexed' | 'indexing' | 'failed';
}

export interface ModelInfo {
  name: string;
  provider: string;
  contextWindow: number;
  supportsVision: boolean;
  status: 'online' | 'offline';
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: string;
  read: boolean;
}
