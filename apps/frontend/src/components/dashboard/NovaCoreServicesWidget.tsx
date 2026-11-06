import React, { useState, useMemo } from 'react';
import {
  Server,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Filter,
  ShieldAlert,
  Radio,
  ExternalLink,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import {
  ServiceHealthItem,
  BackendConnectionStatus,
} from '@/types/dashboard';
import { useDashboardData } from '@/hooks/useDashboardData';

export type ServiceTelemetryState = 'LIVE' | 'STANDBY' | 'STANDALONE' | 'UNAVAILABLE';

export interface NovaCoreServicesWidgetProps {
  className?: string;
  services?: ServiceHealthItem[];
  onRestartService?: (id: string) => void | Promise<void>;
  onRefresh?: () => void;
  isLoading?: boolean;
  connectionStatus?: BackendConnectionStatus;
  lastUpdated?: string;
}

/**
 * Standard baseline service registry used when disconnected or awaiting first probe.
 * Truthfully reflects real endpoints and ports rather than simulated values.
 */
const BASELINE_SERVICES: ServiceHealthItem[] = [
  {
    id: 'srv-backend',
    name: 'Universal Intelligence API',
    category: 'Core Engine',
    status: 'offline',
    latencyMs: 0,
    healthMetric: 'Standalone / Disconnected',
    port: 8000,
    endpoint: '/api/health',
  },
  {
    id: 'srv-ollama',
    name: 'Local Ollama Model Runtime',
    category: 'AI Models',
    status: 'offline',
    latencyMs: 0,
    healthMetric: 'Service Offline',
    port: 11434,
    endpoint: 'http://127.0.0.1:11434',
  },
  {
    id: 'srv-bridge',
    name: 'Windows Native Execution Bridge',
    category: 'Engineering',
    status: 'offline',
    latencyMs: 0,
    healthMetric: 'Daemon Disconnected',
    port: 3001,
    endpoint: 'http://127.0.0.1:3001/health',
  },
  {
    id: 'srv-db',
    name: 'Knowledge Store Database',
    category: 'Storage',
    status: 'offline',
    latencyMs: 0,
    healthMetric: 'Connection Closed',
    port: 5432,
  },
  {
    id: 'srv-memory',
    name: 'Vector Memory & Hybrid RAG',
    category: 'Memory',
    status: 'offline',
    latencyMs: 0,
    healthMetric: 'In-Process Standby',
    port: 8000,
  },
  {
    id: 'srv-graph',
    name: 'Cognitive Knowledge Graph',
    category: 'Graph',
    status: 'offline',
    latencyMs: 0,
    healthMetric: 'In-Process Standby',
    port: 8000,
  },
  {
    id: 'srv-context',
    name: 'Context Engine & Session History',
    category: 'Context',
    status: 'offline',
    latencyMs: 0,
    healthMetric: 'In-Process Standby',
    port: 8000,
  },
  {
    id: 'srv-workflow',
    name: 'Autonomous Workflow Engine',
    category: 'Core Engine',
    status: 'offline',
    latencyMs: 0,
    healthMetric: 'In-Process Standby',
    port: 8000,
  },
];

/**
 * Standardized status badge for service health items.
 */
const ServiceStatusBadge: React.FC<{ state: ServiceTelemetryState }> = ({ state }) => {
  switch (state) {
    case 'LIVE':
      return (
        <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-500/15 border border-emerald-500/30 text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
          <span>LIVE</span>
        </span>
      );
    case 'STANDBY':
      return (
        <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-amber-500/15 border border-amber-500/30 text-amber-300">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
          <span>STANDBY</span>
        </span>
      );
    case 'STANDALONE':
      return (
        <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-slate-800/80 border border-slate-700/80 text-slate-400">
          <span className="w-1.5 h-1.5 rounded-full border border-slate-400" />
          <span>STANDALONE</span>
        </span>
      );
    case 'UNAVAILABLE':
    default:
      return (
        <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-rose-500/15 border border-rose-500/30 text-rose-400">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
          <span>UNAVAILABLE</span>
        </span>
      );
  }
};

export const NovaCoreServicesWidget: React.FC<NovaCoreServicesWidgetProps> = ({
  className,
  services: externalServices,
  onRestartService,
  onRefresh,
  isLoading: externalIsLoading,
  connectionStatus: externalConnectionStatus,
  lastUpdated: externalLastUpdated,
}) => {
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [restartingId, setRestartingId] = useState<string | null>(null);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  // Hook into live dashboard data if props are not explicitly supplied
  const {
    data: liveDashboardData,
    connectionStatus: hookConnectionStatus,
    isRefreshing,
    refresh: hookRefresh,
  } = useDashboardData();

  // Resolved services and connection status
  const connectionStatus = externalConnectionStatus || hookConnectionStatus;
  const isConnected = connectionStatus === 'connected' && !!liveDashboardData?.isConnected;
  const services = externalServices || (isConnected ? liveDashboardData?.services : undefined) || BASELINE_SERVICES;
  const lastUpdated = externalLastUpdated || liveDashboardData?.lastUpdated;
  const isLoading = externalIsLoading !== undefined ? externalIsLoading : isRefreshing;

  const categories = [
    'all',
    'Core Engine',
    'AI Models',
    'Engineering',
    'Storage',
    'Memory',
    'Graph',
    'Context',
  ];

  const filteredServices = useMemo(() => {
    return services.filter((s) => {
      if (activeCategory === 'all') return true;
      return s.category.toLowerCase() === activeCategory.toLowerCase();
    });
  }, [services, activeCategory]);

  // Restart Handler: invokes genuine callback if provided; never fakes background execution
  const handleRestart = async (id: string) => {
    if (!onRestartService) {
      setActionNotice(`Restart of [${id}] requires supervisor daemon privileges.`);
      setTimeout(() => setActionNotice(null), 3500);
      return;
    }
    try {
      setRestartingId(id);
      await onRestartService(id);
    } catch {
      setActionNotice(`Failed to signal restart for service ${id}.`);
      setTimeout(() => setActionNotice(null), 3500);
    } finally {
      setRestartingId(null);
    }
  };

  const handleRefreshClick = () => {
    if (onRefresh) {
      onRefresh();
    } else {
      hookRefresh(true);
    }
  };

  // Health counts
  const healthyCount = isConnected ? services.filter((s) => s.status === 'healthy').length : 0;
  const totalCount = services.length;
  const isAllHealthy = isConnected && healthyCount === totalCount && totalCount > 0;
  const isPartiallyHealthy = isConnected && healthyCount > 0 && !isAllHealthy;

  return (
    <div
      className={cn(
        'glass-panel p-5 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl space-y-4 shadow-xl select-none',
        className
      )}
    >
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800/80 pb-3 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shrink-0">
            <Server className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
                Nova Core Services Health
              </h3>
              {lastUpdated && (
                <span className="text-[10px] font-mono text-slate-500 hidden sm:inline">
                  • Polled: {new Date(lastUpdated).toLocaleTimeString()}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 font-mono">
              {isConnected
                ? `${healthyCount}/${totalCount} AI OS microservices actively verified`
                : 'Standalone mode • Backend service daemon offline'}
            </p>
          </div>
        </div>

        {/* Status Badge & Refresh */}
        <div className="flex items-center space-x-2 shrink-0">
          <button
            onClick={handleRefreshClick}
            disabled={isLoading}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-300 transition-all cursor-pointer disabled:opacity-50"
            title="Refresh Services Status"
            aria-label="Refresh services status"
          >
            <RefreshCw className={cn('w-3.5 h-3.5', isLoading && 'animate-spin text-cyan-400')} />
          </button>

          {isAllHealthy ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span>{healthyCount}/{totalCount} LIVE • HEALTHY</span>
            </span>
          ) : isPartiallyHealthy ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span>{healthyCount}/{totalCount} DEGRADED</span>
            </span>
          ) : isConnected ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-rose-500/15 border border-rose-500/30 text-rose-400 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
              <span>ALL SERVICES OFFLINE</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/80 text-slate-400 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full border border-slate-400" />
              <span>STANDALONE MODE</span>
            </span>
          )}
        </div>
      </div>

      {/* Notice Banner when Action Requires Privileges */}
      {actionNotice && (
        <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-mono flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 shrink-0 text-amber-400" />
          <span>{actionNotice}</span>
        </div>
      )}

      {/* Category Filter Tabs */}
      <div className="flex items-center space-x-1 overflow-x-auto pb-1 scrollbar-none text-[11px] font-mono">
        <Filter className="w-3.5 h-3.5 text-slate-500 mr-1 shrink-0" />
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={cn(
              'px-2.5 py-1 rounded-lg transition-all cursor-pointer whitespace-nowrap',
              activeCategory === cat
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
            )}
          >
            {cat === 'all' ? 'All Services' : cat}
          </button>
        ))}
      </div>

      {/* Grid of Core Services */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        {filteredServices.map((srv) => {
          // Determine individual service state
          const serviceState: ServiceTelemetryState = !isConnected
            ? 'STANDALONE'
            : srv.status === 'healthy'
            ? 'LIVE'
            : srv.status === 'degraded'
            ? 'STANDBY'
            : 'UNAVAILABLE';

          const latencyDisplay = isConnected && srv.status === 'healthy' && srv.latencyMs > 0
            ? `${srv.latencyMs}ms`
            : '—';

          return (
            <div
              key={srv.id}
              className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 hover:border-slate-700 transition-all space-y-2.5 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-1">
                  <div className="flex items-center space-x-1.5 min-w-0">
                    {serviceState === 'LIVE' ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    ) : serviceState === 'STANDBY' ? (
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    ) : serviceState === 'STANDALONE' ? (
                      <span className="w-3 h-3 rounded-full border border-slate-500 shrink-0" />
                    ) : (
                      <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                    )}
                    <h4 className="text-xs font-bold text-slate-100 truncate" title={srv.name}>
                      {srv.name}
                    </h4>
                  </div>
                  <ServiceStatusBadge state={serviceState} />
                </div>

                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mt-2">
                  <span className="bg-slate-800/90 px-2 py-0.5 rounded-full text-slate-300">
                    {srv.category}
                  </span>
                  <span className="font-semibold text-cyan-400">
                    {latencyDisplay}
                  </span>
                </div>

                <div className="text-[11px] font-mono text-slate-300 mt-1.5 truncate" title={srv.healthMetric}>
                  {isConnected ? srv.healthMetric : 'Standalone / Not Connected'}
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-[10px] font-mono text-slate-500">
                <span>
                  Port: {srv.port ? (srv.port === 8000 && srv.category !== 'Core Engine' ? 'In-Process (8000)' : srv.port) : 'Internal'}
                </span>
                <button
                  onClick={() => handleRestart(srv.id)}
                  disabled={restartingId === srv.id}
                  className="text-slate-400 hover:text-cyan-300 flex items-center space-x-1 cursor-pointer disabled:opacity-50 transition-colors"
                  title={onRestartService ? 'Restart service via supervisor' : 'Requires supervisor privilege'}
                >
                  <RefreshCw className={cn('w-2.5 h-2.5', restartingId === srv.id && 'animate-spin text-cyan-400')} />
                  <span>{restartingId === srv.id ? 'Cycling...' : 'Restart'}</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default NovaCoreServicesWidget;
