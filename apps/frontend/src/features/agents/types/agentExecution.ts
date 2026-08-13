import { AgentStatus } from './agent';

export interface AgentExecutionTask {
  id: string;
  agentId: string;
  agentName: string;
  title: string;
  description: string;
  status: AgentStatus;
  progress: number; // 0 to 100
  currentAction: string;
  toolsUsed: string[];
  outputLogs: string[];
  failureReason?: string;
  requiresSecurityApproval?: boolean;
  securityRiskLevel?: 'LOW' | 'MEDIUM' | 'HIGH';
  startedAt: string;
  completedAt?: string;
}

export interface AgentExecutionProvider {
  startTask: (agentId: string, title: string, description: string) => AgentExecutionTask;
  pauseTask: (taskId: string) => void;
  resumeTask: (taskId: string) => void;
  cancelTask: (taskId: string) => void;
  retryTask: (taskId: string) => void;
}
