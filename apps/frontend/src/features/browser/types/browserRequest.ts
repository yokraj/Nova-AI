import { BrowserActionType } from './browserAction';
import { BrowserTarget } from './browserTarget';
import { BrowserRiskLevel } from './browserPermission';

export interface BrowserRequest {
  requestId: string;
  action: BrowserActionType;
  target: BrowserTarget;
  textPayload?: string;
  parameters?: {
    textInput?: string;
    selectedOption?: string;
    downloadDestination?: string;
    uploadFilePath?: string;
    scrollDistance?: number;
    timeoutMs?: number;
  };
  riskLevel: BrowserRiskLevel;
  requiresApproval: boolean;
  timestamp: string;
}
