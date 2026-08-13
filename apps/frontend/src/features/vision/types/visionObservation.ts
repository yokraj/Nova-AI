import { VisionSource } from './visionSource';
import { VisionTarget } from './visionTarget';

export interface VisionObservation {
  id: string;
  source: VisionSource;
  timestamp: string;
  width: number;
  height: number;
  textExtracted?: string;
  detectedTargets: VisionTarget[];
  activeApplication?: string;
  activeWindowTitle?: string;
  confidenceScore: number;
  containsSensitiveData: boolean;
  redactedFields?: string[];
  metadata?: Record<string, any>;
}
