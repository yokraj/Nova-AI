import { VisionActionType } from './visionAction';
import { VisionSource } from './visionSource';
import { VisionRiskLevel } from './visionPermission';

export interface VisionRequest {
  requestId: string;
  action: VisionActionType;
  source: VisionSource;
  targetDescription?: string;
  parameters?: {
    imageBufferBase64?: string;
    filePath?: string;
    textInput?: string;
    minConfidence?: number;
    timeoutMs?: number;
  };
  riskLevel: VisionRiskLevel;
  requiresApproval: boolean;
  timestamp: string;
}
