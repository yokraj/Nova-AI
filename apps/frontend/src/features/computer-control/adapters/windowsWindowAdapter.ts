import { NativeBridgeClient } from '../../native-bridge/client/nativeBridgeClient';
import { ComputerResult, WindowActionType } from '../types/computerControl';

export class WindowsWindowAdapter {
  private client = new NativeBridgeClient();

  async executeWindowAction(
    action: WindowActionType,
    windowTitle?: string,
    processName?: string
  ): Promise<ComputerResult> {
    const started = Date.now();
    let mappedAction: 'WINDOW_LIST' | 'WINDOW_GET_ACTIVE' | 'WINDOW_FOCUS' | 'WINDOW_MINIMIZE' | 'WINDOW_MAXIMIZE' | 'WINDOW_RESTORE' | 'WINDOW_CLOSE' = 'WINDOW_LIST';

    if (action === 'GET_ACTIVE_WINDOW') mappedAction = 'WINDOW_GET_ACTIVE';
    else if (action === 'FOCUS_WINDOW' || action === 'SWITCH_APPLICATION') mappedAction = 'WINDOW_FOCUS';
    else if (action === 'MINIMIZE_WINDOW') mappedAction = 'WINDOW_MINIMIZE';
    else if (action === 'MAXIMIZE_WINDOW') mappedAction = 'WINDOW_MAXIMIZE';
    else if (action === 'RESTORE_WINDOW') mappedAction = 'WINDOW_RESTORE';
    else if (action === 'CLOSE_WINDOW') mappedAction = 'WINDOW_CLOSE';

    const res = await this.client.executeNative({
      requestId: `req-win-${Date.now()}`,
      capability: 'COMPUTER_CONTROL',
      action: mappedAction,
      target: { rawTarget: windowTitle || processName || 'window' },
      parameters: { processName },
      authorization: {
        userId: 'local-user',
        sessionToken: 'session-valid',
        riskLevel: action === 'CLOSE_WINDOW' ? 'MEDIUM' : 'SAFE',
        isApproved: true,
      },
      timestamp: new Date().toISOString(),
    });

    return {
      requestId: res.requestId,
      action,
      success: res.status === 'COMPLETED',
      message: res.message,
      data: res.resultData,
      errorReason: res.errorReason,
      durationSeconds: (Date.now() - started) / 1000,
      verifiedState: res.verification === 'WINDOW_VERIFIED',
      timestamp: new Date().toISOString(),
    };
  }
}
