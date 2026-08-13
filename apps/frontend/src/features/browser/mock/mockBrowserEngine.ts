import { BrowserTab } from '../types/browserTab';
import { BrowserResult } from '../types/browserResult';
import { BrowserRequest } from '../types/browserRequest';

export class MockBrowserEngine {
  private tabs: BrowserTab[] = [
    {
      id: 'tab-1',
      browserId: 'browser-main',
      title: 'Google',
      url: 'https://www.google.com',
      domain: 'google.com',
      status: 'READY',
      active: true,
    },
    {
      id: 'tab-2',
      browserId: 'browser-main',
      title: 'Nova AI - GitHub',
      url: 'https://github.com/yokraj/Nova-AI',
      domain: 'github.com',
      status: 'READY',
      active: false,
    },
  ];

  getActiveTab(): BrowserTab {
    return this.tabs.find((t) => t.active) || this.tabs[0];
  }

  async processRequest(request: BrowserRequest): Promise<BrowserResult> {
    const started = Date.now();
    const url = request.target.url || 'https://www.google.com';

    return {
      requestId: request.requestId,
      success: true,
      status: 'COMPLETED',
      action: request.action,
      targetUrl: url,
      verification: 'URL_MATCHED',
      message: `Browser action "${request.action}" completed for ${url}.`,
      durationSeconds: (Date.now() - started) / 1000 + 0.3,
      extractedText: `Mock Web Page Text for ${url}. Nova AI Browser Engine active.`,
      extractedLinks: [
        { text: 'Documentation', url: `${url}/docs` },
        { text: 'Features', url: `${url}/features` },
      ],
      isSimulated: true,
      timestamp: new Date().toISOString(),
    };
  }
}
