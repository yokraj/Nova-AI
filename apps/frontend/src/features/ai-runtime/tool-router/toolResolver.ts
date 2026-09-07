import { ToolRegistry } from './toolRegistry';
import { StructuredToolCall } from '../types/toolCall';

export class ToolResolver {
  private registry = new ToolRegistry();

  validateCall(toolCall: StructuredToolCall): { isValid: boolean; reason?: string } {
    if (!this.registry.hasTool(toolCall.toolName)) {
      return { isValid: false, reason: `Tool "${toolCall.toolName}" is not registered in ToolRegistry.` };
    }

    const tool = this.registry.getTool(toolCall.toolName)!;
    const args = toolCall.arguments || (toolCall as any).parameters || {};
    for (const [paramName, paramType] of Object.entries(tool.parametersSchema)) {
      if (args[paramName] === undefined) {
        return { isValid: false, reason: `Missing required argument "${paramName}" for tool "${toolCall.toolName}".` };
      }
    }

    return { isValid: true };
  }
}
