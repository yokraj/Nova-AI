import React, { useState } from 'react';
import {
  Bot,
  Search,
  Filter,
  CheckCircle2,
  ArrowRight,
  X,
  Play,
  Pause,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { DashboardAgent } from '@/types/dashboard';
import { MOCK_ACTIVE_AGENTS_EXTENDED } from '@/mock/mockDashboardData';

interface ActiveAgentsWidgetProps {
  className?: string;
  agents?: DashboardAgent[];
  onInspectAgent?: (agent: DashboardAgent) => void;
}

export const ActiveAgentsWidget: React.FC<ActiveAgentsWidgetProps> = ({
  className,
  agents = MOCK_ACTIVE_AGENTS_EXTENDED,
  onInspectAgent,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'busy' | 'idle'>('all');
  const [selectedAgent, setSelectedAgent] = useState<DashboardAgent | null>(null);
  const [localAgents, setLocalAgents] = useState<DashboardAgent[]>(agents);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  React.useEffect(() => {
    setLocalAgents(agents);
  }, [agents]);

  const filteredAgents = localAgents.filter((agent) => {
    const matchesSearch =
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.division.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.currentTask.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || agent.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleInspect = (agent: DashboardAgent) => {
    setSelectedAgent(agent);
    if (onInspectAgent) onInspectAgent(agent);
  };

  const toggleAgentPause = (agentId: string) => {
    setLocalAgents((prev) =>
      prev.map((a) => {
        if (a.id === agentId) {
          const nextStatus = a.status === 'active' || a.status === 'busy' ? 'idle' : 'active';
          setActionNotice(`Agent ${a.name} status switched to ${nextStatus}.`);
          return { ...a, status: nextStatus };
        }
        return a;
      })
    );
  };

  const onlineCount = localAgents.filter((a) => a.status === 'active' || a.status === 'busy').length;

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
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shrink-0">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
              Active Agent Workforce
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              67 Autonomous Agents across 9 Engineering & Operations Divisions
            </p>
          </div>
        </div>

        {/* Status Pill */}
        <div className="flex items-center space-x-2">
          {localAgents[0]?.isLive ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span>LIVE POOL ({onlineCount} ACTIVE)</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span>OFFLINE • CACHED ({onlineCount} ACTIVE)</span>
            </span>
          )}
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        {/* Search Input */}
        <div className="relative flex-1 max-w-sm">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search agents by role, division, or task..."
            className="w-full pl-9 pr-8 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 transition-all font-sans"
            aria-label="Search agents"
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

        {/* Status Filter Tabs */}
        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-[11px] font-mono">
          <Filter className="w-3 h-3 text-slate-500 ml-1 mr-0.5 shrink-0" />
          {(['all', 'active', 'busy', 'idle'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setStatusFilter(tab)}
              className={cn(
                'px-2.5 py-1 rounded-lg uppercase tracking-wider transition-all cursor-pointer',
                statusFilter === tab
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              )}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Agents Stream Grid */}
      {filteredAgents.length === 0 ? (
        <div className="p-8 text-center rounded-2xl bg-slate-900/40 border border-slate-800/80 text-xs font-mono text-slate-500 space-y-1">
          <Bot className="w-6 h-6 mx-auto text-slate-600 mb-2" />
          <p>No agents match filter criteria "{searchQuery || statusFilter}".</p>
          <button
            onClick={() => {
              setSearchQuery('');
              setStatusFilter('all');
            }}
            className="text-cyan-400 hover:text-cyan-300 text-xs font-semibold cursor-pointer underline pt-1"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {filteredAgents.map((agent) => (
            <div
              key={agent.id}
              onClick={() => handleInspect(agent)}
              className={cn(
                'p-3.5 rounded-2xl bg-slate-900/80 border transition-all cursor-pointer space-y-2.5 group',
                selectedAgent?.id === agent.id
                  ? 'border-cyan-500/60 bg-slate-900 shadow-[0_0_15px_rgba(0,240,255,0.15)]'
                  : 'border-slate-800/90 hover:border-slate-700 hover:bg-slate-900/90'
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5 min-w-0">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-slate-950 font-black text-xs shadow-md shrink-0">
                    {agent.avatar}
                  </div>
                  <div className="min-w-0">
                    <div className="text-xs font-bold text-slate-100 truncate group-hover:text-cyan-300 transition-colors">
                      {agent.name}
                    </div>
                    <div className="text-[10px] font-mono text-slate-400 truncate">{agent.division}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <span className="text-[10px] font-mono text-cyan-400 font-semibold">{agent.latencyMs}ms</span>
                  <span
                    className={cn(
                      'text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border uppercase',
                      agent.status === 'active'
                        ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
                        : agent.status === 'busy'
                        ? 'bg-amber-500/15 border-amber-500/30 text-amber-400'
                        : 'bg-slate-800 border-slate-700 text-slate-400'
                    )}
                  >
                    {agent.status}
                  </span>
                </div>
              </div>

              {/* Task Details & Progress */}
              <div className="space-y-1.5 pt-0.5">
                <div className="text-xs text-slate-300 font-medium truncate flex items-center justify-between">
                  <span className="truncate">{agent.currentTask}</span>
                  <span className="text-[10px] font-mono text-cyan-300 font-bold ml-2 shrink-0">
                    {agent.progress}%
                  </span>
                </div>
                <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-400 to-purple-500 rounded-full transition-all duration-300"
                    style={{ width: `${agent.progress}%` }}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1 border-t border-slate-800/60">
                <span>
                  Done: <strong className="text-slate-200">{agent.tasksCompleted}</strong>
                </span>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleAgentPause(agent.id);
                    }}
                    className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-cyan-300 transition-colors"
                    title={agent.status === 'idle' ? 'Activate Agent' : 'Pause Agent'}
                  >
                    {agent.status === 'idle' ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleInspect(agent);
                    }}
                    className="text-cyan-400 hover:text-cyan-200 flex items-center space-x-1 cursor-pointer font-sans text-[11px] font-semibold"
                  >
                    <span>Inspect</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Action Notice */}
      {actionNotice && (
        <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-200 text-xs font-mono flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>{actionNotice}</span>
          </div>
          <button
            onClick={() => setActionNotice(null)}
            className="text-slate-400 hover:text-slate-200 text-xs cursor-pointer font-bold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Detailed Agent Inspection Modal / Dialog */}
      {selectedAgent && (
        <div
          className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedAgent(null)}
        >
          <div
            className="w-full max-w-lg p-6 rounded-3xl bg-slate-950 border border-cyan-500/40 shadow-2xl space-y-4 font-sans text-slate-100"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-slate-950 font-black text-sm shadow-md">
                  {selectedAgent.avatar}
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100">{selectedAgent.name}</h3>
                  <p className="text-xs font-mono text-cyan-400">{selectedAgent.role}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedAgent(null)}
                className="p-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-100 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                <div className="text-slate-500">Current Task Pipeline:</div>
                <div className="text-slate-200 font-sans font-medium">{selectedAgent.currentTask}</div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                  <div className="text-slate-500">Division:</div>
                  <div className="text-slate-200 font-bold">{selectedAgent.division}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                  <div className="text-slate-500">Inference Latency:</div>
                  <div className="text-emerald-400 font-bold">{selectedAgent.latencyMs} ms</div>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex justify-between text-slate-400">
                  <span>Task Progress</span>
                  <span className="text-cyan-300 font-bold">{selectedAgent.progress}%</span>
                </div>
                <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-400 to-purple-500 rounded-full"
                    style={{ width: `${selectedAgent.progress}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800 text-xs font-mono">
              <button
                onClick={() => {
                  toggleAgentPause(selectedAgent.id);
                  setSelectedAgent(null);
                }}
                className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-all cursor-pointer"
              >
                {selectedAgent.status === 'idle' ? 'Activate Agent' : 'Pause Agent'}
              </button>
              <button
                onClick={() => setSelectedAgent(null)}
                className="px-4 py-2 rounded-xl bg-cyan-500 text-slate-950 font-bold transition-all cursor-pointer hover:bg-cyan-400 shadow-sm"
              >
                Close Inspection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActiveAgentsWidget;
