import { ExecutionRequest } from '../types/executionRequest';
import { AuthorizationContext } from '../types/executionContext';

export class PolicyEngine {
  evaluate(request: ExecutionRequest, context?: AuthorizationContext): { allowed: boolean; reason: string } {
    // Critical & High risk actions require explicit approval or admin role
    if (request.riskLevel === 'CRITICAL' && (!context || context.role !== 'ADMINISTRATOR')) {
      return { allowed: false, reason: 'CRITICAL risk actions require Administrator authority.' };
    }

    if (request.policy === 'DENY') {
      return { allowed: false, reason: 'Action denied by execution policy.' };
    }

    return { allowed: true, reason: 'Authorized by execution policy.' };
  }
}
