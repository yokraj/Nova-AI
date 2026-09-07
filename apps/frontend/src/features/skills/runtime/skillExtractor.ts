import { Skill, SkillStep, WorkflowExecutionRecord } from '../types/skill';
import { VariableExtractor } from './variableExtractor';
import { WorkflowNormalizer } from './workflowNormalizer';
import { SkillValidator } from '../security/skillValidator';
import { SkillSecurityGuard } from '../security/skillSecurityGuard';

export interface ExtractionResult {
  qualifies: boolean;
  reason: string;
  candidateSkill?: Omit<Skill, 'id' | 'createdAt' | 'updatedAt' | 'usageCount' | 'successRate' | 'version' | 'history'>;
}

export class SkillExtractor {
  private variableExtractor = new VariableExtractor();
  private normalizer = new WorkflowNormalizer();
  private validator = new SkillValidator();
  private securityGuard = new SkillSecurityGuard();

  extractSkillFromWorkflow(
    record: WorkflowExecutionRecord,
    options?: { forceExplicit?: boolean }
  ): ExtractionResult {
    // 1. Check overall workflow success
    if (!record.overallSuccess) {
      return {
        qualifies: false,
        reason: 'Workflow failed during execution; failed workflows cannot be saved as learned skills.',
      };
    }

    // 2. Prompt Injection Check (untrusted sources)
    const trustCheck = this.securityGuard.validateLearningTrustSource({
      isUserExplicitGoal: true,
      untrustedContentPresent: record.isUntrustedContentPresent,
      untrustedSources: record.untrustedSources,
    });

    if (!trustCheck.trusted) {
      return {
        qualifies: false,
        reason: trustCheck.reason,
      };
    }

    // 3. Qualification Criteria
    const isExplicit =
      options?.forceExplicit ||
      record.userExplicitLearningRequested ||
      /remember|learn|do this the same way|save as skill/i.test(record.goalText);

    const hasMultiSteps = record.steps.length >= 2;

    if (!isExplicit && !hasMultiSteps) {
      return {
        qualifies: false,
        reason: 'Single-step workflow without explicit user instruction does not qualify for skill extraction.',
      };
    }

    // 4. Sanitize and redact sensitive data
    const rawGoal = record.goalText;
    const sensitiveMatch = rawGoal.match(/\b(password|secret|key|token|auth|credential)\b/i);
    if (sensitiveMatch) {
      return {
        qualifies: false,
        reason: 'Workflow contains sensitive credentials or authentication keywords.',
      };
    }

    // 5. Workflow Normalization
    const normalizedGoal = this.normalizer.normalizeGoalText(rawGoal);

    // 6. Variable Extraction
    const varResult = this.variableExtractor.extractVariables(record.steps, normalizedGoal);

    // 7. Step conversion
    const steps: SkillStep[] = record.steps.map((st, idx) => {
      const pStep = varResult.parameterizedSteps.find((ps) => ps.stepNumber === st.stepNumber);
      const normalizedTool = this.normalizer.normalizeToolName(st.toolName || 'system.get_info');

      return {
        id: `step-${idx + 1}`,
        order: idx + 1,
        tool: normalizedTool,
        arguments: st.toolArgs || {},
        argumentTemplates: pStep?.argumentTemplates || {},
        purpose: st.title,
        expectedObservation: st.observation,
        verification: st.verificationConfirmed
          ? {
              type: 'tool_result',
              expectedState: 'verified',
            }
          : undefined,
        retryPolicy: {
          maxAttempts: 2,
          backoffMs: 1000,
        },
        approvalRequired: st.approvalRequired || false,
      };
    });

    // Determine Skill Category & Capabilities
    const requiredTools = Array.from(new Set(steps.map((s) => s.tool)));
    let category: Skill['category'] = 'general';
    if (requiredTools.some((t) => t.startsWith('browser.'))) category = 'browser';
    else if (requiredTools.some((t) => t.startsWith('filesystem.'))) category = 'filesystem';
    else if (requiredTools.some((t) => t.startsWith('application.'))) category = 'automation';
    else if (requiredTools.some((t) => t.startsWith('system.'))) category = 'system';

    const skillName = this.deriveSkillName(normalizedGoal);

    const candidateSkill: Omit<Skill, 'id' | 'createdAt' | 'updatedAt' | 'usageCount' | 'successRate' | 'version' | 'history'> = {
      name: skillName,
      description: `Automated multi-step workflow learned for: "${normalizedGoal}"`,
      purpose: normalizedGoal,
      triggerPatterns: [
        {
          naturalLanguagePattern: normalizedGoal,
          intent: record.intent || 'workflow_execution',
          confidence: 0.95,
        },
      ],
      category,
      status: 'active',
      confidence: 0.9,
      source: isExplicit ? 'user_taught' : 'auto_extracted',
      owner: 'NovaUser',
      requiredTools,
      requiredCapabilities: [category],
      requiredPermissions: [],
      preconditions: ['Target system available'],
      variables: varResult.variables,
      steps,
      verificationRules: ['Verify state change after every tool execution step'],
      recoveryRules: ['Use RecoveryEngine replanning on step failure'],
      constraints: ['Respect ToolPermissionGuard and ExecutionBudget limits'],
      examples: [normalizedGoal],
      tags: [category, 'learned_workflow'],
      dependencies: [],
      compatibility: {
        agentRuntimeVersion: '1.0.0',
      },
    };

    // 8. Validate candidate skill
    const dummySkillObj: Skill = {
      ...candidateSkill,
      id: 'dummy-check',
      version: 1,
      usageCount: 0,
      successRate: 1.0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      history: [],
    };

    const val = this.validator.validateSkill(dummySkillObj);
    if (!val.valid) {
      return {
        qualifies: false,
        reason: `Candidate skill validation failed: ${val.errors.join('; ')}`,
      };
    }

    return {
      qualifies: true,
      reason: `Workflow qualified for learning as skill "${skillName}" (${steps.length} verified steps, ${varResult.variables.length} dynamic variables).`,
      candidateSkill,
    };
  }

  private deriveSkillName(goal: string): string {
    let name = goal.replace(/^(nova,\s*|please\s*|can you\s*)/i, '');
    name = name.charAt(0).toUpperCase() + name.slice(1);
    if (name.length > 40) {
      name = name.substring(0, 40) + '...';
    }
    return name;
  }
}
