import { NativeBridgeClient } from '../../native-bridge/client/nativeBridgeClient';
import { ComputerResult, KeyboardActionType } from '../types/computerControl';

export class WindowsKeyboardAdapter {
  private client = new NativeBridgeClient();

  async executeKeyboardAction(
    action: KeyboardActionType,
    textPayload?: string,
    keyName?: string,
    keyCombination?: string[]
  ): Promise<ComputerResult> {
    const started = Date.now();
    let mappedAction: 'KEYBOARD_TYPE' | 'KEYBOARD_PRESS' | 'KEYBOARD_COMBINATION' | 'CLIPBOARD_GET' | 'CLIPBOARD_SET' = 'KEYBOARD_TYPE';

    if (action === 'PRESS_KEY' || action === 'KEY_DOWN' || action === 'KEY_UP') {
      mappedAction = 'KEYBOARD_PRESS';
    } else if (action === 'KEY_COMBINATION' || action === 'COPY' || action === 'PASTE' || action === 'CUT' || action === 'SELECT_ALL') {
      mappedAction = 'KEYBOARD_COMBINATION';
    }

    const combination = keyCombination || (action === 'COPY' ? ['Ctrl', 'C'] : action === 'PASTE' ? ['Ctrl', 'V'] : action === 'SELECT_ALL' ? ['Ctrl', 'A'] : undefined);

    const res = await this.client.executeNative({
      requestId: `req-kbd-${Date.now()}`,
      capability: 'COMPUTER_CONTROL',
      action: mappedAction,
      target: { rawTarget: 'keyboard' },
      parameters: { textPayload, keyName, keyCombination: combination },
      authorization: {
        userId: 'local-user',
        sessionToken: 'session-valid',
        riskLevel: 'LOW',
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
      verifiedState: res.verification === 'KEYBOARD_VERIFIED',
      timestamp: new Date().toISOString(),
    };
  }

  async getClipboard(): Promise<ComputerResult> {
    const started = Date.now();
    const res = await this.client.executeNative({
      requestId: `req-clip-get-${Date.now()}`,
      capability: 'COMPUTER_CONTROL',
      action: 'CLIPBOARD_GET',
      target: { rawTarget: 'clipboard' },
      authorization: {
        userId: 'local-user',
        sessionToken: 'session-valid',
        riskLevel: 'SAFE',
        isApproved: true,
      },
      timestamp: new Date().toISOString(),
    });

    return {
      requestId: res.requestId,
      action: 'GET_CLIPBOARD',
      success: res.status === 'COMPLETED',
      message: res.message,
      data: res.resultData,
      errorReason: res.errorReason,
      durationSeconds: (Date.now() - started) / 1000,
      verifiedState: res.verification === 'CLIPBOARD_VERIFIED',
      timestamp: new Date().toISOString(),
    };
  }
}
