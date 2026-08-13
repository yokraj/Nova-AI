import { VisionPermissionState } from '../types/visionPermission';

export class ScreenPermissionGuard {
  private currentState: VisionPermissionState = 'GRANTED';

  getPermissionState(): VisionPermissionState {
    return this.currentState;
  }

  setPermissionState(state: VisionPermissionState): void {
    this.currentState = state;
  }

  isScreenAccessAllowed(): boolean {
    return this.currentState === 'GRANTED';
  }
}
