import { BrowserRequest } from '../types/browserRequest';
import { BrowserResult } from '../types/browserResult';

export interface BrowserAdapter {
  adapterName: string;
  canHandle(request: BrowserRequest): boolean;
  execute(request: BrowserRequest): Promise<BrowserResult>;
  verify(request: BrowserRequest): Promise<boolean>;
}
