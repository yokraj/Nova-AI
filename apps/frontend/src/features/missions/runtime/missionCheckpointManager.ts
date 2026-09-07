import { MissionCheckpoint, MissionStatus, MissionResourceBudget } from '../types/mission.js';

const CHECKPOINT_STORAGE_KEY = 'nova_mission_checkpoints';

export class MissionCheckpointManager {
  private static memoryCheckpoints: Map<string, MissionCheckpoint[]> = new Map();
  private secretPatterns: RegExp[] = [
    /bearer\s+[a-zA-Z0-9_.-]+/i,
    /api[-_]?key\s*[:=]\s*[a-zA-Z0-9_-]+/i,
    /password\s*[:=]\s*\S+/i,
    /sk-[a-zA-Z0-9]{20,}/i,
    /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/i,
  ];

  createCheckpoint(params: {
    missionId: string;
    executionId: string;
    status: MissionStatus;
    currentStep: number;
    completedSteps: string[];
    failedSteps?: string[];
    pendingSteps: string[];
    activeAgentId?: string;
    activeSwarmTasks?: string[];
    toolExecutionState?: Record<string, any>;
    retryCounters?: Record<string, number>;
    budgetState: MissionResourceBudget;
    approvalState?: { requiresApproval: boolean; stepId?: string; toolName?: string; riskLevel?: string; reason?: string };
    recoveryState?: { strategy?: string; attemptCount: number; errorType?: string };
    verificationResults?: Array<{ stepId: string; verified: boolean; summary: string }>;
    isSafeResumable?: boolean;
    checkpointVersion?: number;
  }): MissionCheckpoint {
    const sanitizedToolState = this.sanitizeState(params.toolExecutionState || {});

    const checkpoint: MissionCheckpoint = {
      checkpointId: `cp-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      executionId: params.executionId,
      missionId: params.missionId,
      timestamp: new Date().toISOString(),
      status: params.status,
      currentStep: params.currentStep,
      completedSteps: [...params.completedSteps],
      failedSteps: [...(params.failedSteps || [])],
      pendingSteps: [...params.pendingSteps],
      executionPlanVersion: 1,
      activeAgentId: params.activeAgentId,
      activeSwarmTasks: [...(params.activeSwarmTasks || [])],
      toolExecutionState: sanitizedToolState,
      retryCounters: { ...(params.retryCounters || {}) },
      budgetState: { ...params.budgetState },
      approvalState: params.approvalState || { requiresApproval: false },
      recoveryState: params.recoveryState || { attemptCount: 0 },
      verificationResults: [...(params.verificationResults || [])],
      isSafeResumable: params.isSafeResumable ?? true,
      checkpointVersion: params.checkpointVersion || 1,
    };

    const existing = MissionCheckpointManager.memoryCheckpoints.get(params.missionId) || [];
    existing.unshift(checkpoint);
    if (existing.length > 20) existing.pop();
    MissionCheckpointManager.memoryCheckpoints.set(params.missionId, existing);

    this.persistToStorage();
    return checkpoint;
  }

  getLatestCheckpoint(missionId: string): MissionCheckpoint | undefined {
    const list = MissionCheckpointManager.memoryCheckpoints.get(missionId) || [];
    return list[0];
  }

  getAllCheckpoints(missionId: string): MissionCheckpoint[] {
    return MissionCheckpointManager.memoryCheckpoints.get(missionId) || [];
  }

  sanitizeState(obj: Record<string, any>): Record<string, any> {
    try {
      let str = JSON.stringify(obj);
      for (const pattern of this.secretPatterns) {
        str = str.replace(pattern, '[REDACTED_SECRET]');
      }
      return JSON.parse(str);
    } catch {
      return {};
    }
  }

  private persistToStorage(): void {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const obj: Record<string, MissionCheckpoint[]> = {};
        for (const [k, v] of MissionCheckpointManager.memoryCheckpoints.entries()) {
          obj[k] = v;
        }
        window.localStorage.setItem(CHECKPOINT_STORAGE_KEY, JSON.stringify(obj));
      }
    } catch {
      // Storage error ignored
    }
  }
}
