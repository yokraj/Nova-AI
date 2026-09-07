import { VisionActionType } from '../types/visionAction';
import { VisionRiskLevel, VisionPermission } from '../types/visionPermission';

export class VisionPolicy {
  getRiskLevel(action: VisionActionType): VisionRiskLevel {
    switch (action) {
      case 'ANALYZE_IMAGE':
      case 'ANALYZE_PDF':
      case 'READ_TEXT':
      case 'EXTRACT_TEXT':
      case 'DESCRIBE_SCREEN':
      case 'DETECT_ERROR':
      case 'COMPARE_IMAGES':
        return 'SAFE';

      case 'OBSERVE_SCREEN':
      case 'CAPTURE_SCREEN':
      case 'FIND_TARGET':
      case 'HIGHLIGHT_TARGET':
      case 'LOCATE_APPLICATION':
      case 'LOCATE_WINDOW':
      case 'SCROLL_TO_TARGET':
        return 'LOW';

      case 'CLICK_TARGET':
      case 'DOUBLE_CLICK_TARGET':
      case 'TYPE_IN_TARGET':
      case 'OPEN_TARGET':
      case 'SELECT_TARGET':
        return 'MEDIUM';

      default:
        return 'HIGH';
    }
  }

  evaluatePermission(action: VisionActionType): VisionPermission {
    const riskLevel = this.getRiskLevel(action);
    const requiresApproval = riskLevel === 'HIGH' || riskLevel === 'CRITICAL';

    return {
      screenAccess: 'GRANTED',
      cameraAccess: 'NOT_REQUESTED',
      riskLevel,
      requiresApproval,
      reason: requiresApproval
        ? `Visual action "${action}" requires explicit user authorization.`
        : `Visual action "${action}" authorized.`,
    };
  }

  evaluateConfidence(confidence: number): {
    status: 'SAFE_TO_ACT' | 'RE_OBSERVE' | 'NEEDS_CLARIFICATION' | 'BLOCKED';
    actionable: boolean;
    reason: string;
  } {
    if (confidence >= 0.9) {
      return { status: 'SAFE_TO_ACT', actionable: true, reason: 'High visual target confidence (>= 0.90).' };
    } else if (confidence >= 0.75) {
      return { status: 'RE_OBSERVE', actionable: false, reason: 'Moderate visual confidence (0.75 - 0.89); re-observation required.' };
    } else if (confidence >= 0.5) {
      return { status: 'NEEDS_CLARIFICATION', actionable: false, reason: 'Low visual confidence (0.50 - 0.74); action blocked without clarification.' };
    } else {
      return { status: 'BLOCKED', actionable: false, reason: 'Very low target confidence (< 0.50); visual action strictly BLOCKED.' };
    }
  }
}
