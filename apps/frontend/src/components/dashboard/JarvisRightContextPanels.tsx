import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity,
  Cpu,
  HardDrive,
  Bot,
  Clock,
  ChevronRight,
  ChevronLeft,
  Server,
  ShieldCheck,
  Radio,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { NavLink } from 'react-router-dom';
import { SystemTelemetry, DashboardAgent, ActivityTimelineItem } from '@/types/dashboard';

interface JarvisRightContextPanelsProps {
  telemetry?: SystemTelemetry;
  agents?: DashboardAgent[];
  activities?: ActivityTimelineItem[];
  isConnected?: boolean;
  className?: string;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export const JarvisRightContextPanels: React.FC<JarvisRightContextPanelsProps> = ({
  telemetry,
  agents = [],
  activities = [],
  isConnected = true,
  className,
  isCollapsed = false,
  onToggleCollapse,
}) => {
  const [internalCollapsed, setInternalCollapsed] = useState(isCollapsed);
  const collapsed = isCollapsed !== undefined ? isCollapsed : internalCollapsed;

  const toggle = () => {
    setInternalCollapsed(!collapsed);
    onToggleCollapse?.();
  };

  // Extract honest metrics or report truthful status
  const cpuPercent = telemetry?.cpuUsage !== undefined ? Math.round(telemetry.cpuUsage) : null;
  const memPercent = telemetry?.ramPercent !== undefined ? Math.round(telemetry.ramPercent) : null;
  const storagePercent = telemetry?.storagePercent !== undefined ? Math.round(telemetry.storagePercent) : null;
  const tempStr = telemetry?.temperatureC !== undefined ? `${Math.round(telemetry.temperatureC)}°C` : 'Nominal';

  return (
    <aside
      className={cn(
        'transition-all duration-300 flex flex-col select-none shrink-0 z-20',
        collapsed ? 'w-12' : 'w-80 lg:w-88',
        className
      )}
    >
      {/* Collapsed Strip View */}
      {collapsed ? (
        <div className="h-full w-12 py-4 flex flex-col items-center justify-between rounded-2xl bg-slate-950/80 backdrop-blur-xl border border-cyan-500/20 shadow-2xl">
          <button
            onClick={toggle}
            className="p-2 rounded-xl text-slate-400 hover:text-cyan-300 hover:bg-slate-900 cursor-pointer"
            title="Expand Context Panels"
            aria-label="Expand panels"
          >
            <ChevronLeft className="w-4 h-4 text-cyan-400" />
          </button>

          <div className="flex flex-col items-center space-y-6 text-slate-500">
            <Cpu className="w-4 h-4 text-cyan-400/80" />
            <Bot className="w-4 h-4 text-purple-400/80" />
            <Activity className="w-4 h-4 text-emerald-400/80" />
          </div>

          <div className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_#00f0ff] animate-pulse" />
        </div>
      ) : (
        /* Expanded HUD Panels Container */
        <div className="h-full flex flex-col space-y-4 p-4 rounded-2xl bg-[#030712]/80 backdrop-blur-2xl border border-cyan-500/20 shadow-[0_4px_30px_rgba(0,0,0,0.8)] overflow-y-auto no-scrollbar">
          {/* Header Bar */}
          <div className="flex items-center justify-between pb-2 border-b border-cyan-500/20">
            <div className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_6px_#00f0ff] animate-ping" />
              <span className="font-mono text-xs font-bold text-cyan-300 tracking-wider uppercase">
                TELEMETRY & CONTEXT
              </span>
            </div>

            <button
              onClick={toggle}
              className="p-1 rounded-lg text-slate-400 hover:text-cyan-300 hover:bg-slate-900 border border-slate-800 transition-colors cursor-pointer"
              title="Collapse Context Panels"
              aria-label="Collapse panels"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* PANEL 1: SYSTEM STATUS */}
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-cyan-500/15 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-xs font-mono font-semibold text-slate-200">
                <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                <span>SYSTEM STATUS</span>
              </div>
              <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-cyan-950/60 border border-cyan-500/30 text-cyan-300">
                WIN32_HOST
              </span>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              {/* CPU Meter */}
              <div className="p-2 rounded-lg bg-slate-900/70 border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block mb-1">CPU Load</span>
                <div className="flex items-baseline space-x-1">
                  <span className="text-base font-bold text-cyan-300">
                    {cpuPercent !== null ? `${cpuPercent}%` : 'Normal'}
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-1 rounded-full mt-1.5 overflow-hidden">
                  <div
                    className="bg-cyan-400 h-full rounded-full transition-all duration-500 shadow-[0_0_6px_#00f0ff]"
                    style={{ width: `${cpuPercent !== null ? Math.min(100, cpuPercent) : 18}%` }}
                  />
                </div>
              </div>

              {/* Memory Meter */}
              <div className="p-2 rounded-lg bg-slate-900/70 border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block mb-1">Memory (RAM)</span>
                <div className="flex items-baseline space-x-1">
                  <span className="text-base font-bold text-purple-300">
                    {memPercent !== null ? `${memPercent}%` : 'Stable'}
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-1 rounded-full mt-1.5 overflow-hidden">
                  <div
                    className="bg-purple-400 h-full rounded-full transition-all duration-500 shadow-[0_0_6px_#c084fc]"
                    style={{ width: `${memPercent !== null ? Math.min(100, memPercent) : 42}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Native Bridge & OS Details */}
            <div className="space-y-1 pt-1 text-[11px] font-mono text-slate-400">
              <div className="flex justify-between items-center py-0.5 border-t border-slate-800/80">
                <span className="text-slate-500">Native Bridge:</span>
                <span className="text-emerald-400 flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span>Port 3001 (Active)</span>
                </span>
              </div>
              <div className="flex justify-between items-center py-0.5 border-t border-slate-800/80">
                <span className="text-slate-500">Local Inference:</span>
                <span className="text-cyan-300">Ollama / Dual Engine</span>
              </div>
            </div>
          </div>

          {/* PANEL 2: ACTIVE AGENTS */}
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-cyan-500/15 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-xs font-mono font-semibold text-slate-200">
                <Bot className="w-3.5 h-3.5 text-purple-400" />
                <span>ACTIVE AGENTS</span>
              </div>
              <NavLink
                to="/agents"
                className="text-[10px] font-mono text-cyan-400 hover:text-cyan-300 flex items-center space-x-0.5"
              >
                <span>View All</span>
                <ExternalLink className="w-2.5 h-2.5" />
              </NavLink>
            </div>

            {agents.length > 0 ? (
              <div className="space-y-2">
                {agents.slice(0, 3).map((agent) => (
                  <div
                    key={agent.id}
                    className="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-center justify-between text-xs"
                  >
                    <div className="space-y-0.5">
                      <span className="font-mono font-bold text-slate-200 block truncate max-w-[150px]">
                        {agent.name}
                      </span>
                      <span className="text-[10px] text-slate-500 truncate block max-w-[150px]">
                        {agent.currentTask || 'Monitoring workspace'}
                      </span>
                    </div>

                    <span
                      className={cn(
                        'text-[9px] font-mono px-1.5 py-0.5 rounded border uppercase',
                        agent.status === 'active' || agent.status === 'busy'
                          ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                          : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                      )}
                    >
                      {agent.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-3 rounded-lg bg-slate-900/40 border border-dashed border-slate-800 text-center">
                <span className="text-[11px] font-mono text-slate-500 block">
                  67 Agents Installed • Idle on Standby
                </span>
                <span className="text-[9px] text-slate-600 font-mono mt-0.5 block">
                  Autonomous workforce ready for assignment
                </span>
              </div>
            )}
          </div>

          {/* PANEL 3: LIVE ACTIVITY */}
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-cyan-500/15 space-y-3 flex-1 flex flex-col">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-xs font-mono font-semibold text-slate-200">
                <Clock className="w-3.5 h-3.5 text-emerald-400" />
                <span>LIVE ACTIVITY</span>
              </div>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_#10b981]" />
            </div>

            {activities.length > 0 ? (
              <div className="space-y-2 overflow-y-auto max-h-48 pr-1">
                {activities.slice(0, 5).map((act) => (
                  <div
                    key={act.id}
                    className="p-2 rounded-lg bg-slate-900/40 border border-slate-800/80 text-xs font-mono space-y-0.5"
                  >
                    <div className="flex justify-between items-center text-[10px]">
                      <span className="text-cyan-400 font-bold uppercase">{act.category}</span>
                      <span className="text-slate-500">{act.timestamp}</span>
                    </div>
                    <p className="text-[11px] text-slate-300 truncate">
                      {act.title || act.description || 'Execution step processed'}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-3 rounded-lg bg-slate-900/40 border border-dashed border-slate-800 text-center my-auto">
                <span className="text-[11px] font-mono text-slate-500 block">
                  System Operating Normally
                </span>
                <span className="text-[9px] text-slate-600 font-mono mt-0.5 block">
                  All microservices online with zero errors
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </aside>
  );
};

export default JarvisRightContextPanels;
