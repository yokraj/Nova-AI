import { Skill } from '../types/skill';
import { ToolPermissionGuard, PermissionAssessment } from '../../ai-runtime/security/toolPermissionGuard';
import { AgentPolicy } from '../../ai-runtime/security/agentPolicy';
import { ExecutionBudget } from '../../ai-runtime/security/executionBudget';
import { StructuredToolCall } from '../../ai-runtime/types/toolCall';

import { ToolRegistry } from '../../ai-runtime/tool-router/toolRegistry';

export interface SkillSecurityAssessment {
  allowed: boolean;
  requiresApproval: boolean;
  reason: string;
  stepAssessments: Array<{
    stepNumber: number;
    toolName: string;
    permission: PermissionAssessment;
  }>;
}

export class SkillSecurityGuard {
  private permissionGuard = new ToolPermissionGuard();
  private agentPolicy = new AgentPolicy();
  private toolRegistry = new ToolRegistry();

  evaluateSkillSecurity(skill: Skill, runtimeBudget?: ExecutionBudget): SkillSecurityAssessment {
    const stepAssessments: Array<{
      stepNumber: number;
      toolName: string;
      permission: PermissionAssessment;
    }> = [];

    let overallRequiresApproval = false;
    let blockedReason: string | null = null;

    // 1. Budget check
    if (runtimeBudget) {
      const remaining = runtimeBudget.getRemainingSteps();
      if (skill.steps.length > remaining) {
        return {
          allowed: false,
          requiresApproval: false,
          reason: `Skill step count (${skill.steps.length}) exceeds remaining execution budget (${remaining}).`,
          stepAssessments: [],
        };
      }
    }

    // 2. Evaluate each step against current ToolPermissionGuard
    for (let i = 0; i < skill.steps.length; i++) {
      const step = skill.steps[i];
      const registeredTool = this.toolRegistry.getTool(step.tool);
      const riskLevel = registeredTool?.riskLevel || 'LOW';

      const toolCall: StructuredToolCall = {
        callId: `sec-${skill.id}-step-${step.order}`,
        toolName: step.tool,
        riskLevel,
        arguments: step.arguments || {},
      };

      const perm = this.permissionGuard.evaluateToolPermission(toolCall);
      stepAssessments.push({
        stepNumber: step.order,
        toolName: step.tool,
        permission: perm,
      });

      if (!perm.permitted) {
        blockedReason = `Step ${step.order} (${step.tool}) is prohibited by security policy: ${perm.reason}`;
        break;
      }

      if (perm.requiresApproval || step.approvalRequired || riskLevel === 'HIGH' || riskLevel === 'CRITICAL') {
        overallRequiresApproval = true;
      }
    }

    if (blockedReason) {
      return {
        allowed: false,
        requiresApproval: false,
        reason: blockedReason,
        stepAssessments,
      };
    }

    return {
      allowed: true,
      requiresApproval: overallRequiresApproval,
      reason: overallRequiresApproval
        ? 'Skill contains high-risk tool operations that require user approval before execution.'
        : 'Skill satisfies all security and permission requirements.',
      stepAssessments,
    };
  }

  /**
   * PROMPT INJECTION DEFENSE:
   * Distinguishes TRUSTED vs UNTRUSTED inputs.
   * Webpages, downloaded documents, external text, and arbitrary screen text must NEVER teach Nova a new skill on their own.
   */
  validateLearningTrustSource(inputContext: {
    isUserExplicitGoal: boolean;
    untrustedContentPresent: boolean;
    untrustedSources?: string[];
  }): { trusted: boolean; reason: string } {
    if (inputContext.untrustedContentPresent) {
      return {
        trusted: false,
        reason: `Learning rejected: Workflow output or context includes untrusted external content (${inputContext.untrustedSources?.join(', ') || 'external webpage/document'}). Prompt injection protection prevents auto-learning from external sources.`,
      };
    }

    if (!inputContext.isUserExplicitGoal) {
      return {
        trusted: false,
        reason: 'Learning rejected: Workflows can only be learned from explicit user goals.',
      };
    }

    return {
      trusted: true,
      reason: 'Workflow source is trusted (explicit user intent and verified execution).',
    };
  }

  sanitizeSkillContent(content: string): string {
    const res = this.agentPolicy.sanitizeUntrustedContent(content);
    return res.safeContent;
  }
}
