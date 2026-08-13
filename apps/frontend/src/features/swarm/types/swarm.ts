import { AgentDomain } from '../../agents/types/agent';

export type SwarmStatus =
  | 'IDLE'
  | 'PLANNING'
  | 'AWAITING_APPROVAL'
  | 'RUNNING'
  | 'PAUSED'
  | 'RECOVERING'
  | 'VERIFYING'
  | 'SYNTHESIZING'
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCELLED';

export type SwarmTaskState =
  | 'SEQUENTIAL'
  | 'PARALLEL'
  | 'DEPENDENCY_BLOCKED'
  | 'WAITING'
  | 'RUNNING'
  | 'AWAITING_APPROVAL'
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCELLED';

export type SwarmPriority = 'LOW' | 'NORMAL' | 'HIGH' | 'CRITICAL';

export type SwarmMessageType =
  | 'AGENT_REQUEST'
  | 'AGENT_RESULT'
  | 'AGENT_WARNING'
  | 'AGENT_BLOCKED'
  | 'AGENT_HANDOFF'
  | 'AGENT_REVIEW'
  | 'AGENT_APPROVAL_REQUIRED';

export type ConflictResolutionStrategy =
  | 'REQUEST_EVIDENCE'
  | 'ASK_ANOTHER_AGENT'
  | 'PRIORITIZE_CONFIDENCE'
  | 'REQUIRE_APPROVAL'
  | 'MARK_UNRESOLVED';

export interface SwarmAgent {
  agentId: string;
  name: string;
  domain: AgentDomain;
  capabilities: string[];
  tools: string[];
  workload: number;
  isAvailable: boolean;
}

export interface SwarmTask {
  taskId: string;
  title: string;
  description: string;
  assignedAgentId: string;
  assignedAgentName: string;
  state: SwarmTaskState;
  priority: SwarmPriority;
  toolName?: string;
  toolArguments?: Record<string, any>;
  dependencies: string[]; // Upstream taskIds required before execution
  outputSummary?: string;
  errorReason?: string;
  startedAt?: string;
  completedAt?: string;
}

export interface SwarmDependency {
  taskId: string;
  dependsOnTaskId: string;
}

export interface SwarmMessage {
  messageId: string;
  timestamp: string;
  senderAgentId: string;
  senderAgentName: string;
  receiverAgentId?: string; // Broadcast if undefined
  type: SwarmMessageType;
  content: string;
  payload?: any;
}

export interface SwarmConflict {
  conflictId: string;
  taskId: string;
  topic: string;
  agentAId: string;
  agentAFinding: string;
  agentBId: string;
  agentBFinding: string;
  resolutionStrategy?: ConflictResolutionStrategy;
  resolvedOutcome?: string;
}

export interface SwarmContext {
  missionId: string;
  goal: string;
  taskOutputs: Record<string, string>;
  sharedFindings: string[];
  memoryReferences: string[];
  knowledgeReferences: string[];
  activeWarnings: string[];
  conflicts: SwarmConflict[];
}

export interface SwarmEvent {
  eventId: string;
  timestamp: string;
  swarmId: string;
  status: SwarmStatus;
  message: string;
  taskId?: string;
  agentId?: string;
}

export interface SwarmResult {
  swarmId: string;
  missionId: string;
  goal: string;
  success: boolean;
  status: SwarmStatus;
  readinessPercentage: number;
  summary: string;
  tasksCompleted: number;
  totalTasks: number;
  findings: string[];
  recommendations: string[];
  eventHistory: SwarmEvent[];
  messages: SwarmMessage[];
  durationSeconds: number;
}

export interface SwarmExecutionPlan {
  swarmId: string;
  missionId: string;
  goal: string;
  status: SwarmStatus;
  priority: SwarmPriority;
  agents: SwarmAgent[];
  tasks: SwarmTask[];
  dependencies: SwarmDependency[];
  context: SwarmContext;
  progress: number; // 0 to 100
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
}
