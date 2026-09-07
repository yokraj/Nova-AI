import { AgentState } from '../types/agentState';
import { ExecutionPlan } from '../types/executionPlan';
import { ExecutionStep } from '../types/executionStep';
import { ToolResult } from '../types/toolResult';
import { RuntimeEvent } from '../types/runtimeEvent';
import { LocalModelProvider } from '../providers/localModelProvider';
import { MockModelProvider } from '../providers/mockModelProvider';
import { ModelProvider } from '../providers/modelProvider';
import { ToolExecutor } from '../tool-router/toolExecutor';
import { PlanValidator } from '../planner/planValidator';
import { ExecutionBudget } from '../security/executionBudget';
import { ToolPermissionGuard } from '../security/toolPermissionGuard';
import { AgentPolicy } from '../security/agentPolicy';
import { RecoveryEngine } from './recoveryEngine';

export class AgentRuntime {
  private currentState: AgentState = 'IDLE';
  private localProvider = new LocalModelProvider();
  private mockProvider = new MockModelProvider();
  private activeProvider: ModelProvider = this.mockProvider;
  private isLocalConnected = false;

  private toolExecutor = new ToolExecutor();
  private planValidator = new PlanValidator();
  private budget = new ExecutionBudget();
  private permissionGuard = new ToolPermissionGuard();
  private agentPolicy = new AgentPolicy();
  private recoveryEngine = new RecoveryEngine();

  private activePlan: ExecutionPlan | null = null;
  private eventHistory: RuntimeEvent[] = [];
  private isCancelled = false;

  getState(): AgentState {
    return this.currentState;
  }

  getEventHistory(): RuntimeEvent[] {
    return this.eventHistory;
  }

  getActivePlan(): ExecutionPlan | null {
    return this.activePlan;
  }

  getProviderStatus(): { isLocalConnected: boolean; providerName: string } {
    return {
      isLocalConnected: this.isLocalConnected,
      providerName: this.activeProvider.providerName,
    };
  }

  cancelExecution(): void {
    this.isCancelled = true;
    this.transitionState('CANCELLED', 'User requested execution cancellation.');
  }

