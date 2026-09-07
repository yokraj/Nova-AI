import { apiClient } from '../../lib/axios';
import { MemoryItem } from '../../features/memory/types/memory';

export class MemoryApiService {
  async listMemories(): Promise<MemoryItem[]> {
    try {
      const res = await apiClient.get('/memories');
      return res.data;
    } catch (err) {
      console.warn('Backend memories API unavailable, returning empty list:', err);
      return [];
    }
  }

  async createMemory(memory: Omit<MemoryItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<MemoryItem> {
    try {
      const res = await apiClient.post('/memories', memory);
      return res.data;
    } catch (err) {
      console.warn('Backend unavailable, creating local fallback memory:', err);
      const now = new Date().toISOString();
      return {
        ...memory,
        id: `mem-local-${Date.now()}`,
        createdAt: now,
        updatedAt: now,
      };
    }
  }

  async searchMemories(query: string): Promise<MemoryItem[]> {
    try {
      const res = await apiClient.get('/memories/search', { params: { query } });
      return res.data;
    } catch (err) {
      return [];
    }
  }
}

export const memoryApiService = new MemoryApiService();
