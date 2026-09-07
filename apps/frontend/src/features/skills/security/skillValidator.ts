import { Skill, SkillStep } from '../types/skill';
import { ToolRegistry } from '../../ai-runtime/tool-router/toolRegistry';

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export class SkillValidator {
  private toolRegistry = new ToolRegistry();

  validateSkill(skill: Skill): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // 1. Basic properties check
    if (!skill.name || skill.name.trim().length === 0) {
      errors.push('Skill must have a non-empty name.');
    }
    if (!skill.purpose || skill.purpose.trim().length === 0) {
      errors.push('Skill must have a non-empty purpose.');
    }
    if (!skill.steps || skill.steps.length === 0) {
      errors.push('Skill must contain at least one step.');
    }

    // 2. Variable definition check
    const definedVarNames = new Set(skill.variables.map((v) => v.name));

    // 3. Step & Tool validation
    skill.steps.forEach((step, idx) => {
      if (!step.tool) {
        errors.push(`Step ${idx + 1} is missing a tool declaration.`);
        return;
      }

      // Check tool exists in ToolRegistry
      const registeredTool = this.toolRegistry.getTool(step.tool);
      if (!registeredTool) {
        errors.push(`Step ${idx + 1} references unverified tool "${step.tool}" not found in ToolRegistry.`);
      }

      // Check template variables match defined variables
      if (step.argumentTemplates) {
        for (const [argKey, templateVal] of Object.entries(step.argumentTemplates)) {
          const varMatches = String(templateVal).match(/\{\{([^}]+)\}\}/g);
          if (varMatches) {
            for (const match of varMatches) {
              const varName = match.replace(/[{}]/g, '');
              if (!definedVarNames.has(varName)) {
                errors.push(`Step ${idx + 1} argument "${argKey}" uses undefined variable "${varName}".`);
              }
            }
          }
        }
      }

      // Check for raw shell execution or unsafe code string
      const rawArgString = JSON.stringify(step.arguments) + JSON.stringify(step.argumentTemplates || {});
      if (
        rawArgString.includes('cmd.exe') ||
        rawArgString.includes('powershell -Command') ||
        rawArgString.includes('rm -rf') ||
        rawArgString.includes('exec(') ||
        rawArgString.includes('eval(')
      ) {
        errors.push(`Step ${idx + 1} contains prohibited raw shell or unsafe code execution string.`);
      }
    });

    // 4. Verification rules check
    const stepHasVerification = skill.steps.some((s) => s.verification !== undefined || s.expectedObservation !== undefined);
    if (!stepHasVerification && skill.verificationRules.length === 0) {
      warnings.push('Skill has no step verifications or explicit verification rules.');
    }

    // 5. Sensitive data check
    const skillContent = JSON.stringify(skill).toLowerCase();
    const sensitiveTerms = ['password', 'secret', 'apikey', 'api_key', 'token', 'private_key', 'auth_token', 'bearer'];
    for (const term of sensitiveTerms) {
      if (skillContent.includes(`"${term}"`) || skillContent.includes(`:${term}`)) {
        errors.push(`Skill contains prohibited sensitive credential keyword "${term}".`);
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
    };
  }

  isStepSafeForAutomatedExtraction(step: SkillStep): boolean {
    const rawString = JSON.stringify(step).toLowerCase();
    const destructiveTerms = ['delete', 'remove', 'format', 'shutdown', 'restart', 'kill', 'terminate'];

    return !destructiveTerms.some((t) => rawString.includes(t));
  }
}
