import { VisionRequest } from '../types/visionRequest';
import { VisionResult } from '../types/visionResult';
import { VisionObservation } from '../types/visionObservation';
import { VisionTarget } from '../types/visionTarget';

export interface VisionProvider {
  providerName: string;
  isAvailable(): Promise<boolean>;
  observeScreen(): Promise<VisionObservation>;
  analyzeImage(imageSource: string): Promise<VisionObservation>;
  detectTargets(observation: VisionObservation): Promise<VisionTarget[]>;
  executeAction(request: VisionRequest): Promise<VisionResult>;
}
