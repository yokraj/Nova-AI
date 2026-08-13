import { ExecutionOrchestrator } from '../orchestrator/executionOrchestrator';
import { ExecutionRequest } from '../types/executionRequest';
import { ApplicationResolver } from '../resolvers/applicationResolver';

export async function runExecutionRuntimeTests(): Promise<{ passed: boolean; results: string[] }> {
  const orchestrator = new ExecutionOrchestrator();
  const resolver = new ApplicationResolver();
  const results: string[] = [];
  let allPassed = true;

  const logResult = (testName: string, success: boolean, detail: string) => {
    const msg = `[${success ? 'PASS' : 'FAIL'}] ${testName}: ${detail}`;
    results.push(msg);
    if (!success) allPassed = false;
  };

  // Test 1: Application Resolver Alias Lookup
  const app1 = resolver.resolve('vscode');
  logResult(
    'Application Resolver Alias Lookup',
    app1 !== null && app1.name === 'Visual Studio Code',
    app1 ? `Resolved "vscode" to ${app1.name}` : 'Failed to resolve'
  );

  // Test 2: Invalid Application Handling
  const reqInvalid: ExecutionRequest = {
    executionId: 'exec-inv-01',
    commandId: 'cmd-inv-01',
    capability: 'APPLICATION_CONTROL',
    action: 'OPEN_APPLICATION',
    target: 'application-that-does-not-exist',
    requestedBy: 'user',
    workspace: 'default',
    riskLevel: 'LOW',
    policy: 'ALLOW',
    permissions: [],
    timestamp: new Date().toISOString(),
  };

  const resInvalid = await orchestrator.execute(reqInvalid);
  logResult(
    'Invalid Application Handling',
    resInvalid.status === 'FAILED' && resInvalid.error === 'APPLICATION_NOT_INSTALLED',
    `Returned status: ${resInvalid.status}, error: ${resInvalid.error}`
  );

  // Test 3: Command Injection Protection
  const reqInjection: ExecutionRequest = {
    executionId: 'exec-inj-01',
    commandId: 'cmd-inj-01',
    capability: 'APPLICATION_CONTROL',
    action: 'OPEN_APPLICATION',
    target: 'vscode && delete files',
    requestedBy: 'user',
    workspace: 'default',
    riskLevel: 'LOW',
    policy: 'ALLOW',
    permissions: [],
    timestamp: new Date().toISOString(),
  };

  const resInjection = await orchestrator.execute(reqInjection);
  logResult(
    'Command Injection Protection',
    resInjection.status === 'DENIED' && resInjection.error === 'SECURITY_INJECTION_DETECTED',
    `Blocked command injection with status: ${resInjection.status}`
  );

  // Test 4: Path Traversal Protection
  const reqPath: ExecutionRequest = {
    executionId: 'exec-path-01',
    commandId: 'cmd-path-01',
    capability: 'APPLICATION_CONTROL',
    action: 'OPEN_APPLICATION',
    target: '../../some-executable',
    requestedBy: 'user',
    workspace: 'default',
    riskLevel: 'LOW',
    policy: 'ALLOW',
    permissions: [],
    timestamp: new Date().toISOString(),
  };

  const resPath = await orchestrator.execute(reqPath);
  logResult(
    'Path Traversal Protection',
    resPath.status === 'DENIED' && resPath.error === 'SECURITY_INJECTION_DETECTED',
    `Blocked path traversal with status: ${resPath.status}`
  );

  // Test 5: Successful Execution & Verification
  const reqValid: ExecutionRequest = {
    executionId: 'exec-val-01',
    commandId: 'cmd-val-01',
    capability: 'APPLICATION_CONTROL',
    action: 'OPEN_APPLICATION',
    target: 'VS Code',
    requestedBy: 'user',
    workspace: 'default',
    riskLevel: 'LOW',
    policy: 'ALLOW',
    permissions: [],
    timestamp: new Date().toISOString(),
  };

  const resValid = await orchestrator.execute(reqValid);
  logResult(
    'Successful Execution & Verification',
    resValid.status === 'COMPLETED' && resValid.verification === 'PROCESS_RUNNING',
    `Executed "${resValid.target}" with status: ${resValid.status}`
  );

  // Test 6: Audit Log Recording
  const logs = orchestrator.getAuditLogs();
  logResult(
    'Audit Log Recording',
    logs.length >= 4,
    `Recorded ${logs.length} audit events cleanly`
  );

  return { passed: allPassed, results };
}
