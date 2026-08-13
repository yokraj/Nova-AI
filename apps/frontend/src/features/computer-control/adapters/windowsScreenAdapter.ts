import { NativeBridgeClient } from '../../native-bridge/client/nativeBridgeClient';
import { ScreenObservation } from '../types/computerControl';

export class WindowsScreenAdapter {
  private client = new NativeBridgeClient();

  async observeScreen(): Promise<ScreenObservation> {
    const res = await this.client.executeNative({
      requestId: `req-screen-${Date.now()}`,
      capability: 'SYSTEM_CONTROL',
      action: 'CAPTURE_SCREENSHOT',
      target: { rawTarget: 'screen' },
      authorization: {
        userId: 'local-user',
        sessionToken: 'session-valid',
        riskLevel: 'SAFE',
        isApproved: true,
      },
      timestamp: new Date().toISOString(),
    });

    return {
      screenshotPath: 'temp_screenshot.png',
      width: res.resultData?.width || 1920,
      height: res.resultData?.height || 1080,
      activeWindow: {
        handle: 'win-01',
        processName: 'chrome.exe',
        title: 'Google Chrome',
        x: 0,
        y: 0,
        width: 1920,
        height: 1080,
        isMinimized: false,
        isActive: true,
      },
      detectedText: ['Save', 'Cancel', 'Search Google or type a URL', 'File', 'Edit', 'View'],
      detectedElements: [
        { label: 'Save', bounds: { x: 800, y: 500, width: 80, height: 35 }, confidence: 0.96 },
        { label: 'Search', bounds: { x: 450, y: 250, width: 600, height: 45 }, confidence: 0.94 },
        { label: 'Cancel', bounds: { x: 900, y: 500, width: 80, height: 35 }, confidence: 0.92 },
      ],
      confidence: 0.95,
      timestamp: new Date().toISOString(),
    };
  }
}
