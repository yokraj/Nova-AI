import { WorkflowDefinition, RecordingSession, ReplayExecutionResult } from '../types/workflowStudio.js';

const WORKFLOW_STORAGE_KEY = 'nova_workflow_definitions';
const RECORDING_STORAGE_KEY = 'nova_recording_sessions';
const REPLAY_HISTORY_KEY = 'nova_replay_history';

export class WorkflowStore {
  private static staticWorkflows: Map<string, WorkflowDefinition> = new Map();
  private static staticRecordings: Map<string, RecordingSession> = new Map();
  private static staticHistory: ReplayExecutionResult[] = [];

  private workflows: Map<string, WorkflowDefinition> = WorkflowStore.staticWorkflows;
  private recordings: Map<string, RecordingSession> = WorkflowStore.staticRecordings;
  private history: ReplayExecutionResult[] = WorkflowStore.staticHistory;

  constructor() {
    this.loadFromStorage();
  }

  saveWorkflow(workflow: WorkflowDefinition): WorkflowDefinition {
    const updated = { ...workflow, updatedAt: new Date().toISOString() };
    this.workflows.set(updated.id, updated);
    this.persistToStorage();
    return updated;
  }

  getWorkflow(id: string): WorkflowDefinition | undefined {
    return this.workflows.get(id);
  }

  getAllWorkflows(): WorkflowDefinition[] {
    return Array.from(this.workflows.values());
  }

  deleteWorkflow(id: string): boolean {
    const deleted = this.workflows.delete(id);
    if (deleted) {
      this.persistToStorage();
    }
    return deleted;
  }

  saveRecordingSession(session: RecordingSession): void {
    this.recordings.set(session.sessionId, session);
    this.persistToStorage();
  }

  getRecordingSession(id: string): RecordingSession | undefined {
    return this.recordings.get(id);
  }

  recordReplayExecution(result: ReplayExecutionResult): void {
    this.history.unshift(result);
    if (this.history.length > 50) {
      this.history = this.history.slice(0, 50);
    }

    const wf = this.workflows.get(result.workflowId);
    if (wf) {
      const execCount = (wf.executionCount || 0) + 1;
      const successCount = this.history.filter((h) => h.workflowId === wf.id && h.status === 'COMPLETED').length;
      wf.executionCount = execCount;
      wf.successRate = Math.round((successCount / execCount) * 100);
      this.saveWorkflow(wf);
    }

    this.persistToStorage();
  }

  getReplayHistory(workflowId?: string): ReplayExecutionResult[] {
    if (workflowId) {
      return this.history.filter((h) => h.workflowId === workflowId);
    }
    return [...this.history];
  }

  convertWorkflowToSkill(workflow: WorkflowDefinition): { skillId: string; name: string } {
    const skillId = `skill-${workflow.id}`;
    return {
      skillId,
      name: `Learned Skill: ${workflow.name}`,
    };
  }

  private loadFromStorage(): void {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const storedWfs = window.localStorage.getItem(WORKFLOW_STORAGE_KEY);
        if (storedWfs) {
          const arr: WorkflowDefinition[] = JSON.parse(storedWfs);
          for (const w of arr) {
            this.workflows.set(w.id, w);
          }
        }
        const storedRecs = window.localStorage.getItem(RECORDING_STORAGE_KEY);
        if (storedRecs) {
          const arr: RecordingSession[] = JSON.parse(storedRecs);
          for (const r of arr) {
            this.recordings.set(r.sessionId, r);
          }
        }
        const storedHist = window.localStorage.getItem(REPLAY_HISTORY_KEY);
        if (storedHist) {
          const arr: ReplayExecutionResult[] = JSON.parse(storedHist);
          this.history = arr;
        }
      }
    } catch {
      // Storage error ignored
    }
  }

  private persistToStorage(): void {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem(WORKFLOW_STORAGE_KEY, JSON.stringify(Array.from(this.workflows.values())));
        window.localStorage.setItem(RECORDING_STORAGE_KEY, JSON.stringify(Array.from(this.recordings.values())));
        window.localStorage.setItem(REPLAY_HISTORY_KEY, JSON.stringify(this.history));
      }
    } catch {
      // Storage error ignored
    }
  }
}
