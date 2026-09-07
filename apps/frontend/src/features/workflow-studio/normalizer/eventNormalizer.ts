import { SemanticTarget, TargetResolutionStrategy } from '../types/workflowStudio';

export class EventNormalizer {
  normalizeEventTarget(rawEvent: {
    toolName: string;
    arguments: Record<string, any>;
    activeApp?: string;
    windowTitle?: string;
    accessibilityRole?: string;
    accessibilityName?: string;
    domSelector?: string;
    visualText?: string;
    x?: number;
    y?: number;
  }): SemanticTarget {
    let primaryStrategy: TargetResolutionStrategy = 'COORDINATES_FALLBACK';
    let confidence = 0.5;

    if (rawEvent.accessibilityRole && rawEvent.accessibilityName) {
      primaryStrategy = 'ACCESSIBILITY';
      confidence = 0.98;
    } else if (rawEvent.domSelector) {
      primaryStrategy = 'DOM_SELECTOR';
      confidence = 0.95;
    } else if (rawEvent.visualText) {
      primaryStrategy = 'VISUAL_TARGET';
      confidence = 0.90;
    } else if (rawEvent.activeApp || rawEvent.windowTitle) {
      primaryStrategy = 'WINDOW_CONTEXT';
      confidence = 0.80;
    }

    const coordinatesFallback =
      rawEvent.x !== undefined && rawEvent.y !== undefined
        ? { x: rawEvent.x, y: rawEvent.y }
        : rawEvent.arguments?.x !== undefined && rawEvent.arguments?.y !== undefined
        ? { x: rawEvent.arguments.x, y: rawEvent.arguments.y }
        : undefined;

    return {
      strategy: primaryStrategy,
      accessibilityRole: rawEvent.accessibilityRole,
      accessibilityName: rawEvent.accessibilityName,
      domSelector: rawEvent.domSelector || rawEvent.arguments?.selector,
      visualText: rawEvent.visualText || rawEvent.arguments?.text || rawEvent.accessibilityName,
      visualLabel: rawEvent.accessibilityName || rawEvent.visualText,
      activeApp: rawEvent.activeApp || rawEvent.arguments?.applicationName,
      windowTitle: rawEvent.windowTitle,
      coordinatesFallback,
      confidence,
    };
  }
}
