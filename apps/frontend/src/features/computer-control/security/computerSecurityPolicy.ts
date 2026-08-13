import { ComputerRequest } from '../types/computerControl';

export class ComputerSecurityPolicy {
  evaluateRequest(request: ComputerRequest): { allowed: boolean; requiresApproval: boolean; reason: string } {
    if (request.riskLevel === 'CRITICAL' || request.riskLevel === 'HIGH') {
      if (!request.isApproved) {
        return {
          allowed: false,
          requiresApproval: true,
          reason: `Computer operation "${request.action}" at risk level ${request.riskLevel} requires explicit user approval.`,
        };
      }
    }

    return {
      allowed: true,
      requiresApproval: false,
      reason: 'Computer control request approved by policy guard.',
    };
  }
}
