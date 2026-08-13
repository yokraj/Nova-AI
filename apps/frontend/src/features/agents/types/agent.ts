export type AgentStatus =
  | 'IDLE'
  | 'AVAILABLE'
  | 'ASSIGNED'
  | 'PLANNING'
  | 'WORKING'
  | 'WAITING'
  | 'AWAITING_APPROVAL'
  | 'COMPLETED'
  | 'FAILED'
  | 'PAUSED'
  | 'CANCELLED';

export type AgentDomain =
  | 'Research'
  | 'Software Engineering'
  | 'Data'
  | 'Security'
  | 'DevOps'
  | 'Design'
  | 'Writing'
  | 'Analysis'
  | 'Automation'
  | 'System Operations'
  | 'Knowledge'
  | 'Planning'
  | 'Testing'
  | 'Communication';

export interface AgentPerformanceMetrics {
  tasksCompleted: number;
  successRate: number; // 0.0 to 1.0
  averageDurationSeconds: number;
  failuresCount: number;
  currentWorkload: number; // 0 to 100
}

export interface AgentPermissionConfig {
  fileSystemRead: boolean;
  fileSystemWrite: boolean;
  terminalExecute: boolean;
  databaseRead: boolean;
  databaseWrite: boolean;
  deviceControl: boolean;
  networkAccess: boolean;
}

export interface AgentItem {
  id: string;
  name: string;
  description: string;
  domain: AgentDomain;
  status: AgentStatus;
  capabilities: string[];
  tools: string[];
  permissions: AgentPermissionConfig;
  model: string; // e.g. "Qwen 3 8B", "DeepSeek R1"
  version: string;
  currentTask?: string;
  currentMissionId?: string;
  performance: AgentPerformanceMetrics;
  availability: 'high' | 'medium' | 'low';
  lastActive: string;
  createdAt: string;
}

export interface AgentProvider {
  listAgents: () => AgentItem[];
  getAgentById: (id: string) => AgentItem | undefined;
  searchAgents: (query: string, domain?: AgentDomain) => AgentItem[];
}
