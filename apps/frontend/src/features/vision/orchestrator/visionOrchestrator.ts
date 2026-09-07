import { VisionRequest } from '../types/visionRequest';
import { VisionResult } from '../types/visionResult';
import { VisionActionType } from '../types/visionAction';
import { VisionPolicy } from '../security/visionPolicy';
import { ScreenPermissionGuard } from '../security/screenPermissionGuard';
import { VisualActionGuard } from '../security/visualActionGuard';
import { PrivacyGuard } from '../security/privacyGuard';
import { MockVisionProvider } from '../providers/mockVisionProvider';
import { LocalVisionProvider } from '../providers/localVisionProvider';
import { VisualTargetResolver } from '../resolvers/visualTargetResolver';

export class VisionOrchestrator {
  private policy = new VisionPolicy();
  private screenPermissionGuard = new ScreenPermissionGuard();
  private actionGuard = new VisualActionGuard();
  private privacyGuard = new PrivacyGuard();
  private targetResolver = new VisualTargetResolver();
  private localProvider = new LocalVisionProvider();
  private mockProvider = new MockVisionProvider();

  async processVisionCommand(
    commandText: string,
    action: VisionActionType,
    targetDescription?: string,
    parameters?: VisionRequest['parameters']
  ): Promise<VisionResult> {
    const riskLevel = this.policy.getRiskLevel(action);
    const requiresApproval = riskLevel === 'HIGH' || riskLevel === 'CRITICAL';

    // Screen permission check
    if (!this.screenPermissionGuard.isScreenAccessAllowed()) {
      return {
        requestId: `vision-req-${Date.now()}`,
        success: false,
        status: 'DENIED',
        action,
        verification: 'VERIFICATION_FAILED',
        message: 'Screen access permission has been denied or not granted.',
        durationSeconds: 0.1,
        errorReason: 'SCREEN_PERMISSION_DENIED',
        timestamp: new Date().toISOString(),
      };
    }

    const request: VisionRequest = {
      requestId: `vision-req-${Date.now()}`,
      action,
      source: { type: 'SCREEN', sourceId: 'primary-display', permission: 'GRANTED' },
      targetDescription,
      parameters,
      riskLevel,
      requiresApproval,
      timestamp: new Date().toISOString(),
    };

    if (requiresApproval) {
      return {
        requestId: request.requestId,
        success: false,
        status: 'AWAITING_APPROVAL',
        action,
        verification: 'UNVERIFIED',
        message: `Visual action "${action}" requires explicit security approval.`,
        durationSeconds: 0.1,
        timestamp: new Date().toISOString(),
      };
    }

    // Check LocalVisionProvider availability
    const isLocalAvailable = await this.localProvider.isAvailable();
    const provider = isLocalAvailable ? this.localProvider : this.mockProvider;

    // Execute via provider
    const result = await provider.executeAction(request);

    // Apply PrivacyGuard sanitization
    if (result.observation?.textExtracted) {
      const sanitized = this.privacyGuard.sanitizeText(result.observation.textExtracted);
      result.observation.textExtracted = sanitized.sanitizedText;
      result.observation.containsSensitiveData = sanitized.containsSensitiveData;
    }

    return result;
  }
}
