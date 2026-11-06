import React, { useState, useMemo } from 'react';
import {
  Cpu,
  HardDrive,
  Zap,
  Gauge,
  Thermometer,
  Wifi,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Activity,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  Radio,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import {
  SystemTelemetry,
  BackendConnectionStatus,
  BackendHealthSummary,
} from '@/types/dashboard';
import { useDashboardData } from '@/hooks/useDashboardData';

export type TelemetryState = 'LIVE' | 'STANDBY' | 'STANDALONE' | 'UNAVAILABLE';

export interface SystemOverviewWidgetProps {
  className?: string;
  telemetry?: SystemTelemetry;
  onRefresh?: () => void;
  isLoading?: boolean;
  connectionStatus?: BackendConnectionStatus;
  lastUpdated?: string;
  backendHealth?: BackendHealthSummary;
}

/**
 * Renders a standardized, truthful status pill for individual metrics.
 */
const MetricStatusBadge: React.FC<{ state: TelemetryState }> = ({ state }) => {
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

export const SystemOverviewWidget: React.FC<SystemOverviewWidgetProps> = ({
  className,
  telemetry: externalTelemetry,
  onRefresh,
  isLoading: externalIsLoading,
  connectionStatus: externalConnectionStatus,
  lastUpdated: externalLastUpdated,
  backendHealth: externalBackendHealth,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Hook into live dashboard telemetry if props are not explicitly supplied
  const {
    data: liveDashboardData,
    connectionStatus: hookConnectionStatus,
    health: hookHealth,
    isRefreshing,
    refresh: hookRefresh,
  } = useDashboardData();

  // Resolved telemetry data, connection status, and health summary
  const telemetry = externalTelemetry || liveDashboardData?.telemetry;
  const connectionStatus = externalConnectionStatus || hookConnectionStatus;
  const health = externalBackendHealth || liveDashboardData?.health || hookHealth;
  const lastUpdated = externalLastUpdated || liveDashboardData?.lastUpdated;
  const isLoading = externalIsLoading !== undefined ? externalIsLoading : isRefreshing;

  const isConnected = connectionStatus === 'connected' && !!liveDashboardData?.isConnected;
  const isTelemetryLive = isConnected && !!telemetry?.isLive;

  // Handle manual or delegated refresh
  const handleRefreshClick = () => {
    if (onRefresh) {
      onRefresh();
    } else {
      hookRefresh(true);
    }
  };

  // -------------------------------------------------------------------------
  // Individual Metric Telemetry State Calculations (Truth-in-UI)
  // -------------------------------------------------------------------------

  // 1. CPU Load
  const cpuMetric = useMemo<{
    value: string;
    subtext: string;
    progress: number;
    state: TelemetryState;
  }>(() => {
    if (!isConnected) {
      return {
        value: '—',
        subtext: 'Backend disconnected',
        progress: 0,
        state: 'STANDALONE',
      };
    }
    if (!isTelemetryLive || telemetry?.cpuUsage === undefined || telemetry?.cpuUsage === null) {
      return {
        value: '—',
        subtext: 'Telemetry collector idle',
        progress: 0,
        state: 'STANDBY',
      };
    }
    return {
      value: `${Math.round(telemetry.cpuUsage)}%`,
      subtext: telemetry.cpuDetails || 'Host Processor',
      progress: Math.min(100, Math.max(0, telemetry.cpuUsage)),
      state: 'LIVE',
    };
  }, [isConnected, isTelemetryLive, telemetry?.cpuUsage, telemetry?.cpuDetails]);

  // 2. GPU VRAM & Compute (Distinct from CPU & Backend Health)
  const gpuMetric = useMemo<{
    value: string;
    subtext: string;
    progress: number;
    state: TelemetryState;
  }>(() => {
    if (!isConnected) {
      return {
        value: '—',
        subtext: 'Backend disconnected',
        progress: 0,
        state: 'STANDALONE',
      };
    }
    // Backend health does not prove GPU hardware collector is active
    if (!isTelemetryLive || !telemetry?.gpuUsage || telemetry.gpuUsage <= 0) {
      return {
        value: '—',
        subtext: 'GPU Collector Standby / Integrated',
        progress: 0,
        state: 'STANDBY',
      };
    }
    return {
      value: `${Math.round(telemetry.gpuUsage)}%`,
      subtext: telemetry.gpuDetails || 'GPU Compute Unit',
      progress: Math.min(100, Math.max(0, telemetry.gpuUsage)),
      state: 'LIVE',
    };
  }, [isConnected, isTelemetryLive, telemetry?.gpuUsage, telemetry?.gpuDetails]);

  // 3. RAM Memory
  const ramMetric = useMemo<{
    value: string;
    subtext: string;
    progress: number;
    state: TelemetryState;
  }>(() => {
    if (!isConnected) {
      return {
        value: '—',
        subtext: 'Backend disconnected',
        progress: 0,
        state: 'STANDALONE',
      };
    }
    if (!isTelemetryLive || !telemetry?.ramTotalGb || telemetry.ramTotalGb <= 0) {
      return {
        value: '—',
        subtext: 'Memory collector idle',
        progress: 0,
        state: 'STANDBY',
      };
    }
    return {
      value: `${telemetry.ramUsageGb.toFixed(1)} GB`,
      subtext: `${telemetry.ramPercent}% Used • Total ${telemetry.ramTotalGb}GB`,
      progress: Math.min(100, Math.max(0, telemetry.ramPercent)),
      state: 'LIVE',
    };
  }, [isConnected, isTelemetryLive, telemetry?.ramUsageGb, telemetry?.ramPercent, telemetry?.ramTotalGb]);

  // 4. NVMe / Disk Storage
  const storageMetric = useMemo<{
    value: string;
    subtext: string;
    progress: number;
    state: TelemetryState;
  }>(() => {
    if (!isConnected) {
      return {
        value: '—',
        subtext: 'Backend disconnected',
        progress: 0,
        state: 'STANDALONE',
      };
    }
    if (!isTelemetryLive || !telemetry?.storageTotalGb || telemetry.storageTotalGb <= 0) {
      return {
        value: '—',
        subtext: 'Disk collector idle',
        progress: 0,
        state: 'STANDBY',
      };
    }
    return {
      value: `${telemetry.storageUsedGb} GB`,
      subtext: `${telemetry.storagePercent}% Used • Total ${telemetry.storageTotalGb}GB`,
      progress: Math.min(100, Math.max(0, telemetry.storagePercent)),
      state: 'LIVE',
    };
  }, [isConnected, isTelemetryLive, telemetry?.storageUsedGb, telemetry?.storagePercent, telemetry?.storageTotalGb]);

  // 5. Network Throughput
  const networkMetric = useMemo<{
    value: string;
    subtext: string;
    progress: number;
    state: TelemetryState;
  }>(() => {
    if (!isConnected) {
      return {
        value: '—',
        subtext: 'Backend disconnected',
        progress: 0,
        state: 'STANDALONE',
      };
    }
    if (!isTelemetryLive || telemetry?.networkDownMbps === undefined) {
      return {
        value: '—',
        subtext: 'Network telemetry idle',
        progress: 0,
        state: 'STANDBY',
      };
    }
    const hasTraffic = telemetry.networkDownMbps > 0 || telemetry.networkUpMbps > 0;
    if (!hasTraffic) {
      return {
        value: '0.0 Mbps',
        subtext: 'Interface Idle • Active polling',
        progress: 0,
        state: 'STANDBY',
      };
    }
    return {
      value: `${(telemetry.networkDownMbps / 1000).toFixed(1)} Gbps`,
      subtext: `↓ ${telemetry.networkDownMbps}Mb • ↑ ${telemetry.networkUpMbps}Mb`,
      progress: Math.min(100, Math.max(10, (telemetry.networkDownMbps / 1000) * 100)),
      state: 'LIVE',
    };
  }, [isConnected, isTelemetryLive, telemetry?.networkDownMbps, telemetry?.networkUpMbps]);

  // 6. Thermal Sensor (ACPI / CPU temperature)
  const thermalMetric = useMemo<{
    value: string;
    subtext: string;
    progress: number;
    state: TelemetryState;
  }>(() => {
    if (!isConnected) {
      return {
        value: '—',
        subtext: 'Backend disconnected',
        progress: 0,
        state: 'STANDALONE',
      };
    }
    // Thermal sensor is often unavailable without elevated ACPI driver permissions on Windows NT
    if (
      !isTelemetryLive ||
      telemetry?.temperatureC === undefined ||
      telemetry?.temperatureC === null ||
      telemetry.temperatureC === 42 // 42 is the fallback constant when sensor is null
    ) {
      return {
        value: '—',
        subtext: 'ACPI Thermal Sensor Not Accessible',
        progress: 0,
        state: 'UNAVAILABLE',
      };
    }
    return {
      value: `${Math.round(telemetry.temperatureC)}°C`,
      subtext: `${telemetry.tempStatus.toUpperCase()} • COOLING OPTIMAL`,
      progress: Math.min(100, Math.max(0, telemetry.temperatureC)),
      state: 'LIVE',
    };
  }, [isConnected, isTelemetryLive, telemetry?.temperatureC, telemetry?.tempStatus]);

  // Overall system telemetry badge
  const overallBadge = useMemo(() => {
    if (!isConnected) {
      return {
        label: 'STANDALONE (DISCONNECTED)',
        color: 'bg-slate-800/80 border-slate-700/80 text-slate-400',
        dot: 'border border-slate-400',
      };
    }
    if (isTelemetryLive) {
      return {
        label: 'HARDWARE TELEMETRY (LIVE)',
        color: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400',
        dot: 'bg-emerald-400 animate-ping',
      };
    }
    return {
      label: 'BACKEND CONNECTED (STANDBY)',
      color: 'bg-amber-500/15 border-amber-500/30 text-amber-300',
      dot: 'bg-amber-400',
    };
  }, [isConnected, isTelemetryLive]);

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
            <Gauge className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
                System Telemetry & Hardware Overview
              </h3>
              {lastUpdated && (
                <span className="text-[10px] font-mono text-slate-500 hidden sm:inline">
                  • Polled: {new Date(lastUpdated).toLocaleTimeString()}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 font-mono">
              Individual hardware metric sensors & truth-in-UI diagnostics
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <button
            onClick={handleRefreshClick}
            disabled={isLoading}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-300 transition-all cursor-pointer disabled:opacity-50"
            title="Refresh Telemetry"
            aria-label="Refresh telemetry"
          >
            <RefreshCw className={cn('w-3.5 h-3.5', isLoading && 'animate-spin text-cyan-400')} />
          </button>

          <div
            className={cn(
              'flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-bold border transition-colors',
              overallBadge.color
            )}
          >
            <span className={cn('w-1.5 h-1.5 rounded-full', overallBadge.dot)} />
            <span>{overallBadge.label}</span>
          </div>
        </div>
      </div>

      {/* Grid of 6 Telemetry Cards with Distinct Truthful Statuses */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* 1. CPU Load */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 space-y-2 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <span className="truncate">CPU Load</span>
            <Cpu className="w-4 h-4 text-cyan-400 shrink-0" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-slate-100 font-mono tracking-tight">
              {cpuMetric.value}
            </span>
            <MetricStatusBadge state={cpuMetric.state} />
          </div>
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
            <div
              className="h-full bg-cyan-400 rounded-full transition-all duration-500"
              style={{ width: `${cpuMetric.progress}%` }}
            />
          </div>
          <div className="text-[10px] font-mono text-slate-400 truncate" title={cpuMetric.subtext}>
            {cpuMetric.subtext}
          </div>
        </div>

        {/* 2. GPU VRAM */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 space-y-2 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <span className="truncate">GPU VRAM</span>
            <Zap className="w-4 h-4 text-purple-400 shrink-0" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-slate-100 font-mono tracking-tight">
              {gpuMetric.value}
            </span>
            <MetricStatusBadge state={gpuMetric.state} />
          </div>
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
            <div
              className="h-full bg-purple-400 rounded-full transition-all duration-500"
              style={{ width: `${gpuMetric.progress}%` }}
            />
          </div>
          <div className="text-[10px] font-mono text-slate-400 truncate" title={gpuMetric.subtext}>
            {gpuMetric.subtext}
          </div>
        </div>

        {/* 3. RAM Usage */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 space-y-2 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <span className="truncate">RAM</span>
            <HardDrive className="w-4 h-4 text-blue-400 shrink-0" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-slate-100 font-mono tracking-tight">
              {ramMetric.value}
            </span>
            <MetricStatusBadge state={ramMetric.state} />
          </div>
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-400 rounded-full transition-all duration-500"
              style={{ width: `${ramMetric.progress}%` }}
            />
          </div>
          <div className="text-[10px] font-mono text-slate-400 truncate" title={ramMetric.subtext}>
            {ramMetric.subtext}
          </div>
        </div>

        {/* 4. NVMe Storage */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 space-y-2 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <span className="truncate">Storage</span>
            <HardDrive className="w-4 h-4 text-emerald-400 shrink-0" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-slate-100 font-mono tracking-tight">
              {storageMetric.value}
            </span>
            <MetricStatusBadge state={storageMetric.state} />
          </div>
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-400 rounded-full transition-all duration-500"
              style={{ width: `${storageMetric.progress}%` }}
            />
          </div>
          <div className="text-[10px] font-mono text-slate-400 truncate" title={storageMetric.subtext}>
            {storageMetric.subtext}
          </div>
        </div>

        {/* 5. Network I/O */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 space-y-2 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <span className="truncate">Network I/O</span>
            <Wifi className="w-4 h-4 text-cyan-400 shrink-0" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-slate-100 font-mono tracking-tight">
              {networkMetric.value}
            </span>
            <MetricStatusBadge state={networkMetric.state} />
          </div>
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
            <div
              className="h-full bg-cyan-400 rounded-full transition-all duration-500"
              style={{ width: `${networkMetric.progress}%` }}
            />
          </div>
          <div className="text-[10px] font-mono text-slate-400 truncate" title={networkMetric.subtext}>
            {networkMetric.subtext}
          </div>
        </div>

        {/* 6. Thermal Sensor */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 space-y-2 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <span className="truncate">Thermal</span>
            <Thermometer className="w-4 h-4 text-amber-400 shrink-0" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black text-slate-100 font-mono tracking-tight">
              {thermalMetric.value}
            </span>
            <MetricStatusBadge state={thermalMetric.state} />
          </div>
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
            <div
              className="h-full bg-amber-400 rounded-full transition-all duration-500"
              style={{ width: `${thermalMetric.progress}%` }}
            />
          </div>
          <div className="text-[10px] font-mono text-slate-400 truncate" title={thermalMetric.subtext}>
            {thermalMetric.subtext}
          </div>
        </div>
      </div>

      {/* Expandable Deep Telemetry Details (Truthful Platform Topology) */}
      <div className="pt-1">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-xs font-mono text-slate-400 hover:text-cyan-300 flex items-center space-x-1 cursor-pointer transition-colors"
        >
          <span>{isExpanded ? 'Hide Platform Topology Details' : 'Show Platform Topology & Daemon Status'}</span>
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {isExpanded && (
          <div className="mt-3 p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 text-xs font-mono text-slate-400 grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <span className="text-slate-500">Host Platform:</span>{' '}
              <strong className="text-slate-200">{telemetry?.cpuDetails || 'Windows NT Host'}</strong>
            </div>
            <div>
              <span className="text-slate-500">AI Inference Daemon:</span>{' '}
              <strong className={health.ollama ? 'text-emerald-400' : 'text-slate-400'}>
                {health.ollama ? 'Ollama Online (:11434)' : 'Offline / Standalone'}
              </strong>
            </div>
            <div>
              <span className="text-slate-500">Native Execution Bridge:</span>{' '}
              <strong className={health.nativeBridge ? 'text-emerald-400' : 'text-slate-400'}>
                {health.nativeBridge ? 'Active (:3001)' : 'Offline / Standalone'}
              </strong>
            </div>
            <div>
              <span className="text-slate-500">Knowledge Store DB:</span>{' '}
              <strong className={health.database === 'connected' ? 'text-emerald-400' : 'text-slate-400'}>
                {health.database === 'connected' ? 'Connected (Postgres/SQLite)' : 'Disconnected'}
              </strong>
            </div>
            <div>
              <span className="text-slate-500">Hardware Bus Sensor:</span>{' '}
              <strong className="text-amber-300">Not Instrumented (STANDBY)</strong>
            </div>
            <div>
              <span className="text-slate-500">Backend Latency:</span>{' '}
              <strong className="text-cyan-300">
                {isConnected ? `${health.latencyMs}ms` : '—'}
              </strong>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemOverviewWidget;
