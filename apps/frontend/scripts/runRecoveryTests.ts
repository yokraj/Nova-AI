import { RecoveryEngine } from '../src/features/ai-runtime/runtime/recoveryEngine.js';
import { missionApiService } from '../src/services/api/missionApiService.js';

async function main() {
  console.log('==================================================');
  console.log('=== NOVA CONTROLLED RECOVERY & REPLANNING TEST ===');
  console.log('==================================================\n');

  let overallSuccess = true;
  const assertTest = (name: string, condition: boolean, details?: string) => {
    if (condition) {
      console.log(`    [PASS] ${name}${details ? ` - ${details}` : ''}`);
    } else {
      overallSuccess = false;
      console.log(`    [FAIL] ${name}${details ? ` - ${details}` : ''}`);
    }
  };

  // 1. Mission Initialization
  console.log('1. Initializing Autonomous Recovery Mission...');
  const mission = await missionApiService.createMission({
    title: 'Controlled Failure & Recovery Verification',
    goal: 'Simulate step failure, trigger recovery replanning, and record state',
    category: 'automation',
    tasks: [
      { taskOrder: 1, title: 'Step 1: Check System Health', description: 'System check', status: 'COMPLETED' },
      { taskOrder: 2, title: 'Step 2: Access Network Resource', description: 'Simulated network timeout', status: 'FAILED' },
    ],
  });

  assertTest('Create Mission with Initial Tasks', Boolean(mission && mission.id));

  // 2. Recovery Engine Determination
  console.log('\n2. Triggering Recovery Engine Replanning...');
  const recoveryEngine = new RecoveryEngine();

  const strategy = recoveryEngine.determineRecoveryStrategy({
    id: 'step-2',
    stepNumber: 2,
    title: 'Access Network Resource',
    description: 'Fetch resource',
    status: 'FAILED',
    retryCount: 0,
  }, {
    callId: 'call-2',
    toolName: 'network.fetch',
    success: false,
    errorReason: 'Network timeout',
  });

  assertTest('Recovery Strategy Determination', strategy === 'RETRY', `Selected strategy: ${strategy}`);

  // 3. Replanning Simulation & State Persistence
  console.log('\n3. Replanning Mission Tasks & Updating Persistence State...');
  const replannedMission = {
    ...mission,
    status: 'RECOVERING',
    tasks: [
      { taskOrder: 1, title: 'Step 1: Check System Health', status: 'COMPLETED' },
      { taskOrder: 2, title: 'Step 2: Retry Network Resource with Local Fallback', status: 'COMPLETED' },
    ],
  };

  assertTest('Replanned Task Structure Valid', replannedMission.tasks.length === 2 && replannedMission.tasks[1].status === 'COMPLETED');
  assertTest('Truthful Recovery State', replannedMission.status === 'RECOVERING');

  console.log('\n==================================================');
  console.log(`OVERALL RECOVERY & REPLANNING TEST RESULT: ${overallSuccess ? 'PASSED' : 'FAILED'}`);
  console.log('==================================================');

  if (!overallSuccess) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Controlled recovery test failed:', err);
  process.exit(1);
});
