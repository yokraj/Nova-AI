import { NativeBridgeRequest } from '../types/nativeBridgeRequest';
import { NativeBridgeResponse } from '../types/nativeBridgeResponse';

export class NativeBridgeClient {
  private bridgeUrl = 'http://127.0.0.1:3001/api/v1/native-execute';

  getCurrentOrigin(): string {
    if (typeof window !== 'undefined' && window.location && window.location.origin) {
      return window.location.origin;
    }
    return 'http://127.0.0.1:5173';
  }

  async healthCheck(): Promise<{ healthy: boolean; service?: string }> {
    try {
      const res = await fetch('http://127.0.0.1:3001/health', {
        method: 'GET',
      });
      if (res.ok) {
        const data = await res.json();
        return { healthy: data.status === 'healthy', service: data.service };
      }
      return { healthy: false };
    } catch {
      return { healthy: false };
    }
  }

  async executeNative(request: NativeBridgeRequest): Promise<NativeBridgeResponse> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    try {
      const response = await fetch(this.bridgeUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${request.authorization.sessionToken}`,
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        return {
          requestId: request.requestId,
          status: 'FAILED',
          verification: 'VERIFICATION_FAILED',
          message: `Native bridge HTTP error: ${response.statusText}`,
          durationSeconds: 0.1,
          errorReason: 'HTTP_ERROR',
          timestamp: new Date().toISOString(),
        };
      }

      return await response.json();
    } catch (err: any) {
      clearTimeout(timeoutId);

      const isTimeout = err?.name === 'AbortError';
      return {
        requestId: request.requestId,
        status: isTimeout ? 'TIMEOUT' : 'FAILED',
        verification: 'VERIFICATION_FAILED',
        message: isTimeout ? 'Native bridge execution timed out after 10s.' : `Native bridge connection unreachable: ${err?.message}`,
        durationSeconds: 0.1,
        errorReason: isTimeout ? 'TIMEOUT' : 'BRIDGE_UNREACHABLE',
        timestamp: new Date().toISOString(),
      };
    }
  }

  async checkConnection(): Promise<boolean> {
    try {
      const health = await this.healthCheck();
      if (health.healthy) return true;

      const res = await this.executeNative({
        requestId: `ping-${Date.now()}`,
        capability: 'SYSTEM_CONTROL',
        action: 'GET_SYSTEM_INFO',
        target: { rawTarget: 'primary' },
        parameters: {},
        authorization: { userId: 'health', riskLevel: 'LOW', isApproved: true, sessionToken: 'local-dev-token' },
        timestamp: new Date().toISOString(),
      });
      return res.status === 'COMPLETED' || res.status !== 'FAILED';
    } catch {
      return false;
    }
  }
}
