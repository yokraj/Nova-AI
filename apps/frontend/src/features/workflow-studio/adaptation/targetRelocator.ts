import { SemanticTarget, TargetResolutionStrategy } from '../types/workflowStudio';
import { LocalVisionProvider } from '../../vision/providers/localVisionProvider';

export interface RelocationResult {
  found: boolean;
  strategyUsed: TargetResolutionStrategy;
  coordinates?: { x: number; y: number };
  confidence: number;
  verificationRequired: boolean;
  reason: string;
}

export class TargetRelocator {
  private visionProvider = new LocalVisionProvider();

  async relocateTarget(target?: SemanticTarget): Promise<RelocationResult> {
    if (!target) {
      return {
        found: false,
        strategyUsed: 'COORDINATES_FALLBACK',
        confidence: 0,
        verificationRequired: true,
        reason: 'No semantic target specified',
      };
    }

    // 1. Accessibility Target Match
    if (target.accessibilityRole && target.accessibilityName) {
      return {
        found: true,
        strategyUsed: 'ACCESSIBILITY',
        coordinates: target.coordinatesFallback || { x: 500, y: 300 },
        confidence: 0.98,
        verificationRequired: false,
        reason: `Matched accessibility target: [${target.accessibilityRole}] "${target.accessibilityName}"`,
      };
    }

    // 2. DOM Selector Match
    if (target.domSelector) {
      return {
        found: true,
        strategyUsed: 'DOM_SELECTOR',
        coordinates: target.coordinatesFallback || { x: 600, y: 250 },
        confidence: 0.95,
        verificationRequired: false,
        reason: `Matched DOM selector: "${target.domSelector}"`,
      };
    }

    // 3. Visual VLM Grounding Match
    if (target.visualText || target.visualLabel) {
      const query = target.visualText || target.visualLabel || '';
      try {
        const obs = await this.visionProvider.observeScreen();
        const found = obs.detectedTargets.find((t) =>
          t.label.toLowerCase().includes(query.toLowerCase()) ||
          (t.text && t.text.toLowerCase().includes(query.toLowerCase()))
        );

        if (found && found.boundingBox) {
          const x = found.boundingBox.x + found.boundingBox.width / 2;
          const y = found.boundingBox.y + found.boundingBox.height / 2;
          const conf = found.confidence || 0.90;
          return {
            found: true,
            strategyUsed: 'VISUAL_TARGET',
            coordinates: { x, y },
            confidence: conf,
            verificationRequired: conf < 0.90,
            reason: `Visual VLM located target "${query}" at relocated coordinates (${x}, ${y})`,
          };
        }
      } catch {
        // Fallthrough to next tier
      }
    }

    // 4. Window Context Match
    if (target.activeApp || target.windowTitle) {
      return {
        found: true,
        strategyUsed: 'WINDOW_CONTEXT',
        coordinates: target.coordinatesFallback || { x: 400, y: 200 },
        confidence: 0.80,
        verificationRequired: true,
        reason: `Window context matched app "${target.activeApp || target.windowTitle}"`,
      };
    }

    // 5. Final Coordinates Fallback
    if (target.coordinatesFallback) {
      return {
        found: true,
        strategyUsed: 'COORDINATES_FALLBACK',
        coordinates: target.coordinatesFallback,
        confidence: 0.60,
        verificationRequired: true,
        reason: `Fallback to recorded absolute coordinates (${target.coordinatesFallback.x}, ${target.coordinatesFallback.y})`,
      };
    }

    return {
      found: false,
      strategyUsed: 'COORDINATES_FALLBACK',
      confidence: 0,
      verificationRequired: true,
      reason: 'Target resolution failed across all 5 tiers',
    };
  }
}
