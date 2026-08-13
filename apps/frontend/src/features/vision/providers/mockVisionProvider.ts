import { VisionProvider } from './visionProvider';
import { VisionRequest } from '../types/visionRequest';
import { VisionResult } from '../types/visionResult';
import { VisionObservation } from '../types/visionObservation';
import { VisionTarget } from '../types/visionTarget';

export class MockVisionProvider implements VisionProvider {
  providerName = 'MOCK_VISION_PROVIDER';

  async isAvailable(): Promise<boolean> {
    return true;
  }

  async observeScreen(): Promise<VisionObservation> {
    return {
      id: `obs-${Date.now()}`,
      source: { type: 'SCREEN', sourceId: 'primary-display', permission: 'GRANTED' },
      timestamp: new Date().toISOString(),
      width: 1920,
      height: 1080,
      textExtracted: 'VS Code editor active. TypeScript compilation report visible.',
      activeApplication: 'VS Code',
      activeWindowTitle: 'Nova-AI - Visual Studio Code',
      detectedTargets: [
        {
          id: 'target-settings',
          type: 'BUTTON',
          label: 'Settings',
          confidence: 0.97,
          boundingBox: { x: 40, y: 980, width: 36, height: 36 },
          application: 'VS Code',
          actionable: true,
        },
        {
          id: 'target-submit',
          type: 'BUTTON',
          label: 'Submit',
          confidence: 0.95,
          boundingBox: { x: 820, y: 640, width: 120, height: 44 },
          actionable: true,
        },
        {
          id: 'target-err',
          type: 'ERROR_MESSAGE',
          label: 'TypeScript Error TS2307',
          confidence: 0.99,
          text: 'Cannot find module or its corresponding type declarations.',
          actionable: false,
        },
      ],
      confidenceScore: 0.97,
      containsSensitiveData: false,
    };
  }

  async analyzeImage(imageSource: string): Promise<VisionObservation> {
    return this.observeScreen();
  }

  async detectTargets(observation: VisionObservation): Promise<VisionTarget[]> {
    return observation.detectedTargets;
  }

  async executeAction(request: VisionRequest): Promise<VisionResult> {
    const started = Date.now();
    const obs = await this.observeScreen();

    return {
      requestId: request.requestId,
      success: true,
      status: 'COMPLETED',
      action: request.action,
      observation: obs,
      verification: 'TARGET_VERIFIED',
      message: `[SIMULATED] Executed visual action "${request.action}" on target.`,
      durationSeconds: (Date.now() - started) / 1000 + 0.4,
      extractedText: obs.textExtracted,
      detectedErrors: ['TypeScript compilation error detected in editor window.'],
      isSimulated: true,
      timestamp: new Date().toISOString(),
    };
  }
}
