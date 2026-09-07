import { WorkflowDefinition, WorkflowVariable } from '../types/workflowStudio';

export class WorkflowVariableExtractor {
  extractVariables(workflow: WorkflowDefinition): WorkflowVariable[] {
    const varsMap = new Map<string, WorkflowVariable>();

    // 1. Scan explicit {{varName}} templates in node labels and argument strings
    for (const node of workflow.nodes) {
      const textsToScan: string[] = [node.label, node.visualTargetQuery || '', node.expectedState || ''];
      if (node.arguments) {
        for (const val of Object.values(node.arguments)) {
          if (typeof val === 'string') textsToScan.push(val);
        }
      }

      for (const text of textsToScan) {
        const matches = text.match(/{{([a-zA-Z0-9_]+)}}/g);
        if (matches) {
          for (const match of matches) {
            const varName = match.replace(/[{}]/g, '').trim();
            if (!varsMap.has(varName)) {
              varsMap.set(varName, {
                name: varName,
                type: varName.toLowerCase().includes('path') ? 'PATH' : varName.toLowerCase().includes('url') ? 'URL' : 'STRING',
                defaultValue: '',
                required: true,
                description: `Dynamic variable extracted from workflow template: ${varName}`,
              });
            }
          }
        }
      }
    }

    return Array.from(varsMap.values());
  }

  substituteVariables(template: string, values: Record<string, any>): string {
    if (!template) return template;
    let result = template;
    for (const [key, val] of Object.entries(values)) {
      const pattern = new RegExp(`\\{\\{${key}\\}\\}`, 'g');
      result = result.replace(pattern, String(val));
    }
    return result;
  }
}
