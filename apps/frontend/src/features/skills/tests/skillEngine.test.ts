import { SkillManager } from '../runtime/skillManager';
import { WorkflowRecorder } from '../runtime/workflowRecorder';
import { SkillExtractor } from '../runtime/skillExtractor';
import { VariableExtractor } from '../runtime/variableExtractor';
import { SkillValidator } from '../security/skillValidator';
import { SkillSecurityGuard } from '../security/skillSecurityGuard';
import { SkillMatcher } from '../resolver/skillMatcher';
import { SkillAdapter } from '../resolver/skillAdapter';
import { SkillMemoryBridge } from '../runtime/skillMemoryBridge';
import { SkillMissionBridge } from '../runtime/skillMissionBridge';
import { SkillSwarmBridge } from '../runtime/skillSwarmBridge';
import { SkillVoiceHandler } from '../runtime/skillVoiceHandler';
import { Skill } from '../types/skill';

export async function runSkillEngineTests(): Promise<{ passed: boolean; results: string[] }> {
  const results: string[] = [];
  let allPassed = true;

  const logTest = (name: string, success: boolean, details?: string) => {
    if (success) {
      results.push(`[PASS] ${name}${details ? ` - ${details}` : ''}`);
    } else {
      allPassed = false;
      results.push(`[FAIL] ${name}${details ? ` - ${details}` : ''}`);
    }
  };

  try {
    const manager = new SkillManager();
    await manager.clearAllSkills();

    // 1. Skill Creation
    const mockSkillData: Omit<Skill, 'id' | 'createdAt' | 'updatedAt' | 'usageCount' | 'successRate' | 'version' | 'history'> = {
      name: 'Build My Project',
      description: 'Build React application on Desktop',
      purpose: 'Build project',
      triggerPatterns: [{ naturalLanguagePattern: 'Build My Project', intent: 'workflow_execution', confidence: 0.95 }],
      category: 'automation',
      status: 'active',
      confidence: 0.9,
      source: 'user_taught',
      owner: 'NovaUser',
      requiredTools: ['application.open', 'filesystem.read_directory'],
      requiredCapabilities: ['automation'],
      requiredPermissions: [],
      preconditions: ['Disk ready'],
      variables: [
        { name: 'projectName', type: 'string', description: 'Name of project', required: true, defaultValue: 'NovaApp', examples: ['NovaApp'] },
        { name: 'location', type: 'path', description: 'Target path', required: true, defaultValue: 'Desktop/NovaApp', examples: ['Desktop/NovaApp'] },
      ],
      steps: [
        {
          id: 'step-1',
          order: 1,
          tool: 'application.open',
          arguments: { applicationName: 'VS Code' },
          argumentTemplates: { applicationName: '{{appName}} font' },
          purpose: 'Open IDE',
        },
        {
          id: 'step-2',
          order: 2,
          tool: 'filesystem.read_directory',
          arguments: { path: 'Desktop/NovaApp' },
          argumentTemplates: { path: '{{location}}' },
          purpose: 'Inspect directory',
          verification: { type: 'tool_result', expectedState: 'verified' },
        },
      ],
      verificationRules: ['Verify state change'],
      recoveryRules: ['Replan on failure'],
      constraints: ['Respect permissions'],
      examples: ['Build My Project'],
      tags: ['automation', 'build'],
      dependencies: [],
      compatibility: { agentRuntimeVersion: '1.0.0' },
    };

    // Create via Provider/Manager
    const recorder = new WorkflowRecorder();
    recorder.startRecording('Create a React project called NovaApp on Desktop', 'workflow_execution', true);
    recorder.recordStep({
      stepNumber: 1,
      title: 'Open VS Code',
      toolName: 'application.open',
      toolArgs: { applicationName: 'VS Code' },
      success: true,
      verificationConfirmed: true,
    });
    recorder.recordStep({
      stepNumber: 2,
      title: 'Check Desktop/NovaApp',
      toolName: 'filesystem.read_directory',
      toolArgs: { path: 'Desktop/NovaApp' },
      success: true,
      verificationConfirmed: true,
    });
    const finishedRecord = recorder.finishRecording(true);

    logTest('Test 1: Workflow Capture', finishedRecord !== null && finishedRecord.steps.length === 2);

    // 2. Explicit learning command & Skill extraction
    const extractor = new SkillExtractor();
    const extRes = extractor.extractSkillFromWorkflow(finishedRecord!, { forceExplicit: true });
    logTest('Test 2: Explicit Learning & Extraction', extRes.qualifies && extRes.candidateSkill !== undefined);

    // 3. Save skill via manager
    const savedSkill = await manager.learnExplicitWorkflow(finishedRecord!);
    logTest('Test 3: Skill Creation & Persistence', savedSkill !== undefined && savedSkill.version === 1);

    // 4. Variable Extraction
    const varExtractor = new VariableExtractor();
    const varRes = varExtractor.extractVariables(finishedRecord!.steps, 'Create a React project called SolarApp on Desktop');
    logTest('Test 4: Variable Extraction', varRes.variables.length > 0);

    // 5. Skill Validation
    const validator = new SkillValidator();
    const valRes = validator.validateSkill(savedSkill);
    logTest('Test 5: Skill Validation', valRes.valid);

    // 6. Skill Search
    const searchRes = await manager.listSkills({ searchQuery: 'React' });
    logTest('Test 6: Skill Search', searchRes.length === 1 && searchRes[0].id === savedSkill.id);

    // 7. Skill Matching & Confidence Scoring
    const matcher = new SkillMatcher();
    const matches = matcher.matchSkill('Use my Create React project skill for SolarApp', [savedSkill]);
    logTest('Test 7: Skill Matching & Confidence Scoring', matches.length > 0 && matches[0].confidenceScore >= 50);

    // 8. Skill Adaptation & Variable Substitution
    const adapter = new SkillAdapter();
    const adapted = adapter.adaptSkillToExecutionPlan(savedSkill, { projectName: 'SolarApp', path: 'Documents/SolarApp' });
    logTest('Test 8: Skill Adaptation & Variable Substitution', adapted.resolvedVariables.projectName === 'SolarApp');

    // 9. Permission Enforcement & High-Risk Approval Preservation
    const secGuard = new SkillSecurityGuard();
    const highRiskSkill: Skill = {
      ...savedSkill,
      id: 'high-risk-test',
      steps: [
        {
          id: 'step-sys',
          order: 1,
          tool: 'system.power_restart',
          arguments: {},
          purpose: 'Restart OS',
        },
      ],
    };
    const secAssessment = secGuard.evaluateSkillSecurity(highRiskSkill);
    logTest('Test 9: High-Risk Approval Preservation', secAssessment.requiresApproval === true);

    // 10. Prompt Injection Rejection
    const untrustedCheck = secGuard.validateLearningTrustSource({
      isUserExplicitGoal: true,
      untrustedContentPresent: true,
      untrustedSources: ['https://malicious-site.com'],
    });
    logTest('Test 10: Prompt Injection Rejection', untrustedCheck.trusted === false);

    // 11. Invalid Tool Rejection
    const invalidToolSkill: Skill = {
      ...savedSkill,
      steps: [
        {
          id: 'step-fake',
          order: 1,
          tool: 'nonexistent.fake_tool',
          arguments: {},
          purpose: 'Fake action',
        },
      ],
    };
    const invalidVal = validator.validateSkill(invalidToolSkill);
    logTest('Test 11: Invalid Tool Rejection', invalidVal.valid === false);

    // 12. Skill Disable & Enable
    const disabled = await manager.disableSkill(savedSkill.id);
    logTest('Test 12: Skill Disable', disabled.status === 'disabled');
    const enabled = await manager.enableSkill(savedSkill.id);
    logTest('Test 13: Skill Enable', enabled.status === 'active');

    // 13. Version Creation & Rollback
    const v2 = await manager.createVersion(savedSkill.id, 'Added test step', 'User request');
    logTest('Test 14: Skill Version Creation', v2.version === 2);
    const rolledBack = await manager.rollbackVersion(savedSkill.id, 1);
    logTest('Test 15: Skill Rollback', rolledBack.version === 3);

    // 14. Memory Integration
    const memBridge = new SkillMemoryBridge();
    const memItem = memBridge.convertSkillToMemoryItem(savedSkill);
    logTest('Test 16: Memory Integration', memItem.type === 'Workflow' && memItem.relationships.includes(savedSkill.id));

    // 15. Mission Integration
    const missionBridge = new SkillMissionBridge();
    const missionTemplate = missionBridge.createMissionTaskFromSkill(savedSkill, 'task-101');
    logTest('Test 17: Mission Integration', missionTemplate.taskId === 'task-101');

    // 16. Swarm Integration
    const swarmBridge = new SkillSwarmBridge();
    const swarmCheck = swarmBridge.verifySwarmAgentCanExecuteSkill(savedSkill, ['application', 'filesystem'], 'worker');
    logTest('Test 18: Swarm Integration', swarmCheck.canExecute === true);

    // 17. Voice Integration
    const voiceHandler = new SkillVoiceHandler();
    const voiceParsed = voiceHandler.parseVoiceCommand('Nova, learn this workflow');
    logTest('Test 19: Voice Integration', voiceParsed.action === 'LEARN_WORKFLOW');

    // 18. Skill Test Mode
    const testMode = await manager.prepareSkillTestMode(savedSkill.id, { location: 'Desktop/TestApp' });
    logTest('Test 20: Skill Test Mode', testMode.skill.id === savedSkill.id && testMode.steps.length === 2);

    // 19. Explicit Delete / Forget
    const deleted = await manager.deleteSkill(savedSkill.id);
    logTest('Test 21: Explicit Forget / Delete', deleted === true);

  } catch (err: any) {
    allPassed = false;
    results.push(`[FAIL] Exception during Skill Engine Unit Tests: ${err.message}`);
  }

  return { passed: allPassed, results };
}
