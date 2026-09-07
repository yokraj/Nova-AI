import { apiClient } from '../../lib/axios';

export interface KnowledgeEntityApi {
  id: string;
  name: string;
  entityType: string;
  description?: string;
  workspace: string;
  project?: string;
}

export class KnowledgeApiService {
  async listEntities(): Promise<KnowledgeEntityApi[]> {
    try {
      const res = await apiClient.get('/graph/entities');
      return res.data;
    } catch (err) {
      console.warn('Backend graph API unavailable, returning empty list:', err);
      return [];
    }
  }

  async createEntity(entity: Omit<KnowledgeEntityApi, 'id'>): Promise<KnowledgeEntityApi> {
    try {
      const res = await apiClient.post('/graph/entities', entity);
      return res.data;
    } catch (err) {
      return {
        ...entity,
        id: `entity-local-${Date.now()}`,
      };
    }
  }
}

export const knowledgeApiService = new KnowledgeApiService();
