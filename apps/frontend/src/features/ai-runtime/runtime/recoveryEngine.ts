import { ExecutionStep } from '../types/executionStep';
import { ToolResult } from '../types/toolResult';

export type RecoveryStrategy = 'RETRY' | 'ALTERNATIVE_TOOL' | 'REPLAN' | 'ASK_APPROVAL' | 'ABORT';

export class RecoveryEngine {
  determineRecoveryStrategy(step: ExecutionStep, result?: ToolResult): RecoveryStrategy {
    const retries = step.retryCount || 0;

    if (retries < 2) {
      return 'RETRY';
    }

    if (result?.errorReason?.includes('already exists')) {
      return 'REPLAN';
    }

    if (result?.errorReason?.includes('permission')) {
      return 'ASK_APPROVAL';
    }

    return 'ABORT';
  }
}
