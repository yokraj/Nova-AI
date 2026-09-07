import { Skill } from '../types/skill';
import { MemoryItem } from '../../memory/types/memory';

export class SkillMemoryBridge {
  convertSkillToMemoryItem(skill: Skill): MemoryItem {
    return {
      id: `mem-${skill.id}`,
      type: 'Workflow',
      title: `Learned Skill: ${skill.name}`,
      content: `Learned multi-step workflow "${skill.name}" with ${skill.steps.length} steps. Purpose: ${skill.purpose}. Required tools: ${skill.requiredTools.join(', ')}.`,
      summary: skill.description,
      createdAt: skill.createdAt,
      updatedAt: skill.updatedAt,
      source: {
        origin: 'User instruction',
        timestamp: skill.createdAt,
        referenceId: skill.id,
        confidence: skill.confidence,
      },
      importance: skill.category === 'system' ? 'High' : 'Normal',
      confidence: skill.confidence,
      tags: [...skill.tags, 'learned_skill', skill.category],
      project: 'Nova',
      workspace: 'LocalWorkstation',
      relationships: [skill.id],
      status: skill.status === 'active' ? 'active' : 'archived',
    };
  }
}
