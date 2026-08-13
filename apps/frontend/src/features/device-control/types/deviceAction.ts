export type ActionRiskLevel = 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type CommandPolicy = 'ALLOW' | 'ALLOW_WITH_APPROVAL' | 'DENY';

export interface DeviceActionRequest {
  id: string;
  commandText: string;
  targetDeviceId: string;
  targetDeviceName: string;
  actionType: string;
  capabilityRequired: string;
  riskLevel: ActionRiskLevel;
  policy: CommandPolicy;
  scope: string;
  requiresApproval: boolean;
  status: 'PREVIEW' | 'AWAITING_APPROVAL' | 'EXECUTING' | 'VERIFYING' | 'COMPLETED' | 'FAILED' | 'REJECTED';
  durationSeconds?: number;
  resultMessage?: string;
  timestamp: string;
}

export interface ActionApprovalProvider {
  calculateRisk: (commandText: string, capability: string) => ActionRiskLevel;
  checkPolicy: (riskLevel: ActionRiskLevel) => CommandPolicy;
  requestApproval: (actionId: string) => Promise<boolean>;
}
