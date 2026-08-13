import { MetricCardData } from '@/types';

export const MOCK_DASHBOARD_METRICS: MetricCardData[] = [
  {
    title: 'Active Agents',
    value: '12',
    change: '+2 this week',
    isPositive: true,
    iconName: 'Bot',
  },
  {
    title: 'Indexed Repositories',
    value: '8',
    change: '100% synchronized',
    isPositive: true,
    iconName: 'Code2',
  },
  {
    title: 'Total Memories',
    value: '142,850',
    change: '+1.4k today',
    isPositive: true,
    iconName: 'Brain',
  },
  {
    title: 'Gateway Latency',
    value: '14.2 ms',
    change: '-3.1 ms optimization',
    isPositive: true,
    iconName: 'Zap',
  },
];

export const MOCK_SYSTEM_HEALTH = {
  status: 'healthy',
  cpuUsage: 24.5,
  memoryUsageMb: 4096,
  gpuMemoryUsageMb: 8192,
  activeConnections: 18,
  uptimeSeconds: 864000,
};
