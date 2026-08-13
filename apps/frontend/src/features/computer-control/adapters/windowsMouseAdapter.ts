import { NativeBridgeClient } from '../../native-bridge/client/nativeBridgeClient';
import { ComputerResult, MouseActionType } from '../types/computerControl';

export class WindowsMouseAdapter {
  private client = new NativeBridgeClient();

  async executeMouseAction(
    action: MouseActionType,
    x?: number,
    y?: number,
    scrollDelta?: number
  ): Promise<ComputerResult> {
    const started = Date.now();
    const mappedAction =
      action === 'CLICK'
        ? 'MOUSE_CLICK'
        : action === 'DOUBLE_CLICK'
        ? 'MOUSE_DOUBLE_CLICK'
        : action === 'RIGHT_CLICK'
        ? 'MOUSE_RIGHT_CLICK'
        : action === 'SCROLL'
        ? 'MOUSE_SCROLL'
        : 'MOUSE_MOVE';

    const res = await this.client.executeNative({
      requestId: `req-mouse-${Date.now()}`,
      capability: 'COMPUTER_CONTROL',
      action: mappedAction,
      target: { rawTarget: 'mouse', x, y },
      parameters: { scrollDelta },
      authorization: {
        userId: 'local-user',
        sessionToken: 'session-valid',
        riskLevel: action === 'CLICK' || action === 'SCROLL' || action === 'MOVE_MOUSE' ? 'SAFE' : 'LOW',
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
      verifiedState: res.verification === 'MOUSE_VERIFIED',
      timestamp: new Date().toISOString(),
    };
  }
}
