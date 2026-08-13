import { MissionTask } from './missionTask';

export interface MissionPlan {
  missionId: string;
  inferredOutcome: string;
  constraints: string[];
  tasks: MissionTask[];
  estimatedTimeSeconds: number;
}

export interface MissionPlanningProvider {
  understandGoal: (goal: string) => { outcome: string; constraints: string[] };
  generatePlan: (missionId: string, goal: string) => MissionPlan;
}
