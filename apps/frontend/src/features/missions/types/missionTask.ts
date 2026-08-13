export type MissionTaskStatus =
  | 'PENDING'
  | 'READY'
  | 'ASSIGNED'
  | 'RUNNING'
  | 'WAITING'
  | 'BLOCKED'
  | 'AWAITING_APPROVAL'
  | 'COMPLETED'
  | 'FAILED'
  | 'SKIPPED'
  | 'CANCELLED';

export interface MissionTask {
  id: string;
  missionId: string;
  title: string;
  description: string;
  status: MissionTaskStatus;
  progress: number;
  assignedAgentId: string;
  assignedAgentName: string;
  dependencies: string[]; // Dependee task IDs
  toolsRequired: string[];
  permissionsRequired: string[];
  startedAt?: string;
  completedAt?: string;
  outputLog?: string;
  errorReason?: string;
}
