import { CdpClient } from './cdpClient';
import { CdpTargetTab } from '../types/cdpTypes';

export class CdpConnectionManager {
  private client = new CdpClient();
  private isConnected = false;
  private activePort = 9222;
  private activeTabId?: string;

  async checkHealth(): Promise<{ isHealthy: boolean; port: number; message: string }> {
    try {
      const res = await this.client.connect(this.activePort);
      this.isConnected = res.success;
      return {
        isHealthy: res.success,
        port: this.activePort,
        message: res.message,
      };
    } catch (err: any) {
      this.isConnected = false;
      return {
        isHealthy: false,
        port: this.activePort,
        message: `CDP health check failed: ${err?.message}`,
      };
    }
  }

  async connect(port = 9222): Promise<boolean> {
    this.activePort = port;
    const health = await this.checkHealth();
    return health.isHealthy;
  }

  async getActiveTabs(): Promise<CdpTargetTab[]> {
    const res = await this.client.listTabs();
    return res.tabs;
  }

  setActiveTab(tabId: string): void {
    this.activeTabId = tabId;
  }

  getActiveTabId(): string | undefined {
    return this.activeTabId;
  }

  disconnect(): void {
    this.isConnected = false;
  }
}
