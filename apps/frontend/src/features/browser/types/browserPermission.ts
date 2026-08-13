export type BrowserRiskLevel = 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface BrowserPermission {
  riskLevel: BrowserRiskLevel;
  requiresApproval: boolean;
  reason: string;
  allowedDomains?: string[];
  blockedDomains?: string[];
}
