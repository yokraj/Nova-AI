import { MissionItem, MissionProvider } from '../types/mission';
import { MissionTask } from '../types/missionTask';
import { MissionPlan, MissionPlanningProvider } from '../types/missionPlan';
import { MOCK_MISSIONS, MOCK_MISSION_TASKS } from './mockMissionData';

export class MockMissionEngine implements MissionProvider, MissionPlanningProvider {
  private missions: MissionItem[] = [...MOCK_MISSIONS];
  private taskMap: Record<string, MissionTask[]> = { ...MOCK_MISSION_TASKS };

  listMissions(): MissionItem[] {
    return this.missions;
  }

  getMissionById(id: string): MissionItem | undefined {
    return this.missions.find((m) => m.id === id);
  }

  getTasksForMission(missionId: string): MissionTask[] {
    return this.taskMap[missionId] || [];
  }

  understandGoal(goal: string) {
    return {
      outcome: `Production-ready deliverable for goal: "${goal}"`,
      constraints: ['React', 'TypeScript', 'Zero Backend Mutation', 'Local-First Safety'],
    };
  }

  generatePlan(missionId: string, goal: string): MissionPlan {
    const tasks: MissionTask[] = [
      {
        id: `tsk-${Date.now()}-1`,
        missionId,
        title: 'Analyze Requirements & Constraints',
        description: 'Define execution blueprint and agent dependencies.',
        status: 'COMPLETED',
        progress: 100,
        assignedAgentId: 'ag-architect',
        assignedAgentName: 'Solution Architect Agent',
        dependencies: [],
        toolsRequired: ['Memory Store'],
        permissionsRequired: ['fileSystemRead'],
      },
      {
        id: `tsk-${Date.now()}-2`,
        missionId,
        title: 'Execute Primary Implementation',
        description: 'Build core application structures.',
        status: 'RUNNING',
        progress: 50,
        assignedAgentId: 'ag-fe',
        assignedAgentName: 'Engineering Agent',
        dependencies: [`tsk-${Date.now()}-1`],
        toolsRequired: ['File System', 'TypeScript'],
        permissionsRequired: ['fileSystemWrite'],
      },
    ];

    this.taskMap[missionId] = tasks;

    return {
      missionId,
      inferredOutcome: `Completed deliverable for "${goal}"`,
      constraints: ['React', 'TypeScript', 'Security Gate'],
      tasks,
      estimatedTimeSeconds: 45,
    };
  }

  createMission(goal: string, autonomyLevel: 'ASSISTED' | 'SUPERVISED' | 'AUTONOMOUS' = 'SUPERVISED'): MissionItem {
    const id = `msn_${Date.now()}`;
    const newMission: MissionItem = {
      id,
      title: goal.length > 50 ? goal.slice(0, 50) + '...' : goal,
      goal,
      description: `Autonomous mission inferred by Nova for "${goal}".`,
      status: 'PLANNING',
      priority: 'HIGH',
      autonomyLevel,
      progress: 25,
      createdAt: new Date().toLocaleTimeString(),
      assignedAgents: ['Solution Architect', 'Engineering Agent'],
      tasksCount: 2,
      completedTasksCount: 1,
    };

    this.missions.unshift(newMission);
    this.generatePlan(id, goal);

    return newMission;
  }

  pauseMission(id: string) {
    const m = this.getMissionById(id);
    if (m) m.status = 'PAUSED';
  }

  resumeMission(id: string) {
    const m = this.getMissionById(id);
    if (m) m.status = 'EXECUTING';
  }

  cancelMission(id: string) {
    const m = this.getMissionById(id);
    if (m) m.status = 'CANCELLED';
  }

  replanMission(id: string) {
    const m = this.getMissionById(id);
    if (m) {
      m.status = 'REPLANNING';
      setTimeout(() => {
        m.status = 'EXECUTING';
      }, 1000);
    }
  }
}
