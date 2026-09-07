import { NativeBridgeServer } from '../src/features/native-bridge/server/nativeBridgeServer.js';
import { AgentRuntime } from '../src/features/ai-runtime/runtime/agentRuntime.js';
import { auditApiService } from '../src/services/api/auditApiService.js';
import * as fs from 'fs';
import * as path from 'path';

async function main() {
  console.log('==================================================');
  console.log('=== NOVA REAL SAFE E2E WORKFLOW TEST SUITE ===');
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

  // 1. Start Native Bridge Server & AgentRuntime
  const server = new NativeBridgeServer();
  await server.start();

  const runtime = new AgentRuntime();

  const sandboxDir = path.resolve(process.cwd(), '.nova_test_sandbox');
  const demoDir = path.join(sandboxDir, 'NovaAgentTest');
  const readmePath = path.join(demoDir, 'test.txt');

  // Clean prior sandbox if exists
  if (fs.existsSync(sandboxDir)) {
    fs.rmSync(sandboxDir, { recursive: true, force: true });
  }

  // E2E Goal: "Create NovaAgentTest on Desktop"
  const goal = 'Create NovaAgentTest on Desktop';

  console.log(`[E2E PIPELINE] Executing Goal: ${goal}`);
  const result = await runtime.executeGoal(goal);

  assertTest('AgentRuntime E2E Goal Execution', result.state === 'COMPLETED', `Result state: ${result.state}`);
  assertTest('Real Sandbox Directory Creation', fs.existsSync(demoDir), `Path: ${demoDir}`);
  assertTest('Real README/Test File Creation', fs.existsSync(readmePath), `Path: ${readmePath}`);

  if (fs.existsSync(readmePath)) {
    const content = fs.readFileSync(readmePath, 'utf-8');
    assertTest('Real File Content Verification', content.includes('Hello Nova Agent'), 'Content validated');
  }

  // Audit Logging Verification
  const audit = await auditApiService.recordAuditEvent({
    eventType: 'REAL_E2E_WORKFLOW_VERIFICATION',
    action: 'workflow.execute',
    toolName: 'agent_runtime.execute_goal',
    riskLevel: 'SAFE',
    actor: 'E2ETestRunner',
    decision: 'ALLOWED',
    details: { goal, stepsCount: result.stepsExecuted },
  });

  assertTest('Audit Logging Verification', Boolean(audit && audit.id));

  // Cleanup Sandbox
  if (fs.existsSync(sandboxDir)) {
    fs.rmSync(sandboxDir, { recursive: true, force: true });
  }
  await server.stop();

  console.log('\n==================================================');
  console.log(`OVERALL E2E WORKFLOW TEST RESULT: ${overallSuccess ? 'PASSED' : 'FAILED'}`);
  console.log('==================================================');

  if (!overallSuccess) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Real E2E workflow test failed:', err);
  process.exit(1);
});
