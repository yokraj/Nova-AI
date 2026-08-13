import { ComputerResult, ComputerTarget, MouseActionType, KeyboardActionType, WindowActionType, ScreenObservation } from '../types/computerControl';
import { CoordinateGuard } from '../security/coordinateGuard';
import { UITargetResolver } from '../resolvers/uiTargetResolver';
import { WindowsMouseAdapter } from '../adapters/windowsMouseAdapter';
import { WindowsKeyboardAdapter } from '../adapters/windowsKeyboardAdapter';
import { WindowsWindowAdapter } from '../adapters/windowsWindowAdapter';
import { WindowsScreenAdapter } from '../adapters/windowsScreenAdapter';
import { ComputerSecurityPolicy } from '../security/computerSecurityPolicy';

export class ComputerOrchestrator {
  private coordinateGuard = new CoordinateGuard();
  private targetResolver = new UITargetResolver();
  private mouseAdapter = new WindowsMouseAdapter();
  private keyboardAdapter = new WindowsKeyboardAdapter();
  private windowAdapter = new WindowsWindowAdapter();
  private screenAdapter = new WindowsScreenAdapter();
  private securityPolicy = new ComputerSecurityPolicy();

  async observeScreen(): Promise<ScreenObservation> {
    return this.screenAdapter.observeScreen();
  }

  async executeMouseAction(
    action: MouseActionType,
    target?: ComputerTarget,
    x?: number,
    y?: number,
    scrollDelta?: number
  ): Promise<ComputerResult> {
    let finalX = x;
    let finalY = y;

    if (target && (finalX === undefined || finalY === undefined)) {
      const obs = await this.observeScreen();
      const resolved = this.targetResolver.resolveTarget(target, obs);
      finalX = resolved.resolvedX;
      finalY = resolved.resolvedY;
    }

    if (finalX !== undefined && finalY !== undefined) {
      const coordCheck = this.coordinateGuard.validateCoordinates(finalX, finalY);
      if (!coordCheck.valid) {
        return {
          requestId: `req-mouse-${Date.now()}`,
          action,
          success: false,
          message: coordCheck.reason || 'Invalid coordinates.',
          errorReason: 'COORDINATE_OUT_OF_BOUNDS',
          durationSeconds: 0,
          verifiedState: false,
          timestamp: new Date().toISOString(),
        };
      }
    }

    const secCheck = this.securityPolicy.evaluateRequest({
      requestId: `req-mouse-${Date.now()}`,
      action,
      target,
      coordinates: finalX !== undefined && finalY !== undefined ? { x: finalX, y: finalY } : undefined,
      riskLevel: 'LOW',
      isApproved: true,
      timestamp: new Date().toISOString(),
    });

    if (!secCheck.allowed) {
      return {
        requestId: `req-mouse-${Date.now()}`,
        action,
        success: false,
        message: secCheck.reason,
        errorReason: 'SECURITY_DENIED',
        durationSeconds: 0,
        verifiedState: false,
        timestamp: new Date().toISOString(),
      };
    }

    return this.mouseAdapter.executeMouseAction(action, finalX, finalY, scrollDelta);
  }

  async executeKeyboardAction(
    action: KeyboardActionType,
    textPayload?: string,
    keyName?: string,
    keyCombination?: string[]
  ): Promise<ComputerResult> {
    const secCheck = this.securityPolicy.evaluateRequest({
      requestId: `req-kbd-${Date.now()}`,
      action,
      textPayload,
      keyCombination,
      riskLevel: 'LOW',
      isApproved: true,
      timestamp: new Date().toISOString(),
    });

    if (!secCheck.allowed) {
      return {
        requestId: `req-kbd-${Date.now()}`,
        action,
        success: false,
        message: secCheck.reason,
        errorReason: 'SECURITY_DENIED',
        durationSeconds: 0,
        verifiedState: false,
        timestamp: new Date().toISOString(),
      };
    }

    return this.keyboardAdapter.executeKeyboardAction(action, textPayload, keyName, keyCombination);
  }

  async executeWindowAction(
    action: WindowActionType,
    windowTitle?: string,
    processName?: string
  ): Promise<ComputerResult> {
    return this.windowAdapter.executeWindowAction(action, windowTitle, processName);
  }

  async getClipboard(): Promise<ComputerResult> {
    return this.keyboardAdapter.getClipboard();
  }
}
