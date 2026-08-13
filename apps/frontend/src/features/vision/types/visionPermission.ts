export type VisionRiskLevel = 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type VisionPermissionState =
  | 'NOT_REQUESTED'
  | 'REQUESTING'
  | 'GRANTED'
  | 'DENIED'
  | 'REVOKED';

export interface VisionPermission {
  screenAccess: VisionPermissionState;
  cameraAccess: VisionPermissionState;
  riskLevel: VisionRiskLevel;
  requiresApproval: boolean;
  reason: string;
}
