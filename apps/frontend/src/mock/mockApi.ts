import { MOCK_DASHBOARD_METRICS, MOCK_SYSTEM_HEALTH } from './mockDashboard';
import { MOCK_CHAT_MESSAGES } from './mockChat';
import { MOCK_MEMORY_ITEMS } from './mockMemory';
import { MOCK_AGENTS } from './mockAgents';
import { MOCK_ANALYTICS_DATA } from './mockAnalytics';
import { MOCK_REPOSITORIES } from './mockRepositories';
import { MOCK_MODELS } from './mockModels';
import { MOCK_NOTIFICATIONS } from './mockNotifications';
import { MOCK_SETTINGS } from './mockSettings';

/**
 * Mock API Service Layer for Frontend Isolation.
 * Simulates async HTTP response delays.
 */
export const mockApi = {
  getDashboardMetrics: async () => {
    await delay(150);
    return MOCK_DASHBOARD_METRICS;
  },
  getSystemHealth: async () => {
    await delay(100);
    return MOCK_SYSTEM_HEALTH;
  },
  getChatMessages: async () => {
    await delay(100);
    return MOCK_CHAT_MESSAGES;
  },
  getMemoryItems: async () => {
    await delay(120);
    return MOCK_MEMORY_ITEMS;
  },
  getAgents: async () => {
    await delay(100);
    return MOCK_AGENTS;
  },
  getAnalyticsData: async () => {
    await delay(150);
    return MOCK_ANALYTICS_DATA;
  },
  getRepositories: async () => {
    await delay(120);
    return MOCK_REPOSITORIES;
  },
  getModels: async () => {
    await delay(100);
    return MOCK_MODELS;
  },
  getNotifications: async () => {
    await delay(80);
    return MOCK_NOTIFICATIONS;
  },
  getSettings: async () => {
    await delay(80);
    return MOCK_SETTINGS;
  },
};

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
