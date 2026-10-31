import { AgentInfo } from './index';

export type BackendConnectionStatus = 'connected' | 'connecting' | 'disconnected' | 'error';

export interface BackendHealthSummary {
  status: 'ok' | 'degraded' | 'unhealthy' | 'offline';
  version?: string;
  database?: 'connected' | 'disconnected';
  nativeBridge?: boolean;
  ollama?: boolean;
  latencyMs: number;
}

export type CommandVisualState =
  | 'idle'
  | 'listening'
  | 'processing'
  | 'executing'
  | 'waiting_for_permission'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface SystemTelemetry {
  cpuUsage: number;
  cpuDetails: string;
  gpuUsage: number;
  gpuDetails: string;
  ramUsageGb: number;
  ramTotalGb: number;
  ramPercent: number;
  storageUsedGb: number;
  storageTotalGb: number;
  storagePercent: number;
  networkDownMbps: number;
  networkUpMbps: number;
  temperatureC: number;
  tempStatus: 'nominal' | 'elevated' | 'critical';
  isLive?: boolean;
}

export interface ServiceHealthItem {
  id: string;
  name: string;
  category: string;
  status: 'healthy' | 'degraded' | 'maintenance' | 'offline';
  latencyMs: number;
  healthMetric: string;
  port?: number;
  endpoint?: string;
}

export interface DashboardAgent extends AgentInfo {
  currentTask: string;
  progress: number;
  latencyMs: number;
  division: string;
  skills?: string[];
  cpuShare?: string;
  isLive?: boolean;
}

export interface MissionSubtask {
  id: string;
  title: string;
  status: 'completed' | 'in_progress' | 'pending';
  assignedAgent?: string;
}

export interface MissionItem {
  id: string;
  title: string;
  category: 'Research' | 'Engineering' | 'Automation' | 'Security' | 'Documentation';
  status: 'running' | 'queued' | 'completed' | 'failed' | 'paused';
  progress: number;
  assignedAgents: number;
  elapsedTime: string;
  subtasksCompleted: number;
  subtasksTotal: number;
  subtasks?: MissionSubtask[];
  isLive?: boolean;
}

export interface MockDevice {
  id: string;
  name: string;
  type: 'Desktop' | 'Mobile' | 'Laptop' | 'Display' | 'IoT Hub';
  os: string;
  status: 'online' | 'offline' | 'connected' | 'attention';
  ip: string;
  specs: string;
  batteryPercent?: number;
  signalStrength?: string;
  lastActive: string;
  isLive?: boolean;
}

export interface MockAutomation {
  id: string;
  name: string;
  trigger: string;
  status: 'active' | 'scheduled' | 'completed' | 'paused';
  lastRun: string;
  nextRun: string;
  executionCount: number;
  category: 'Routine' | 'Maintenance' | 'Monitoring' | 'Analytics';
  isLive?: boolean;
}

export interface ActivityTimelineItem {
  id: string;
  title: string;
  description: string;
  category: 'agent' | 'memory' | 'security' | 'automation' | 'system';
  timestamp: string;
  icon: string;
  isLive?: boolean;
}

export interface QuickActionItem {
  id: string;
  title: string;
  description: string;
  iconName: string;
  category: 'create' | 'run' | 'navigate';
  commandSuggestion?: string;
}

export interface AnalyticsSeries {
  aiRequestsOverTime: Array<{ time: string; requests: number; latency: number }>;
  agentActivityDistribution: Array<{ name: string; tasks: number }>;
  memoryGrowth: Array<{ day: string; memories: number; entities: number }>;
  isLive?: boolean;
}

export interface KnowledgeUpdateItem {
  entity: string;
  type: string;
  relation: string;
  target: string;
  time: string;
}

export interface AttachedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  dataUrl?: string;
}

export interface AttachedVision {
  id: string;
  title: string;
  previewUrl: string;
  timestamp: string;
}
