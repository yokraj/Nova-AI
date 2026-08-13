import { ExecutionPlan } from '../types/executionPlan';
import { ToolResolver } from '../tool-router/toolResolver';

export class PlanValidator {
  private toolResolver = new ToolResolver();

  validatePlan(plan: ExecutionPlan): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!plan.steps || plan.steps.length === 0) {
      return { valid: false, errors: ['Execution plan must contain at least one step.'] };
    }

    for (const step of plan.steps) {
      if (step.toolCall) {
        const val = this.toolResolver.validateCall(step.toolCall);
        if (!val.isValid) {
          errors.push(`Step ${step.stepNumber} (${step.title}): ${val.reason}`);
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}
