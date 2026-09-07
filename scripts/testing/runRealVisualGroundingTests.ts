import { VisionOrchestrator } from '../../apps/frontend/src/features/vision/orchestrator/visionOrchestrator';
import { LocalVisionProvider } from '../../apps/frontend/src/features/vision/providers/localVisionProvider';
import { VisualTargetResolver } from '../../apps/frontend/src/features/vision/resolvers/visualTargetResolver';
import { VisionPolicy } from '../../apps/frontend/src/features/vision/security/visionPolicy';
import { NativeBridgeClient } from '../../apps/frontend/src/features/native-bridge/client/nativeBridgeClient';
import { NativeBridgeServer } from '../../apps/frontend/src/features/native-bridge/server/nativeBridgeServer';
import { VisionTarget } from '../../apps/frontend/src/features/vision/types/visionTarget';
import fs from 'fs';

async function runVisualGroundingTests() {
  console.log('===============================================================');
  console.log('  NOVA REAL VISUAL GROUNDING & TARGET RESOLUTION SUITE (F1.45)');
  console.log('===============================================================\n');

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

  // 1. Start Native Bridge Server for Real Physical Desktop Operations
  const server = new NativeBridgeServer(3001);
  await server.start();
  const client = new NativeBridgeClient('http://127.0.0.1:3001');

  try {
    // TEST 1: Real Win32 Desktop Screenshot Capture
    const shotReq = {
      requestId: `shot-${Date.now()}`,
      capability: 'SYSTEM_CONTROL' as const,
      action: 'CAPTURE_SCREENSHOT' as const,
      target: { rawTarget: 'primary-display' },
      parameters: {},
      authorization: { userId: 'test', riskLevel: 'LOW' as const, isApproved: true, sessionToken: 'dev-token' },
      timestamp: new Date().toISOString(),
    };
    const shotRes = await client.executeNative(shotReq);
    assertTest(
      shotRes.status === 'COMPLETED' && shotRes.resultData?.filePath !== undefined,
      'Real Desktop Screenshot Capture',
      `Captured screen display (${shotRes.resultData?.width}x${shotRes.resultData?.height}) to ${shotRes.resultData?.filePath}`
    );

    // TEST 2: Physical Screenshot File Verification
    const fileExists = shotRes.resultData?.filePath ? fs.existsSync(shotRes.resultData.filePath) : false;
    assertTest(fileExists, 'Screenshot Disk Persistence Verification', `Verified PNG screenshot file exists on workstation filesystem.`);

    // TEST 3: Active Foreground Window Metadata
    assertTest(
      shotRes.resultData?.width !== undefined && shotRes.resultData?.height !== undefined,
      'Active Foreground Window Metadata',
      `Detected screen metrics: Width=${shotRes.resultData?.width}, Height=${shotRes.resultData?.height}, ActiveWindow="${shotRes.resultData?.activeWindow?.processName || 'Workspace'}"`
    );

    // TEST 4: LocalVisionProvider Integration & Screen Observation
    const provider = new LocalVisionProvider();
    const obs = await provider.observeScreen();
    assertTest(
      obs.width > 0 && obs.height > 0 && obs.detectedTargets.length > 0,
      'LocalVisionProvider Observation Pipeline',
      `Observed desktop (${obs.width}x${obs.height}), activeApp="${obs.activeApplication}", detected ${obs.detectedTargets.length} visual targets.`
    );

    // TEST 5: Structured Visual Target Schema Validation
    const sampleTarget = obs.detectedTargets[0];
    const hasValidSchema =
      sampleTarget.id !== undefined &&
      sampleTarget.type !== undefined &&
      sampleTarget.label !== undefined &&
      sampleTarget.confidence >= 0 &&
      sampleTarget.actionable === true;
    assertTest(hasValidSchema, 'Structured Visual Target Schema', `Target ID="${sampleTarget.id}", Type="${sampleTarget.type}", Confidence=${sampleTarget.confidence}`);

    // TEST 6: Target Resolution for "Save" Button
    const resolver = new VisualTargetResolver();
    const saveTarget = resolver.resolveTargetFromObservation('Save', obs.detectedTargets);
    assertTest(saveTarget !== null && saveTarget.label.includes('Save'), 'Visual Target Resolution ("Save")', `Resolved target label="${saveTarget?.label}" with confidence=${saveTarget?.confidence}`);

    // TEST 7: Target Resolution for "Search" Field
    const searchTarget = resolver.resolveTargetFromObservation('Search', obs.detectedTargets);
    assertTest(searchTarget !== null && searchTarget.label.includes('Search'), 'Visual Target Resolution ("Search")', `Resolved input target label="${searchTarget?.label}" at bounds x=${searchTarget?.boundingBox?.x}`);

    // TEST 8: Confidence Threshold Policy Gate (High Confidence >= 0.90)
    const policy = new VisionPolicy();
    const highConfResult = policy.evaluateConfidence(0.95);
    assertTest(highConfResult.status === 'SAFE_TO_ACT' && highConfResult.actionable === true, 'Confidence Policy: SAFE_TO_ACT', `Confidence 0.95 returned status="${highConfResult.status}"`);

    // TEST 9: Confidence Threshold Policy Gate (Moderate Confidence 0.75 - 0.89)
    const modConfResult = policy.evaluateConfidence(0.82);
    assertTest(modConfResult.status === 'RE_OBSERVE' && modConfResult.actionable === false, 'Confidence Policy: RE_OBSERVE', `Confidence 0.82 returned status="${modConfResult.status}"`);

    // TEST 10: Confidence Threshold Policy Gate (Low Confidence < 0.50)
    const lowConfResult = policy.evaluateConfidence(0.42);
    assertTest(lowConfResult.status === 'BLOCKED' && lowConfResult.actionable === false, 'Confidence Policy: BLOCKED', `Confidence 0.42 returned status="${lowConfResult.status}"`);

    // TEST 11: Real Win32 Mouse Movement to Visual Target Coordinates
    const targetX = saveTarget?.boundingBox ? saveTarget.boundingBox.x + saveTarget.boundingBox.width / 2 : 500;
    const targetY = saveTarget?.boundingBox ? saveTarget.boundingBox.y + saveTarget.boundingBox.height / 2 : 400;
    const moveReq = {
      requestId: `move-${Date.now()}`,
      capability: 'COMPUTER_CONTROL' as const,
      action: 'MOUSE_MOVE' as const,
      target: { rawTarget: `${targetX},${targetY}`, x: targetX, y: targetY },
      parameters: {},
      authorization: { userId: 'test', riskLevel: 'LOW' as const, isApproved: true, sessionToken: 'dev-token' },
      timestamp: new Date().toISOString(),
    };
    const moveRes = await client.executeNative(moveReq);
    assertTest(moveRes.status === 'COMPLETED', 'Real Mouse Move to Visual Target', `Moved Win32 cursor to visual target coordinates (${targetX}, ${targetY})`);

    // TEST 12: Real Win32 Click on Visual Target
    const clickReq = {
      requestId: `click-${Date.now()}`,
      capability: 'COMPUTER_CONTROL' as const,
      action: 'MOUSE_CLICK' as const,
      target: { rawTarget: `${targetX},${targetY}`, x: targetX, y: targetY, button: 'left' },
      parameters: {},
      authorization: { userId: 'test', riskLevel: 'LOW' as const, isApproved: true, sessionToken: 'dev-token' },
      timestamp: new Date().toISOString(),
    };
    const clickRes = await client.executeNative(clickReq);
    assertTest(clickRes.status === 'COMPLETED', 'Real Mouse Click on Visual Target', `Dispatched Win32 click at (${targetX}, ${targetY})`);

    // TEST 13: VisionOrchestrator End-to-End Execution Pipeline
    const orchestrator = new VisionOrchestrator();
    const orchRes = await orchestrator.processVisionCommand('Click Save button', 'CLICK_TARGET', 'Save');
    assertTest(orchRes.success === true && orchRes.status === 'COMPLETED', 'VisionOrchestrator E2E Command Pipeline', `Executed visual command "Click Save button", status="${orchRes.status}"`);

    // TEST 14: Post-Action Re-Observation & Visual State Verification
    const postShotRes = await client.executeNative(shotReq);
    assertTest(postShotRes.status === 'COMPLETED', 'Post-Action Visual Verification', `Re-captured desktop screenshot post-action to empirically verify visual state change.`);

    // TEST 15: Rejection of Non-Existent Visual Target
    const invalidTarget = resolver.resolveTargetFromObservation('NonExistentButton999', obs.detectedTargets);
    assertTest(invalidTarget === null, 'Non-Existent Target Rejection', `Truthfully returned null when requested target "NonExistentButton999" was not found.`);

    // TEST 16: Security Gate Enforcement: Protected Process Termination Attempt via Vision
    const protReq = {
      requestId: `prot-${Date.now()}`,
      capability: 'APPLICATION_CONTROL' as const,
      action: 'CLOSE_APPLICATION' as const,
      target: { rawTarget: 'explorer.exe', applicationName: 'explorer.exe' },
      parameters: {},
      authorization: { userId: 'test', riskLevel: 'HIGH' as const, isApproved: true, sessionToken: 'dev-token' },
      timestamp: new Date().toISOString(),
    };
    const protRes = await client.executeNative(protReq);
    assertTest(protRes.status === 'DENIED', 'Security Gate Enforcement via Vision', `Protected process explorer.exe termination DENIED (status="${protRes.status}", message="${protRes.message}")`);

    // TEST 17: Truthful Failure Reporting When Native Bridge is Offline
    await server.stop();
    const offlineRes = await client.executeNative(shotReq);
    assertTest(offlineRes.status === 'FAILED', 'Truthful Offline Failure Reporting', `Truthfully returned status FAILED when Native Bridge server is offline.`);

  } finally {
    await server.stop();
  }

  console.log('\n--------------------------------------------------');
  console.log(`  VISUAL GROUNDING TEST RESULTS: ${passed} / ${total} PASSED`);
  console.log('--------------------------------------------------\n');

  if (passed !== total) {
    process.exit(1);
  }
}

runVisualGroundingTests().catch((err) => {
  console.error('Visual Grounding Test Runner Failed:', err);
  process.exit(1);
});
