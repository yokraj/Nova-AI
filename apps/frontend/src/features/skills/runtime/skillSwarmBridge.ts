import { Skill } from '../types/skill';

export interface SwarmAgentCapabilityCheck {
  canExecute: boolean;
  reason: string;
  missingTools: string[];
}

export class SkillSwarmBridge {
  verifySwarmAgentCanExecuteSkill(
    skill: Skill,
    agentCapabilities: string[],
    agentRole: string
  ): SwarmAgentCapabilityCheck {
    const missingTools: string[] = [];

    // Check if agent's role or capabilities allow all tools in the skill
    for (const tool of skill.requiredTools) {
      const domain = tool.split('.')[0];
      if (!agentCapabilities.includes(domain) && !agentCapabilities.includes(tool) && agentRole !== 'orchestrator') {
        missingTools.push(tool);
      }
    }

    if (missingTools.length > 0) {
      return {
        canExecute: false,
        reason: `Swarm Agent (${agentRole}) lacks required capabilities/tools: ${missingTools.join(', ')}`,
        missingTools,
      };
    }

    return {
      canExecute: true,
      reason: `Swarm Agent (${agentRole}) has required capabilities to execute skill "${skill.name}".`,
      missingTools: [],
    };
  }
}
