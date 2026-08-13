import { create } from 'zustand';
import { MetricCardData } from '@/types';
import { MOCK_DASHBOARD_METRICS } from '@/mock/mockDashboard';

interface DashboardState {
  metrics: MetricCardData[];
  isLoading: boolean;
  setMetrics: (metrics: MetricCardData[]) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  metrics: MOCK_DASHBOARD_METRICS,
  isLoading: false,
  setMetrics: (metrics) => set({ metrics }),
}));
