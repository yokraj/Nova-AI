import React, { useState } from 'react';
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
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { SystemTelemetry } from '@/types/dashboard';
import { MOCK_TELEMETRY } from '@/mock/mockDashboardData';

interface SystemOverviewWidgetProps {
  className?: string;
  telemetry?: SystemTelemetry;
  onRefresh?: () => void;
  isLoading?: boolean;
}

export const SystemOverviewWidget: React.FC<SystemOverviewWidgetProps> = ({
  className,
  telemetry = MOCK_TELEMETRY,
  onRefresh,
  isLoading = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const t = telemetry;

  return (
    <div
      className={cn(
        'glass-panel p-5 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl space-y-4 shadow-xl select-none',
        className
      )}
    >
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shrink-0">
            <Gauge className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
              System Telemetry & Hardware Overview
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Live hardware metrics, compute load & thermal guard
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-300 transition-all cursor-pointer disabled:opacity-50"
              title="Refresh Telemetry"
              aria-label="Refresh telemetry"
            >
              <RefreshCw className={cn('w-3.5 h-3.5', isLoading && 'animate-spin text-cyan-400')} />
            </button>
          )}

          {t.isLive ? (
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span>HARDWARE NOMINAL (LIVE)</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-400 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span>TELEMETRY OFFLINE • LOCAL</span>
            </div>
          )}
        </div>
      </div>

      {/* Grid of 6 Telemetry Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* 1. CPU Load */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <span>CPU Load</span>
            <Cpu className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-slate-100 font-mono tracking-tight">
            {t.cpuUsage}%
          </div>
          {/* Progress bar */}
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
            <div
              className="h-full bg-cyan-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, t.cpuUsage)}%` }}
            />
          </div>
          <div className="text-[10px] font-mono text-slate-400 truncate">{t.cpuDetails}</div>
        </div>

        {/* 2. GPU VRAM */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <span>GPU VRAM</span>
            <Zap className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-black text-slate-100 font-mono tracking-tight">
            {t.gpuUsage}%
          </div>
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
            <div
              className="h-full bg-purple-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, t.gpuUsage)}%` }}
            />
          </div>
          <div className="text-[10px] font-mono text-slate-400 truncate">{t.gpuDetails}</div>
        </div>

        {/* 3. RAM Usage */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <span>RAM</span>
            <HardDrive className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-black text-slate-100 font-mono tracking-tight">
            {t.ramUsageGb} <span className="text-sm font-normal text-slate-400">GB</span>
          </div>
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, t.ramPercent)}%` }}
            />
          </div>
          <div className="text-[10px] font-mono text-slate-400 flex justify-between">
            <span>{t.ramPercent}% Used</span>
            <span>Total: {t.ramTotalGb}GB</span>
          </div>
        </div>

        {/* 4. NVMe Storage */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <span>Storage</span>
            <HardDrive className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-slate-100 font-mono tracking-tight">
            {t.storageUsedGb} <span className="text-sm font-normal text-slate-400">GB</span>
          </div>
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, t.storagePercent)}%` }}
            />
          </div>
          <div className="text-[10px] font-mono text-slate-400 flex justify-between">
            <span>{t.storagePercent}% Used</span>
            <span>NVMe 1TB</span>
          </div>
        </div>

        {/* 5. Network I/O */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <span>Network I/O</span>
            <Wifi className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-slate-100 font-mono tracking-tight">
            {(t.networkDownMbps / 1000).toFixed(1)} <span className="text-sm font-normal text-slate-400">Gbps</span>
          </div>
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
            <div className="h-full bg-cyan-400 rounded-full w-3/4" />
          </div>
          <div className="text-[10px] font-mono text-slate-400 truncate">
            ↓ {t.networkDownMbps}Mb • ↑ {t.networkUpMbps}Mb
          </div>
        </div>

        {/* 6. Temperature */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            <span>Thermal</span>
            <Thermometer className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-slate-100 font-mono tracking-tight">
            {t.temperatureC}°C
          </div>
          <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
            <div
              className={cn(
                'h-full rounded-full transition-all duration-500',
                t.temperatureC > 75 ? 'bg-rose-500' : t.temperatureC > 60 ? 'bg-amber-400' : 'bg-emerald-400'
              )}
              style={{ width: `${Math.min(100, (t.temperatureC / 100) * 100)}%` }}
            />
          </div>
          <div className="text-[10px] font-mono text-emerald-400 font-bold uppercase truncate">
            {t.tempStatus} • COOLING OPTIMAL
          </div>
        </div>
      </div>

      {/* Expandable Deep Telemetry Details */}
      <div className="pt-1">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-xs font-mono text-slate-400 hover:text-cyan-300 flex items-center space-x-1 cursor-pointer transition-colors"
        >
          <span>{isExpanded ? 'Hide Hardware Bus Details' : 'Show Hardware Bus & Thread Topology'}</span>
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {isExpanded && (
          <div className="mt-3 p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 text-xs font-mono text-slate-400 grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <span className="text-slate-500">PCIe Link:</span>{' '}
              <strong className="text-slate-200">Gen 5.0 x16 (64 GB/s)</strong>
            </div>
            <div>
              <span className="text-slate-500">Memory Bandwidth:</span>{' '}
              <strong className="text-slate-200">DDR5 6000MHz (96 GB/s)</strong>
            </div>
            <div>
              <span className="text-slate-500">Inference Device:</span>{' '}
              <strong className="text-cyan-300">CUDA 12.4 • TensorRT</strong>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemOverviewWidget;
