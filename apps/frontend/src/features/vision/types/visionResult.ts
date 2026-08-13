import { VisionObservation } from './visionObservation';

export type VisionVerificationState =
  | 'TARGET_VERIFIED'
  | 'STATE_CHANGED'
  | 'TEXT_MATCHED'
  | 'SCREENSHOT_ANALYZED'
  | 'UNVERIFIED'
  | 'VERIFICATION_FAILED';

export interface VisionResult {
  requestId: string;
  success: boolean;
  status:
    | 'COMPLETED'
    | 'FAILED'
    | 'DENIED'
    | 'AWAITING_APPROVAL'
    | 'TIMED_OUT'
    | 'VERIFICATION_FAILED';
  action: string;
  observation?: VisionObservation;
  verification: VisionVerificationState;
  message: string;
  durationSeconds: number;
  extractedText?: string;
  detectedErrors?: string[];
  isSimulated?: boolean;
  errorReason?: string;
  timestamp: string;
}
