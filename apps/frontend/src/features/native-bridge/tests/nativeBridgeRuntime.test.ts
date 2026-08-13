import { BridgeSecurityGuard } from '../security/bridgeSecurityGuard';
import { ExecutableRegistry } from '../security/executableRegistry';
import { BridgeOriginGuard } from '../security/bridgeOriginGuard';
import { NativeBridgeRequest } from '../types/nativeBridgeRequest';

export async function runNativeBridgeUnitTests(): Promise<{ passed: boolean; results: string[] }> {
  const securityGuard = new BridgeSecurityGuard();
  const execRegistry = new ExecutableRegistry();
  const originGuard = new BridgeOriginGuard();
  const results: string[] = [];
  let allPassed = true;

  const logResult = (testName: string, success: boolean, detail: string) => {
    const msg = `[${success ? 'PASS' : 'FAIL'}] UNIT TEST: ${testName} - ${detail}`;
    results.push(msg);
    if (!success) allPassed = false;
  };

  // Test 1: Executable Whitelist Resolution
  const vsCodeExec = execRegistry.resolveExecutable('VS Code');
  logResult('Executable Whitelist Resolution (VS Code)', vsCodeExec !== null && vsCodeExec.windowsCommand === 'code', 'Resolved VS Code to code command');

  // Test 2: Arbitrary Executable Rejection
  const untrustedExec = execRegistry.isTrustedAlias('malicious_hack.exe');
  logResult('Arbitrary Binary Rejection', !untrustedExec, 'Blocked untrusted executable');

  // Test 3: Origin Guard Localhost Check
  const localOrigin = originGuard.isAllowedOrigin('http://127.0.0.1:5173', '127.0.0.1');
  const remoteOrigin = originGuard.isAllowedOrigin('http://external-hacker.com', '192.168.1.50');
  logResult('Origin Guard Localhost Enforcement', localOrigin && !remoteOrigin, 'Allowed 127.0.0.1, blocked remote origin');

  // Test 4: Structured Request Security Validation
  const validReq: NativeBridgeRequest = {
    requestId: 'unit-01',
    capability: 'APPLICATION_CONTROL',
    action: 'OPEN_APPLICATION',
    target: { rawTarget: 'VS Code', applicationAlias: 'VS Code' },
    authorization: { userId: 'user', sessionToken: 'tok', riskLevel: 'LOW', isApproved: true },
    timestamp: new Date().toISOString(),
  };

  const valCheck = securityGuard.validateRequest(validReq);
  logResult('Structured Request Security Validation', valCheck.valid, 'Valid request accepted');

  // Test 5: Arbitrary Binary Request Rejection
  const invalidReq: NativeBridgeRequest = {
    requestId: 'unit-02',
    capability: 'APPLICATION_CONTROL',
    action: 'OPEN_APPLICATION',
    target: { rawTarget: 'c:/arbitrary/cmd.exe', applicationAlias: 'arbitrary' },
    authorization: { userId: 'user', sessionToken: 'tok', riskLevel: 'LOW', isApproved: true },
    timestamp: new Date().toISOString(),
  };

  const invalCheck = securityGuard.validateRequest(invalidReq);
  logResult('Arbitrary Binary Request Rejection', !invalCheck.valid, `Blocked: ${invalCheck.reason}`);

  return { passed: allPassed, results };
}
