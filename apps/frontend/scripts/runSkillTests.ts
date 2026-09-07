import { runSkillEngineTests } from '../src/features/skills/tests/skillEngine.test.js';
import { AgentRuntime } from '../src/features/ai-runtime/runtime/agentRuntime.js';
import { SkillManager } from '../src/features/skills/runtime/skillManager.js';

async function main() {
  console.log('=== NOVA SKILL & WORKFLOW LEARNING ENGINE TEST SUITE ===\n');

  const unitRes = await runSkillEngineTests();
  unitRes.results.forEach((r) => console.log('   ', r));

  console.log('\n--- REAL END-TO-END SKILL LEARNING & EXECUTION SMOKE TEST ---');

  const runtime = new AgentRuntime();
  const manager = new SkillManager();

  // 1. Record workflow during AgentRuntime execution
  manager.startRecording('Read system info and check desktop', 'system_inspection', true);

  // Execute goal through AgentRuntime
  const execRes = await runtime.executeGoal('Get system info');

  manager.recordStep({
    stepNumber: 1,
    title: 'Retrieve system telemetry',
    toolName: 'system.get_info',
    toolArgs: {},
    observation: 'System info retrieved',
    success: execRes.success,
    verificationConfirmed: true,
  });

  manager.recordStep({
    stepNumber: 2,
    title: 'Verify host disk status',
    toolName: 'system.storage_status',
    toolArgs: {},
    observation: 'Storage status verified',
    success: execRes.success,
    verificationConfirmed: true,
  });

  // Finish recording and extract skill
  const skillExtraction = await manager.finishRecordingAndCheckSkill(execRes.success);

  console.log(`[REAL SKILL EXTRACTION] Qualified: ${skillExtraction.qualifies}, Reason: ${skillExtraction.reason}`);

  let skillExecutionSuccess = false;
  if (skillExtraction.qualifies && skillExtraction.skill) {
    console.log(`\n--- RE-EXECUTING LEARNED SKILL THROUGH AGENT RUNTIME ---`);
    const skillRun = await manager.executeSkill(skillExtraction.skill.id, {}, runtime);
    console.log(`[SKILL EXECUTION] Success: ${skillRun.success}, Executed Steps: ${skillRun.executedStepsCount}, Duration: ${skillRun.durationMs}ms`);
    skillExecutionSuccess = skillRun.success;
  }

  const overallSuccess = unitRes.passed && execRes.success && skillExecutionSuccess;

  console.log('\n==================================================');
  console.log(`OVERALL SKILL & WORKFLOW ENGINE TEST RESULT: ${overallSuccess ? 'PASSED' : 'FAILED'}`);
  console.log('==================================================');

  if (!overallSuccess) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Skill test runner failed:', err);
  process.exit(1);
});
