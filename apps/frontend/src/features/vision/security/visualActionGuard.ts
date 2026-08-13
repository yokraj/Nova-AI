import { VisionTarget } from '../types/visionTarget';

export class VisualActionGuard {
  private minConfidenceThreshold = 0.85;

  validateVisualAction(actionName: string, target?: VisionTarget | null): { safe: boolean; reason?: string } {
    if (actionName === 'CLICK_TARGET' || actionName === 'TYPE_IN_TARGET' || actionName === 'DOUBLE_CLICK_TARGET') {
      if (!target) {
        return { safe: false, reason: `Visual action "${actionName}" requires a validated target.` };
      }
      if (target.confidence < this.minConfidenceThreshold) {
        return {
          safe: false,
          reason: `Target confidence (${(target.confidence * 100).toFixed(0)}%) is below safety threshold (${(this.minConfidenceThreshold * 100).toFixed(0)}%). Uncontrolled coordinate clicking is forbidden.`,
        };
      }
    }
    return { safe: true };
  }
}
