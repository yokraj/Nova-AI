import { apiClient } from '../../lib/axios';

export interface AgentApiItem {
  id: string;
  name: string;
  role: string;
  description: string;
  status: string;
  capabilities: string[];
  performanceScore: number;
  tasksCompleted: number;
  createdAt: string;
  updatedAt: string;
}

export class AgentApiService {
  async listAgents(): Promise<AgentApiItem[]> {
    try {
      const res = await apiClient.get('/agents');
      return res.data;
    } catch (err) {
      console.warn('Backend agents API unavailable, returning empty list:', err);
      return [];
    }
  }

  async createAgent(agent: { name: string; role: string; description: string; capabilities?: string[] }): Promise<AgentApiItem> {
    try {
      const res = await apiClient.post('/agents', agent);
      return res.data;
    } catch (err) {
      const now = new Date().toISOString();
      return {
        id: `agent-local-${Date.now()}`,
        name: agent.name,
        role: agent.role,
        description: agent.description,
        status: 'IDLE',
        capabilities: agent.capabilities || [],
        performanceScore: 1.0,
        tasksCompleted: 0,
        createdAt: now,
        updatedAt: now,
      };
    }
  }
}

export const agentApiService = new AgentApiService();
