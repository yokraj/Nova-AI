import { apiClient } from '../../lib/axios';

export interface MissionApiItem {
  id: string;
  title: string;
  goal: string;
  category: string;
  status: string;
  progressPercent: number;
  assignedAgent?: string;
  tasks?: any[];
  createdAt: string;
  updatedAt: string;
}

export class MissionApiService {
  async listMissions(): Promise<MissionApiItem[]> {
    try {
      const res = await apiClient.get('/missions');
      return res.data;
    } catch (err) {
      console.warn('Backend missions API unavailable, returning empty list:', err);
      return [];
    }
  }

  async createMission(mission: { title: string; goal: string; category?: string; tasks?: any[] }): Promise<MissionApiItem> {
    try {
      const res = await apiClient.post('/missions', mission);
      return res.data;
    } catch (err) {
      const now = new Date().toISOString();
      return {
        id: `mission-local-${Date.now()}`,
        title: mission.title,
        goal: mission.goal,
        category: mission.category || 'automation',
        status: 'PENDING',
        progressPercent: 0,
        tasks: mission.tasks || [],
        createdAt: now,
        updatedAt: now,
      };
    }
  }

  async pauseMission(id: string): Promise<MissionApiItem | null> {
    try {
      const res = await apiClient.post(`/missions/${id}/pause`);
      return res.data;
    } catch {
      return null;
    }
  }

  async resumeMission(id: string): Promise<MissionApiItem | null> {
    try {
      const res = await apiClient.post(`/missions/${id}/resume`);
      return res.data;
    } catch {
      return null;
    }
  }

  async cancelMission(id: string): Promise<MissionApiItem | null> {
    try {
      const res = await apiClient.post(`/missions/${id}/cancel`);
      return res.data;
    } catch {
      return null;
    }
  }

  async getCheckpoints(id: string): Promise<any[]> {
    try {
      const res = await apiClient.get(`/missions/${id}/checkpoints`);
      return res.data;
    } catch {
      return [];
    }
  }

  async createCheckpoint(id: string, checkpointData: any): Promise<any> {
    try {
      const res = await apiClient.post(`/missions/${id}/checkpoints`, checkpointData);
      return res.data;
    } catch {
      return null;
    }
  }

  async respondApproval(id: string, approved: boolean, authorizedBy: string = 'Operator'): Promise<any> {
    try {
      const res = await apiClient.post(`/missions/${id}/approval`, { approved, authorizedBy });
      return res.data;
    } catch {
      return null;
    }
  }
}

export const missionApiService = new MissionApiService();
