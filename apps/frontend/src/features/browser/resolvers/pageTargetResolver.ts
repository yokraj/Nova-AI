import { BrowserTarget } from '../types/browserTarget';

export class PageTargetResolver {
  resolveElementTarget(elementDescription: string): Partial<BrowserTarget> {
    const clean = elementDescription.toLowerCase();
    let elementType: 'button' | 'link' | 'input' | 'select' | 'text' | 'form' | 'unknown' = 'unknown';

    if (clean.includes('link')) elementType = 'link';
    else if (clean.includes('button')) elementType = 'button';
    else if (clean.includes('search') || clean.includes('input') || clean.includes('field')) elementType = 'input';
    else if (clean.includes('select') || clean.includes('option')) elementType = 'select';
    else if (clean.includes('form') || clean.includes('submit')) elementType = 'form';

    return {
      elementText: elementDescription,
      elementType,
      elementSelector: `[data-nova-target="${clean.replace(/\s+/g, '-')}"]`,
    };
  }
}
