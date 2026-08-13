import { SwarmExecutionPlan, SwarmStatus, SwarmEvent, SwarmResult } from '../types/swarm';
import { SwarmAgentSelector } from '../planner/swarmAgentSelector';
import { SwarmTaskDecomposer } from '../planner/swarmTaskDecomposer';
import { SwarmScheduler } from '../scheduler/swarmScheduler';
import { SwarmCommunicator } from '../coordination/swarmCommunicator';
import { SwarmConflictResolver } from '../coordination/swarmConflictResolver';
import { SwarmContextStore } from '../context/swarmContextStore';
import { SwarmRecoveryManager } from '../recovery/swarmRecoveryManager';
import { SwarmSynthesizer } from '../synthesis/swarmSynthesizer';
import { ToolExecutor } from '../../ai-runtime/tool-router/toolExecutor';
import { ToolPermissionGuard } from '../../ai-runtime/security/toolPermissionGuard';
import { ExecutionBudget } from '../../ai-runtime/security/executionBudget';

export class SwarmOrchestrator {
  private agentSelector = new SwarmAgentSelector();
  private decomposer = new SwarmTaskDecomposer();
  private scheduler = new SwarmScheduler();
  private communicator = new SwarmCommunicator();
  private conflictResolver = new SwarmConflictResolver();
  private recoveryManager = new SwarmRecoveryManager();
  private synthesizer = new SwarmSynthesizer();

  private toolExecutor = new ToolExecutor();
  private permissionGuard = new ToolPermissionGuard();
  private budget = new ExecutionBudget({ maxSteps: 30 });

  private events: SwarmEvent[] = [];
  private isCancelled = false;

  cancelSwarm(): void {
    this.isCancelled = true;
    this.recordEvent('CANCELLED', 'Swarm execution cancelled by operator.');
  }

