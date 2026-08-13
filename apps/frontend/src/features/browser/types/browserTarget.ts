export interface BrowserTarget {
  rawTarget: string;
  url?: string;
  domain?: string;
  tabId?: string;
  selector?: string;
  elementSelector?: string;
  elementText?: string;
  elementType?: 'button' | 'link' | 'input' | 'select' | 'text' | 'form' | 'unknown';
}
