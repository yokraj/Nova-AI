export interface BudgetConfig {
  maxSteps: number;
  maxRetriesPerStep: number;
  maxDurationSeconds: number;
  maxConsecutiveFailures: number;
}

export class ExecutionBudget {
  private config: BudgetConfig;
  private currentStepCount = 0;
  private currentFailureCount = 0;
  private startTimeMs = Date.now();

  constructor(config?: Partial<BudgetConfig>) {
    this.config = {
      maxSteps: config?.maxSteps ?? 30,
      maxRetriesPerStep: config?.maxRetriesPerStep ?? 2,
      maxDurationSeconds: config?.maxDurationSeconds ?? 120,
      maxConsecutiveFailures: config?.maxConsecutiveFailures ?? 3,
    };
  }

  incrementStep(): { isWithinBudget: boolean; reason?: string } {
    this.currentStepCount++;
    if (this.currentStepCount > this.config.maxSteps) {
      return { isWithinBudget: false, reason: `Max execution steps limit (${this.config.maxSteps}) reached.` };
    }

    const elapsedSec = (Date.now() - this.startTimeMs) / 1000;
    if (elapsedSec > this.config.maxDurationSeconds) {
      return { isWithinBudget: false, reason: `Max execution duration (${this.config.maxDurationSeconds}s) exceeded.` };
    }

    return { isWithinBudget: true };
  }

  recordFailure(): { isWithinBudget: boolean; reason?: string } {
    this.currentFailureCount++;
    if (this.currentFailureCount >= this.config.maxConsecutiveFailures) {
      return { isWithinBudget: false, reason: `Max consecutive failures (${this.config.maxConsecutiveFailures}) reached.` };
    }
    return { isWithinBudget: true };
  }

  recordSuccess(): void {
    this.currentFailureCount = 0;
  }

  getMaxRetriesPerStep(): number {
    return this.config.maxRetriesPerStep;
  }

  getRemainingSteps(): number {
    return Math.max(0, this.config.maxSteps - this.currentStepCount);
  }
}
