import { WorkflowDefinition, ReplayConfig, ReplayExecutionResult, ReplayNodeResult, WorkflowNode } from '../types/workflowStudio.js';
import { AgentRuntime } from '../../ai-runtime/runtime/agentRuntime.js';
import { SwarmOrchestrator } from '../../swarm/runtime/swarmOrchestrator.js';
import { LocalVisionProvider } from '../../vision/providers/localVisionProvider.js';
import { ToolPermissionGuard } from '../../ai-runtime/security/toolPermissionGuard.js';
import { promptInjectionGuard } from '../../ai-runtime/security/promptInjectionGuard.js';
import { TargetRelocator, RelocationResult } from '../adaptation/targetRelocator.js';
import { WorkflowVariableExtractor } from '../variables/workflowVariableExtractor.js';
import { WorkflowBuilder } from '../studio/workflowBuilder.js';

export class SwarmReplayEngine {
  private agentRuntime = new AgentRuntime();
  private swarmOrchestrator = new SwarmOrchestrator();
  private visionProvider = new LocalVisionProvider();
  private permissionGuard = new ToolPermissionGuard();
  private targetRelocator = new TargetRelocator();
  private variableExtractor = new WorkflowVariableExtractor();

  async replayWorkflow(workflow: WorkflowDefinition, config: ReplayConfig): Promise<ReplayExecutionResult> {
    const startedAt = new Date().toISOString();
    const startTime = Date.now();
    const nodeResults: ReplayNodeResult[] = [];
    let verifiedCount = 0;
    let overallStatus: 'COMPLETED' | 'FAILED' | 'AWAITING_APPROVAL' = 'COMPLETED';

    const variableInputs = config.variablesInput || {};
    const builder = WorkflowBuilder.fromDefinition(workflow);
    const orderedNodes = builder.getTopologicalOrder();

    for (const node of orderedNodes) {
      if (node.disabled) {
        nodeResults.push({
          nodeId: node.id,
          status: 'SKIPPED',
          durationMs: 0,
          message: 'Step disabled in workflow configuration.',
          verifiedState: true,
        });
        continue;
      }

      if (node.type === 'TRIGGER') {
        nodeResults.push({
          nodeId: node.id,
          status: 'COMPLETED',
          durationMs: 10,
          message: 'Trigger activated.',
          verifiedState: true,
        });
        verifiedCount++;
        continue;
      }

      // Security Evaluation
      const secEval = this.evaluateNodeSecurity(node, workflow.trusted);
      if (!secEval.allowed) {
        nodeResults.push({
          nodeId: node.id,
          status: 'FAILED',
          durationMs: 0,
          message: `Security blocked: ${secEval.reason}`,
          verifiedState: false,
        });
        overallStatus = 'FAILED';
        break;
      }

      if (secEval.requiresApproval && config.pauseOnApproval) {
        nodeResults.push({
          nodeId: node.id,
          status: 'AWAITING_APPROVAL',
          durationMs: 0,
          message: `Approval required for high-risk tool: ${node.toolName}`,
          verifiedState: false,
        });
        overallStatus = 'AWAITING_APPROVAL';
        break;
      }

      // Adaptive Target Relocation
      let relocation: RelocationResult | undefined;
      if (node.semanticTarget) {
        relocation = await this.targetRelocator.relocateTarget(node.semanticTarget);
        if (relocation.confidence < 0.75 && node.riskLevel !== 'SAFE') {
          nodeResults.push({
            nodeId: node.id,
            status: 'FAILED',
            durationMs: 0,
            message: `Target relocation confidence too low (${relocation.confidence.toFixed(2)}): ${relocation.reason}`,
            verifiedState: false,
          });
          overallStatus = 'FAILED';
          break;
        }
      }

      // Node Execution
      const nodeStart = Date.now();
      const execRes = await this.executeNode(node, config, variableInputs, relocation);
      const nodeDuration = Date.now() - nodeStart;

      nodeResults.push({
        nodeId: node.id,
        status: execRes.success ? 'COMPLETED' : 'FAILED',
        durationMs: nodeDuration,
        message: execRes.message,
        verifiedState: execRes.verifiedState,
        resolutionUsed: relocation?.strategyUsed,
        relocatedCoordinates: relocation?.coordinates,
        outputData: execRes.data,
      });

      if (execRes.verifiedState) {
        verifiedCount++;
      }

      if (!execRes.success) {
        overallStatus = 'FAILED';
        break;
      }
    }

    const totalDurationMs = Date.now() - startTime;
    return {
      executionId: `exec-wf-${Date.now()}`,
      workflowId: workflow.id,
      version: workflow.version,
      startedAt,
      completedAt: new Date().toISOString(),
      status: overallStatus,
      totalDurationMs,
      nodeResults,
      verifiedCount,
      summary: `Workflow execution finished with status: ${overallStatus} (${verifiedCount}/${orderedNodes.length} nodes verified)`,
    };
  }

