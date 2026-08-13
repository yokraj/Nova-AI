import React, { useState } from 'react';
import { Workflow, Play, Pause, RefreshCw } from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard } from '@/components/cards/Cards';
import { StatusBadge } from '@/components/status/StatusIndicators';
import { MOCK_AUTOMATIONS, MockAutomation } from '@/mock/mockDashboardData';

export const AutomationCenterWidget: React.FC<{ className?: string }> = ({ className }) => {
  const [automations, setAutomations] = useState<MockAutomation[]>(MOCK_AUTOMATIONS);
  const [runningId, setRunningId] = useState<string | null>(null);

  const toggleStatus = (id: string) => {
    setAutomations((prev) =>
      prev.map((item) => {
        if (item.id === id) {
          const nextStatus = item.status === 'active' ? 'paused' : 'active';
          return { ...item, status: nextStatus };
        }
        return item;
      })
    );
  };

  const triggerNow = (id: string) => {
    setRunningId(id);
    setTimeout(() => {
      setRunningId(null);
      setAutomations((prev) =>
        prev.map((item) =>
          item.id === id
            ? { ...item, lastRun: 'Just now', executionCount: item.executionCount + 1 }
            : item
        )
      );
    }, 1200);
  };

  return (
    <GlassCard className={cn('p-5 space-y-4', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Workflow className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              No-Code Automation & Workflow Studio
            </h3>
            <p className="text-xs text-slate-400">Scheduled routines, background macros & event triggers</p>
          </div>
        </div>
        <StatusBadge label="4 ROUTINES" variant="success" />
      </div>

      {/* Automations Stream Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {automations.map((auto) => (
          <div
            key={auto.id}
            className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 hover:border-slate-700 transition-all space-y-2.5"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                  {auto.category}
                </span>
                <StatusBadge
                  label={auto.status}
                  variant={auto.status === 'active' ? 'success' : auto.status === 'scheduled' ? 'cyan' : 'warning'}
                />
              </div>
              <span className="text-[10px] font-mono text-slate-500">Runs: {auto.executionCount}</span>
            </div>

            <div>
              <h4 className="text-xs font-bold text-slate-100">{auto.name}</h4>
              <p className="text-[11px] font-mono text-slate-400 mt-0.5">Trigger: {auto.trigger}</p>
            </div>

            <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/60">
              <div className="space-y-0.5">
                <div>Last: <span className="text-slate-200">{auto.lastRun}</span></div>
                <div>Next: <span className="text-cyan-300">{auto.nextRun}</span></div>
              </div>

              <div className="flex items-center space-x-1.5">
                <button
                  onClick={() => triggerNow(auto.id)}
                  disabled={runningId === auto.id}
                  className="px-2.5 py-1 rounded-lg bg-emerald-500/15 text-emerald-300 hover:bg-emerald-500/25 border border-emerald-500/30 text-xs font-semibold transition-all cursor-pointer flex items-center space-x-1"
                >
                  <RefreshCw className={cn('w-3 h-3', runningId === auto.id && 'animate-spin')} />
                  <span>{runningId === auto.id ? 'Running...' : 'Run Now'}</span>
                </button>
                <button
                  onClick={() => toggleStatus(auto.id)}
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-300 text-xs transition-all cursor-pointer"
                  title={auto.status === 'active' ? 'Pause Automation' : 'Activate Automation'}
                >
                  {auto.status === 'active' ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </GlassCard>
  );
};

export default AutomationCenterWidget;
