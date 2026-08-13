export type CommandRiskLevel = 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type CommandPolicy = 'ALLOW' | 'ALLOW_WITH_APPROVAL' | 'DENY';

export interface CommandPermissionAssessment {
  riskLevel: CommandRiskLevel;
  policy: CommandPolicy;
  requiredCapability: string;
  scope: string;
  reason: string;
  requiresApproval: boolean;
}