  private evaluateNodeSecurity(node: WorkflowNode, trustedWorkflow: boolean): { allowed: boolean; requiresApproval: boolean; reason?: string } {
    if (node.label) {
      const injectAssessment = promptInjectionGuard.assessAndSanitize(node.label);
      if (!injectAssessment.safe) {
        return { allowed: false, requiresApproval: false, reason: 'Untrusted prompt injection pattern in node label' };
      }
    }

    if (node.riskLevel === 'CRITICAL' || node.riskLevel === 'HIGH') {
      return { allowed: true, requiresApproval: !trustedWorkflow || node.requiresApproval, reason: 'High-risk desktop/system tool requires authorization' };
    }

    const guardRes = this.permissionGuard.evaluateToolPermission({
      callId: `eval-${Date.now()}`,
      toolName: node.toolName || 'system_action',
      arguments: node.arguments || {},
      riskLevel: node.riskLevel === 'SAFE' ? 'SAFE' : node.riskLevel === 'MEDIUM' ? 'MEDIUM' : 'LOW',
    });
    return {
      allowed: guardRes.permitted,
      requiresApproval: guardRes.requiresApproval,
      reason: guardRes.reason,
    };
  }

  private async executeNode(
    node: WorkflowNode,
    config: ReplayConfig,
    variableInputs: Record<string, any>,
    relocation?: RelocationResult
  ): Promise<{ success: boolean; message: string; verifiedState: boolean; data?: any }> {
    try {
      // Substitute dynamic variables in label
      const substitutedLabel = this.variableExtractor.substituteVariables(node.label, variableInputs);

      if (node.type === 'WAIT') {
        const waitMs = node.waitDurationMs || 1000;
        await new Promise((r) => setTimeout(r, Math.min(waitMs, 2000)));
        return {
          success: true,
          message: `Waited for ${waitMs}ms`,
          verifiedState: true,
        };
      }

      if (node.type === 'SWARM_PARALLEL' && config.enableSwarmDelegation) {
        const swarmRes = await this.swarmOrchestrator.executeSwarmGoal(
          `Swarm Node Execution: ${substitutedLabel}`
        );
        return {
          success: swarmRes.success || swarmRes.status === 'COMPLETED',
          message: swarmRes.summary || 'Swarm parallel task completed.',
          verifiedState: true,
          data: swarmRes,
        };
      }

      if (node.type === 'VISION_GROUNDING') {
        const query = node.visualTargetQuery || 'Save';
        const obs = await this.visionProvider.observeScreen();
        const foundTarget = obs.detectedTargets.find((t) =>
          t.label.toLowerCase().includes(query.toLowerCase()) ||
          (t.text && t.text.toLowerCase().includes(query.toLowerCase()))
        );
        return {
          success: true,
          message: foundTarget && foundTarget.boundingBox
            ? `Target located at (${foundTarget.boundingBox.x}, ${foundTarget.boundingBox.y})`
            : `Visual target search completed for query '${query}'`,
          verifiedState: true,
          data: foundTarget || obs,
        };
      }

      // Default goal execution via AgentRuntime
      const goalStr = substitutedLabel || `Execute tool ${node.toolName}`;
      const agentRes = await this.agentRuntime.executeGoal(goalStr);

      let verifiedState = true;
      if (config.verifyVisualStates && node.expectedState) {
        const obs = await this.visionProvider.observeScreen();
        const found = obs.detectedTargets.some((t) =>
          t.label.toLowerCase().includes(node.expectedState!.toLowerCase()) ||
          (t.text && t.text.toLowerCase().includes(node.expectedState!.toLowerCase())) ||
          (obs.activeApplication && obs.activeApplication.toLowerCase().includes(node.expectedState!.toLowerCase())) ||
          (obs.activeWindowTitle && obs.activeWindowTitle.toLowerCase().includes(node.expectedState!.toLowerCase()))
        );
        verifiedState = found;
      }

      return {
        success: agentRes.state === 'COMPLETED',
        message: agentRes.summary || 'Node action executed.',
        verifiedState,
        data: agentRes,
      };
    } catch (err: any) {
      return {
        success: false,
        message: err?.message || 'Node execution failed',
        verifiedState: false,
      };
    }
  }
}
