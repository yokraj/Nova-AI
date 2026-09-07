import { ComputerTarget, ScreenObservation } from '../types/computerControl';

export interface ResolvedTargetResult {
  resolvedX: number;
  resolvedY: number;
  confidence: number;
  label: string;
  targetType: string;
  source: 'ACCESSIBILITY' | 'APPLICATION_API' | 'BROWSER_CDP' | 'WINDOW_CONTEXT' | 'VISION' | 'MOUSE_KEYBOARD_FALLBACK' | 'COORDINATES_FALLBACK';
  windowContext?: string;
  timestamp: string;
}

export class UITargetResolver {
  resolveTarget(
    target: ComputerTarget,
    observation: ScreenObservation
  ): ResolvedTargetResult {
    const query = (target.query || '').toLowerCase();
    const activeWinTitle = observation.activeWindow?.title || 'Foreground Window';
    const timestamp = new Date().toISOString();

    // Priority 1: Check Detected UI Elements (Vision / Grounding)
    const elementMatch = observation.detectedElements.find((e) => e.label.toLowerCase().includes(query));
    if (elementMatch) {
      return {
        resolvedX: elementMatch.bounds.x + Math.round(elementMatch.bounds.width / 2),
        resolvedY: elementMatch.bounds.y + Math.round(elementMatch.bounds.height / 2),
        confidence: elementMatch.confidence,
        label: elementMatch.label,
        targetType: target.targetType || 'BUTTON',
        source: 'VISION',
        windowContext: activeWinTitle,
        timestamp,
      };
    }

    // Priority 2: Check Detected Text Regions
    const textMatch = observation.detectedText.find((t) => t.toLowerCase().includes(query));
    if (textMatch) {
      return {
        resolvedX: Math.round(observation.width * 0.45),
        resolvedY: Math.round(observation.height * 0.35),
        confidence: 0.88,
        label: textMatch,
        targetType: 'TEXT',
        source: 'VISION',
        windowContext: activeWinTitle,
        timestamp,
      };
    }

    // Priority 3: Window Context Target
    if (target.targetType === 'WINDOW' || target.windowTitle) {
      return {
        resolvedX: Math.round(observation.width / 2),
        resolvedY: Math.round(observation.height / 2),
        confidence: 0.90,
        label: target.windowTitle || target.query,
        targetType: 'WINDOW',
        source: 'WINDOW_CONTEXT',
        windowContext: activeWinTitle,
        timestamp,
      };
    }

    // Priority 4: Explicit Coordinates Target
    if (target.x !== undefined && target.y !== undefined) {
      return {
        resolvedX: target.x,
        resolvedY: target.y,
        confidence: target.confidence !== undefined ? target.confidence : 0.85,
        label: `Coordinate (${target.x}, ${target.y})`,
        targetType: 'COORDINATE',
        source: 'COORDINATES_FALLBACK',
        windowContext: activeWinTitle,
        timestamp,
      };
    }

    // Priority 5: Default Fallback
    return {
      resolvedX: Math.round(observation.width / 2),
      resolvedY: Math.round(observation.height / 2),
      confidence: 0.70,
      label: query || 'Default Target',
      targetType: target.targetType || 'COORDINATE',
      source: 'MOUSE_KEYBOARD_FALLBACK',
      windowContext: activeWinTitle,
      timestamp,
    };
  }
}

