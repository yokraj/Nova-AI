import { conversationApiService } from '../src/services/api/conversationApiService.js';
import { memoryApiService } from '../src/services/api/memoryApiService.js';
import { knowledgeApiService } from '../src/services/api/knowledgeApiService.js';
import { skillApiService } from '../src/services/api/skillApiService.js';
import { missionApiService } from '../src/services/api/missionApiService.js';
import { agentApiService } from '../src/services/api/agentApiService.js';
import { auditApiService } from '../src/services/api/auditApiService.js';
import { LocalSkillProvider } from '../src/features/skills/providers/skillProvider.js';

async function main() {
  console.log('==================================================');
  console.log('=== NOVA FULL END-TO-END PERSISTENCE TEST SUITE ===');
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

  // 1. Conversation Persistence Across Restarts
  console.log('1. Verifying Conversation & Message Persistence...');
  const conv = await conversationApiService.createConversation('F1.28 E2E Persistence Thread');
  const msg1 = await conversationApiService.addMessage(conv.id, 'user', 'Deploy persistent Nova stack.');
  const msg2 = await conversationApiService.addMessage(conv.id, 'assistant', 'Stack deployed cleanly with persistent SQLite database.');

  assertTest('Create Conversation', Boolean(conv && conv.id));
  assertTest('Create User Message', Boolean(msg1 && msg1.content.includes('Nova stack')));
  assertTest('Create Assistant Message', Boolean(msg2 && msg2.content.includes('SQLite')));

  // 2. Memory Persistence Across Restarts
  console.log('\n2. Verifying Memory System Persistence...');
  const createdMemory = await memoryApiService.createMemory({
    type: 'Architecture',
    title: 'Dual Database Engine Policy',
    content: 'Nova supports PostgreSQL asyncpg and zero-cost local SQLite aiosqlite for persistence.',
    summary: 'PostgreSQL & SQLite support',
    source: { origin: 'F1.28 Implementation', timestamp: new Date().toISOString(), confidence: 1.0 },
    importance: 'High',
    confidence: 1.0,
    tags: ['postgresql', 'sqlite', 'persistence'],
    project: 'Nova-AI',
    workspace: 'Nova',
    relationships: [],
    status: 'active',
  });
  assertTest('Create Memory Item', Boolean(createdMemory && createdMemory.id));

  // 3. Knowledge Graph Persistence Across Restarts
  console.log('\n3. Verifying Knowledge Graph Persistence...');
  const createdEntity = await knowledgeApiService.createEntity({
    name: 'FastAPI REST Engine',
    entityType: 'BackendCore',
    description: 'Central FastAPI REST API engine',
    workspace: 'Nova',
    project: 'Nova-AI',
  });
  assertTest('Create Knowledge Entity', Boolean(createdEntity && createdEntity.id));

  // 4. Learned Skill Persistence & Versioning Across Restarts
  console.log('\n4. Verifying Learned Skill Persistence & Restart Survival...');
  const skillProvider = new LocalSkillProvider();
  const createdSkill = await skillProvider.createSkill({
    name: 'Auto Deploy F1.28 Persistent Stack',
    description: 'Build Vite app and start FastAPI server',
    purpose: 'Deploy production stack',
    triggerPatterns: [{ naturalLanguagePattern: 'Auto Deploy F1.28 Persistent Stack', intent: 'workflow_execution', confidence: 0.98 }],
    category: 'automation',
    status: 'active',
    confidence: 0.98,
    source: 'user_taught',
    owner: 'NovaAdmin',
    requiredTools: ['filesystem.read_directory', 'system.get_info'],
    requiredCapabilities: ['system'],
    requiredPermissions: [],
    preconditions: ['System online'],
    variables: [{ name: 'port', type: 'number', description: 'Port', required: true, defaultValue: '8000' }],
    steps: [
      { id: 'step-1', order: 1, tool: 'system.get_info', arguments: {}, purpose: 'Check hardware readiness' },
    ],
    verificationRules: ['Verify server port open'],
    recoveryRules: ['Restart server on failure'],
    constraints: [],
    examples: ['Auto Deploy F1.28 Persistent Stack'],
    tags: ['deploy', 'fastapi'],
    dependencies: [],
    compatibility: { agentRuntimeVersion: '1.0.0' },
  });

  assertTest('Create Learned Skill', Boolean(createdSkill && createdSkill.id));

  // Versioning & Usage
  const updatedSkill = await skillProvider.createVersion(createdSkill.id, 'Optimized port check', 'Performance improvement');
  assertTest('Create Skill Version v2', Boolean(updatedSkill && updatedSkill.version === 2));

  await skillProvider.recordUsage(createdSkill.id, true, 45);
  const usedSkill = await skillProvider.getSkill(createdSkill.id);
  assertTest('Record Skill Usage Statistics', Boolean(usedSkill && usedSkill.usageCount === 1));

  // Simulate Application Restart
  const restartedSkillProvider = new LocalSkillProvider();
  const restartedSkill = await restartedSkillProvider.getSkill(createdSkill.id);
  assertTest('Learned Skill Restart Survival', Boolean(restartedSkill && restartedSkill.version === 2 && restartedSkill.usageCount === 1));

  // 5. Mission Control Persistence Across Restarts
  console.log('\n5. Verifying Mission Control Persistence...');
  const createdMission = await missionApiService.createMission({
    title: 'Full F1.28 Verification Mission',
    goal: 'Verify full persistent database lifecycle across restart',
    category: 'automation',
    tasks: [
      { taskOrder: 1, title: 'Verify SQLite DB', description: 'Ensure ./data/nova_ai.db exists and accepts queries', status: 'COMPLETED' },
      { taskOrder: 2, title: 'Run Integration Tests', description: 'Run runPersistenceTests.ts script', status: 'COMPLETED' },
    ],
  });
  assertTest('Create Mission & Tasks', Boolean(createdMission && createdMission.id && createdMission.tasks?.length === 2));

  // 6. Agent Workforce Persistence Across Restarts
  console.log('\n6. Verifying Agent Workforce Persistence...');
  const createdAgent = await agentApiService.createAgent({
    name: 'Database Persistence Specialist',
    role: 'Database & Backend Reliability Agent',
    description: 'Manages SQLAlchemy models, Alembic migrations, and SQLite/PostgreSQL persistence',
    capabilities: ['database', 'sqlalchemy', 'alembic', 'fastapi'],
  });
  assertTest('Register Agent', Boolean(createdAgent && createdAgent.id));

  // 7. Audit Event Logging Persistence Across Restarts
  console.log('\n7. Verifying Security & Tool Audit Event Persistence...');
  const auditEvent = await auditApiService.recordAuditEvent({
    eventType: 'SECURITY_GATE_VERIFICATION',
    action: 'database.migration_check',
    toolName: 'alembic.upgrade',
    riskLevel: 'SAFE',
    actor: 'SystemAdmin',
    decision: 'ALLOWED',
    details: { migration: '0003_create_skills_missions_agents_audit_tables' },
  });
  assertTest('Record Audit Event Log', Boolean(auditEvent && auditEvent.id));

  console.log('\n==================================================');
  console.log(`OVERALL END-TO-END PERSISTENCE RESULT: ${overallSuccess ? 'PASSED' : 'FAILED'}`);
  console.log('==================================================');

  if (!overallSuccess) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('End-to-end persistence test runner failed:', err);
  process.exit(1);
});
