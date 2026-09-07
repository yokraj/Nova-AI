import { DemonstrationRecorder } from '../src/features/workflow-studio/recorder/demonstrationRecorder.js';
import { WorkflowBuilder } from '../src/features/workflow-studio/studio/workflowBuilder.js';
import { SwarmReplayEngine } from '../src/features/workflow-studio/replay/swarmReplayEngine.js';
import { WorkflowStore } from '../src/features/workflow-studio/persistence/workflowStore.js';
import { WorkflowDefinition, WorkflowNode } from '../src/features/workflow-studio/types/workflowStudio.js';

async function main() {
  console.log('==================================================');
  console.log('=== NOVA WORKFLOW STUDIO & REPLAY SUITE ===');
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

  // 1. Start Recording Session
  const recorder = new DemonstrationRecorder();
  const session = recorder.startRecording('Test Desktop Workflow');
  assertTest('1. Start Recording Session', Boolean(session && session.isRecording), `Session ID: ${session.sessionId}`);

  // 2. Record Actions
  recorder.recordAction({
    actionType: 'NAVIGATE',
    capability: 'BROWSER_CONTROL',
    toolName: 'browser_navigate',
    arguments: { url: 'https://example.com' },
    activeApp: 'Chrome Browser',
  });
  recorder.recordAction({
    actionType: 'CLICK',
    capability: 'COMPUTER_CONTROL',
    toolName: 'click_coordinate',
    arguments: { x: 400, y: 300 },
    activeApp: 'Desktop Workstation',
  });
  const activeSess = recorder.getActiveSession();
  assertTest('2. Record Actions Stream', activeSess?.recordedActions.length === 2);

  // 3. Stop Recording & Convert to Workflow
  const finishedSess = recorder.stopRecording();
  assertTest('3. Stop Recording Session', Boolean(finishedSess && !finishedSess.isRecording));
  const convertedWf = recorder.convertSessionToWorkflow(finishedSess!);
  assertTest('3. Session Conversion to Workflow DAG', convertedWf.nodes.length === 3 && convertedWf.edges.length === 2);

  // 4. Add Workflow Node
  const builder = new WorkflowBuilder('Custom Studio Workflow', 'Interactive multi-agent workflow');
  const trigNode = builder.addNode({
    label: 'Trigger Activation',
    type: 'TRIGGER',
    riskLevel: 'SAFE',
    requiresApproval: false,
    x: 100,
    y: 100,
  });
  const actNode = builder.addNode({
    label: 'Open VS Code App',
    type: 'DESKTOP_ACTION',
    capability: 'APPLICATION_CONTROL',
    toolName: 'launch_application',
    arguments: { appName: 'code.exe' },
    riskLevel: 'SAFE',
    requiresApproval: false,
    x: 280,
    y: 100,
  });
  assertTest('4. Add Workflow Node', builder.getWorkflow().nodes.length === 2);

  // 5. Add Workflow Edge
  const edge = builder.addEdge(trigNode.id, actNode.id);
  assertTest('5. Link Workflow Nodes Edge', Boolean(edge && edge.sourceNodeId === trigNode.id));

  // 6. Assign Swarm Role
  const swarmAssigned = builder.assignAgentRole(actNode.id, 'CodeAssistant');
  assertTest('6. Assign Swarm Agent Role', swarmAssigned && builder.getWorkflow().nodes[1].assignedAgentRole === 'CodeAssistant');

  // 7. Topological Order
  const topoOrder = builder.getTopologicalOrder();
  assertTest('7. Topological Graph Ordering', topoOrder[0].id === trigNode.id && topoOrder[1].id === actNode.id);

  // 8. Vision Target Grounding Node
  const visNode = builder.addNode({
    label: 'Locate Submit Button',
    type: 'VISION_GROUNDING',
    capability: 'VISION_CONTROL',
    visualTargetQuery: 'Blue Submit Button',
    riskLevel: 'SAFE',
    requiresApproval: false,
    x: 460,
    y: 100,
  });
  builder.addEdge(actNode.id, visNode.id);
  assertTest('8. Vision Grounding Node Creation', visNode.type === 'VISION_GROUNDING');

  // 9. Risk Level Evaluation
  const highRiskNode = builder.addNode({
    label: 'Delete System Log',
    type: 'DESKTOP_ACTION',
    capability: 'FILE_SYSTEM',
    toolName: 'delete_file',
    arguments: { path: 'C:/temp/log.txt' },
    riskLevel: 'HIGH',
    requiresApproval: true,
    x: 640,
    y: 100,
  });
  builder.addEdge(visNode.id, highRiskNode.id);
  assertTest('9. High Risk Level Flagging', highRiskNode.riskLevel === 'HIGH' && highRiskNode.requiresApproval);

  // 10. Graph Validation
  const valRes = builder.validateWorkflow();
  assertTest('10. DAG Graph Validation', valRes.valid && valRes.errors.length === 0);

  // 11. Swarm Replay Engine Execution
  const replayEngine = new SwarmReplayEngine();
  const wfDef = builder.getWorkflow();
  wfDef.trusted = true; // Trusted for high-risk execution

  console.log('\n12. Executing Workflow Replay via SwarmReplayEngine...');
  const execResult = await replayEngine.replayWorkflow(wfDef, {
    workflowId: wfDef.id,
    enableSwarmDelegation: true,
    verifyVisualStates: false,
    pauseOnApproval: false,
    stepTimeoutMs: 10000,
  });

  console.log('Node Results Details:', JSON.stringify(execResult.nodeResults, null, 2));

  assertTest('12. Swarm Replay Execution Result', execResult.status === 'COMPLETED' || execResult.status === 'AWAITING_APPROVAL', execResult.summary);
  assertTest('13. Verified Node Execution Count', execResult.verifiedCount > 0, `Verified: ${execResult.verifiedCount}`);

  // 14. Persistence & Store Operations
  const store = new WorkflowStore();
  store.saveWorkflow(wfDef);
  const fetchedWf = store.getWorkflow(wfDef.id);
  assertTest('14. Workflow Persistence & Store Retrieval', Boolean(fetchedWf && fetchedWf.name === wfDef.name));

  // 15. Record Replay Execution History
  store.recordReplayExecution(execResult);
  const history = store.getReplayHistory(wfDef.id);
  assertTest('15. Replay Execution History Store', history.length === 1 && history[0].status === 'COMPLETED');

  // 16. Delete Workflow
  const deleted = store.deleteWorkflow(wfDef.id);
  assertTest('16. Delete Workflow from Store', deleted && store.getWorkflow(wfDef.id) === undefined);

  console.log('\n==================================================');
  console.log(`OVERALL WORKFLOW STUDIO TEST RESULT: ${overallSuccess ? 'PASSED' : 'FAILED'}`);
  console.log('==================================================');

  if (!overallSuccess) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Workflow Studio test runner failed:', err);
  process.exit(1);
});
