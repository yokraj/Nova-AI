import React from 'react';
import { Cpu, HardDrive, Zap, Gauge, Thermometer, Wifi } from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard, MetricCard } from '@/components/cards/Cards';
import { CircularGauge, ProgressBar, StatusBadge } from '@/components/status/StatusIndicators';
import { MOCK_TELEMETRY } from '@/mock/mockDashboardData';

export const SystemOverviewWidget: React.FC<{ className?: string }> = ({ className }) => {
  const t = MOCK_TELEMETRY;

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Gauge className="w-4 h-4" />
          </div>
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
            System Telemetry & Hardware Overview
          </h3>
        </div>
        <StatusBadge label="HARDWARE NOMINAL" variant="success" />
      </div>

      {/* Grid of Metric Cards & Progress Gauges */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* CPU */}
        <MetricCard
          title="CPU Load"
          value={`${t.cpuUsage}%`}
          change={t.cpuDetails}
          isPositive={true}
          icon={Cpu}
        />

        {/* GPU */}
        <MetricCard
          title="GPU VRAM"
          value={`${t.gpuUsage}%`}
          change={t.gpuDetails}
          isPositive={true}
          icon={Zap}
        />

        {/* RAM */}
        <GlassCard className="space-y-2 p-4">
          <div className="flex items-center justify-between text-xs text-slate-400 font-semibold uppercase tracking-wider">
            <span>RAM Usage</span>
            <HardDrive className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100 font-mono tracking-tight">
            {t.ramUsageGb} GB
          </div>
          <ProgressBar progress={t.ramPercent} />
          <div className="text-[11px] font-mono text-slate-400 flex justify-between">
            <span>Used: {t.ramPercent}%</span>
            <span>Total: {t.ramTotalGb}GB</span>
          </div>
        </GlassCard>

        {/* Storage */}
        <GlassCard className="space-y-2 p-4">
          <div className="flex items-center justify-between text-xs text-slate-400 font-semibold uppercase tracking-wider">
            <span>Storage</span>
            <HardDrive className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100 font-mono tracking-tight">
            {t.storageUsedGb} GB
          </div>
          <ProgressBar progress={t.storagePercent} />
          <div className="text-[11px] font-mono text-slate-400 flex justify-between">
            <span>Used: {t.storagePercent}%</span>
            <span>NVMe 1TB</span>
          </div>
        </GlassCard>

        {/* Network */}
        <MetricCard
          title="Network I/O"
          value={`${(t.networkDownMbps / 1000).toFixed(1)} Gbps`}
          change={`↓ ${t.networkDownMbps}Mb / ↑ ${t.networkUpMbps}Mb`}
          isPositive={true}
          icon={Wifi}
        />

        {/* Temperature Gauge */}
        <GlassCard className="p-4 flex flex-col items-center justify-center text-center space-y-1">
          <div className="flex items-center space-x-1 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            <Thermometer className="w-4 h-4 text-amber-400" />
            <span>Core Temp</span>
          </div>
          <CircularGauge value={t.temperatureC} max={100} label={`${t.temperatureC}°C`} />
          <span className="text-[10px] font-mono text-emerald-400 font-bold uppercase mt-1">
            {t.tempStatus}
          </span>
        </GlassCard>
      </div>
    </div>
  );
};

export default SystemOverviewWidget;
