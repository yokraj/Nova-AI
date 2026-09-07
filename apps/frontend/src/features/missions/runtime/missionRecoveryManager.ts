import { MissionItem, MissionCheckpoint, RecoveryClassification, MissionResourceBudget } from '../types/mission.js';
import { MissionCheckpointManager } from './missionCheckpointManager.js';
import { StepIdempotencyEngine } from './stepIdempotencyEngine.js';
import { RecoveryEngine, RecoveryStrategy } from '../../ai-runtime/runtime/recoveryEngine.js';
import { AgentRuntime } from '../../ai-runtime/runtime/agentRuntime.js';

export class MissionRecoveryManager {
  private checkpointManager = new MissionCheckpointManager();
  private idempotencyEngine = new StepIdempotencyEngine();
  private recoveryEngine = new RecoveryEngine();
  private agentRuntime = new AgentRuntime();

  classifyRestartRecovery(mission: MissionItem, checkpoint?: MissionCheckpoint): RecoveryClassification {
    if (!checkpoint || !checkpoint.isSafeResumable) {
      return 'ABORT_REQUIRED';
    }

    if (checkpoint.approvalState.requiresApproval) {
      return 'REQUIRES_USER_APPROVAL';
    }

    if (mission.status === 'RECOVERING' || mission.status === 'REPLANNING') {
      return 'REQUIRES_REVALIDATION';
    }

    if (checkpoint.budgetState.remainingDurationSeconds <= 0 || checkpoint.budgetState.executedSteps >= checkpoint.budgetState.maxSteps) {
      return 'ABORT_REQUIRED';
    }

    return 'SAFE_TO_RESUME';
  }

  async resumeMission(mission: MissionItem): Promise<{ success: boolean; message: string; checkpoint?: MissionCheckpoint }> {
    const cp = this.checkpointManager.getLatestCheckpoint(mission.id);
    const classification = this.classifyRestartRecovery(mission, cp);

    if (classification === 'ABORT_REQUIRED') {
      mission.status = 'FAILED';
      return { success: false, message: 'Mission cannot be resumed safely. Remaining budget exhausted or invalid checkpoint.', checkpoint: cp };
    }

    if (classification === 'REQUIRES_USER_APPROVAL') {
      mission.status = 'AWAITING_APPROVAL';
      return { success: false, message: 'Mission requires user authorization before resuming high-risk step.', checkpoint: cp };
    }

    // Step Idempotency Verification prior to step execution
    if (cp && cp.pendingSteps.length > 0) {
      const nextStepId = cp.pendingSteps[0];
      const idempRes = await this.idempotencyEngine.verifyStepCompletion({
        id: nextStepId,
        title: `Step ${cp.currentStep + 1}`,
        toolName: cp.toolExecutionState.toolName || 'system_action',
        arguments: cp.toolExecutionState.arguments || {},
      });

      if (idempRes.completed) {
        cp.completedSteps.push(nextStepId);
        cp.pendingSteps.shift();
        cp.currentStep += 1;
        cp.budgetState.executedSteps += 1;

        this.checkpointManager.createCheckpoint({
          missionId: mission.id,
          executionId: cp.executionId,
          status: cp.pendingSteps.length === 0 ? 'COMPLETED' : 'EXECUTING',
          currentStep: cp.currentStep,
          completedSteps: cp.completedSteps,
          pendingSteps: cp.pendingSteps,
          budgetState: cp.budgetState,
        });

        if (cp.pendingSteps.length === 0) {
          mission.status = 'COMPLETED';
          mission.progress = 100;
          return { success: true, message: 'Mission completed upon idempotency state verification.', checkpoint: cp };
        }
      }
    }

    // Execute remaining goal via AgentRuntime
    mission.status = 'EXECUTING';
    const agentRes = await this.agentRuntime.executeGoal(mission.goal);

    const isComplete = agentRes.state === 'COMPLETED';
    mission.status = isComplete ? 'COMPLETED' : 'FAILED';
    mission.progress = isComplete ? 100 : mission.progress;

    const newCp = this.checkpointManager.createCheckpoint({
      missionId: mission.id,
      executionId: cp?.executionId || `exec-${Date.now()}`,
      status: mission.status,
      currentStep: (cp?.currentStep || 0) + 1,
      completedSteps: [...(cp?.completedSteps || []), `step-${Date.now()}`],
      pendingSteps: [],
      budgetState: cp?.budgetState || this.getDefaultBudget(),
    });

    return {
      success: isComplete,
      message: agentRes.summary || `Mission execution state: ${mission.status}`,
      checkpoint: newCp,
    };
  }

  evaluateRecoveryStrategy(step: any, errorReason: string): RecoveryStrategy {
    return this.recoveryEngine.determineRecoveryStrategy(step, {
      callId: `recovery-${Date.now()}`,
      toolName: step.toolName || 'action',
      success: false,
      errorReason,
      durationMs: 0,
      verifiedState: false,
    });
  }

  getDefaultBudget(): MissionResourceBudget {
    return {
      maxSteps: 50,
      executedSteps: 0,
      retriesCount: 0,
      maxDurationSeconds: 3600,
      elapsedDurationSeconds: 0,
      remainingDurationSeconds: 3600,
      swarmConcurrencyLimit: 4,
    };
  }
}
