import { apiClient } from '../../lib/axios';

export interface AuditEventApiItem {
  id: string;
  eventType: string;
  action: string;
  toolName?: string;
  riskLevel: string;
  actor: string;
  decision: string;
  details: Record<string, any>;
  createdAt: string;
}

export class AuditApiService {
  async recordAuditEvent(event: Omit<AuditEventApiItem, 'id' | 'createdAt'>): Promise<AuditEventApiItem> {
    try {
      const res = await apiClient.post('/audit/events', event);
      return res.data;
    } catch (err) {
      return {
        ...event,
        id: `audit-local-${Date.now()}`,
        createdAt: new Date().toISOString(),
      };
    }
  }

  async listAuditEvents(limit = 50): Promise<AuditEventApiItem[]> {
    try {
      const res = await apiClient.get('/audit/events', { params: { limit } });
      return res.data;
    } catch (err) {
      return [];
    }
  }
}

export const auditApiService = new AuditApiService();
