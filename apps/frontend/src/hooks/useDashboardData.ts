import { useState, useEffect, useCallback, useRef } from 'react';
import {
  dashboardApiService,
  DashboardDataPayload,
} from '../services/api/dashboardApiService';
import {
  BackendConnectionStatus,
  BackendHealthSummary,
  MockDevice,
} from '../types/dashboard';
import { APP_CONFIG } from '../config/app.config';

export function useDashboardData() {
  const [data, setData] = useState<DashboardDataPayload | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [connectionStatus, setConnectionStatus] = useState<BackendConnectionStatus>('connecting');
  const [lastError, setLastError] = useState<string | null>(null);

  const [health, setHealth] = useState<BackendHealthSummary>({
    status: 'offline',
    latencyMs: 0,
    database: 'disconnected',
    nativeBridge: false,
    ollama: false,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const isMountedRef = useRef<boolean>(true);

  const fetchDashboardData = useCallback(async (isManualRefresh = false) => {
    if (isManualRefresh) setIsRefreshing(true);
    try {
      const snapshot = await dashboardApiService.getDashboardSnapshot();
      if (!isMountedRef.current) return;

      setData(snapshot);
      setHealth(snapshot.health);
      setConnectionStatus(snapshot.isConnected ? 'connected' : 'disconnected');
      setLastError(snapshot.isConnected ? null : 'Backend offline or unreachable on http://localhost:8000');
    } catch (err: any) {
      if (!isMountedRef.current) return;
      setConnectionStatus('error');
      setLastError(err?.message || 'Error communicating with Nova-AI backend');
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    }
  }, []);

  // Setup WebSocket or Polling
  useEffect(() => {
    isMountedRef.current = true;
    fetchDashboardData();

    // Try WebSocket connection for live telemetry only if an authentication token is present.
    // This avoids unauthenticated handshake rejections (1008 policy violation) and browser console errors,
    // gracefully falling back to interval polling when unauthenticated.
    const meta = typeof window !== 'undefined' ? (import.meta as any) : undefined;
    const devToken = meta?.env?.DEV ? (meta.env.VITE_DEV_AUTH_TOKEN as string | undefined) : undefined;
    const token = typeof localStorage !== 'undefined' ? (localStorage.getItem('nova_auth_token') || devToken) : devToken;

    if (token) {
      try {
        const wsUrl = `${APP_CONFIG.wsUrl}?token=${encodeURIComponent(token)}`;
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!isMountedRef.current) return;
          setConnectionStatus('connected');
        };

        ws.onmessage = (event) => {
          if (!isMountedRef.current) return;
          try {
            const parsed = JSON.parse(event.data);
            if (parsed && typeof parsed === 'object') {
              setData((prev) => (prev ? { ...prev, ...parsed, isConnected: true } : prev));
            }
          } catch {
            // Ignore invalid JSON frames
          }
        };

        ws.onerror = () => {
          // WebSocket error, fallback to polling
        };

        ws.onclose = () => {
          // Closed, fall back to interval
        };
      } catch {
        // WS constructor failed in sandbox/environment
      }
    }

    // Standard interval polling fallback every 8 seconds
    const interval = setInterval(() => {
      fetchDashboardData(false);
    }, 8000);

    return () => {
      isMountedRef.current = false;
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [fetchDashboardData]);

  // Action Handlers wired to real endpoints
  const pauseMission = useCallback(async (missionId: string): Promise<boolean> => {
    const res = await dashboardApiService.pauseMission(missionId);
    if (res.success) {
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          missions: prev.missions.map((m) => (m.id === missionId ? { ...m, status: 'paused' } : m)),
        };
      });
      return true;
    }
    return false;
  }, []);

  const resumeMission = useCallback(async (missionId: string): Promise<boolean> => {
    const res = await dashboardApiService.resumeMission(missionId);
    if (res.success) {
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          missions: prev.missions.map((m) => (m.id === missionId ? { ...m, status: 'running' } : m)),
        };
      });
      return true;
    }
    return false;
  }, []);

  const cancelMission = useCallback(async (missionId: string): Promise<boolean> => {
    const res = await dashboardApiService.cancelMission(missionId);
    if (res.success) {
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          missions: prev.missions.map((m) => (m.id === missionId ? { ...m, status: 'failed' } : m)),
        };
      });
      return true;
    }
    return false;
  }, []);

  const approveMission = useCallback(async (missionId: string): Promise<boolean> => {
    const res = await dashboardApiService.approveMission(missionId);
    if (res.success) {
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          missions: prev.missions.map((m) => (m.id === missionId ? { ...m, status: 'running' } : m)),
        };
      });
      return true;
    }
    return false;
  }, []);

  const executeAutomation = useCallback(async (workflowId: string): Promise<boolean> => {
    const res = await dashboardApiService.executeAutomation(workflowId);
    if (res.success) {
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          automations: prev.automations.map((a) =>
            a.id === workflowId ? { ...a, executionCount: a.executionCount + 1, lastRun: 'Just now' } : a
          ),
        };
      });
      return true;
    }
    return false;
  }, []);

  const cancelAutomation = useCallback(async (workflowId: string): Promise<boolean> => {
    const res = await dashboardApiService.cancelAutomation(workflowId);
    if (res.success) {
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          automations: prev.automations.map((a) =>
            a.id === workflowId ? { ...a, status: 'paused' } : a
          ),
        };
      });
      return true;
    }
    return false;
  }, []);

  const markNotificationRead = useCallback(async (id: string): Promise<boolean> => {
    const ok = await dashboardApiService.markNotificationRead(id);
    setData((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        notifications: prev.notifications.map((n) => (n.id === id ? { ...n, read: true } : n)),
      };
    });
    return ok;
  }, []);

  const deleteNotification = useCallback(async (id: string): Promise<boolean> => {
    const ok = await dashboardApiService.deleteNotification(id);
    setData((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        notifications: prev.notifications.filter((n) => n.id !== id),
      };
    });
    return ok;
  }, []);

  const pingDevice = useCallback(async (device: MockDevice): Promise<boolean> => {
    try {
      const res = await fetch(`${APP_CONFIG.nativeBridgeUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000),
      });
      const isOnline = res.ok;
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          devices: prev.devices.map((d) =>
            d.id === device.id ? { ...d, status: isOnline ? 'online' : 'offline', isLive: isOnline } : d
          ),
        };
      });
      return isOnline;
    } catch {
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          devices: prev.devices.map((d) =>
            d.id === device.id ? { ...d, status: 'offline', isLive: false } : d
          ),
        };
      });
      return false;
    }
  }, []);

  return {
    data,
    isLoading,
    isRefreshing,
    connectionStatus,
    health,
    lastError,
    refresh: () => fetchDashboardData(true),
    pauseMission,
    resumeMission,
    cancelMission,
    approveMission,
    executeAutomation,
    cancelAutomation,
    markNotificationRead,
    deleteNotification,
    pingDevice,
  };
}

