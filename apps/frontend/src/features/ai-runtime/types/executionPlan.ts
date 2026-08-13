import { ExecutionStep } from './executionStep';

export interface ExecutionPlan {
  planId: string;
  goal: string;
  steps: ExecutionStep[];
  isParallelAllowed?: boolean;
  estimatedDurationSeconds: number;
  createdAt: string;
}
