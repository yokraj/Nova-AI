import { runAgentRuntimeTests } from '../src/features/ai-runtime/tests/agentRuntime.test.js';
import { AgentRuntime } from '../src/features/ai-runtime/runtime/agentRuntime.js';

async function main() {
  console.log('=== NOVA AGENT RUNTIME & AUTONOMOUS EXECUTION LOOP TEST SUITE ===\n');

  const res = await runAgentRuntimeTests();
  res.results.forEach((r) => console.log('   ', r));

  console.log('\n--- REAL END-TO-END SMOKE TEST ---');
  const runtime = new AgentRuntime();
  const e2eRes = await runtime.executeGoal('Create NovaAgentTest on Desktop');

  console.log(`[E2E RESULT] Status: ${e2eRes.state}, Summary: ${e2eRes.summary}`);

  console.log('\n======================================');
  console.log(`OVERALL AGENT RUNTIME TEST RESULT: ${res.passed && e2eRes.success ? 'PASSED' : 'FAILED'}`);
  console.log('======================================');

  if (!res.passed || !e2eRes.success) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Test runner failed:', err);
  process.exit(1);
});
