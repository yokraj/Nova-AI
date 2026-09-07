import { ScheduledTask, TaskStatus } from '../types/scheduledTask';
import { promptInjectionGuard } from '../../ai-runtime/security/promptInjectionGuard';

export interface SecurityPolicyResult {
  allowed: boolean;
  status: TaskStatus;
  requiresApproval: boolean;
  reason: string;
  sanitizedGoal?: string;
}

export class BackgroundTaskPolicy {
  evaluateTaskSecurity(task: ScheduledTask): SecurityPolicyResult {
    // 1. Check prompt injection in goal and name
    const nameSanitize = promptInjectionGuard.assessAndSanitize(task.name);
    const goalSanitize = promptInjectionGuard.assessAndSanitize(task.goal);

    if (!nameSanitize.safe || !goalSanitize.safe) {
      const patterns = (nameSanitize.detectedPatterns || []).concat(goalSanitize.detectedPatterns || []);
      return {
        allowed: false,
        status: 'CANCELLED',
        requiresApproval: false,
        reason: `Task contains untrusted prompt injection patterns: ${patterns.join(', ')}`,
      };
    }

    const sanitizedGoal = goalSanitize.sanitizedText;
    const lowerGoal = sanitizedGoal.toLowerCase();

    // 2. Risk Level Evaluation
    const isCritical = lowerGoal.includes('shutdown') || lowerGoal.includes('format-volume');
    const isHigh = lowerGoal.includes('delete_file') || lowerGoal.includes('terminate_process') || lowerGoal.includes('power_') || lowerGoal.includes('rm -rf');
    const isMedium = lowerGoal.includes('write_file') || lowerGoal.includes('type_text') || lowerGoal.includes('wifi_set');

    if (isCritical || isHigh) {
      return {
        allowed: true,
        status: 'WAITING_APPROVAL',
        requiresApproval: true,
        reason: `High risk background task "${task.name}" requires explicit user approval before execution.`,
        sanitizedGoal,
      };
    }

    if (isMedium && !task.trustedPolicy) {
      return {
        allowed: true,
        status: 'WAITING_APPROVAL',
        requiresApproval: true,
        reason: `Medium risk task "${task.name}" requires explicit user approval or trusted schedule policy.`,
        sanitizedGoal,
      };
    }

    return {
      allowed: true,
      status: 'QUEUED',
      requiresApproval: false,
      reason: `Task "${task.name}" passed security policy evaluation.`,
      sanitizedGoal,
    };
  }
}
