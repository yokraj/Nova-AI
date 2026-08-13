import { SwarmTask } from '../types/swarm';
import { RecoveryEngine } from '../../ai-runtime/runtime/recoveryEngine';

export class SwarmRecoveryManager {
  private recoveryEngine = new RecoveryEngine();

  handleTaskFailure(task: SwarmTask, errorReason: string): 'RETRY_TASK' | 'REASSIGN_AGENT' | 'REPLAN' | 'ASK_USER' | 'ABORT_SWARM' {
    const mockStep = {
      id: task.taskId,
      stepNumber: 1,
      title: task.title,
      description: task.description,
      status: 'FAILED' as const,
    };
    const mockResult = {
      callId: `call-${task.taskId}`,
      toolName: task.toolName || 'system.get_info',
      success: false,
      durationMs: 10,
      errorReason,
    };

    const strategy = this.recoveryEngine.determineRecoveryStrategy(mockStep, mockResult);

    if (strategy === 'RETRY') return 'RETRY_TASK';
    if (strategy === 'REPLAN') return 'REPLAN';
    if (strategy === 'ASK_APPROVAL') return 'ASK_USER';
    return 'ABORT_SWARM';
  }
}