  private transitionState(newState: AgentState, message: string, step?: ExecutionStep, toolResult?: ToolResult) {
    this.currentState = newState;
    const evt: RuntimeEvent = {
      eventId: `evt-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
      timestamp: new Date().toISOString(),
      state: newState,
      message,
      step,
      toolResult,
    };
    this.eventHistory.push(evt);
  }

  async checkModelConnection(): Promise<boolean> {
    const isOnline = await this.localProvider.isAvailable();
    this.isLocalConnected = isOnline;
    if (isOnline) {
      this.activeProvider = this.localProvider;
    } else {
      this.activeProvider = this.mockProvider;
    }
    return isOnline;
  }

  async executeGoal(goalText: string): Promise<{
    success: boolean;
    state: AgentState;
    plan?: ExecutionPlan;
    summary: string;
    isLocalModelUsed: boolean;
  }> {
    this.isCancelled = false;
    this.eventHistory = [];
    this.transitionState('UNDERSTANDING', `Analyzing user goal: "${goalText}"`);

    // Check model provider connection
    const localConnected = await this.checkModelConnection();

    // Step 1: Planning
    this.transitionState(
      'PLANNING',
      localConnected
        ? 'Generating structured plan using REAL LOCAL MODEL...'
        : 'LOCAL MODEL UNAVAILABLE — Using Mock Fallback plan generator...'
    );

    let plan: ExecutionPlan;
    try {
      plan = await this.activeProvider.generatePlan(goalText);
    } catch (err: any) {
      // If local model fails during plan generation, fall back to mock
      this.activeProvider = this.mockProvider;
      this.isLocalConnected = false;
      this.transitionState('REPLANNING', `Local model error: ${err.message}. Falling back to Mock Engine...`);
      plan = await this.mockProvider.generatePlan(goalText);
    }

    return this.executePlan(plan);
  }

  async executePlan(plan: ExecutionPlan): Promise<{
    success: boolean;
    state: AgentState;
    plan: ExecutionPlan;
    summary: string;
    isLocalModelUsed: boolean;
  }> {
    this.activePlan = plan;

    // Step 2: Validate Plan
    const val = this.planValidator.validatePlan(plan);
    if (!val.valid) {
      this.transitionState('FAILED', `Plan validation failed: ${val.errors.join('; ')}`);
      return {
        success: false,
        state: 'FAILED',
        plan,
        summary: val.errors.join('; '),
        isLocalModelUsed: this.activeProvider === this.localProvider,
      };
    }

    // Step 3: Execution Loop
    const observations: string[] = [];

    for (const step of plan.steps) {
      if (this.isCancelled) {
        return {
          success: false,
          state: 'CANCELLED',
          plan,
          summary: 'Execution cancelled by user.',
          isLocalModelUsed: this.activeProvider === this.localProvider,
        };
      }

      const budgetCheck = this.budget.incrementStep();
      if (!budgetCheck.isWithinBudget) {
        this.transitionState('TIMED_OUT', budgetCheck.reason || 'Budget exceeded.');
        return {
          success: false,
          state: 'TIMED_OUT',
          plan,
          summary: budgetCheck.reason || 'Budget limit reached.',
          isLocalModelUsed: this.activeProvider === this.localProvider,
        };
      }

      step.status = 'EXECUTING';
      this.transitionState('EXECUTING', `Executing Step ${step.stepNumber}: ${step.title}`, step);

      if (step.toolCall) {
        // Permission check
        const perm = this.permissionGuard.evaluateToolPermission(step.toolCall);
        if (perm.requiresApproval) {
          step.status = 'AWAITING_APPROVAL';
          this.transitionState('AWAITING_APPROVAL', perm.reason, step);
        }

        // Execute Tool
        const toolRes = await this.toolExecutor.executeTool(step.toolCall);
        step.toolResult = toolRes;

        // Prompt Injection Defense
        if (toolRes.observationSummary) {
          const sanitizeRes = this.agentPolicy.sanitizeUntrustedContent(toolRes.observationSummary);
          toolRes.observationSummary = sanitizeRes.safeContent;
          observations.push(sanitizeRes.safeContent);
        }

        // Step 4: Observation
        this.transitionState('OBSERVING', `Observation: ${toolRes.observationSummary || 'Tool execution completed.'}`, step, toolRes);

        // Step 5: Verification
        this.transitionState('VERIFYING', `Verifying state change for step ${step.stepNumber}...`, step, toolRes);
        if (toolRes.success && toolRes.verifiedState) {
          step.status = 'COMPLETED';
          step.verificationConfirmed = true;
          this.budget.recordSuccess();
        } else {
          step.status = 'FAILED';
          this.budget.recordFailure();

          // Step 6: Recovery / Replanning
          this.transitionState('RECOVERING', `Step ${step.stepNumber} failed. Initiating recovery...`, step, toolRes);
          const strategy = this.recoveryEngine.determineRecoveryStrategy(step, toolRes);

          if (strategy === 'ABORT') {
            this.transitionState('FAILED', `Execution failed at step ${step.stepNumber}: ${toolRes.errorReason || 'Unrecoverable error.'}`, step);
            return {
              success: false,
              state: 'FAILED',
              plan,
              summary: toolRes.errorReason || 'Unrecoverable tool failure.',
              isLocalModelUsed: this.activeProvider === this.localProvider,
            };
          }
        }
      } else {
        step.status = 'COMPLETED';
      }
    }

    this.transitionState('COMPLETED', `Goal "${plan.goalText}" successfully executed and verified across all plan steps.`);
    return {
      success: true,
      state: 'COMPLETED',
      plan,
      summary: `Successfully executed ${plan.steps.length} verified steps for goal: "${plan.goalText}".`,
      isLocalModelUsed: this.activeProvider === this.localProvider,
    };
  }
}
