export type CommandMode = 'text' | 'voice' | 'vision' | 'file' | 'command';

export type CommandStage = 'idle' | 'understanding' | 'planning' | 'selecting_capabilities' | 'mission_created' | 'running';

export interface CommandSimulationState {
  stage: CommandStage;
  rawPrompt: string;
  parsedIntent?: string;
  selectedAgents?: string[];
  missionId?: string;
  statusMessage?: string;
}

export interface SecurityApprovalRequest {
  id: string;
  title: string;
  requesterAgent: string;
  actionType: 'Admin Action' | 'Sensitive Action' | 'Device Permission' | 'Approval Required';
  riskLevel: 'low' | 'medium' | 'high';
  timestamp: string;
}
