import { StructuredToolCall } from '../types/toolCall';

export class ToolPermissionGuard {
  evaluateToolPermission(toolCall: StructuredToolCall): { permitted: boolean; requiresApproval: boolean; reason: string } {
    const risk = toolCall.riskLevel || 'LOW';

    if (risk === 'HIGH' || risk === 'CRITICAL') {
      return {
        permitted: true,
        requiresApproval: true,
        reason: `High risk tool "${toolCall.toolName}" requires explicit user approval.`,
      };
    }

    return {
      permitted: true,
      requiresApproval: false,
      reason: `Tool "${toolCall.toolName}" authorized under ${risk} risk policy.`,
    };
  }
}
