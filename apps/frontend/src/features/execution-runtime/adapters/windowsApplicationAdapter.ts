import { CapabilityAdapter } from '../types/capability';
import { ExecutionRequest } from '../types/executionRequest';
import { ExecutionResult } from '../types/executionResult';
import { ApplicationResolver } from '../resolvers/applicationResolver';
import { NativeBridgeClient } from '../../native-bridge/client/nativeBridgeClient';
import { NativeBridgeRequest } from '../../native-bridge/types/nativeBridgeRequest';

export class WindowsApplicationAdapter implements CapabilityAdapter {
  capabilityName = 'APPLICATION_CONTROL';
  private resolver = new ApplicationResolver();
  private bridgeClient = new NativeBridgeClient();

  canHandle(request: ExecutionRequest): boolean {
    return (
      request.capability === 'APPLICATION_CONTROL' &&
      request.action === 'OPEN_APPLICATION'
    );
  }

  async validate(request: ExecutionRequest): Promise<boolean> {
    return this.resolver.isSupported(request.target);
  }

  async execute(request: ExecutionRequest): Promise<ExecutionResult> {
    const startedAt = new Date().toISOString();

    const resolvedApp = this.resolver.resolve(request.target);
    if (!resolvedApp) {
      const completedAt = new Date().toISOString();
      return {
        executionId: request.executionId,
        status: 'FAILED',
        capability: request.capability,
        action: request.action,
        target: request.target,
        startedAt,
        completedAt,
        durationSeconds: 0.1,
        verification: 'VERIFICATION_FAILED',
        message: `Application "${request.target}" was not found or is not supported.`,
        error: 'APPLICATION_NOT_INSTALLED',
      };
    }

    // Try executing through Native Bridge first
    const bridgeReq: NativeBridgeRequest = {
      requestId: request.executionId,
      capability: 'APPLICATION_CONTROL',
      action: 'OPEN_APPLICATION',
      target: {
        rawTarget: request.target,
        applicationAlias: resolvedApp.name,
      },
      authorization: {
        userId: request.requestedBy || 'user',
        sessionToken: 'session-local-token',
        riskLevel: request.riskLevel || 'LOW',
        isApproved: true,
      },
      timestamp: startedAt,
    };

    const bridgeRes = await this.bridgeClient.executeNative(bridgeReq);

    if (bridgeRes.status === 'COMPLETED') {
      return {
        executionId: request.executionId,
        status: 'COMPLETED',
        capability: request.capability,
        action: request.action,
        target: resolvedApp.name,
        startedAt,
        completedAt: new Date().toISOString(),
        durationSeconds: bridgeRes.durationSeconds,
        verification: 'PROCESS_RUNNING',
        message: bridgeRes.message,
        metadata: {
          executableName: resolvedApp.executableName,
          processName: resolvedApp.processName,
          nativeBridge: true,
        },
      };
    }

    // Native Bridge must be running for real OS execution and process verification
    const completedAt = new Date().toISOString();
    const isBridgeUnavailable = bridgeRes.errorReason === 'BRIDGE_UNREACHABLE' || bridgeRes.status === 'FAILED';

    return {
      executionId: request.executionId,
      status: 'FAILED',
      capability: request.capability,
      action: request.action,
      target: resolvedApp.name,
      startedAt,
      completedAt,
      durationSeconds: bridgeRes.durationSeconds || 0.1,
      verification: 'VERIFICATION_FAILED',
      message: isBridgeUnavailable
        ? 'Native Bridge is unavailable. Start Nova Native Bridge on port 3001.'
        : bridgeRes.message || `Failed to launch ${resolvedApp.name} via Native Bridge.`,
      error: bridgeRes.errorReason || 'LAUNCH_FAILED',
      metadata: {
        executableName: resolvedApp.executableName,
        processName: resolvedApp.processName,
        nativeBridge: false,
      },
    };

  }

  async verify(request: ExecutionRequest): Promise<boolean> {
    const resolved = this.resolver.resolve(request.target);
    return resolved !== null;
  }

  describe(request: ExecutionRequest): string {
    const resolved = this.resolver.resolve(request.target);
    return `Launch Windows Application: ${resolved ? resolved.name : request.target}`;
  }
}
