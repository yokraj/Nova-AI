import { NativeBridgeClient } from '../../native-bridge/client/nativeBridgeClient';
import { NativeBridgeRequest } from '../../native-bridge/types/nativeBridgeRequest';
import { NativeSystemAction } from '../../native-bridge/types/nativeBridgeCapability';
import { ExecutionRequest } from '../types/executionRequest';
import { ExecutionResult } from '../types/executionResult';
import { CapabilityAdapter } from '../types/capability';

export class WindowsSystemAdapter implements CapabilityAdapter {

  capabilityName = 'SYSTEM_CONTROL';
  private bridgeClient = new NativeBridgeClient();

  canHandle(request: ExecutionRequest): boolean {
    return request.capability === 'SYSTEM_CONTROL';
  }

  async validate(request: ExecutionRequest): Promise<boolean> {
    return request.capability === 'SYSTEM_CONTROL';
  }

  async verify(request: ExecutionRequest): Promise<boolean> {
    return true;
  }

  describe(request: ExecutionRequest): string {
    return `Execute System Control: ${request.action} on ${request.target}`;
  }

  async execute(request: ExecutionRequest): Promise<ExecutionResult> {

    const startedAt = Date.now();
    const action = this.mapExecutionActionToNative(request.action);

    const bridgeReq: NativeBridgeRequest = {
      requestId: request.executionId,
      capability: 'SYSTEM_CONTROL',
      action,
      target: {
        rawTarget: request.target,
      },
      parameters: {
        volumeLevel: request.parameters?.volumeLevel,
        brightnessLevel: request.parameters?.brightnessLevel,
        enabledState: request.parameters?.enabledState,
        processName: request.parameters?.processName || request.target,
      },
      authorization: {
        userId: request.requestedBy || 'user',
        sessionToken: 'session-sys-token',
        riskLevel: request.riskLevel,
        isApproved: request.policy === 'ALLOW',
      },
      timestamp: new Date().toISOString(),
    };

    try {
      const res = await this.bridgeClient.executeNative(bridgeReq);
      const now = new Date().toISOString();

      return {
        executionId: request.executionId,
        status: res.status === 'COMPLETED' ? 'COMPLETED' : 'FAILED',
        capability: 'SYSTEM_CONTROL',
        action: request.action,
        target: request.target,
        startedAt: new Date(startedAt).toISOString(),
        completedAt: now,
        durationSeconds: (Date.now() - startedAt) / 1000,
        verification: res.status === 'COMPLETED' ? 'STATE_VERIFIED' : 'VERIFICATION_FAILED',
        message: res.message,
        error: res.errorReason,
        metadata: res.resultData,
      };
    } catch (err: any) {
      const now = new Date().toISOString();
      return {
        executionId: request.executionId,
        status: 'FAILED',
        capability: 'SYSTEM_CONTROL',
        action: request.action,
        target: request.target,
        startedAt: new Date(startedAt).toISOString(),
        completedAt: now,
        durationSeconds: (Date.now() - startedAt) / 1000,
        verification: 'VERIFICATION_FAILED',
        message: `System execution failed: ${err?.message}`,
        error: 'SYSTEM_EXECUTION_ERROR',
      };
    }
  }

  private mapExecutionActionToNative(execAction: string): NativeSystemAction {
    switch (execAction) {
      case 'GET_SYSTEM_INFO':
        return 'GET_SYSTEM_INFO';
      case 'GET_CPU_STATUS':
        return 'GET_CPU_STATUS';
      case 'GET_MEMORY_STATUS':
        return 'GET_MEMORY_STATUS';
      case 'GET_STORAGE_STATUS':
        return 'GET_STORAGE_STATUS';
      case 'GET_BATTERY_STATUS':
        return 'GET_BATTERY_STATUS';
      case 'GET_VOLUME':
        return 'GET_VOLUME';
      case 'SET_VOLUME':
        return 'SET_VOLUME';
      case 'MUTE_VOLUME':
        return 'MUTE_VOLUME';
      case 'UNMUTE_VOLUME':
        return 'UNMUTE_VOLUME';
      case 'GET_BRIGHTNESS':
        return 'GET_BRIGHTNESS';
      case 'SET_BRIGHTNESS':
        return 'SET_BRIGHTNESS';
      case 'GET_NETWORK_STATUS':
        return 'GET_NETWORK_STATUS';
      case 'SET_WIFI_STATE':
        return 'SET_WIFI_STATE';
      case 'SET_BLUETOOTH_STATE':
        return 'SET_BLUETOOTH_STATE';
      case 'POWER_LOCK':
        return 'POWER_LOCK';
      case 'POWER_SLEEP':
        return 'POWER_SLEEP';
      case 'POWER_RESTART':
        return 'POWER_RESTART';
      case 'POWER_SHUTDOWN':
        return 'POWER_SHUTDOWN';
      case 'POWER_SIGNOUT':
        return 'POWER_SIGNOUT';
      case 'LIST_PROCESSES':
        return 'LIST_PROCESSES';
      case 'FIND_PROCESS':
        return 'FIND_PROCESS';
      case 'TERMINATE_PROCESS':
        return 'TERMINATE_PROCESS';
      case 'CAPTURE_SCREENSHOT':
        return 'CAPTURE_SCREENSHOT';
      default:
        return 'GET_SYSTEM_INFO';
    }
  }
}
