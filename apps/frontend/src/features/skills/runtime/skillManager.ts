import { Skill, SkillExecutionResult, SkillFilter, WorkflowExecutionRecord } from '../types/skill';
import { LocalSkillProvider } from '../providers/skillProvider';
import { WorkflowRecorder } from './workflowRecorder';
import { SkillExtractor } from './skillExtractor';
import { SkillValidator } from '../security/skillValidator';
import { SkillSecurityGuard } from '../security/skillSecurityGuard';
import { SkillMatcher } from '../resolver/skillMatcher';
import { SkillAdapter } from '../resolver/skillAdapter';
import { AgentRuntime } from '../../ai-runtime/runtime/agentRuntime';
import { SkillMemoryBridge } from './skillMemoryBridge';

export class SkillManager {
  private provider = new LocalSkillProvider();
  private recorder = new WorkflowRecorder();
  private extractor = new SkillExtractor();
  private validator = new SkillValidator();
  private securityGuard = new SkillSecurityGuard();
  private matcher = new SkillMatcher();
  private adapter = new SkillAdapter();
  private memoryBridge = new SkillMemoryBridge();

  // Workflow recording methods
  startRecording(goalText: string, intent?: string, isExplicit?: boolean): void {
    this.recorder.startRecording(goalText, intent, isExplicit);
  }

  recordStep(step: {
    stepNumber: number;
    title: string;
    toolName?: string;
    toolArgs?: Record<string, any>;
    observation?: string;
    success: boolean;
    verificationConfirmed: boolean;
    approvalRequired?: boolean;
    recoveryUsed?: string;
  }): void {
    this.recorder.recordStep(step);
  }

  flagUntrustedContent(source: string): void {
    this.recorder.flagUntrustedContent(source);
  }

  async finishRecordingAndCheckSkill(overallSuccess: boolean): Promise<{
    qualifies: boolean;
    reason: string;
    skill?: Skill;
  }> {
    const record = this.recorder.finishRecording(overallSuccess);
    if (!record) {
      return { qualifies: false, reason: 'No active recording found.' };
    }

    const extResult = this.extractor.extractSkillFromWorkflow(record);
    if (!extResult.qualifies || !extResult.candidateSkill) {
      return { qualifies: false, reason: extResult.reason };
    }

    // Save skill
    const savedSkill = await this.provider.createSkill(extResult.candidateSkill);
    return {
      qualifies: true,
      reason: extResult.reason,
      skill: savedSkill,
    };
  }

  async learnExplicitWorkflow(record: WorkflowExecutionRecord): Promise<Skill> {
    record.userExplicitLearningRequested = true;
    const extResult = this.extractor.extractSkillFromWorkflow(record, { forceExplicit: true });
    if (!extResult.qualifies || !extResult.candidateSkill) {
      throw new Error(`Failed to learn explicit workflow: ${extResult.reason}`);
    }
    return await this.provider.createSkill(extResult.candidateSkill);
  }

  // Management operations
  async listSkills(filter?: SkillFilter): Promise<Skill[]> {
    return await this.provider.listSkills(filter);
  }

  async getSkill(id: string): Promise<Skill | undefined> {
    return await this.provider.getSkill(id);
  }

  async updateSkill(id: string, updates: Partial<Skill>): Promise<Skill> {
    return await this.provider.updateSkill(id, updates);
  }

  async disableSkill(id: string): Promise<Skill> {
    return await this.provider.updateSkill(id, { status: 'disabled' });
  }

  async enableSkill(id: string): Promise<Skill> {
    return await this.provider.updateSkill(id, { status: 'active' });
  }

  async deleteSkill(id: string): Promise<boolean> {
    return await this.provider.deleteSkill(id);
  }

  async createVersion(id: string, changes: string, reason: string): Promise<Skill> {
    return await this.provider.createVersion(id, changes, reason);
  }

  async rollbackVersion(id: string, targetVersion: number): Promise<Skill> {
    return await this.provider.rollbackVersion(id, targetVersion);
  }

  async clearAllSkills(): Promise<void> {
    await this.provider.clearAllSkills();
  }

  // Matching & Retrieval
  async findMatchingSkills(query: string) {
    const all = await this.provider.listSkills();
    return this.matcher.matchSkill(query, all);
  }

  // Execution via AgentRuntime
  async executeSkill(
    skillId: string,
    variableValues: Record<string, any> = {},
    agentRuntime: AgentRuntime
  ): Promise<SkillExecutionResult> {
    const skill = await this.provider.getSkill(skillId);
    if (!skill) {
      return {
        success: false,
        skillId,
        skillVersion: 0,
        summary: `Skill ${skillId} not found.`,
        executedStepsCount: 0,
        durationMs: 0,
        adaptedVariables: variableValues,
        errors: [`Skill ${skillId} not found.`],
      };
    }

    if (skill.status === 'disabled') {
      return {
        success: false,
        skillId: skill.id,
        skillVersion: skill.version,
        summary: `Skill "${skill.name}" is disabled and cannot be executed.`,
        executedStepsCount: 0,
        durationMs: 0,
        adaptedVariables: variableValues,
        errors: [`Skill "${skill.name}" is currently disabled.`],
      };
    }

    // Security evaluation
    const secAssessment = this.securityGuard.evaluateSkillSecurity(skill);
    if (!secAssessment.allowed) {
      return {
        success: false,
        skillId: skill.id,
        skillVersion: skill.version,
        summary: `Security policy blocked skill execution: ${secAssessment.reason}`,
        executedStepsCount: 0,
        durationMs: 0,
        adaptedVariables: variableValues,
        errors: [secAssessment.reason],
      };
    }

    // Adapt skill to ExecutionPlan
    const startMs = Date.now();
    const { plan, resolvedVariables } = this.adapter.adaptSkillToExecutionPlan(skill, variableValues);

    // Validate Plan
    const val = this.validator.validateSkill(skill);
    if (!val.valid) {
      return {
        success: false,
        skillId: skill.id,
        skillVersion: skill.version,
        summary: `Skill validation failed: ${val.errors.join('; ')}`,
        executedStepsCount: 0,
        durationMs: 0,
        adaptedVariables: resolvedVariables,
        errors: val.errors,
      };
    }

    // Execute through AgentRuntime using the resolved skill execution plan
    const runRes = await agentRuntime.executePlan(plan);
    const durationMs = Date.now() - startMs;

    // Record outcome
    await this.provider.recordUsage(skill.id, runRes.success, durationMs);

    return {
      success: runRes.success,
      skillId: skill.id,
      skillVersion: skill.version,
      summary: runRes.summary,
      executedStepsCount: plan.steps.length,
      durationMs,
      adaptedVariables: resolvedVariables,
    };
  }

  // Safe Test Mode
  async prepareSkillTestMode(skillId: string, variableValues: Record<string, any> = {}) {
    const skill = await this.provider.getSkill(skillId);
    if (!skill) throw new Error(`Skill ${skillId} not found.`);

    const { plan, resolvedVariables } = this.adapter.adaptSkillToExecutionPlan(skill, variableValues);
    const secAssessment = this.securityGuard.evaluateSkillSecurity(skill);

    return {
      skill,
      goal: plan.goal,
      steps: plan.steps,
      resolvedVariables,
      requiresApproval: secAssessment.requiresApproval,
      securityReason: secAssessment.reason,
    };
  }

  getMemoryItemForSkill(skill: Skill) {
    return this.memoryBridge.convertSkillToMemoryItem(skill);
  }
}
