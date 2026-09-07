import { apiClient } from '../../lib/axios';
import { Skill, SkillFilter } from '../../features/skills/types/skill';

export class SkillApiService {
  async listSkills(filter?: SkillFilter): Promise<Skill[]> {
    try {
      const params: Record<string, any> = {};
      if (filter?.category) params.category = filter.category;
      if (filter?.status) params.status = filter.status;
      if (filter?.searchQuery) params.query = filter.searchQuery;

      const res = await apiClient.get('/skills', { params });
      return res.data;
    } catch (err) {
      console.warn('Backend skills API unavailable, throwing for local fallback:', err);
      throw err;
    }
  }

  async createSkill(skillData: Omit<Skill, 'id' | 'createdAt' | 'updatedAt' | 'usageCount' | 'successRate' | 'version' | 'history'>): Promise<Skill> {
    try {
      const res = await apiClient.post('/skills', skillData);
      return res.data;
    } catch (err) {
      console.warn('Backend skills API unavailable, throwing for local fallback:', err);
      throw err;
    }
  }

  async getSkill(id: string): Promise<Skill | undefined> {
    try {
      const res = await apiClient.get(`/skills/${id}`);
      return res.data;
    } catch (err) {
      return undefined;
    }
  }

  async updateSkill(id: string, updates: Partial<Skill>): Promise<Skill> {
    const res = await apiClient.put(`/skills/${id}`, updates);
    return res.data;
  }

  async deleteSkill(id: string): Promise<boolean> {
    const res = await apiClient.delete(`/skills/${id}`);
    return res.status === 200;
  }
}

export const skillApiService = new SkillApiService();
