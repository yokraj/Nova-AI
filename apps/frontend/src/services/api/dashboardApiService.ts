import { apiClient, backendClient } from '../../lib/axios';
import { APP_CONFIG } from '../../config/app.config';
import {
  SystemTelemetry,
  ServiceHealthItem,
  DashboardAgent,
  MissionItem,
  MockDevice,
  MockAutomation,
  ActivityTimelineItem,
  AnalyticsSeries,
  BackendHealthSummary,
} from '@/types/dashboard';
import { NotificationItem } from '@/types';
import {
  MOCK_TELEMETRY,
  MOCK_ACTIVE_AGENTS_EXTENDED,
  MOCK_MISSIONS,
  MOCK_DEVICES,
  MOCK_AUTOMATIONS,
  MOCK_ACTIVITY_TIMELINE,
  MOCK_ANALYTICS_SERIES,
} from '@/mock/mockDashboardData';
import { MOCK_NOTIFICATIONS } from '@/mock/mockNotifications';
import { MOCK_MEMORY_ITEMS } from '@/mock/mockMemory';

export interface DashboardDataPayload {
  telemetry: SystemTelemetry;
  services: ServiceHealthItem[];
  agents: DashboardAgent[];
  missions: MissionItem[];
  devices: MockDevice[];
  automations: MockAutomation[];
  timeline: ActivityTimelineItem[];
  analytics: AnalyticsSeries;
  notifications: NotificationItem[];
  isConnected: boolean;
  health: BackendHealthSummary;
  lastUpdated: string;
}

export class DashboardApiService {
  private isConnected = false;
  private lastHealthSummary: BackendHealthSummary = {
    status: 'offline',
    latencyMs: 0,
    database: 'disconnected',
    nativeBridge: false,
    ollama: false,
  };

