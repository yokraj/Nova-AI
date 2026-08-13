import { ExecutionRequest } from '../types/executionRequest';
import { ExecutionResult } from '../types/executionResult';
import { AuthorizationContext } from '../types/executionContext';
import { CapabilityRegistry } from '../adapters/capabilityRegistry';
import { PolicyEngine } from '../security/policyEngine';
import { CommandInjectionGuard } from '../security/commandInjectionGuard';
import { AuditLogger } from '../security/auditLogger';

export class ExecutionOrchestrator {
  private registry = new CapabilityRegistry();
  private policyEngine = new PolicyEngine();
  private injectionGuard = new CommandInjectionGuard();
  private auditLogger = new AuditLogger();

  async execute(request: ExecutionRequest, context?: AuthorizationContext): Promise<ExecutionResult> {
    const startedAt = new Date().toISOString();

    // Step 1: Security Injection Check
    if (!this.injectionGuard.isSafe(request.target)) {
      const result: ExecutionResult = {
        executionId: request.executionId,
        status: 'DENIED',
        capability: request.capability,
        action: request.action,
        target: request.target,
        startedAt,
        completedAt: new Date().toISOString(),
        durationSeconds: 0,
        verification: 'VERIFICATION_FAILED',
        message: 'Execution denied: Command injection pattern or invalid target detected.',
        error: 'SECURITY_INJECTION_DETECTED',
      };
      this.auditLogger.record(request, result);
      return result;
    }

    // Step 2: Policy & Authorization Evaluation
    const policyEval = this.policyEngine.evaluate(request, context);
    if (!policyEval.allowed) {
      const result: ExecutionResult = {
        executionId: request.executionId,
        status: 'DENIED',
        capability: request.capability,
        action: request.action,
        target: request.target,
        startedAt,
        completedAt: new Date().toISOString(),
        durationSeconds: 0,
        verification: 'VERIFICATION_FAILED',
        message: `Execution policy denied request: ${policyEval.reason}`,
        error: 'POLICY_DENIED',
      };
      this.auditLogger.record(request, result);
      return result;
    }

    // Step 3: Capability Adapter Resolution
    const adapter = this.registry.findAdapter(request);
    if (!adapter) {
      const result: ExecutionResult = {
        executionId: request.executionId,
        status: 'FAILED',
        capability: request.capability,
        action: request.action,
        target: request.target,
        startedAt,
        completedAt: new Date().toISOString(),
        durationSeconds: 0,
        verification: 'UNVERIFIED',
        message: `No capability adapter registered for ${request.capability} -> ${request.action}.`,
        error: 'UNSUPPORTED_CAPABILITY',
      };
      this.auditLogger.record(request, result);
      return result;
    }

    // Step 4: Adapter Target Validation
    const isValidTarget = await adapter.validate(request);
    if (!isValidTarget) {
      const result: ExecutionResult = {
        executionId: request.executionId,
        status: 'FAILED',
        capability: request.capability,
        action: request.action,
        target: request.target,
        startedAt,
        completedAt: new Date().toISOString(),
        durationSeconds: 0.1,
        verification: 'VERIFICATION_FAILED',
        message: `Could not resolve target application or resource "${request.target}".`,
        error: 'APPLICATION_NOT_INSTALLED',
      };
      this.auditLogger.record(request, result);
      return result;
    }

    // Step 5: Adapter Execution with Timeout Protection (10s limit)
    try {
      const executionPromise = adapter.execute(request);
      const timeoutPromise = new Promise<ExecutionResult>((_, reject) =>
        setTimeout(() => reject(new Error('TIMEOUT')), 10000)
      );

      const result = (await Promise.race([executionPromise, timeoutPromise])) as ExecutionResult;

      this.auditLogger.record(request, result);
      return result;
    } catch (err: any) {
      const result: ExecutionResult = {
        executionId: request.executionId,
        status: err.message === 'TIMEOUT' ? 'TIMED_OUT' : 'FAILED',
        capability: request.capability,
        action: request.action,
        target: request.target,
        startedAt,
        completedAt: new Date().toISOString(),
        durationSeconds: 10,
        verification: 'VERIFICATION_FAILED',
        message: err.message === 'TIMEOUT' ? 'Execution timed out.' : 'Execution failed during process launch.',
        error: err.message === 'TIMEOUT' ? 'TIMEOUT' : 'EXECUTION_FAILED',
      };
      this.auditLogger.record(request, result);
      return result;
    }
  }

  getAuditLogs() {
    return this.auditLogger.getEvents();
  }
}
