import { NativeBridgeServer } from '../src/features/native-bridge/server/nativeBridgeServer';
import { MockCommandRouter } from '../src/features/universal-command/mock/mockCommandRouter';
import { MockExecutionEngine } from '../src/features/universal-command/mock/mockExecutionEngine';
import { exec } from 'child_process';

let totalTests = 0;
let passedTests = 0;

function assert(condition: boolean, description: string) {
  totalTests++;
  if (condition) {
    passedTests++;
    console.log(`  ✓ PASS: ${description}`);
  } else {
    console.error(`  ✗ FAIL: ${description}`);
  }
}

function isWindowsProcessRunning(processName: string): Promise<boolean> {
  return new Promise((resolve) => {
    exec('tasklist', (err, stdout) => {
      if (err || !stdout) {
        resolve(false);
        return;
      }
      resolve(stdout.toLowerCase().includes(processName.toLowerCase()));
    });
  });
}

function killWindowsProcess(processName: string): Promise<void> {
  return new Promise((resolve) => {
    exec(`taskkill /F /IM "${processName}"`, () => resolve());
  });
}

async function runRealCommandExecutionTests() {
  console.log('\n==================================================');
  console.log('  NOVA REAL COMMAND EXECUTION PATH E2E TESTS');
  console.log('==================================================\n');

  const router = new MockCommandRouter();
  const engine = new MockExecutionEngine();
  const bridgeServer = new NativeBridgeServer();
  const port = 3001;

  // Start Native Bridge Server for online security & execution tests
  const serverStarted = await bridgeServer.start(port);
  assert(serverStarted, 'Native Bridge server started on 127.0.0.1:3001');

  try {
    // TEST 1: Real Application Execution ("hey Nova open Notepad")
    console.log('\n[Phase 1: Real Native Execution Verification]');
    const input = 'hey Nova open Notepad';
    const routedCmd = router.routeCommand(input, 'TEXT');

    assert(
      routedCmd.intent.category === 'APPLICATION_CONTROL',
      '"hey Nova open Notepad" resolves to intent category APPLICATION_CONTROL'
    );
    assert(
      routedCmd.intent.extractedAction === 'OPEN_APPLICATION',
      'Action resolves to OPEN_APPLICATION'
    );

    // Clean up notepad first if already running
    await killWindowsProcess('notepad.exe');

    // Execute command through real engine -> orchestrator -> native client -> native bridge
    const executedCmd = await engine.executeCommand(routedCmd);

    assert(
      executedCmd.executionState === 'COMPLETED',
      'Execution state progresses to COMPLETED after native launch'
    );
    assert(
      executedCmd.result !== undefined && executedCmd.result.success === true,
      'Command result reports success = true'
    );

    // Verify Notepad is physically running on Windows OS
    const isNotepadActive = await isWindowsProcessRunning('notepad.exe');
    assert(
      isNotepadActive,
      'REAL OS VERIFICATION: notepad.exe is physically running on Windows OS'
    );

    // Clean up launched notepad process
    await killWindowsProcess('notepad.exe');

    // TEST 2: Untrusted Executable Blocked
    console.log('\n[Phase 2: Untrusted Executable Security Gate]');
    const untrustedInput = 'open untrusted_malware.exe';
    const untrustedCmd = router.routeCommand(untrustedInput, 'TEXT');
    const untrustedResult = await engine.executeCommand(untrustedCmd);

    assert(
      untrustedResult.executionState === 'FAILED' || untrustedResult.executionState === 'DENIED',
      'Untrusted executable launch attempt is blocked'
    );

    // TEST 3: Protected Process Guard
    console.log('\n[Phase 3: Protected Process Security Gate]');
    const terminateProtectedInput = 'close explorer.exe';
    const protectedCmd = router.routeCommand(terminateProtectedInput, 'TEXT');
    const protectedResult = await engine.executeCommand(protectedCmd);

    assert(
      protectedResult.executionState === 'FAILED' || protectedResult.executionState === 'DENIED',
      'Protected process termination attempt (explorer.exe) is DENIED'
    );

    assert(
      (protectedResult.result?.errorReason as string) === 'PROTECTED_PROCESS' || (protectedResult.result?.message || '').toLowerCase().includes('protected'),
      'Native Bridge correctly returns PROTECTED_PROCESS error reason'
    );



    // TEST 4: Path Traversal Protection
    console.log('\n[Phase 4: Path Traversal Protection]');
    const maliciousPathInput = 'open ../../windows/system32/cmd.exe';
    const pathCmd = router.routeCommand(maliciousPathInput, 'TEXT');
    const pathResult = await engine.executeCommand(pathCmd);

    assert(
      pathResult.executionState === 'FAILED' || pathResult.executionState === 'DENIED',
      'Path traversal attempt is rejected by application resolver'
    );
  } finally {
    await bridgeServer.stop();
  }

  // TEST 5: Native Bridge Unavailable Failure Handling
  console.log('\n[Phase 5: Native Bridge Offline Failure Handling]');
  const offlineInput = 'open Notepad';
  const offlineCmd = router.routeCommand(offlineInput, 'TEXT');
  const failedCmd = await engine.executeCommand(offlineCmd);

  assert(
    failedCmd.executionState === 'FAILED',
    'Execution state is FAILED when Native Bridge server is offline'
  );
  assert(
    failedCmd.result !== undefined && failedCmd.result.success === false,
    'Command result reports success = false when Native Bridge is offline'
  );
  assert(
    failedCmd.result?.message.includes('Native Bridge is unavailable') || false,
    'Truthful error message displayed: "Native Bridge is unavailable. Start Nova Native Bridge on port 3001."'
  );

  console.log('\n--------------------------------------------------');
  console.log(`  RESULTS: ${passedTests} / ${totalTests} PASSED`);
  console.log('--------------------------------------------------\n');

  if (passedTests !== totalTests) {
    process.exitCode = 1;
  } else {
    process.exitCode = 0;
  }
}

runRealCommandExecutionTests().catch((err) => {
  console.error('Test execution error:', err);
  process.exit(1);
});

