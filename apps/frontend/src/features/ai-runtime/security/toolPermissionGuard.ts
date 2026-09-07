import { StructuredToolCall } from '../types/toolCall';

export interface PermissionAssessment {
  permitted: boolean;
  requiresApproval: boolean;
  requiresElevation?: boolean;
  reason: string;
}

export class ToolPermissionGuard {
  private elevatedTools = ['windows_elevated_launch', 'system_elevated_process', 'regedit', 'mmc', 'taskmgr'];

  evaluateToolPermission(toolCall: StructuredToolCall): PermissionAssessment {
    const risk = toolCall.riskLevel || 'LOW';
    const lowerName = (toolCall.toolName || '').toLowerCase();
    const isElevated = this.elevatedTools.some((t) => lowerName.includes(t)) || (toolCall as any).requiresElevation === true;

    if (isElevated) {
      return {
        permitted: true,
        requiresApproval: true,
        requiresElevation: true,
        reason: 'Administrator permission is required for this action.',
      };
    }

    if (risk === 'HIGH' || risk === 'CRITICAL') {
      return {
        permitted: true,
        requiresApproval: true,
        requiresElevation: false,
        reason: `High risk tool "${toolCall.toolName}" requires explicit user approval.`,
      };
    }

    return {
      permitted: true,
      requiresApproval: false,
      requiresElevation: false,
      reason: `Tool "${toolCall.toolName}" authorized under ${risk} risk policy.`,
    };
  }
}
