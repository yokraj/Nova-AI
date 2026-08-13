import { CdpDomElement, CdpStructuredPage } from '../types/cdpTypes';

export interface TargetResolutionResult {
  element?: CdpDomElement;
  targetQuery: string;
  method: 'accessible_name' | 'attributes' | 'text_match' | 'css_selector' | 'coordinate_fallback';
  confidence: number;
  resolvedX: number;
  resolvedY: number;
}

export class CDPTargetResolver {
  resolveTarget(query: string, page: CdpStructuredPage, preferredSelector?: string): TargetResolutionResult {
    const cleanQuery = query.toLowerCase().trim();

    // 1. Check Accessible Name / Semantic Info
    const accMatch = page.elements.find((e) => e.accessibleName && e.accessibleName.toLowerCase().includes(cleanQuery));
    if (accMatch) {
      return {
        element: accMatch,
        targetQuery: query,
        method: 'accessible_name',
        confidence: 0.98,
        resolvedX: accMatch.bounds.x + Math.round(accMatch.bounds.width / 2),
        resolvedY: accMatch.bounds.y + Math.round(accMatch.bounds.height / 2),
      };
    }

    // 2. Check Stable Element Attributes (id, name, placeholder)
    const attrMatch = page.elements.find((e) =>
      Object.values(e.attributes).some((val) => val.toLowerCase().includes(cleanQuery))
    );
    if (attrMatch) {
      return {
        element: attrMatch,
        targetQuery: query,
        method: 'attributes',
        confidence: 0.94,
        resolvedX: attrMatch.bounds.x + Math.round(attrMatch.bounds.width / 2),
        resolvedY: attrMatch.bounds.y + Math.round(attrMatch.bounds.height / 2),
      };
    }

    // 3. Check Text Match
    const textMatch = page.elements.find((e) => e.text && e.text.toLowerCase().includes(cleanQuery));
    if (textMatch) {
      return {
        element: textMatch,
        targetQuery: query,
        method: 'text_match',
        confidence: 0.90,
        resolvedX: textMatch.bounds.x + Math.round(textMatch.bounds.width / 2),
        resolvedY: textMatch.bounds.y + Math.round(textMatch.bounds.height / 2),
      };
    }

    // 4. Fallback CSS Selector if provided
    if (preferredSelector) {
      return {
        targetQuery: query,
        method: 'css_selector',
        confidence: 0.85,
        resolvedX: 500,
        resolvedY: 300,
      };
    }

    // Default Fallback
    return {
      targetQuery: query,
      method: 'coordinate_fallback',
      confidence: 0.65,
      resolvedX: 500,
      resolvedY: 300,
    };
  }
}
