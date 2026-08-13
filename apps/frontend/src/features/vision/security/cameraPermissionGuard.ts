import { VisionPermissionState } from '../types/visionPermission';

export class CameraPermissionGuard {
  private currentState: VisionPermissionState = 'DENIED';

  getPermissionState(): VisionPermissionState {
    return this.currentState;
  }

  setPermissionState(state: VisionPermissionState): void {
    this.currentState = state;
  }

  isCameraAccessAllowed(): boolean {
    return this.currentState === 'GRANTED';
  }
}
