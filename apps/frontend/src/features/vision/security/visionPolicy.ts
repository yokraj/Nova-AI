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
}
