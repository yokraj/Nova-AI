import { SwarmContext, SwarmConflict } from '../types/swarm';

export class SwarmContextStore {
  private context: SwarmContext;

  constructor(missionId: string, goal: string) {
    this.context = {
      missionId,
      goal,
      taskOutputs: {},
      sharedFindings: [],
      memoryReferences: ['mem-ref-defaults'],
      knowledgeReferences: ['kn-entity-project'],
      activeWarnings: [],
      conflicts: [],
    };
  }

  recordTaskOutput(taskId: string, outputSummary: string): void {
    this.context.taskOutputs[taskId] = outputSummary;
    this.context.sharedFindings.push(`[Task ${taskId}]: ${outputSummary}`);
  }

  addWarning(warningText: string): void {
    this.context.activeWarnings.push(warningText);
  }

  addConflict(conflict: SwarmConflict): void {
    this.context.conflicts.push(conflict);
  }

  getContext(): SwarmContext {
    return { ...this.context };
  }
}