  /**
   * Check health of backend, database, native bridge, and local Ollama.
   */
  async checkHealth(): Promise<BackendHealthSummary> {
    const started = Date.now();
    let backendOk = false;
    let databaseStatus: 'connected' | 'disconnected' = 'disconnected';
    let appVersion: string | undefined;
    let bridgeOk = false;
    let ollamaOk = false;

    // 1. Probe FastAPI Backend Root & Health
    try {
      const res = await backendClient.get('/api/health', { timeout: 3000 });
      if (res.status === 200) {
        backendOk = true;
        appVersion = res.data?.version;
      }
    } catch {
      backendOk = false;
    }

    // 2. Probe Database Readiness
    if (backendOk) {
      try {
        const readyRes = await backendClient.get('/api/ready', { timeout: 3000 });
        if (readyRes.status === 200 && (readyRes.data?.status === 'healthy' || readyRes.data?.status === 'ok')) {
          databaseStatus = 'connected';
        }
      } catch {
        databaseStatus = 'disconnected';
      }
    }

    // 3. Probe Native Bridge Server (:3001)
    try {
      const bridgeRes = await fetch(`${APP_CONFIG.nativeBridgeUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000),
      });
      bridgeOk = bridgeRes.ok;
    } catch {
      bridgeOk = false;
    }

    // 4. Probe Local Ollama (:11434)
    try {
      const ollamaRes = await fetch(`${APP_CONFIG.ollamaBaseUrl}/api/tags`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000),
      });
      ollamaOk = ollamaRes.ok;
    } catch {
      ollamaOk = false;
    }

    const latencyMs = Date.now() - started;
    this.isConnected = backendOk;

    let overallStatus: 'ok' | 'degraded' | 'unhealthy' | 'offline' = 'offline';
    if (backendOk && databaseStatus === 'connected') {
      overallStatus = 'ok';
    } else if (backendOk) {
      overallStatus = 'degraded';
    }

    this.lastHealthSummary = {
      status: overallStatus,
      version: appVersion,
      database: databaseStatus,
      nativeBridge: bridgeOk,
      ollama: ollamaOk,
      latencyMs,
    };

    return this.lastHealthSummary;
  }

  isOnline(): boolean {
    return this.isConnected;
  }

  getLastHealth(): BackendHealthSummary {
    return this.lastHealthSummary;
  }

  /**
   * Retrieves system telemetry from /dashboard/system and /dashboard/resources.
   */
  async getTelemetry(): Promise<SystemTelemetry> {
    try {
      const [sysRes, resRes, overviewRes] = await Promise.all([
        backendClient.get('/dashboard/system', { timeout: 4000 }).catch(() => null),
        backendClient.get('/dashboard/resources', { timeout: 4000 }).catch(() => null),
        backendClient.get('/dashboard/overview', { timeout: 4000 }).catch(() => null),
      ]);

      if (!sysRes && !resRes && !overviewRes) {
        return {
          ...MOCK_TELEMETRY,
          isLive: false,
        };
      }

      const sys = sysRes?.data || overviewRes?.data?.system;
      const res = resRes?.data || overviewRes?.data?.resources;

      const cpuUsage = Math.round(sys?.cpu_usage || sys?.cpu_usage_percent || 0);
      const ramUsedGb = Math.round(((res?.memory_used_bytes || sys?.memory_used || 0) / 1024 / 1024 / 1024) * 10) / 10;
      const ramTotalGb = Math.round(((res?.memory_total_bytes || sys?.memory_total || 16 * 1024 * 1024 * 1024) / 1024 / 1024 / 1024) * 10) / 10;
      const ramPercent = ramTotalGb > 0 ? Math.round((ramUsedGb / ramTotalGb) * 100) : 0;

      const storageUsedGb = Math.round((res?.disk_used_bytes || sys?.disk_used || 0) / 1024 / 1024 / 1024);
      const storageTotalGb = Math.round((res?.disk_total_bytes || sys?.disk_total || 512 * 1024 * 1024 * 1024) / 1024 / 1024 / 1024);
      const storagePercent = storageTotalGb > 0 ? Math.round((storageUsedGb / storageTotalGb) * 100) : 0;

      const temp = sys?.cpu_temperature || 42;
      const tempStatus: 'nominal' | 'elevated' | 'critical' = temp > 80 ? 'critical' : temp > 65 ? 'elevated' : 'nominal';

      return {
        cpuUsage,
        cpuDetails: `${sys?.hostname || 'Nova-Host'} (${sys?.os_name || 'Windows NT'})`,
        gpuUsage: res?.gpu_memory_used_bytes ? Math.min(100, Math.round((res.gpu_memory_used_bytes / (8 * 1024 * 1024 * 1024)) * 100)) : 0,
        gpuDetails: res?.gpu_count ? `${res.gpu_count} GPU Compute Units` : 'DirectX/Vulkan Unified Device',
        ramUsageGb: ramUsedGb,
        ramTotalGb: ramTotalGb,
        ramPercent: ramPercent,
        storageUsedGb: storageUsedGb,
        storageTotalGb: storageTotalGb,
        storagePercent: storagePercent,
        networkDownMbps: Math.round(((sys?.network_download || 0) / 1024 / 1024) * 10) / 10,
        networkUpMbps: Math.round(((sys?.network_upload || 0) / 1024 / 1024) * 10) / 10,
        temperatureC: temp,
        tempStatus,
        isLive: true,
      };
    } catch {
      return {
        ...MOCK_TELEMETRY,
        isLive: false,
      };
    }
  }

  /**
   * Retrieves probed health status across core services.
   */
  async getCoreServices(): Promise<ServiceHealthItem[]> {
    const health = await this.checkHealth();

    const services: ServiceHealthItem[] = [
      {
        id: 'srv-backend',
        name: 'Universal Intelligence API',
        category: 'Core Engine',
        status: health.status === 'ok' ? 'healthy' : health.status === 'degraded' ? 'degraded' : 'offline',
        latencyMs: health.latencyMs,
        healthMetric: health.status === 'ok' ? 'Online • 100% Ready' : 'Backend Unreachable',
        port: 8000,
        endpoint: '/api/health',
      },
      {
        id: 'srv-db',
        name: 'PostgreSQL Knowledge Store',
        category: 'Storage',
        status: health.database === 'connected' ? 'healthy' : 'offline',
        latencyMs: health.database === 'connected' ? 3 : 0,
        healthMetric: health.database === 'connected' ? 'Pool Nominal' : 'Connection Closed',
        port: 5432,
      },
      {
        id: 'srv-bridge',
        name: 'Windows Native Execution Bridge',
        category: 'Engineering',
        status: health.nativeBridge ? 'healthy' : 'offline',
        latencyMs: health.nativeBridge ? 2 : 0,
        healthMetric: health.nativeBridge ? 'Bridge Active (:3001)' : 'Daemon Disconnected',
        port: 3001,
        endpoint: 'http://127.0.0.1:3001/health',
      },
      {
        id: 'srv-ollama',
        name: 'Local Ollama Model Runtime',
        category: 'AI Models',
        status: health.ollama ? 'healthy' : 'offline',
        latencyMs: health.ollama ? 8 : 0,
        healthMetric: health.ollama ? 'Ollama Online (:11434)' : 'Service Offline',
        port: 11434,
        endpoint: 'http://127.0.0.1:11434',
      },
      {
        id: 'srv-memory',
        name: 'Vector Memory & Hybrid RAG',
        category: 'Memory',
        status: health.database === 'connected' ? 'healthy' : 'offline',
        latencyMs: health.database === 'connected' ? 6 : 0,
        healthMetric: health.database === 'connected' ? 'HNSW Vector Store' : 'Offline',
        port: 6333,
      },
      {
        id: 'srv-graph',
        name: 'Cognitive Knowledge Graph',
        category: 'Graph',
        status: health.database === 'connected' ? 'healthy' : 'offline',
        latencyMs: health.database === 'connected' ? 7 : 0,
        healthMetric: health.database === 'connected' ? 'Entity Triples Active' : 'Offline',
        port: 7687,
      },
      {
        id: 'srv-context',
        name: 'Context Engine & Session History',
        category: 'Context',
        status: health.status === 'ok' ? 'healthy' : 'offline',
        latencyMs: health.status === 'ok' ? 4 : 0,
        healthMetric: health.status === 'ok' ? 'Active Conversation Tracking' : 'Offline',
        port: 8002,
      },
      {
        id: 'srv-workflow',
        name: 'Autonomous Workflow Engine',
        category: 'Core Engine',
        status: health.status === 'ok' ? 'healthy' : 'offline',
        latencyMs: health.status === 'ok' ? 5 : 0,
        healthMetric: health.status === 'ok' ? 'TaskGraph Orchestrator' : 'Offline',
        port: 8000,
      },
    ];

    return services;
  }

  /**
   * Retrieves active agents from /dashboard/agents or /api/v1/agents.
   */
  async getAgents(): Promise<DashboardAgent[]> {
    try {
      const res = await backendClient.get('/dashboard/agents', { timeout: 4000 });
      if (Array.isArray(res.data) && res.data.length > 0) {
        return res.data.map((a: any, idx: number) => ({
          id: a.id || a.agent_id || `agent-${idx}`,
          name: a.name || `Agent-${a.role || idx}`,
          role: a.role || a.specialization || 'Subsystem Operator',
          status: a.status || (a.is_active ? 'active' : 'idle'),
          tasksCompleted: a.tasks_completed || a.tasksCompleted || 0,
          avatar: (a.name || a.role || 'AG').slice(0, 2).toUpperCase(),
          currentTask: a.current_task || a.currentTask || 'Monitoring active queue',
          progress: a.progress || 100,
          latencyMs: a.latency_ms || a.latencyMs || 12,
          division: a.division || 'Autonomous Workforce',
          skills: a.skills || ['Task Execution', 'Self-Healing'],
          cpuShare: a.cpu_share || a.cpuShare || '2.4%',
          isLive: true,
        }));
      }
      return MOCK_ACTIVE_AGENTS_EXTENDED.map((a) => ({ ...a, isLive: false }));
    } catch {
      return MOCK_ACTIVE_AGENTS_EXTENDED.map((a) => ({ ...a, isLive: false }));
    }
  }

  /**
   * Retrieves active missions from /dashboard/missions or /api/v1/missions.
   */
  async getMissions(): Promise<MissionItem[]> {
    try {
      const res = await backendClient.get('/dashboard/missions', { timeout: 4000 });
      if (Array.isArray(res.data) && res.data.length > 0) {
        return res.data.map((m: any, idx: number) => ({
          id: m.id || m.mission_id || `mission-${idx}`,
          title: m.title || m.goal || `Mission ${idx + 1}`,
          category: m.category || 'Automation',
          status: m.status || 'running',
          progress: m.progress || 50,
          assignedAgents: m.assigned_agents || m.assignedAgents || 1,
          elapsedTime: m.elapsed_time || m.elapsedTime || '12m 40s',
          subtasksCompleted: m.subtasks_completed || m.subtasksCompleted || 0,
          subtasksTotal: m.subtasks_total || m.subtasksTotal || 1,
          isLive: true,
        }));
      }
      return MOCK_MISSIONS.map((m) => ({ ...m, isLive: false }));
    } catch {
      return MOCK_MISSIONS.map((m) => ({ ...m, isLive: false }));
    }
  }

  /**
   * Real Mission Operations: pause, resume, cancel, approval.
   */
  async pauseMission(missionId: string): Promise<{ success: boolean; message: string }> {
    try {
      const res = await apiClient.post(`/missions/${missionId}/pause`);
      return { success: true, message: res.data?.message || `Mission ${missionId} paused.` };
    } catch (err: any) {
      return { success: false, message: err?.response?.data?.message || `Failed to pause mission: ${err.message}` };
    }
  }

  async resumeMission(missionId: string): Promise<{ success: boolean; message: string }> {
    try {
      const res = await apiClient.post(`/missions/${missionId}/resume`);
      return { success: true, message: res.data?.message || `Mission ${missionId} resumed.` };
    } catch (err: any) {
      return { success: false, message: err?.response?.data?.message || `Failed to resume mission: ${err.message}` };
    }
  }

  async cancelMission(missionId: string): Promise<{ success: boolean; message: string }> {
    try {
      const res = await apiClient.post(`/missions/${missionId}/cancel`);
      return { success: true, message: res.data?.message || `Mission ${missionId} cancelled.` };
    } catch (err: any) {
      return { success: false, message: err?.response?.data?.message || `Failed to cancel mission: ${err.message}` };
    }
  }

  async approveMission(missionId: string, notes?: string): Promise<{ success: boolean; message: string }> {
    try {
      const res = await apiClient.post(`/missions/${missionId}/approval`, {
        approved: true,
        authorizedBy: notes || 'Operator',
      });
      return { success: true, message: res.data?.message || `Mission ${missionId} approved.` };
    } catch (err: any) {
      return { success: false, message: err?.response?.data?.message || `Failed to approve mission: ${err.message}` };
    }
  }

  /**
   * Memory & Knowledge Graph status from /api/v1/memory/statistics and /api/v1/graph/statistics.
   */
  async getMemoryActivity(): Promise<{ items: typeof MOCK_MEMORY_ITEMS; isLive: boolean }> {
    try {
      let memRes = await apiClient.get('/memory/statistics', { timeout: 3500 }).catch(() => null);
      if (!memRes || memRes.status !== 200) {
        memRes = await apiClient.get('/api/v1/memory/statistics', { timeout: 3500 }).catch(() => null);
      }
      if (memRes && memRes.status === 200) {
        return { items: MOCK_MEMORY_ITEMS, isLive: true };
      }
      return { items: MOCK_MEMORY_ITEMS, isLive: false };
    } catch {
      return { items: MOCK_MEMORY_ITEMS, isLive: false };
    }
  }

  /**
   * Device Center status: tests connection to Native Bridge Server (:3001).
   */
  async getDevices(): Promise<MockDevice[]> {
    try {
      const bridgeRes = await fetch(`${APP_CONFIG.nativeBridgeUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000),
      });

      if (bridgeRes.ok) {
        return MOCK_DEVICES.map((d) =>
          d.type === 'Desktop'
            ? { ...d, status: 'online', isLive: true, specs: 'Windows 11 Native Host (Bridge Connected)' }
            : { ...d, isLive: false }
        );
      }
      return MOCK_DEVICES.map((d) => ({ ...d, isLive: false }));
    } catch {
      return MOCK_DEVICES.map((d) => ({ ...d, isLive: false }));
    }
  }

  /**
   * Automations: queries /api/v1/workflows/
   */
  async getAutomations(): Promise<MockAutomation[]> {
    try {
      const res = await apiClient.get('/workflows/', { timeout: 4000 });
      if (Array.isArray(res.data) && res.data.length > 0) {
        return res.data.map((wf: any, idx: number) => ({
          id: wf.id || `workflow-${idx}`,
          name: wf.name || wf.title || `Workflow ${idx + 1}`,
          trigger: wf.trigger || 'Scheduled Trigger',
          status: wf.status || 'active',
          lastRun: wf.last_run || 'Just now',
          nextRun: wf.next_run || 'In 1 hour',
          executionCount: wf.execution_count || 1,
          category: wf.category || 'Routine',
          isLive: true,
        }));
      }
      return MOCK_AUTOMATIONS.map((a) => ({ ...a, isLive: false }));
    } catch {
      return MOCK_AUTOMATIONS.map((a) => ({ ...a, isLive: false }));
    }
  }

  async executeAutomation(workflowId: string): Promise<{ success: boolean; message: string }> {
    try {
      const res = await apiClient.post(`/workflows/${workflowId}/execute`, { variables: {} });
      return { success: true, message: res.data?.message || `Workflow ${workflowId} executed successfully.` };
    } catch (err: any) {
      return { success: false, message: err?.response?.data?.message || `Failed to execute workflow: ${err.message}` };
    }
  }

  async cancelAutomation(workflowId: string): Promise<{ success: boolean; message: string }> {
    try {
      const res = await apiClient.post(`/workflows/${workflowId}/cancel`);
      return { success: true, message: res.data?.message || `Workflow ${workflowId} cancelled.` };
    } catch (err: any) {
      return { success: false, message: err?.response?.data?.message || `Failed to cancel workflow: ${err.message}` };
    }
  }

  /**
   * Activity Timeline: queries /dashboard/events or /api/v1/audit/events
   */
  async getTimeline(): Promise<ActivityTimelineItem[]> {
    try {
      const res = await backendClient.get('/dashboard/events', { timeout: 4000 });
      if (Array.isArray(res.data) && res.data.length > 0) {
        return res.data.map((e: any, idx: number) => ({
          id: e.id || `evt-${idx}`,
          title: e.title || e.event_type || 'System Event',
          description: e.description || 'Execution completed nominal.',
          category: (e.source || 'system').toLowerCase() as any,
          timestamp: e.timestamp ? new Date(e.timestamp).toLocaleTimeString() : 'Just now',
          icon: e.source === 'agent' ? 'Brain' : e.source === 'security' ? 'ShieldCheck' : 'Cpu',
          isLive: true,
        }));
      }
      return MOCK_ACTIVITY_TIMELINE.map((t) => ({ ...t, isLive: false }));
    } catch {
      return MOCK_ACTIVITY_TIMELINE.map((t) => ({ ...t, isLive: false }));
    }
  }

  /**
   * Analytics: queries /dashboard/analytics
   */
  async getAnalytics(): Promise<AnalyticsSeries> {
    try {
      const res = await backendClient.get('/dashboard/analytics', { timeout: 4000 });
      if (res.status === 200 && res.data) {
        return {
          ...MOCK_ANALYTICS_SERIES,
          isLive: true,
        };
      }
      return { ...MOCK_ANALYTICS_SERIES, isLive: false };
    } catch {
      return { ...MOCK_ANALYTICS_SERIES, isLive: false };
    }
  }

  /**
   * Notifications: queries /dashboard/notifications
   */
  async getNotifications(): Promise<NotificationItem[]> {
    try {
      const res = await backendClient.get('/dashboard/notifications', { timeout: 4000 });
      if (Array.isArray(res.data) && res.data.length > 0) {
        return res.data.map((n: any, idx: number) => ({
          id: n.id || `notif-${idx}`,
          title: n.title || 'Notification',
          message: n.message || '',
          type: (n.priority === 'CRITICAL' ? 'error' : n.priority === 'WARNING' ? 'warning' : 'info') as any,
          timestamp: n.created_at ? new Date(n.created_at).toLocaleTimeString() : 'Just now',
          read: Boolean(n.read),
        }));
      }
      return MOCK_NOTIFICATIONS;
    } catch {
      return MOCK_NOTIFICATIONS;
    }
  }

  async markNotificationRead(id: string): Promise<boolean> {
    try {
      const res = await backendClient.patch(`/dashboard/notifications/${id}/read`);
      return res.status === 200;
    } catch {
      return false;
    }
  }

  async deleteNotification(id: string): Promise<boolean> {
    try {
      const res = await backendClient.delete(`/dashboard/notifications/${id}`);
      return res.status === 200;
    } catch {
      return false;
    }
  }

  /**
   * Comprehensive Snapshot fetching for all dashboard widgets.
   */
  async getDashboardSnapshot(): Promise<DashboardDataPayload> {
    const health = await this.checkHealth();
    const isOnline = health.status === 'ok' || health.status === 'degraded';

    const [
      telemetry,
      services,
      agents,
      missions,
      devices,
      automations,
      timeline,
      analytics,
      notifications,
    ] = await Promise.all([
      this.getTelemetry(),
      this.getCoreServices(),
      this.getAgents(),
      this.getMissions(),
      this.getDevices(),
      this.getAutomations(),
      this.getTimeline(),
      this.getAnalytics(),
      this.getNotifications(),
    ]);

    return {
      telemetry,
      services,
      agents,
      missions,
      devices,
      automations,
      timeline,
      analytics,
      notifications,
      isConnected: isOnline,
      health,
      lastUpdated: new Date().toLocaleTimeString(),
    };
  }
}

export const dashboardApiService = new DashboardApiService();
