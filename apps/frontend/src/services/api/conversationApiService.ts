import { apiClient } from '../../lib/axios';

export interface ConversationApiItem {
  id: string;
  title: string;
  status: string;
  createdAt: string;
  updatedAt: string;
}

export interface MessageApiItem {
  id: string;
  conversationId: string;
  role: string;
  content: string;
  tokenCount: number;
  createdAt: string;
}

export class ConversationApiService {
  async listConversations(): Promise<ConversationApiItem[]> {
    try {
      const res = await apiClient.get('/conversations');
      return res.data;
    } catch (err) {
      console.warn('Backend conversations unavailable, returning empty list fallback:', err);
      return [];
    }
  }

  async createConversation(title: string): Promise<ConversationApiItem> {
    try {
      const res = await apiClient.post('/conversations', { title });
      return res.data;
    } catch (err) {
      console.warn('Backend unavailable, generating local conversation item:', err);
      return {
        id: `conv-local-${Date.now()}`,
        title,
        status: 'ACTIVE',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    }
  }

  async getConversation(id: string): Promise<ConversationApiItem | null> {
    try {
      const res = await apiClient.get(`/conversations/${id}`);
      return res.data;
    } catch (err) {
      return null;
    }
  }

  async addMessage(conversationId: string, role: string, content: string): Promise<MessageApiItem> {
    try {
      const res = await apiClient.post(`/conversations/${conversationId}/messages`, {
        role,
        content,
      });
      return res.data;
    } catch (err) {
      return {
        id: `msg-local-${Date.now()}`,
        conversationId,
        role,
        content,
        tokenCount: content.split(/\s+/).length,
        createdAt: new Date().toISOString(),
      };
    }
  }
}

export const conversationApiService = new ConversationApiService();
