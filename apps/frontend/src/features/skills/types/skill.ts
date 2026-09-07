export type SkillCategory =
  | 'development'
  | 'automation'
  | 'system'
  | 'browser'
  | 'filesystem'
  | 'data_processing'
  | 'communication'
  | 'general';

export type SkillStatus = 'active' | 'disabled' | 'draft' | 'deprecated' | 'archived';

export interface SkillVariable {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'path' | 'url';
  description: string;
  required: boolean;
  defaultValue?: string | number | boolean;
  examples?: string[];
}

export interface SkillTrigger {
  naturalLanguagePattern: string;
  intent: string;
  confidence: number;
  contextRequirements?: Record<string, string>;
}

export interface SkillStep {
  id: string;
  order: number;
  tool: string;
  arguments: Record<string, any>;
  argumentTemplates?: Record<string, string>;
  purpose: string;
  conditions?: Record<string, any>;
  expectedObservation?: string;
  verification?: {
    type: 'tool_result' | 'file_exists' | 'process_running' | 'custom';
    target?: string;
    expectedState?: string;
  };
  retryPolicy?: {
    maxAttempts: number;
    backoffMs: number;
  };
  approvalRequired?: boolean;
}

export interface SkillVersionHistoryItem {
  version: number;
  changes: string;
  reason: string;
  timestamp: string;
  successRate: number;
  stepsCount: number;
}

export interface Skill {
  id: string;
  name: string;
  description: string;
  purpose: string;
  triggerPatterns: SkillTrigger[];
  category: SkillCategory;
  version: number;
  status: SkillStatus;
  confidence: number;
  successRate: number;
  usageCount: number;
  createdAt: string;
  updatedAt: string;
  lastUsedAt?: string;
  source: 'user_taught' | 'auto_extracted' | 'system_builtin';
  owner: string;
  requiredTools: string[];
  requiredCapabilities: string[];
  requiredPermissions: string[];
  preconditions: string[];
  variables: SkillVariable[];
  steps: SkillStep[];
  verificationRules: string[];
  recoveryRules: string[];
  constraints: string[];
  examples: string[];
  tags: string[];
  dependencies: string[];
  compatibility: {
    minOsVersion?: string;
    agentRuntimeVersion?: string;
    requiredAdapters?: string[];
  };
  history: SkillVersionHistoryItem[];
}

export interface WorkflowExecutionRecord {
  id: string;
  goalText: string;
  intent: string;
  startTime: string;
  endTime: string;
  durationMs: number;
  steps: Array<{
    stepNumber: number;
    title: string;
    toolName?: string;
    toolArgs?: Record<string, any>;
    observation?: string;
    success: boolean;
    verificationConfirmed: boolean;
    approvalRequired?: boolean;
    recoveryUsed?: string;
  }>;
  overallSuccess: boolean;
  isUntrustedContentPresent: boolean;
  untrustedSources?: string[];
  userExplicitLearningRequested?: boolean;
}

export interface SkillExecutionResult {
  success: boolean;
  skillId: string;
  skillVersion: number;
  summary: string;
  executedStepsCount: number;
  durationMs: number;
  adaptedVariables: Record<string, any>;
  errors?: string[];
}

export interface SkillFilter {
  category?: SkillCategory;
  status?: SkillStatus;
  searchQuery?: string;
  tags?: string[];
}
