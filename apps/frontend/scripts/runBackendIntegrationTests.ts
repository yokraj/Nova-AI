import { conversationApiService } from '../src/services/api/conversationApiService.js';
import { memoryApiService } from '../src/services/api/memoryApiService.js';
import { knowledgeApiService } from '../src/services/api/knowledgeApiService.js';
import { skillApiService } from '../src/services/api/skillApiService.js';
import { missionApiService } from '../src/services/api/missionApiService.js';
import { agentApiService } from '../src/services/api/agentApiService.js';
import { auditApiService } from '../src/services/api/auditApiService.js';
import { LocalSkillProvider } from '../src/features/skills/providers/skillProvider.js';
import { SkillManager } from '../src/features/skills/runtime/skillManager.js';
import { AgentRuntime } from '../src/features/ai-runtime/runtime/agentRuntime.js';

async function main() {
  console.log('=== NOVA BACKEND & PERSISTENCE INTEGRATION TEST SUITE ===\n');

  let allPassed = true;
  const logTest = (name: string, success: boolean, details?: string) => {
    if (success) {
      console.log(`    [PASS] ${name}${details ? ` - ${details}` : ''}`);
    } else {
      allPassed = false;
      console.log(`    [FAIL] ${name}${details ? ` - ${details}` : ''}`);
    }
  };

  // 1. Test Conversation API Persistence
  console.log('1. Testing Conversation Persistence...');
  const conv = await conversationApiService.createConversation('Persistent Deploy Thread');
  const msg = await conversationApiService.addMessage(conv.id, 'user', 'Deploy React app to production server.');
  logTest('Conversation Creation', Boolean(conv.id && conv.title === 'Persistent Deploy Thread'));
  logTest('Message Persistence', Boolean(msg.id && msg.content.includes('Deploy React app')));

  // 2. Test Memory API Persistence
  console.log('\n2. Testing Memory Persistence...');
  const mem = await memoryApiService.createMemory({
    type: 'Workflow',
    title: 'Deployment Strategy',
    content: 'User prefers automated Vite build and Ollama local model inference.',
    summary: 'Build and LLM preference',
    source: { origin: 'User instruction', timestamp: new Date().toISOString(), confidence: 0.95 },
    importance: 'High',
    confidence: 0.95,
    tags: ['pnpm', 'vite', 'ollama'],
    project: 'Nova',
    workspace: 'LocalWorkstation',
    relationships: [],
    status: 'active',
  });
  logTest('Memory Creation', Boolean(mem.id && mem.title === 'Deployment Strategy'));

  // 3. Test Knowledge Graph Persistence
  console.log('\n3. Testing Knowledge Graph Persistence...');
  const entity = await knowledgeApiService.createEntity({
    name: 'Nova AI Kernel',
    entityType: 'SystemComponent',
    description: 'Universal AI Operating System Kernel',
    workspace: 'Nova',
    project: 'Nova-AI',
  });
  logTest('Knowledge Entity Creation', Boolean(entity.id && entity.name === 'Nova AI Kernel'));

  // 4. Test Skill Learning Persistence (F1.26 Engine)
  console.log('\n4. Testing Skill Learning Engine Persistence...');
  const skillProvider = new LocalSkillProvider();
  await skillProvider.clearAllSkills();

  const createdSkill = await skillProvider.createSkill({
    name: 'Deploy React Project Persistent',
    description: 'Build and deploy React project automatically',
    purpose: 'Build and deploy',
    triggerPatterns: [{ naturalLanguagePattern: 'Deploy React Project Persistent', intent: 'workflow_execution', confidence: 0.95 }],
    category: 'automation',
    status: 'active',
    confidence: 0.95,
    source: 'user_taught',
    owner: 'NovaUser',
    requiredTools: ['application.open', 'filesystem.create_directory'],
    requiredCapabilities: ['automation'],
    requiredPermissions: [],
    preconditions: ['Disk ready'],
    variables: [{ name: 'location', type: 'path', description: 'Target path', required: true, defaultValue: 'Desktop/NovaApp' }],
    steps: [
      { id: 'step-1', order: 1, tool: 'application.open', arguments: { applicationName: 'VS Code' }, purpose: 'Launch IDE' },
    ],
    verificationRules: ['Verify state change'],
    recoveryRules: ['Replan on failure'],
    constraints: [],
    examples: ['Deploy React Project Persistent'],
    tags: ['react', 'deploy'],
    dependencies: [],
    compatibility: { agentRuntimeVersion: '1.0.0' },
  });

  logTest('Skill Persistence Creation', Boolean(createdSkill.id && createdSkill.version === 1));

  // Simulate Application Restart (re-instantiate provider and query again)
  const restartedProvider = new LocalSkillProvider();
  const retrievedSkill = await restartedProvider.getSkill(createdSkill.id);
  if (!retrievedSkill) {
    console.log('    [DEBUG] createdSkill.id:', createdSkill.id);
    console.log('    [DEBUG] restartedProvider skills:', await restartedProvider.listSkills());
  }
  logTest('Skill Application Restart Survival', Boolean(retrievedSkill && retrievedSkill.name === 'Deploy React Project Persistent'));

  // 5. Test Mission Control Persistence
  console.log('\n5. Testing Mission Control Persistence...');
  const mission = await missionApiService.createMission({
    title: 'Nova F1.27 Build Verification',
    goal: 'Verify full persistence layer across restart',
    category: 'automation',
    tasks: [
      { taskOrder: 1, title: 'Database Migration', description: 'Run Alembic 0003 migration', status: 'COMPLETED' },
    ],
  });
  logTest('Mission Creation', Boolean(mission.id && mission.title === 'Nova F1.27 Build Verification'));

  // 6. Test Agent Workforce Persistence
  console.log('\n6. Testing Agent Workforce Persistence...');
  const agent = await agentApiService.createAgent({
    name: 'DevOps Automated Agent',
    role: 'DevOps & System Automation Agent',
    description: 'Automates build scripts and database persistence tasks',
    capabilities: ['system', 'filesystem', 'automation'],
  });
  logTest('Agent Workforce Registration', Boolean(agent.id && agent.role.includes('DevOps')));

  // 7. Test Audit Event Logging Persistence
  console.log('\n7. Testing Audit Event Logging Persistence...');
  const auditEvent = await auditApiService.recordAuditEvent({
    eventType: 'TOOL_EXECUTION',
    action: 'system.volume_set',
    toolName: 'system.volume_set',
    riskLevel: 'LOW',
    actor: 'User',
    decision: 'ALLOWED',
    details: { level: 50 },
  });
  logTest('Audit Event Logging', Boolean(auditEvent.id && auditEvent.action === 'system.volume_set'));

  // 8. Test E2E Skill Execution through AgentRuntime
  console.log('\n8. Testing E2E Skill Execution through AgentRuntime...');
  const manager = new SkillManager();
  const runtime = new AgentRuntime();
  const execResult = await manager.executeSkill(createdSkill.id, { location: 'Desktop/NovaApp' }, runtime);
  logTest('E2E Skill Execution via AgentRuntime', Boolean(execResult.success && execResult.executedStepsCount === 1));

  console.log('\n==================================================');
  console.log(`OVERALL BACKEND INTEGRATION RESULT: ${allPassed ? 'PASSED' : 'FAILED'}`);
  console.log('==================================================');

  if (!allPassed) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Backend integration test runner failed:', err);
  process.exit(1);
});
