import { Skill } from '../types/skill';

export interface MissionSkillTemplate {
  taskId: string;
  taskTitle: string;
  skillId: string;
  skillName: string;
  stepsCount: number;
  requiredTools: string[];
}

export class SkillMissionBridge {
  createMissionTaskFromSkill(skill: Skill, taskId: string): MissionSkillTemplate {
    return {
      taskId,
      taskTitle: `Execute Skill: ${skill.name}`,
      skillId: skill.id,
      skillName: skill.name,
      stepsCount: skill.steps.length,
      requiredTools: [...skill.requiredTools],
    };
  }
}
