import { SkillVariable } from '../types/skill';

export interface ExtractedVariablesResult {
  variables: SkillVariable[];
  parameterizedSteps: Array<{
    stepNumber: number;
    toolName?: string;
    originalArgs?: Record<string, any>;
    argumentTemplates?: Record<string, string>;
  }>;
}

export class VariableExtractor {
  extractVariables(
    steps: Array<{ stepNumber: number; toolName?: string; toolArgs?: Record<string, any> }>,
    goalText: string
  ): ExtractedVariablesResult {
    const variables: SkillVariable[] = [];
    const varMap = new Map<string, SkillVariable>();

    const parameterizedSteps: Array<{
      stepNumber: number;
      toolName?: string;
      originalArgs?: Record<string, any>;
      argumentTemplates?: Record<string, string>;
    }> = [];

    // Helper to register dynamic variable
    const registerVar = (
      suggestedName: string,
      type: 'string' | 'number' | 'boolean' | 'path' | 'url',
      description: string,
      defaultValue: any
    ): string => {
      let varName = suggestedName;
      let counter = 1;
      while (varMap.has(varName) && varMap.get(varName)?.defaultValue !== defaultValue) {
        varName = `${suggestedName}${counter++}`;
      }

      if (!varMap.has(varName)) {
        const v: SkillVariable = {
          name: varName,
          type,
          description,
          required: true,
          defaultValue: defaultValue?.toString() || '',
          examples: [defaultValue?.toString() || ''],
        };
        varMap.set(varName, v);
      }
      return varName;
    };

    // Extract from Goal Text first (e.g. project name, folder name)
    const projectMatch = goalText.match(/(?:project|app|called|named|folder)\s+([A-Za-z0-9_-]+)/i);
    let goalProjectName: string | undefined;
    if (projectMatch && projectMatch[1]) {
      goalProjectName = projectMatch[1];
      registerVar('projectName', 'string', 'Target project name', goalProjectName);
    }

    for (const step of steps) {
      const argumentTemplates: Record<string, string> = {};
      const args = step.toolArgs || {};

      for (const [key, val] of Object.entries(args)) {
        if (typeof val === 'string') {
          // Check if value matches goal project name
          if (goalProjectName && val.includes(goalProjectName)) {
            const template = val.replace(goalProjectName, `{{projectName}}`);
            argumentTemplates[key] = template;
          }
          // Check if path
          else if (val.includes('/') || val.includes('\\') || key === 'path' || key === 'location') {
            // Replace user-specific desktop path or extract trailing folder
            let semanticPath = val;
            if (val.match(/^[A-Z]:\\Users\\[^\\]+\\Desktop/i)) {
              semanticPath = val.replace(/^[A-Z]:\\Users\\[^\\]+\\/i, '');
            } else if (val.match(/^[A-Z]:\\Users\\[^\\]+\\/i)) {
              semanticPath = val.replace(/^[A-Z]:\\Users\\[^\\]+\\/i, '');
            }

            // Extract variable
            const varName = registerVar(key === 'path' ? 'targetPath' : key, 'path', `Target file or directory path`, semanticPath);
            argumentTemplates[key] = `{{${varName}}}`;
          }
          // Check if URL
          else if (val.startsWith('http://') || val.startsWith('https://') || key === 'url') {
            const varName = registerVar('targetUrl', 'url', 'Target website URL', val);
            argumentTemplates[key] = `{{${varName}}}`;
          }
          // Check if app name
          else if (key === 'applicationName' || key === 'processName') {
            const varName = registerVar('appName', 'string', 'Target application name', val);
            argumentTemplates[key] = `{{${varName}}}`;
          }
          // Generic text/query
          else if (key === 'text' || key === 'query' || key === 'targetQuery') {
            const varName = registerVar(key, 'string', `Target ${key}`, val);
            argumentTemplates[key] = `{{${varName}}}`;
          } else {
            argumentTemplates[key] = String(val);
          }
        } else if (typeof val === 'number') {
          const varName = registerVar(key, 'number', `Numeric argument ${key}`, val);
          argumentTemplates[key] = `{{${varName}}}`;
        } else {
          argumentTemplates[key] = JSON.stringify(val);
        }
      }

      parameterizedSteps.push({
        stepNumber: step.stepNumber,
        toolName: step.toolName,
        originalArgs: args,
        argumentTemplates,
      });
    }

    return {
      variables: Array.from(varMap.values()),
      parameterizedSteps,
    };
  }
}
