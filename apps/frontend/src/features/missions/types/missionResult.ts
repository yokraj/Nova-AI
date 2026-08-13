export interface MissionResultSummary {
  missionId: string;
  isSuccess: boolean;
  isPartial: boolean;
  completedTasksCount: number;
  totalTasksCount: number;
  finalDeliverable: string;
  summaryReport: string;
  keyOutputs: string[];
}
