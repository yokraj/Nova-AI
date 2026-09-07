import { WorkflowExecutionRecord } from '../types/skill';

export class WorkflowRecorder {
  private activeRecord: WorkflowExecutionRecord | null = null;

  startRecording(goalText: string, intent = 'workflow_execution', userExplicitLearningRequested = false): void {
    this.activeRecord = {
      id: `rec-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
      goalText,
      intent,
      startTime: new Date().toISOString(),
      endTime: '',
      durationMs: 0,
      steps: [],
      overallSuccess: false,
      isUntrustedContentPresent: false,
      untrustedSources: [],
      userExplicitLearningRequested,
    };
  }

  recordStep(step: {
    stepNumber: number;
    title: string;
    toolName?: string;
    toolArgs?: Record<string, any>;
    observation?: string;
    success: boolean;
    verificationConfirmed: boolean;
    approvalRequired?: boolean;
    recoveryUsed?: string;
  }): void {
    if (!this.activeRecord) return;

    this.activeRecord.steps.push({
      stepNumber: step.stepNumber,
      title: step.title,
      toolName: step.toolName,
      toolArgs: step.toolArgs ? { ...step.toolArgs } : undefined,
      observation: step.observation,
      success: step.success,
      verificationConfirmed: step.verificationConfirmed,
      approvalRequired: step.approvalRequired,
      recoveryUsed: step.recoveryUsed,
    });
  }

  flagUntrustedContent(source: string): void {
    if (!this.activeRecord) return;
    this.activeRecord.isUntrustedContentPresent = true;
    if (!this.activeRecord.untrustedSources) {
      this.activeRecord.untrustedSources = [];
    }
    if (!this.activeRecord.untrustedSources.includes(source)) {
      this.activeRecord.untrustedSources.push(source);
    }
  }

  finishRecording(overallSuccess: boolean): WorkflowExecutionRecord | null {
    if (!this.activeRecord) return null;

    const endTime = new Date().toISOString();
    const startMs = new Date(this.activeRecord.startTime).getTime();
    const endMs = new Date(endTime).getTime();

    this.activeRecord.endTime = endTime;
    this.activeRecord.durationMs = Math.max(0, endMs - startMs);
    this.activeRecord.overallSuccess = overallSuccess;

    const record = this.activeRecord;
    this.activeRecord = null;
    return record;
  }

  getActiveRecord(): WorkflowExecutionRecord | null {
    return this.activeRecord;
  }
}
