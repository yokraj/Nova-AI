export interface ExecutionRequest {
  executionId: string;
  commandId: string;
  capability: string; // e.g. "APPLICATION_CONTROL"
  action: string;     // e.g. "OPEN_APPLICATION"
  target: string;     // e.g. "VS Code"
  parameters?: Record<string, any>;
  requestedBy: string; // e.g. "user" | "agent-architect"
  workspace: string;
  riskLevel: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  policy: 'ALLOW' | 'ALLOW_WITH_APPROVAL' | 'DENY';
  permissions: string[];
  timestamp: string;
}
