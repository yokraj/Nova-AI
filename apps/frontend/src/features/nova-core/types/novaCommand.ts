import { NovaCoreState, NovaExecutionStage } from './novaCore';

export type NovaCommandMode = 'text' | 'voice' | 'vision' | 'file' | 'command';

export interface NovaCommand {
  id: string;
  prompt: string;
  mode: NovaCommandMode;
  timestamp: string;
}

export interface NovaResponse {
  commandId: string;
  prompt: string;
  state: NovaCoreState;
  executionStage: NovaExecutionStage;
  spokenText: string;
  detailedOutput?: string;
  assignedAgent?: string;
  missionId?: string;
  securityApprovalRequired?: boolean;
  securityActionTitle?: string;
  securityRiskLevel?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  suggestedDrawer?: 'agents' | 'missions' | 'devices' | 'memory' | 'knowledge' | 'automation' | 'telemetry';
}
