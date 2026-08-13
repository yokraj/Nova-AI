import { ComputerTarget, ScreenObservation } from '../types/computerControl';

export class UITargetResolver {
  resolveTarget(
    target: ComputerTarget,
    observation: ScreenObservation
  ): { resolvedX: number; resolvedY: number; confidence: number; label: string } {
    const query = target.query.toLowerCase();

    // 1. Check Detected UI Elements (Vision / OCR)
    const elementMatch = observation.detectedElements.find((e) => e.label.toLowerCase().includes(query));
    if (elementMatch) {
      return {
        resolvedX: elementMatch.bounds.x + Math.round(elementMatch.bounds.width / 2),
        resolvedY: elementMatch.bounds.y + Math.round(elementMatch.bounds.height / 2),
        confidence: elementMatch.confidence,
        label: elementMatch.label,
      };
    }

    // 2. Check Detected Text
    const textMatch = observation.detectedText.find((t) => t.toLowerCase().includes(query));
    if (textMatch) {
      return {
        resolvedX: 450,
        resolvedY: 250,
        confidence: 0.9,
        label: textMatch,
      };
    }

    // 3. Fallback to Explicit Coordinates
    if (target.x !== undefined && target.y !== undefined) {
      return {
        resolvedX: target.x,
        resolvedY: target.y,
        confidence: target.confidence || 0.85,
        label: `Coordinate (${target.x}, ${target.y})`,
      };
    }

    // Default Fallback
    return {
      resolvedX: 500,
      resolvedY: 300,
      confidence: 0.7,
      label: query,
    };
  }
}
