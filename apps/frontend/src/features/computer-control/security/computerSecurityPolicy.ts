import { ComputerRequest } from '../types/computerControl';

export class ComputerSecurityPolicy {
  evaluateRequest(request: ComputerRequest): { allowed: boolean; requiresApproval: boolean; reason: string } {
    // 1. High/Critical Risk Actions Always Require Approval
    if (request.riskLevel === 'CRITICAL' || request.riskLevel === 'HIGH') {
      if (!request.isApproved) {
        return {
          allowed: false,
          requiresApproval: true,
          reason: `Computer operation "${request.action}" at risk level ${request.riskLevel} requires explicit user approval.`,
        };
      }
    }

    // 2. Target Confidence Policy Thresholds
    if (request.target && request.target.confidence !== undefined) {
      const conf = request.target.confidence;

      if (conf < 0.50) {
        return {
          allowed: false,
          requiresApproval: false,
          reason: `Target confidence ${conf.toFixed(2)} is below critical minimum safe threshold (0.50). Action BLOCKED.`,
        };
      }

      if (conf < 0.75 && (request.action === 'CLICK' || request.action === 'DOUBLE_CLICK' || request.action === 'RIGHT_CLICK')) {
        return {
          allowed: false,
          requiresApproval: true,
          reason: `Target confidence ${conf.toFixed(2)} is below 0.75 threshold. Blind click prevented. Re-observation or confirmation required.`,
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

