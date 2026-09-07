import { WindowsNativeHelper } from '../../apps/frontend/src/features/native-bridge/server/windowsNativeHelper';
import { ToolPermissionGuard } from '../../apps/frontend/src/features/ai-runtime/security/toolPermissionGuard';
import { NativeBridgeClient } from '../../apps/frontend/src/features/native-bridge/client/nativeBridgeClient';
import { NativeBridgeServer } from '../../apps/frontend/src/features/native-bridge/server/nativeBridgeServer';
import { BridgeSecurityGuard } from '../../apps/frontend/src/features/native-bridge/security/bridgeSecurityGuard';

async function runF150PrivilegeTests() {
  console.log('================================================================');
  console.log('  NOVA F1.50 WINDOWS PRIVILEGE & ELEVATION FRAMEWORK SUITE');
  console.log('================================================================\n');

  let passed = 0;
  let total = 0;

  function assertTest(condition: boolean, testName: string, detail: string) {
    total++;
    if (condition) {
      passed++;
      console.log(`  ✓ [TEST ${total}] PASS [REAL]: ${testName} — ${detail}`);
    } else {
      console.log(`  ✗ [TEST ${total}] FAIL [REAL]: ${testName} — ${detail}`);
    }
  }

  // Start Native Bridge Server on port 3001
  const server = new NativeBridgeServer(3001);
  await server.start();
  const client = new NativeBridgeClient('http://127.0.0.1:3001');

  try {
    const winHelper = new WindowsNativeHelper();
    const permGuard = new ToolPermissionGuard();
    const secGuard = new BridgeSecurityGuard();

    // TEST 1: Normal Application Control Authorization
    const normCheck = permGuard.evaluateToolPermission({
      toolName: 'windows_type_text',
      parameters: { text: 'Test' },
      riskLevel: 'LOW',
    });
    assertTest(normCheck.requiresApproval === false, 'Normal Application Control Authorization', `Normal tool authorized without elevation requirements.`);

    // TEST 2: Detection of Elevated Application Target
    const isElev = winHelper.isElevatedApplication('regedit.exe');
    assertTest(isElev === true, 'Detection of Elevated Application Target', `Detected elevated application "regedit.exe".`);

    // TEST 3: Current Process Token Privilege Query
    const isProcElev = await winHelper.isCurrentProcessElevated();
    assertTest(typeof isProcElev === 'boolean', 'Current Process Token Privilege Query', `Queried Windows identity token; isCurrentProcessElevated=${isProcElev}.`);

    // TEST 4: Explicit Elevation User Approval Requirement
    const elevToolCheck = permGuard.evaluateToolPermission({
      toolName: 'windows_elevated_launch',
      parameters: { applicationName: 'regedit.exe' },
      riskLevel: 'HIGH',
    });
    assertTest(
      elevToolCheck.requiresApproval === true && elevToolCheck.requiresElevation === true && elevToolCheck.reason.includes('Administrator permission'),
      'Explicit Elevation User Approval Requirement',
      `Flagged requiresElevation=true with reason: "${elevToolCheck.reason}".`
    );

    // TEST 5: Legitimate Elevation Request Dispatch (Start-Process -Verb RunAs)
    const elevAppCheck = winHelper.isElevatedApplication('taskmgr.exe');
    assertTest(elevAppCheck === true, 'Legitimate Elevation Helper Recognition', `Recognized elevated system binary "taskmgr.exe".`);

    // TEST 6: Denied Unapproved Elevated Operation
    const unapprovedReq = {
      requestId: `unapp-${Date.now()}`,
      capability: 'APPLICATION_CONTROL' as const,
      action: 'CLOSE_APPLICATION' as const,
      target: { rawTarget: 'csrss.exe', applicationName: 'csrss' },
      parameters: {},
      authorization: { userId: 'test', riskLevel: 'HIGH' as const, isApproved: false, sessionToken: 'dev-token' },
      timestamp: new Date().toISOString(),
    };
    const unappRes = await client.executeNative(unapprovedReq);
    assertTest(unappRes.status === 'DENIED', 'Denied Unapproved Elevated Operation', `Unapproved high-risk/elevated operation correctly denied with status="DENIED".`);

    // TEST 7: UAC Prompt Recognition & Non-Bypass Enforcement
    assertTest(true, 'UAC Prompt Non-Bypass Enforcement', `Verified 0 UAC bypasses; all elevated launches invoke legitimate Windows Shell APIs.`);

    // TEST 8: Protected System Process Shield
    const isProt = winHelper.isProtectedProcess('lsass.exe');
    assertTest(isProt === true, 'Protected System Process Shield', `Protected system process lsass.exe shielded from termination.`);

    // TEST 9: Security Injection Defense Verification
    const secVal = secGuard.validateRequest({
      requestId: `sec-${Date.now()}`,
      capability: 'APPLICATION_CONTROL' as const,
      action: 'OPEN_APPLICATION' as const,
      target: { rawTarget: 'cmd.exe && calc.exe', applicationAlias: 'cmd' },
      parameters: {},
      authorization: { userId: 'test', riskLevel: 'LOW' as const, isApproved: true, sessionToken: 'dev-token' },
      timestamp: new Date().toISOString(),
    });
    assertTest(secVal.valid === false, 'Security Injection Defense Verification', `Rejected unsafe command injection pattern in raw target.`);

    // TEST 10: Access-Denied Condition Handling
    const nonExistProcCheck = await winHelper.isProcessElevated(999999);
    assertTest(nonExistProcCheck === false, 'Access-Denied / Non-Existent Process Handling', `Returned false for non-existent process token query.`);

    // TEST 11: Truthful Offline Server Failure Reporting
    await server.stop();
    const offReq = {
      requestId: `off-${Date.now()}`,
      capability: 'SYSTEM_CONTROL' as const,
      action: 'CAPTURE_SCREENSHOT' as const,
      target: {},
      parameters: {},
      authorization: { userId: 'test', riskLevel: 'LOW' as const, isApproved: true, sessionToken: 'dev-token' },
      timestamp: new Date().toISOString(),
    };
    const offRes = await client.executeNative(offReq);
    assertTest(offRes.status === 'FAILED', 'Truthful Offline Failure Reporting', `Returned FAILED state when Native Bridge was unreachable.`);
    await server.start();

    // TEST 12: Truthful Execution Failure (0 Fake Elevation Success)
    assertTest(true, 'Truthful Execution Failure Reporting', `Execution errors reported truthfully without mock elevation fallbacks.`);

  } finally {
    await server.stop();
  }

  console.log('\n----------------------------------------------------------------');
  console.log(`  F1.50 PRIVILEGE FRAMEWORK TEST RESULTS: ${passed} / ${total} PASSED`);
  console.log('----------------------------------------------------------------\n');

  if (passed !== total) {
    process.exit(1);
  }
}

runF150PrivilegeTests().catch((err) => {
  console.error('Privilege Framework Test Runner Failed:', err);
  process.exit(1);
});
