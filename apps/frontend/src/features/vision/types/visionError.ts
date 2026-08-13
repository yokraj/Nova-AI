export type VisionErrorType =
  | 'SCREEN_PERMISSION_DENIED'
  | 'CAMERA_PERMISSION_DENIED'
  | 'SENSITIVE_DATA_BLOCKED'
  | 'TARGET_NOT_FOUND'
  | 'LOW_CONFIDENCE_THRESHOLD'
  | 'UNSAFE_VISUAL_ACTION'
  | 'VISION_MODEL_UNAVAILABLE';

export interface VisionError {
  type: VisionErrorType;
  message: string;
  targetDescription?: string;
}
