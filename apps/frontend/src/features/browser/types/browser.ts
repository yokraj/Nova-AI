export type BrowserStatus = 'IDLE' | 'OPEN' | 'NAVIGATING' | 'BUSY' | 'CLOSED' | 'ERROR';

export interface BrowserInstance {
  id: string;
  name: string;
  executable?: string;
  version?: string;
  status: BrowserStatus;
  capabilities: string[];
  trusted: boolean;
}
