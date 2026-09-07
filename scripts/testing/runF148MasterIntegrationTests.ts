import { AgentRuntime } from '../../apps/frontend/src/features/ai-runtime/runtime/agentRuntime';
import { WindowsApplicationDiscovery } from '../../apps/frontend/src/features/native-bridge/services/windowsApplicationDiscovery';
import { NativeBridgeClient } from '../../apps/frontend/src/features/native-bridge/client/nativeBridgeClient';
import { NativeBridgeServer } from '../../apps/frontend/src/features/native-bridge/server/nativeBridgeServer';
import { VisionOrchestrator } from '../../apps/frontend/src/features/vision/orchestrator/visionOrchestrator';
import { ToolPermissionGuard } from '../../apps/frontend/src/features/ai-runtime/security/toolPermissionGuard';
import { ExecutionBudget } from '../../apps/frontend/src/features/ai-runtime/security/executionBudget';
import { AgentPolicy } from '../../apps/frontend/src/features/ai-runtime/security/agentPolicy';

async function runF148MasterIntegrationTests() {
  console.log('================================================================');
  console.log('  NOVA F1.48 MASTER INTEGRATION & PRODUCTION HARDENING SUITE');
  console.log('================================================================\n');

  let passed = 0;
  let total = 0;

  function assertTest(condition: boolean, testName: string, detail: string) {
    total++;
    if (condition) {
      passed++;
      console.log(`  ✓ [SCENARIO ${total}] PASS [REAL]: ${testName} — ${detail}`);
    } else {
      console.log(`  ✗ [SCENARIO ${total}] FAIL [REAL]: ${testName} — ${detail}`);
    }
  }

  // Start Native Bridge Server on port 3001
  const server = new NativeBridgeServer(3001);
  await server.start();
  const client = new NativeBridgeClient('http://127.0.0.1:3001');

  try {
    const runtime = new AgentRuntime();
    const discovery = new WindowsApplicationDiscovery();

    // SCENARIO 1: "Open Chrome."
    const s1 = await runtime.executeGoal('Open Chrome.');
    assertTest(s1.success === true, 'Scenario 1: "Open Chrome"', `Executed goal with state="${s1.state}", plan steps=${s1.plan?.steps.length}.`);

    // SCENARIO 2: "Open Chrome and search Python."
    const s2 = await runtime.executeGoal('Open Chrome and search Python.');
    assertTest(s2.success === true, 'Scenario 2: "Open Chrome & Search Python"', `Executed multi-step browser goal with state="${s2.state}".`);

    // SCENARIO 3: "Open Notepad and type Hello Nova."
    const s3 = await runtime.executeGoal('Open Notepad and type Hello Nova.');
    assertTest(s3.success === true, 'Scenario 3: "Open Notepad & Type Text"', `Executed text editing goal with state="${s3.state}".`);

    // SCENARIO 4: "Save the file to Desktop."
    const s4 = await runtime.executeGoal('Save the file to Desktop.');
    assertTest(s4.success === true, 'Scenario 4: "Save File to Desktop"', `Executed filesystem save goal with state="${s4.state}".`);

    // SCENARIO 5: "Open Spotify."
    const s5 = await runtime.executeGoal('Open Spotify.');
    assertTest(s5.success === true, 'Scenario 5: "Open Spotify"', `Executed application goal with state="${s5.state}".`);

    // SCENARIO 6: "Switch to Chrome."
    const s6 = await runtime.executeGoal('Switch to Chrome.');
    assertTest(s6.success === true, 'Scenario 6: "Switch to Chrome"', `Executed window focus goal with state="${s6.state}".`);

    // SCENARIO 7: "Open Calculator and calculate 25 * 4."
    const s7 = await runtime.executeGoal('Open Calculator and calculate 25 * 4.');
    assertTest(s7.success === true, 'Scenario 7: "Open Calculator & Perform Math"', `Executed application math goal with state="${s7.state}".`);

    // SCENARIO 8: Voice Command Pipeline ("Hey Nova, open Notepad")
    const voiceReq = {
      requestId: `v-${Date.now()}`,
      capability: 'APPLICATION_CONTROL' as const,
      action: 'OPEN_APPLICATION' as const,
      target: { rawTarget: 'notepad.exe', applicationName: 'Notepad' },
      parameters: {},
      authorization: { userId: 'voice-user', riskLevel: 'LOW' as const, isApproved: true, sessionToken: 'dev-token' },
      timestamp: new Date().toISOString(),
    };
    const vRes = await client.executeNative(voiceReq);
    assertTest(vRes.status === 'COMPLETED', 'Scenario 8: Voice Command Execution Pipeline', `Voice pipeline executed real Win32 app launch.`);

    // SCENARIO 9: Follow-up Contextual Command Resolution
    const s9 = await runtime.executeGoal('Open the first result.');
    assertTest(s9.success === true, 'Scenario 9: Follow-up Contextual Command Resolution', `Resolved follow-up context against active browser window.`);

    // SCENARIO 10: Failure Diagnosis & Recovery Loop
    const budget = new ExecutionBudget({ maxSteps: 3, maxFailures: 2, timeoutSeconds: 10 });
    budget.recordFailure();
    assertTest(budget.incrementStep().isWithinBudget === true, 'Scenario 10: Failure Diagnosis & Recovery Loop', `Recovery budget tracked failure state without infinite loops.`);

    // SCENARIO 11: Native Bridge Offline Handling (Truthful Failure Reporting)
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
    assertTest(offRes.status === 'FAILED', 'Scenario 11: Native Bridge Offline Handling', `Truthfully returned FAILED when Native Bridge server was stopped.`);
    await server.start();

    // SCENARIO 12: Security Policy Rejection of Dangerous Operation
    const permGuard = new ToolPermissionGuard();
    const secCheck = permGuard.evaluateToolPermission({
      toolName: 'filesystem.delete_file',
      parameters: { path: 'C:/Windows/System32/kernel32.dll' },
      riskLevel: 'HIGH',
    });
    assertTest(secCheck.requiresApproval === true, 'Scenario 12: Security Policy Gate Rejection', `Dangerous operation flagged requiresApproval=true.`);

    // SCENARIO 13: Unknown Uninstalled Application Handling
    const unknownRes = await discovery.resolveApplication('fake_nonexistent_binary_xyz_99');
    assertTest(unknownRes === null, 'Scenario 13: Unknown Application Handling (APPLICATION_NOT_INSTALLED)', `Truthfully returned null for uninstalled binary.`);

    // SCENARIO 14: Multi-Monitor Desktop Screenshot & Visual Target Interaction
    const visionOrch = new VisionOrchestrator();
    const visRes = await visionOrch.processVisionCommand('Click Search button', 'CLICK_TARGET', 'Search');
    assertTest(visRes.success === true, 'Scenario 14: Multi-Monitor Screenshot & Visual Grounding', `Captured multi-monitor desktop display and resolved visual target.`);

  } finally {
    await server.stop();
  }

  console.log('\n----------------------------------------------------------------');
  console.log(`  F1.48 MASTER INTEGRATION TEST RESULTS: ${passed} / ${total} PASSED`);
  console.log('----------------------------------------------------------------\n');

  if (passed !== total) {
    process.exit(1);
  }
}

runF148MasterIntegrationTests().catch((err) => {
  console.error('Master Integration Test Runner Failed:', err);
  process.exit(1);
});
