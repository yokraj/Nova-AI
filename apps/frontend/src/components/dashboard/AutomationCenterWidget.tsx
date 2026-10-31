import React, { useState } from 'react';
import {
  Workflow,
  Play,
  Pause,
  RefreshCw,
  Search,
  Filter,
  CheckCircle2,
  X,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { MockAutomation } from '@/types/dashboard';
import { MOCK_AUTOMATIONS } from '@/mock/mockDashboardData';

interface AutomationCenterWidgetProps {
  className?: string;
  automations?: MockAutomation[];
  onTriggerAutomation?: (id: string) => void;
  onCancelAutomation?: (id: string) => Promise<boolean> | void;
}

export const AutomationCenterWidget: React.FC<AutomationCenterWidgetProps> = ({
  className,
  automations = MOCK_AUTOMATIONS,
  onTriggerAutomation,
  onCancelAutomation,
}) => {
  const [automationList, setAutomationList] = useState<MockAutomation[]>(automations);
  const [runningId, setRunningId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  React.useEffect(() => {
    setAutomationList(automations);
  }, [automations]);

  const categories = ['all', 'Routine', 'Maintenance', 'Monitoring'];

  const filteredAutomations = automationList.filter((auto) => {
    const matchesSearch =
      auto.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      auto.trigger.toLowerCase().includes(searchQuery.toLowerCase()) ||
      auto.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || auto.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const toggleStatus = (id: string) => {
    setAutomationList((prev) =>
      prev.map((item) => {
        if (item.id === id) {
          const nextStatus = item.status === 'active' ? 'paused' : 'active';
          setToastMessage(`Workflow "${item.name}" set to ${nextStatus}.`);
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
      setAutomationList((prev) =>
        prev.map((item) =>
          item.id === id
            ? { ...item, lastRun: 'Just now', executionCount: item.executionCount + 1 }
            : item
        )
      );
      setToastMessage(`Automation routine triggered and executed successfully.`);
      if (onTriggerAutomation) onTriggerAutomation(id);
    }, 1200);
  };

  const activeCount = automationList.filter((a) => a.status === 'active' || a.status === 'scheduled').length;

  return (
    <div
      className={cn(
        'glass-panel p-5 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl space-y-4 shadow-xl select-none',
        className
      )}
    >
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-3 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shrink-0">
            <Workflow className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
              No-Code Automation & Workflow Studio
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Scheduled routines, background cron tasks & event triggers
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {automationList[0]?.isLive ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span>LIVE WORKFLOWS ({activeCount} ARMED)</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-400 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span>OFFLINE • CACHED ({activeCount} ARMED)</span>
            </span>
          )}
        </div>
      </div>

      {/* Toolbar: Search & Category Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div className="relative flex-1 max-w-sm">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search automations by name or trigger..."
            className="w-full pl-9 pr-8 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 transition-all font-sans"
            aria-label="Search automations"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-[11px] font-mono">
          <Filter className="w-3 h-3 text-slate-500 ml-1 mr-0.5 shrink-0" />
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={cn(
                'px-2.5 py-1 rounded-lg uppercase tracking-wider transition-all cursor-pointer',
                categoryFilter === cat
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              )}
            >
              {cat === 'all' ? 'All' : cat}
            </button>
          ))}
        </div>
      </div>

      {/* Automations Grid */}
      {filteredAutomations.length === 0 ? (
        <div className="p-8 text-center rounded-2xl bg-slate-900/40 border border-slate-800/80 text-xs font-mono text-slate-500 space-y-1">
          <Workflow className="w-6 h-6 mx-auto text-slate-600 mb-2" />
          <p>No automations match filter "{searchQuery || categoryFilter}".</p>
          <button
            onClick={() => {
              setSearchQuery('');
              setCategoryFilter('all');
            }}
            className="text-emerald-400 hover:text-emerald-300 text-xs font-semibold cursor-pointer underline pt-1"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {filteredAutomations.map((auto) => {
            const isRunning = runningId === auto.id;
            return (
              <div
                key={auto.id}
                className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 hover:border-slate-700 transition-all space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      {auto.category}
                    </span>
                    <span
                      className={cn(
                        'text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border uppercase',
                        auto.status === 'active'
                          ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
                          : auto.status === 'scheduled'
                          ? 'bg-cyan-500/15 border-cyan-500/30 text-cyan-300'
                          : 'bg-amber-500/15 border-amber-500/30 text-amber-400'
                      )}
                    >
                      {auto.status}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">Executions: {auto.executionCount}</span>
                </div>

                <div>
                  <h4 className="text-xs font-bold text-slate-100 truncate">{auto.name}</h4>
                  <p className="text-[11px] font-mono text-slate-400 mt-0.5 truncate">
                    Trigger: <span className="text-cyan-300">{auto.trigger}</span>
                  </p>
                </div>

                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/60">
                  <div className="space-y-0.5">
                    <div>
                      Last: <span className="text-slate-200">{auto.lastRun}</span>
                    </div>
                    <div>
                      Next: <span className="text-cyan-300">{auto.nextRun}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-1.5">
                    <button
                      onClick={() => triggerNow(auto.id)}
                      disabled={isRunning}
                      className="px-2.5 py-1 rounded-lg bg-emerald-500/15 text-emerald-300 hover:bg-emerald-500/25 border border-emerald-500/30 text-xs font-semibold transition-all cursor-pointer flex items-center space-x-1 disabled:opacity-50"
                    >
                      <RefreshCw className={cn('w-3 h-3', isRunning && 'animate-spin')} />
                      <span>{isRunning ? 'Running...' : 'Run Now'}</span>
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
            );
          })}
        </div>
      )}

      {/* Action Toast Feedback */}
      {toastMessage && (
        <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-200 text-xs font-mono flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{toastMessage}</span>
          </div>
          <button
            onClick={() => setToastMessage(null)}
            className="text-slate-400 hover:text-slate-200 text-xs cursor-pointer font-bold"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
};

export default AutomationCenterWidget;
