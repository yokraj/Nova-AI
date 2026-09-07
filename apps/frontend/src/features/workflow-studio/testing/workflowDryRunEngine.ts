import { WorkflowDefinition, DryRunResult, DryRunStepAssessment } from '../types/workflowStudio';
import { ToolPermissionGuard } from '../../ai-runtime/security/toolPermissionGuard';
import { NativeBridgeClient } from '../../native-bridge/client/nativeBridgeClient';
import { LocalVisionProvider } from '../../vision/providers/localVisionProvider';
import { WorkflowBuilder } from '../studio/workflowBuilder';

export class WorkflowDryRunEngine {
  private permissionGuard = new ToolPermissionGuard();
  private nativeClient = new NativeBridgeClient();
  private visionProvider = new LocalVisionProvider();

  async performDryRun(workflow: WorkflowDefinition, variableInputs: Record<string, any> = {}): Promise<DryRunResult> {
    const stepAssessments: DryRunStepAssessment[] = [];
    const missingDependencies: string[] = [];
    let totalRiskScore = 0;
    let overallStatus: DryRunResult['overallStatus'] = 'READY';

    // 1. Check Native Bridge & Local VLM Availability
    const nativeConnected = await this.nativeClient.checkConnection();
    if (!nativeConnected) {
      missingDependencies.push('Native Windows Bridge (http://127.0.0.1:3001)');
    }

    const visionAvailable = await this.visionProvider.isAvailable();
    if (!visionAvailable) {
      missingDependencies.push('Local Ollama Vision Model (llava:latest)');
    }

    // 2. Validate DAG Structure
    const builder = WorkflowBuilder.fromDefinition(workflow);
    const graphVal = builder.validateWorkflow();
    if (!graphVal.valid) {
      overallStatus = 'BLOCKED';
    }

    const orderedNodes = builder.getTopologicalOrder();

    // 3. Step-by-Step Pre-Flight Assessment
    for (const node of orderedNodes) {
      const issues: string[] = [];
      let stepStatus: DryRunStepAssessment['status'] = 'READY';

      if (node.disabled) {
        stepAssessments.push({
          nodeId: node.id,
          nodeLabel: node.label,
          status: 'READY',
          riskLevel: node.riskLevel,
          targetReadiness: 'Disabled Step',
          permissionStatus: 'Skipped',
          issues: ['Step is disabled in workflow configuration.'],
        });
        continue;
      }

      // Risk score aggregation
      if (node.riskLevel === 'CRITICAL') totalRiskScore += 10;
      else if (node.riskLevel === 'HIGH') totalRiskScore += 5;
      else if (node.riskLevel === 'MEDIUM') totalRiskScore += 2;
      else totalRiskScore += 1;

      // Tool Permission check
      const permRes = this.permissionGuard.evaluateToolPermission({
        callId: `dryrun-${node.id}`,
        toolName: node.toolName || 'system_action',
        arguments: node.arguments || {},
        riskLevel: node.riskLevel,
      });

      if (!permRes.permitted) {
        stepStatus = 'BLOCKED';
        issues.push(`Permission denied: ${permRes.reason}`);
      } else if (permRes.requiresApproval || node.requiresApproval || node.riskLevel === 'HIGH' || node.riskLevel === 'CRITICAL') {
        stepStatus = 'REQUIRES_APPROVAL';
        issues.push('Requires explicit user authorization before execution.');
      }

      // Target readiness check
      let targetReadiness = 'Ready';
      if (node.type === 'VISION_GROUNDING' && !visionAvailable) {
        targetReadiness = 'Vision Unavailable';
        if (stepStatus !== 'BLOCKED') stepStatus = 'WARNING';
        issues.push('Local Vision VLM is unavailable for visual target grounding.');
      } else if (node.type === 'BROWSER_ACTION') {
        targetReadiness = 'Browser Target Configured';
      }

      if (stepStatus === 'BLOCKED') overallStatus = 'BLOCKED';
      else if (stepStatus === 'REQUIRES_APPROVAL' && overallStatus !== 'BLOCKED') overallStatus = 'REQUIRES_APPROVAL';
      else if (stepStatus === 'WARNING' && overallStatus === 'READY') overallStatus = 'WARNING';

      stepAssessments.push({
        nodeId: node.id,
        nodeLabel: node.label,
        status: stepStatus,
        riskLevel: node.riskLevel,
        resolvedTool: node.toolName || 'custom_action',
        targetReadiness,
        permissionStatus: permRes.requiresApproval ? 'Requires Approval' : 'Authorized',
        issues,
      });
    }

    return {
      workflowId: workflow.id,
      valid: graphVal.valid && overallStatus !== 'BLOCKED',
      overallStatus,
      stepAssessments,
      missingDependencies,
      totalRiskScore,
      summary: `Dry-Run completed with status: ${overallStatus} (${stepAssessments.length} steps evaluated, ${missingDependencies.length} missing dependencies)`,
    };
  }
}
