import { BrowserRequest } from '../types/browserRequest';
import { BrowserResult } from '../types/browserResult';
import { BrowserActionType } from '../types/browserAction';
import { BrowserTargetResolver } from '../resolvers/browserTargetResolver';
import { BrowserPolicy } from '../security/browserPolicy';
import { BrowserPermissionGuard } from '../security/browserPermissionGuard';
import { NativeBrowserAdapter } from '../adapters/nativeBrowserAdapter';
import { ExecutionOrchestrator } from '../../execution-runtime/orchestrator/executionOrchestrator';

export class BrowserOrchestrator {
  private targetResolver = new BrowserTargetResolver();
  private policy = new BrowserPolicy();
  private permissionGuard = new BrowserPermissionGuard();
  private adapter = new NativeBrowserAdapter();
  private executionOrchestrator = new ExecutionOrchestrator();

  async processBrowserCommand(
    commandText: string,
    action: BrowserActionType,
    rawTargetInput: string,
    parameters?: BrowserRequest['parameters']
  ): Promise<BrowserResult> {
    const target = this.targetResolver.resolveTarget(rawTargetInput);
    const riskLevel = this.policy.getRiskLevel(action);
    const requiresApproval = riskLevel === 'HIGH' || riskLevel === 'CRITICAL';

    const request: BrowserRequest = {
      requestId: `browser-req-${Date.now()}`,
      action,
      target,
      parameters,
      riskLevel,
      requiresApproval,
      timestamp: new Date().toISOString(),
    };

    const guardCheck = this.permissionGuard.validateRequest(request);
    if (!guardCheck.valid) {
      return {
        requestId: request.requestId,
        success: false,
        status: 'DENIED',
        action,
        targetUrl: target.url,
        verification: 'VERIFICATION_FAILED',
        message: guardCheck.reason || 'Browser security check failed.',
        durationSeconds: 0.1,
        errorReason: 'SECURITY_VIOLATION',
        timestamp: new Date().toISOString(),
      };
    }

    if (requiresApproval) {
      return {
        requestId: request.requestId,
        success: false,
        status: 'AWAITING_APPROVAL',
        action,
        targetUrl: target.url,
        verification: 'UNVERIFIED',
        message: `Browser action "${action}" on ${target.url || target.rawTarget} requires authorization.`,
        durationSeconds: 0.1,
        timestamp: new Date().toISOString(),
      };
    }

    // Execute via ExecutionOrchestrator & Native Adapter
    return this.adapter.execute(request);
  }
}
