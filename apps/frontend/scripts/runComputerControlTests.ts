import { NativeBridgeServer } from '../src/features/native-bridge/server/nativeBridgeServer.js';
import { ComputerOrchestrator } from '../src/features/computer-control/orchestrator/computerOrchestrator.js';
import { CoordinateGuard } from '../src/features/computer-control/security/coordinateGuard.js';
import { UITargetResolver } from '../src/features/computer-control/resolvers/uiTargetResolver.js';
import { ComputerSecurityPolicy } from '../src/features/computer-control/security/computerSecurityPolicy.js';
import { ToolRegistry } from '../src/features/ai-runtime/tool-router/toolRegistry.js';
import { ToolExecutor } from '../src/features/ai-runtime/tool-router/toolExecutor.js';

async function runComputerControlTests() {
  console.log('=== NOVA REAL COMPUTER CONTROL & CROSS-APP AUTOMATION TEST SUITE ===\n');

  const server = new NativeBridgeServer();
  const orchestrator = new ComputerOrchestrator();
  const coordGuard = new CoordinateGuard();
  const targetResolver = new UITargetResolver();
  const securityPolicy = new ComputerSecurityPolicy();
  const registry = new ToolRegistry();
  const executor = new ToolExecutor();

  const results: { test: string; success: boolean; detail: string }[] = [];
  let allPassed = true;

  const logResult = (test: string, success: boolean, detail: string) => {
    console.log(`    [${success ? 'PASS' : 'FAIL'}] COMPUTER CONTROL TEST: ${test} - ${detail}`);
    results.push({ test, success, detail });
    if (!success) allPassed = false;
  };

  const serverStarted = await server.start(3001);
  logResult('Native Bridge Server Start', serverStarted, 'Server bound to 127.0.0.1:3001');

  try {
    // 1. Tool Registry Verification
    const computerTools = ['computer.click', 'computer.type_text', 'computer.observe_screen', 'computer.close_window'];
    const toolsRegistered = computerTools.every((t) => registry.getTool(t) !== undefined);
    logResult('Computer Control Tools Registered', toolsRegistered, `Registered ${computerTools.length} computer tools in ToolRegistry`);

    // 2. Coordinate Safety Validation
    const validCoord = coordGuard.validateCoordinates(500, 400);
    const invalidCoord = coordGuard.validateCoordinates(-50, 5000);
    logResult(
      'Mouse Coordinate Safety Validation',
      validCoord.valid && !invalidCoord.valid,
      `Valid (500, 400): ${validCoord.valid}, Invalid (-50, 5000) rejected: ${!invalidCoord.valid}`
    );

    // 3. UI Target Resolution & Confidence Thresholding
    const obs = await orchestrator.observeScreen();
    const resolved = targetResolver.resolveTarget({ targetType: 'BUTTON', query: 'Save' }, obs);
    logResult(
      'UI Target Resolution & Confidence',
      resolved.confidence >= 0.85 && resolved.label.includes('Save'),
      `Target "${resolved.label}" resolved at (${resolved.resolvedX}, ${resolved.resolvedY}) with ${Math.round(resolved.confidence * 100)}% confidence`
    );

    // 4. Safe Mouse Movement & Click
    const clickRes = await orchestrator.executeMouseAction('CLICK', undefined, 500, 400);
    logResult('Safe Mouse Click Execution', clickRes.success && clickRes.verifiedState, `Clicked at (500, 400) - Status: ${clickRes.message}`);

    // 5. Text Typing Execution
    const typeRes = await orchestrator.executeKeyboardAction('TYPE_TEXT', 'Hello Nova Computer Control');
    logResult('Text Typing Execution', typeRes.success && typeRes.verifiedState, `Typed text - Status: ${typeRes.message}`);

    // 6. Key Combination Execution (Ctrl+C / Ctrl+V)
    const comboRes = await orchestrator.executeKeyboardAction('KEY_COMBINATION', undefined, undefined, ['Ctrl', 'C']);
    logResult('Key Combination Execution (Ctrl+C)', comboRes.success && comboRes.verifiedState, `Shortcut - Status: ${comboRes.message}`);

    // 7. Window Discovery & Focus
    const winRes = await orchestrator.executeWindowAction('FOCUS_WINDOW', 'Google Chrome', 'chrome.exe');
    logResult('Window Discovery & Foreground Focus', winRes.success, `Window focus - Status: ${winRes.message}`);

    // 8. Clipboard Read Verification
    const clipRes = await orchestrator.getClipboard();
    logResult('Clipboard Operations & Verification', clipRes.success, `Clipboard - Status: ${clipRes.message}`);

    // 9. ToolExecutor Computer Tool Routing
    const toolExecRes = await executor.executeTool({
      callId: 'call-comp-1',
      toolName: 'computer.observe_screen',
      arguments: {},
    });
    logResult('ToolExecutor Computer Tool Integration', toolExecRes.success, `Observation: ${toolExecRes.observationSummary}`);

    // 10. REAL SAFE WINDOWS DESKTOP SMOKE TEST
    console.log('\n--- REAL SAFE WINDOWS COMPUTER CONTROL SMOKE TEST ---');

    // Step A: Launch Application (Notepad)
    const launchRes = await executor.executeTool({
      callId: 'call-smoke-app',
      toolName: 'application.open',
      arguments: { applicationName: 'Notepad' },
    });

    // Step B: Type harmless text
    const typeSmokeRes = await executor.executeTool({
      callId: 'call-smoke-type',
      toolName: 'computer.type_text',
      arguments: { text: 'Nova AI Real Computer Control Verified' },
    });

    // Step C: Select all and copy
    const copySmokeRes = await executor.executeTool({
      callId: 'call-smoke-copy',
      toolName: 'computer.copy',
      arguments: {},
    });

    // Step D: Verify workflow
    const smokePassed = launchRes.success && typeSmokeRes.success && copySmokeRes.success;
    logResult(
      'Real Desktop Workflow Smoke Test',
      smokePassed,
      `Notepad launch: ${launchRes.success}, Type text: ${typeSmokeRes.success}, Copy: ${copySmokeRes.success}`
    );
  } finally {
    await server.stop();
  }

  console.log('\n======================================');
  console.log(`OVERALL COMPUTER CONTROL TEST RESULT: ${allPassed ? 'PASSED' : 'FAILED'}`);
  console.log('======================================\n');

  if (!allPassed) {
    process.exit(1);
  }
}

runComputerControlTests().catch((err) => {
  console.error('Computer Control Test Runner Exception:', err);
  process.exit(1);
});
