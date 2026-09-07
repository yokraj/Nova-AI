import { ScheduledTask, TriggerType } from '../types/scheduledTask';

export interface TriggerEvent {
  type: TriggerType;
  targetPath?: string;
  processName?: string;
  skillId?: string;
  missionId?: string;
  timestamp: string;
}

export class TriggerEngine {
  matchEventToTasks(event: TriggerEvent, tasks: ScheduledTask[]): ScheduledTask[] {
    const matched: ScheduledTask[] = [];

    for (const task of tasks) {
      if (!task.enabled || !task.trigger) continue;
      if (task.trigger.type !== event.type) continue;

      let isMatch = false;

      if (event.type.startsWith('FILE_')) {
        if (event.targetPath && task.trigger.targetPath) {
          isMatch = event.targetPath.toLowerCase().includes(task.trigger.targetPath.toLowerCase());
        } else {
          isMatch = true;
        }
      } else if (event.type.includes('PROCESS_') || event.type.includes('APPLICATION_')) {
        if (event.processName && task.trigger.processName) {
          isMatch = event.processName.toLowerCase().includes(task.trigger.processName.toLowerCase());
        } else {
          isMatch = true;
        }
      } else if (event.type === 'SKILL_COMPLETED') {
        if (event.skillId && task.trigger.skillId) {
          isMatch = event.skillId === task.trigger.skillId;
        } else {
          isMatch = true;
        }
      } else if (event.type === 'MISSION_COMPLETED') {
        if (event.missionId && task.trigger.missionId) {
          isMatch = event.missionId === task.trigger.missionId;
        } else {
          isMatch = true;
        }
      } else {
        isMatch = true;
      }

      if (isMatch) {
        matched.push(task);
      }
    }

    return matched;
  }
}
