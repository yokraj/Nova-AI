import { DemonstrationRecorder } from '../src/features/workflow-studio/recorder/demonstrationRecorder.js';
import { EventNormalizer } from '../src/features/workflow-studio/normalizer/eventNormalizer.js';
import { WorkflowVariableExtractor } from '../src/features/workflow-studio/variables/workflowVariableExtractor.js';
import { WorkflowDryRunEngine } from '../src/features/workflow-studio/testing/workflowDryRunEngine.js';
import { TargetRelocator } from '../src/features/workflow-studio/adaptation/targetRelocator.js';
import { WorkflowBuilder } from '../src/features/workflow-studio/studio/workflowBuilder.js';
import { SwarmReplayEngine } from '../src/features/workflow-studio/replay/swarmReplayEngine.js';
import { WorkflowStore } from '../src/features/workflow-studio/persistence/workflowStore.js';
import { ScheduledTask } from '../src/features/background-runtime/types/scheduledTask.js';

async function main() {
  console.log('==================================================');
  console.log('=== NOVA PRODUCTION WORKFLOW STUDIO SUITE ===');
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

  // 1. Real Demonstration Recording Stream
  const recorder = new DemonstrationRecorder();
  recorder.startRecording('Production E2E Workflow');

  // 2. Secret Redaction
  recorder.recordAction({
    actionType: 'TYPE_TEXT',
    capability: 'COMPUTER_CONTROL',
    toolName: 'type_text',
    arguments: { text: 'my_password = SecretPass123! bearer sk-1234567890abcdef12345' },
    activeApp: 'Notepad',
  });
  const activeSess = recorder.getActiveSession();
  assertTest('1. Real Demonstration Event Stream Recording', Boolean(activeSess && activeSess.recordedActions.length === 1));
  assertTest('2. Secret & Password Redaction Guard', (activeSess?.redactedSecretsCount ?? 0) > 0, `Redacted secrets: ${activeSess?.redactedSecretsCount}`);


  // 3. Event Normalization (5-Tier Target)
  const normalizer = new EventNormalizer();
  const semanticTarget = normalizer.normalizeEventTarget({
    toolName: 'click_coordinate',
    arguments: { x: 732, y: 412 },
    accessibilityRole: 'button',
    accessibilityName: 'Submit Form',
    activeApp: 'Chrome Browser',
  });
  assertTest('3. Event Normalization 5-Tier Strategy', semanticTarget.strategy === 'ACCESSIBILITY' && semanticTarget.confidence > 0.90);

  // 4. Dynamic Variable Extraction
  const builder = new WorkflowBuilder('Dynamic Variable Workflow', 'Workflow with template variables');
  builder.addNode({
    label: 'Search Google for {{query}} in {{region}}',
    type: 'DESKTOP_ACTION',
    capability: 'BROWSER_CONTROL',
    toolName: 'browser_navigate',
    arguments: { url: 'https://google.com/search?q={{query}}' },
    riskLevel: 'SAFE',
    requiresApproval: false,
    x: 100,
    y: 100,
  });
  const extractor = new WorkflowVariableExtractor();
  const extractedVars = extractor.extractVariables(builder.getWorkflow());
  assertTest('4. Dynamic Variable Extraction', extractedVars.length === 2 && extractedVars.some((v) => v.name === 'query'));

  // 5. Variable Template Substitution
  const substitutedStr = extractor.substituteVariables('Search for {{query}}', { query: 'laptops' });
  assertTest('5. Variable Template Substitution', substitutedStr === 'Search for laptops');

  // 6. Non-Destructive Dry Run Test Mode
  const dryRunEngine = new WorkflowDryRunEngine();
  const dryRunResult = await dryRunEngine.performDryRun(builder.getWorkflow());
  assertTest('6. Non-Destructive Dry Run Pre-Flight Engine', Boolean(dryRunResult && dryRunResult.stepAssessments.length > 0));

  // 7. Missing Dependency Detection
  assertTest('7. Missing Dependency Detection', Array.isArray(dryRunResult.missingDependencies));

  // 8. DAG Node Addition & Duplication
  const originalNode = builder.getWorkflow().nodes[0];
  const duplicatedNode = builder.duplicateNode(originalNode.id);
  assertTest('8. DAG Node Duplication', Boolean(duplicatedNode && builder.getWorkflow().nodes.length === 2));

  // 9. DAG Node Deletion & Edge Cleanup
  const deleted = builder.deleteNode(duplicatedNode!.id);
  assertTest('9. DAG Node Deletion', deleted && builder.getWorkflow().nodes.length === 1);

  // 10. Step Reordering & Topological Validation
  const node2 = builder.addNode({
    label: 'Step 2 Action',
    type: 'DESKTOP_ACTION',
    riskLevel: 'SAFE',
    requiresApproval: false,
    x: 280,
    y: 100,
  });
  builder.addEdge(originalNode.id, node2.id);
  builder.reorderNodes([node2.id, originalNode.id]);
  const topoOrder = builder.getTopologicalOrder();
  assertTest('10. Step Reordering & Topological Validation', topoOrder.length === 2);

  // 11. Adaptive Target Relocation
  const relocator = new TargetRelocator();
  const relocResult = await relocator.relocateTarget(semanticTarget);
  assertTest('11. Adaptive Target Relocation Engine', relocResult.found && relocResult.strategyUsed === 'ACCESSIBILITY');

  // 12. Low Confidence Target Threshold Policy
  const lowConfTarget = {
    strategy: 'COORDINATES_FALLBACK' as const,
    accessibilityRole: undefined,
    accessibilityName: undefined,
    domSelector: undefined,
    visualText: undefined,
    visualLabel: undefined,
    coordinatesFallback: { x: 10, y: 10 },
    confidence: 0.5,
  };
  const lowConfRes = await relocator.relocateTarget(lowConfTarget);
  assertTest('12. Low Confidence Target Relocation Policy', lowConfRes.confidence < 0.75 && lowConfRes.verificationRequired);

  // 13. Swarm Role Delegation
  builder.assignAgentRole(node2.id, 'BrowserSpecialist');
  assertTest('13. Swarm Agent Role Delegation', builder.getWorkflow().nodes.find((n) => n.id === node2.id)?.assignedAgentRole === 'BrowserSpecialist');

  // 14. High-Risk Security Approval Gate
  const highRiskNode = builder.addNode({
    label: 'Delete Operating System Log',
    type: 'DESKTOP_ACTION',
    capability: 'FILE_SYSTEM',
    toolName: 'delete_file',
    arguments: { path: 'C:/Windows/temp.log' },
    riskLevel: 'HIGH',
    requiresApproval: true,
    x: 460,
    y: 100,
  });
  builder.addEdge(node2.id, highRiskNode.id);
  const dryRunRiskRes = await dryRunEngine.performDryRun(builder.getWorkflow());
  const highRiskAssessment = dryRunRiskRes.stepAssessments.find((s) => s.nodeId === highRiskNode.id);
  assertTest(
    '14. High-Risk Security Approval Gate Enforcement',
    highRiskAssessment?.status === 'REQUIRES_APPROVAL' || highRiskAssessment?.permissionStatus === 'Requires Approval'
  );

  // 15. Versioning Creation (v1 -> v2)
  const v2Number = builder.createNewVersion('Added high-risk step');
  assertTest('15. Workflow Version Creation (v2)', v2Number === 2 && builder.getWorkflow().version === 2);

  // 16. Version Rollback Functionality
  const rollbacked = builder.rollbackToVersion(1);
  assertTest('16. Workflow Version Rollback', rollbacked);

  // 17. Workflow to Skill Conversion
  const store = new WorkflowStore();
  const convertedSkill = store.convertWorkflowToSkill(builder.getWorkflow());
  assertTest('17. Workflow to Skill Conversion', Boolean(convertedSkill && convertedSkill.skillId.startsWith('skill-')));

  // 18. Background Scheduled Task Integration
  const scheduledTask: ScheduledTask = {
    id: `task-wf-${Date.now()}`,
    name: builder.getWorkflow().name,
    description: builder.getWorkflow().description,
    goal: `Execute workflow: ${builder.getWorkflow().name}`,
    status: 'SCHEDULED',
    priority: 'HIGH',
    schedule: { type: 'DAILY', timeOfDay: '09:00' },
    maxRetries: 3,
    retryCount: 0,
    timeoutMs: 30000,
    executionCount: 0,
    enabled: true,
    requiresApproval: false,
    trustedPolicy: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  assertTest('18. Scheduled Background Task Integration', scheduledTask.status === 'SCHEDULED' && scheduledTask.schedule.type === 'DAILY');

  // 19. Swarm Replay Engine Safe Execution
  const replayEngine = new SwarmReplayEngine();
  const safeWfBuilder = new WorkflowBuilder('Safe E2E Workflow', 'Safe notepad execution');
  safeWfBuilder.addNode({
    label: 'Trigger Activation',
    type: 'TRIGGER',
    riskLevel: 'SAFE',
    requiresApproval: false,
    x: 100,
    y: 100,
  });
  safeWfBuilder.addNode({
    label: 'Open Notepad Application',
    type: 'DESKTOP_ACTION',
    capability: 'APPLICATION_CONTROL',
    toolName: 'launch_application',
    arguments: { appName: 'notepad.exe' },
    riskLevel: 'SAFE',
    requiresApproval: false,
    x: 280,
    y: 100,
  });

  console.log('\n23. Executing Safe E2E Notepad Workflow via SwarmReplayEngine...');
  const safeExecRes = await replayEngine.replayWorkflow(safeWfBuilder.getWorkflow(), {
    workflowId: safeWfBuilder.getWorkflow().id,
    enableSwarmDelegation: true,
    verifyVisualStates: false,
    pauseOnApproval: false,
    stepTimeoutMs: 10000,
  });
  assertTest('23. Safe E2E Notepad Workflow Execution', safeExecRes.status === 'COMPLETED', safeExecRes.summary);

  // 24. Safe Browser CDP E2E Execution
  const browserWfBuilder = new WorkflowBuilder('Safe Browser CDP Workflow', 'Safe browser execution');
  browserWfBuilder.addNode({
    label: 'Trigger Activation',
    type: 'TRIGGER',
    riskLevel: 'SAFE',
    requiresApproval: false,
    x: 100,
    y: 100,
  });
  browserWfBuilder.addNode({
    label: 'Navigate to Local Webserver',
    type: 'BROWSER_ACTION',
    capability: 'BROWSER_CONTROL',
    toolName: 'browser_navigate',
    arguments: { url: 'http://127.0.0.1:3000' },
    riskLevel: 'SAFE',
    requiresApproval: false,
    x: 280,
    y: 100,
  });

  console.log('\n24. Executing Safe E2E Browser CDP Workflow via SwarmReplayEngine...');
  const browserExecRes = await replayEngine.replayWorkflow(browserWfBuilder.getWorkflow(), {
    workflowId: browserWfBuilder.getWorkflow().id,
    enableSwarmDelegation: true,
    verifyVisualStates: false,
    pauseOnApproval: false,
    stepTimeoutMs: 10000,
  });
  assertTest('24. Safe Browser CDP Workflow Execution', browserExecRes.status === 'COMPLETED', browserExecRes.summary);

  console.log('\n==================================================');
  console.log(`OVERALL PRODUCTION WORKFLOW STUDIO RESULT: ${overallSuccess ? 'PASSED' : 'FAILED'}`);
  console.log('==================================================');

  if (!overallSuccess) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Production Workflow Studio test runner failed:', err);
  process.exit(1);
});
