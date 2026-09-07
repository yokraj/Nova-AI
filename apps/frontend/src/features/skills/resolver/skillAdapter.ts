import { Skill } from '../types/skill';
import { ExecutionPlan } from '../../ai-runtime/types/executionPlan';
import { ExecutionStep } from '../../ai-runtime/types/executionStep';
import { ToolCall } from '../../ai-runtime/types/toolCall';

export class SkillAdapter {
  adaptSkillToExecutionPlan(
    skill: Skill,
    variableValues: Record<string, any> = {}
  ): {
    plan: ExecutionPlan;
    resolvedVariables: Record<string, any>;
  } {
    // 1. Resolve variables (use provided -> default -> example -> empty string)
    const resolvedVariables: Record<string, any> = {};

    for (const v of skill.variables) {
      if (variableValues[v.name] !== undefined) {
        resolvedVariables[v.name] = variableValues[v.name];
      } else if (v.defaultValue !== undefined) {
        resolvedVariables[v.name] = v.defaultValue;
      } else if (v.examples && v.examples.length > 0) {
        resolvedVariables[v.name] = v.examples[0];
      } else {
        resolvedVariables[v.name] = '';
      }
    }

    // 2. Build ExecutionSteps from SkillSteps with variable substitution
    const executionSteps: ExecutionStep[] = skill.steps.map((step) => {
      const substitutedArgs: Record<string, any> = { ...step.arguments };

      if (step.argumentTemplates) {
        for (const [argKey, templateStr] of Object.entries(step.argumentTemplates)) {
          let valStr = String(templateStr);
          for (const [varName, varVal] of Object.entries(resolvedVariables)) {
            valStr = valStr.replace(new RegExp(`\\{\\{${varName}\\}\\}`, 'g'), String(varVal));
          }
          substitutedArgs[argKey] = valStr;
        }
      }

      const toolCall: ToolCall = {
        callId: `call-${skill.id}-step-${step.order}`,
        toolName: step.tool,
        arguments: substitutedArgs,
      };

      return {
        id: step.id || `step-${step.order}`,
        stepNumber: step.order,
        title: step.purpose,
        description: step.purpose,
        toolCall,
        status: 'PENDING',
        verificationConfirmed: false,
      };
    });

    const goal = `Execute Skill: ${skill.name} (v${skill.version})`;
    const plan: ExecutionPlan = {
      planId: `plan-skill-${skill.id}-${Date.now()}`,
      goal,
      goalText: goal,
      steps: executionSteps,
      estimatedDurationSeconds: 1.0,
      createdAt: new Date().toISOString(),
    };

    return {
      plan,
      resolvedVariables,
    };
  }
}
