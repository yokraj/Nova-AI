export interface ResourceBudgetConfig {
  maxDurationMs: number;
  maxSteps: number;
  maxRetries: number;
  maxConcurrentTasks: number;
}

export class ResourceBudgetGuard {
  private config: ResourceBudgetConfig = {
    maxDurationMs: 30000,
    maxSteps: 10,
    maxRetries: 3,
    maxConcurrentTasks: 2,
  };

  constructor(config?: Partial<ResourceBudgetConfig>) {
    if (config) {
      this.config = { ...this.config, ...config };
    }
  }

  isWithinConcurrencyLimit(activeRunningCount: number): boolean {
    return activeRunningCount < this.config.maxConcurrentTasks;
  }

  isStepLimitExceeded(stepCount: number): boolean {
    return stepCount >= this.config.maxSteps;
  }

  isRetryLimitExceeded(retryCount: number): boolean {
    return retryCount >= this.config.maxRetries;
  }

  isDurationExceeded(durationMs: number): boolean {
    return durationMs >= this.config.maxDurationMs;
  }

  getConfig(): ResourceBudgetConfig {
    return { ...this.config };
  }
}
