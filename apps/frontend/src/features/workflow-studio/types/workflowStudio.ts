export type WorkflowNodeType =
  | 'TRIGGER'
  | 'DESKTOP_ACTION'
  | 'BROWSER_ACTION'
  | 'VISION_GROUNDING'
  | 'SKILL_DELEGATION'
  | 'SWARM_PARALLEL'
  | 'CONDITION'
  | 'WAIT'
  | 'VERIFICATION';

export type ActionCapability =
  | 'FILE_SYSTEM'
  | 'APPLICATION_CONTROL'
  | 'SYSTEM_CONTROL'
  | 'COMPUTER_CONTROL'
  | 'BROWSER_CONTROL'
  | 'VISION_CONTROL';

export type TargetResolutionStrategy =
  | 'ACCESSIBILITY'
  | 'DOM_SELECTOR'
  | 'VISUAL_TARGET'
  | 'WINDOW_CONTEXT'
  | 'COORDINATES_FALLBACK';

export interface SemanticTarget {
  strategy: TargetResolutionStrategy;
  accessibilityRole?: string;
  accessibilityName?: string;
  domSelector?: string;
  visualText?: string;
  visualLabel?: string;
  activeApp?: string;
  windowTitle?: string;
  coordinatesFallback?: { x: number; y: number };
  confidence: number;
}

export interface WorkflowVariable {
  name: string;
  type: 'STRING' | 'NUMBER' | 'BOOLEAN' | 'PATH' | 'URL';
  defaultValue: any;
  required: boolean;
  validationPattern?: string;
  description: string;
}

export interface WorkflowNode {
  id: string;
  label: string;
  type: WorkflowNodeType;
  capability?: ActionCapability;
  toolName?: string;
  arguments?: Record<string, any>;
  semanticTarget?: SemanticTarget;
  assignedAgentRole?: string;
  visualTargetQuery?: string;
  selector?: string;
  riskLevel: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  requiresApproval: boolean;
  expectedState?: string;
  waitDurationMs?: number;
  conditionExpression?: string;
  retryCount?: number;
  maxRetries?: number;
  disabled?: boolean;
  x: number;
  y: number;
}

export interface WorkflowEdge {
  id: string;
  sourceNodeId: string;
  targetNodeId: string;
  condition?: string;
}

export interface RecordedAction {
  actionId: string;
  timestamp: string;
  actionType: string;
  capability: ActionCapability;
  toolName: string;
  arguments: Record<string, any>;
  activeApp?: string;
  windowTitle?: string;
  semanticTarget?: SemanticTarget;
  screenshotBase64?: string;
  containsSensitiveData?: boolean;
}

export interface RecordingSession {
  sessionId: string;
  title: string;
  startedAt: string;
  endedAt?: string;
  isRecording: boolean;
  recordedActions: RecordedAction[];
  redactedSecretsCount: number;
}

export interface WorkflowVersion {
  versionNumber: number;
  createdAt: string;
  author: string;
  changeSummary: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  variables: WorkflowVariable[];
}

export interface WorkflowDefinition {
  id: string;
  name: string;
  description: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  variables: WorkflowVariable[];
  tags: string[];
  createdAt: string;
  updatedAt: string;
  version: number;
  versionsHistory: WorkflowVersion[];
  trusted: boolean;
  successRate?: number;
  executionCount?: number;
}

export interface ReplayConfig {
  workflowId: string;
  enableSwarmDelegation: boolean;
  verifyVisualStates: boolean;
  pauseOnApproval: boolean;
  stepTimeoutMs: number;
  variablesInput?: Record<string, any>;
}

export interface ReplayNodeResult {
  nodeId: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'AWAITING_APPROVAL' | 'SKIPPED';
  durationMs: number;
  message: string;
  verifiedState: boolean;
  resolutionUsed?: TargetResolutionStrategy;
  relocatedCoordinates?: { x: number; y: number };
  outputData?: any;
}

export interface ReplayExecutionResult {
  executionId: string;
  workflowId: string;
  version: number;
  startedAt: string;
  completedAt?: string;
  status: 'COMPLETED' | 'FAILED' | 'AWAITING_APPROVAL';
  totalDurationMs: number;
  nodeResults: ReplayNodeResult[];
  verifiedCount: number;
  summary: string;
}

export interface DryRunStepAssessment {
  nodeId: string;
  nodeLabel: string;
  status: 'READY' | 'WARNING' | 'BLOCKED' | 'REQUIRES_APPROVAL';
  riskLevel: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  resolvedTool?: string;
  targetReadiness: string;
  permissionStatus: string;
  issues: string[];
}

export interface DryRunResult {
  workflowId: string;
  valid: boolean;
  overallStatus: 'READY' | 'WARNING' | 'BLOCKED' | 'REQUIRES_APPROVAL';
  stepAssessments: DryRunStepAssessment[];
  missingDependencies: string[];
  totalRiskScore: number;
  summary: string;
}