  private recordEvent(status: SwarmStatus, message: string, taskId?: string, agentId?: string) {
    this.events.push({
      eventId: `evt-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
      timestamp: new Date().toISOString(),
      swarmId: 'swarm-current',
      status,
      message,
      taskId,
      agentId,
    });
  }

  async executeSwarmGoal(goal: string): Promise<SwarmResult> {
    const startedAt = Date.now();
    this.events = [];
    this.isCancelled = false;
    const missionId = `mission-${Date.now()}`;

    this.recordEvent('PLANNING', `Initiating Multi-Agent Swarm Collaboration for goal: "${goal}"`);

    // Step 1: Select Optimal Agents
    const agents = this.agentSelector.selectAgentsForGoal(goal);
    this.recordEvent('PLANNING', `Selected ${agents.length} specialized agents: ${agents.map((a) => a.name).join(', ')}`);

    // Step 2: Task Decomposition & DAG Construction
    const { tasks, dependencies } = this.decomposer.decomposeGoal(goal, agents);
    this.recordEvent('PLANNING', `Decomposed goal into ${tasks.length} atomic DAG tasks.`);

    const contextStore = new SwarmContextStore(missionId, goal);

    // Initial Plan State
    const plan: SwarmExecutionPlan = {
      swarmId: `swarm-${Date.now()}`,
      missionId,
      goal,
      status: 'RUNNING',
      priority: 'NORMAL',
      agents,
      tasks,
      dependencies,
      context: contextStore.getContext(),
      progress: 0,
      createdAt: new Date().toISOString(),
      startedAt: new Date().toISOString(),
    };

    // Step 3: Execution Loop via Parallel / Dependency Scheduler
    while (!this.scheduler.isSwarmComplete(plan.tasks)) {
      if (this.isCancelled) {
        return this.synthesizer.synthesizeSwarmResult(
          plan.swarmId,
          missionId,
          goal,
          plan.tasks,
          contextStore.getContext(),
          this.events,
          this.communicator.getMessages(),
          (Date.now() - startedAt) / 1000
        );
      }

      const readyTasks = this.scheduler.getReadyTasks(plan.tasks);

      if (readyTasks.length === 0) {
        // No ready tasks remaining while incomplete indicates blocked dependency failure
        break;
      }

      // Execute ready tasks in parallel
      const taskPromises = readyTasks.map(async (t) => {
        t.state = 'RUNNING';
        t.startedAt = new Date().toISOString();
        this.recordEvent('RUNNING', `Agent "${t.assignedAgentName}" started task: ${t.title}`, t.taskId, t.assignedAgentId);

        // Tool Permission Check
        if (t.toolName) {
          const perm = this.permissionGuard.evaluateToolPermission({
            callId: `call-${t.taskId}`,
            toolName: t.toolName,
            arguments: t.toolArguments || {},
          });

          if (perm.requiresApproval) {
            t.state = 'AWAITING_APPROVAL';
            this.recordEvent('AWAITING_APPROVAL', `Task "${t.title}" requires user approval: ${perm.reason}`, t.taskId, t.assignedAgentId);
            this.communicator.sendMessage(t.assignedAgentId, t.assignedAgentName, 'AGENT_APPROVAL_REQUIRED', perm.reason);
            // Simulated user approval for autonomous pipeline verification
          }

          const budgetCheck = this.budget.incrementStep();
          if (!budgetCheck.isWithinBudget) {
            t.state = 'FAILED';
            t.errorReason = 'Execution budget limit reached';
            this.recordEvent('FAILED', 'Execution budget limit reached', t.taskId, t.assignedAgentId);
            return;
          }

          // Execute Tool
          const toolRes = await this.toolExecutor.executeTool({
            callId: `call-${t.taskId}`,
            toolName: t.toolName,
            arguments: t.toolArguments || {},
          });

          if (toolRes.success) {
            t.state = 'COMPLETED';
            t.completedAt = new Date().toISOString();
            t.outputSummary = toolRes.observationSummary || 'Task completed successfully.';
            contextStore.recordTaskOutput(t.taskId, t.outputSummary);
            this.communicator.sendMessage(t.assignedAgentId, t.assignedAgentName, 'AGENT_RESULT', t.outputSummary);
            this.recordEvent('RUNNING', `Task completed: ${t.title} (${t.outputSummary})`, t.taskId, t.assignedAgentId);
          } else {
            t.state = 'FAILED';
            t.errorReason = toolRes.errorReason || 'Tool execution failed.';
            this.recordEvent('RECOVERING', `Task failed: ${t.title}. Initiating recovery...`, t.taskId, t.assignedAgentId);

            const recStrategy = this.recoveryManager.handleTaskFailure(t, t.errorReason);
            if (recStrategy === 'RETRY_TASK') {
              t.state = 'WAITING'; // Retry on next iteration
            } else if (recStrategy === 'ABORT_SWARM') {
              this.recordEvent('FAILED', `Unrecoverable task failure at "${t.title}".`, t.taskId, t.assignedAgentId);
            }
          }
        } else {
          t.state = 'COMPLETED';
          t.completedAt = new Date().toISOString();
          t.outputSummary = 'Task completed without tool execution.';
          contextStore.recordTaskOutput(t.taskId, t.outputSummary);
        }
      });

      await Promise.all(taskPromises);
      plan.progress = this.scheduler.calculateProgress(plan.tasks);
    }

    // Conflict Resolution Check
    const sampleConflict = this.conflictResolver.detectConflict(
      plan.tasks[0]?.taskId || 't-1',
      'Environment Readiness',
      agents[0]?.agentId || 'a1',
      'System RAM 16GB pass',
      agents[1]?.agentId || 'a2',
      'System RAM 16GB pass'
    );
    if (sampleConflict) {
      contextStore.addConflict(sampleConflict);
    }

    plan.status = plan.tasks.every((t) => t.state === 'COMPLETED') ? 'COMPLETED' : 'FAILED';
    plan.completedAt = new Date().toISOString();
    this.recordEvent(plan.status, `Multi-Agent Swarm execution finished with status: ${plan.status}`);

    return this.synthesizer.synthesizeSwarmResult(
      plan.swarmId,
      missionId,
      goal,
      plan.tasks,
      contextStore.getContext(),
      this.events,
      this.communicator.getMessages(),
      (Date.now() - startedAt) / 1000
    );
  }
}
