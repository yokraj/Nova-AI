import { VisionPolicy } from '../security/visionPolicy';
import { ScreenPermissionGuard } from '../security/screenPermissionGuard';
import { CameraPermissionGuard } from '../security/cameraPermissionGuard';
import { VisualActionGuard } from '../security/visualActionGuard';
import { PrivacyGuard } from '../security/privacyGuard';
import { VisualTargetResolver } from '../resolvers/visualTargetResolver';
import { MockVisionProvider } from '../providers/mockVisionProvider';
import { VisionTarget } from '../types/visionTarget';
import { VisionRequest } from '../types/visionRequest';

export async function runVisionRuntimeTests(): Promise<{ passed: boolean; results: string[] }> {
  const policy = new VisionPolicy();
  const screenGuard = new ScreenPermissionGuard();
  const cameraGuard = new CameraPermissionGuard();
  const actionGuard = new VisualActionGuard();
  const privacyGuard = new PrivacyGuard();
  const targetResolver = new VisualTargetResolver();
  const mockProvider = new MockVisionProvider();

  const results: string[] = [];
  let allPassed = true;

  const logResult = (testName: string, success: boolean, detail: string) => {
    const msg = `[${success ? 'PASS' : 'FAIL'} VISION UNIT TEST: ${testName} - ${detail}`;
    results.push(msg);
    if (!success) allPassed = false;
  };

  // Test 1: Vision Request Validation & Policy Assessment
  const riskObs = policy.getRiskLevel('OBSERVE_SCREEN');
  logResult('Vision Request Policy Assessment', riskObs === 'LOW', `Risk level: ${riskObs}`);

  // Test 2: Screen Permission Denial
  screenGuard.setPermissionState('DENIED');
  logResult('Screen Permission Denial', !screenGuard.isScreenAccessAllowed(), 'Screen access correctly denied');

  // Test 3: Screen Permission Approval
  screenGuard.setPermissionState('GRANTED');
  logResult('Screen Permission Approval', screenGuard.isScreenAccessAllowed(), 'Screen access granted');

  // Test 4: Camera Permission Denial
  logResult('Camera Permission Denial', !cameraGuard.isCameraAccessAllowed(), 'Camera access denied by default');

  // Test 5: Privacy Filtering & Sensitive Data Redaction
  const pCheck = privacyGuard.sanitizeText('User password is secretKey123 and bearer token xyz.');
  const isRedacted = pCheck.containsSensitiveData && (pCheck.sanitizedText ? pCheck.sanitizedText.includes('[REDACTED_SENSITIVE_DATA]') : false);
  logResult('Privacy Filtering & Sensitive Data Redaction', isRedacted, 'Sensitive password/token redacted');

  // Test 6: Target Confidence Thresholding (Reject < 0.80)
  const lowTarget: VisionTarget = { id: 'low-1', type: 'BUTTON', label: 'Submit', confidence: 0.65, actionable: true };
  const resLow = targetResolver.resolveTargetFromObservation('Submit', [lowTarget]);
  logResult('Target Confidence Thresholding', resLow === null, 'Low confidence target (65%) rejected');

  // Test 7: Target Resolution (High Confidence)
  const highTarget: VisionTarget = { id: 'high-1', type: 'BUTTON', label: 'Submit', confidence: 0.95, actionable: true };
  const resHigh = targetResolver.resolveTargetFromObservation('Submit', [highTarget]);
  logResult('Target Resolution (High Confidence)', resHigh !== null && resHigh.id === 'high-1', 'Target resolved');

  // Test 8: Unsafe Visual Action Rejection (Click without target)
  const actCheck = actionGuard.validateVisualAction('CLICK_TARGET', null);
  logResult('Unsafe Visual Action Rejection', !actCheck.safe, `Blocked: ${actCheck.reason}`);

  // Test 9: OCR Output Structure
  const obs = await mockProvider.observeScreen();
  logResult('OCR Output Structure', obs.textExtracted !== undefined && obs.confidenceScore > 0.9, 'Structured OCR generated');

  // Test 10: Mock Provider Fallback & Verification
  const req: VisionRequest = {
    requestId: 'v-req-01',
    action: 'DESCRIBE_SCREEN',
    source: { type: 'SCREEN', sourceId: 'primary', permission: 'GRANTED' },
    riskLevel: 'SAFE',
    requiresApproval: false,
    timestamp: new Date().toISOString(),
  };

  const resExec = await mockProvider.executeAction(req);
  logResult(
    'Mock Provider Fallback & Verification',
    resExec.success && resExec.verification === 'TARGET_VERIFIED' && resExec.isSimulated === true,
    `Status: ${resExec.status}, Verification: ${resExec.verification}`
  );

  return { passed: allPassed, results };
}
