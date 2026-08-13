export type MissionStatus =
  | 'DRAFT'
  | 'UNDERSTANDING'
  | 'PLANNING'
  | 'AWAITING_APPROVAL'
  | 'READY'
  | 'EXECUTING'
  | 'PAUSED'
  | 'REPLANNING'
  | 'VERIFYING'
  | 'COMPLETED'
  | 'PARTIALLY_COMPLETED'
  | 'FAILED'
  | 'CANCELLED';

export type MissionPriority = 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT';

export type AutonomyLevel = 'ASSISTED' | 'SUPERVISED' | 'AUTONOMOUS';

export interface MissionItem {
  id: string;
  title: string;
  goal: string;
  description: string;
  status: MissionStatus;
  priority: MissionPriority;
  autonomyLevel: AutonomyLevel;
  progress: number; // 0 to 100
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  assignedAgents: string[];
  tasksCount: number;
  completedTasksCount: number;
}

export interface MissionProvider {
  listMissions: () => MissionItem[];
  getMissionById: (id: string) => MissionItem | undefined;
}
