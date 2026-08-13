import React, { useState } from 'react';
import { Bot, ArrowRight, CheckCircle2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard } from '@/components/cards/Cards';
import { ProgressBar, StatusBadge } from '@/components/status/StatusIndicators';
import { MOCK_ACTIVE_AGENTS_EXTENDED } from '@/mock/mockDashboardData';

export const ActiveAgentsWidget: React.FC<{ className?: string }> = ({ className }) => {
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [inspectModalText, setInspectModalText] = useState<string | null>(null);

  const agents = MOCK_ACTIVE_AGENTS_EXTENDED;

  const handleInspect = (name: string, role: string, task: string) => {
    setInspectModalText(`Agent '${name}' (${role}) is currently executing: "${task}"`);
  };

  return (
    <GlassCard className={cn('p-5 space-y-4', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Active Agent Workforce
            </h3>
            <p className="text-xs text-slate-400">67 Specialized Agents across 9 Engineering Divisions</p>
          </div>
        </div>
        <StatusBadge label="6 ONLINE" variant="cyan" />
      </div>

      {/* Agents Stream Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {agents.map((agent) => (
          <div
            key={agent.id}
            onClick={() => setSelectedAgentId(agent.id)}
            className={cn(
              'p-3.5 rounded-2xl bg-slate-900/80 border transition-all cursor-pointer space-y-2.5',
              selectedAgentId === agent.id
                ? 'border-cyan-500/60 bg-slate-900 shadow-[0_0_15px_rgba(0,240,255,0.15)]'
                : 'border-slate-800/90 hover:border-slate-700 hover:bg-slate-900/90'
            )}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-slate-950 font-black text-xs shadow-md">
                  {agent.avatar}
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-100">{agent.name}</div>
                  <div className="text-[10px] font-mono text-slate-400">{agent.division}</div>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <span className="text-[10px] font-mono text-cyan-400 font-semibold">{agent.latencyMs}ms</span>
                <StatusBadge
                  label={agent.status}
                  variant={agent.status === 'active' ? 'success' : agent.status === 'busy' ? 'warning' : 'info'}
                />
              </div>
            </div>

            {/* Task Details & Progress */}
            <div className="space-y-1.5 pt-1">
              <div className="text-xs text-slate-300 font-medium truncate flex items-center justify-between">
                <span>{agent.currentTask}</span>
                <span className="text-[10px] font-mono text-cyan-300 font-bold ml-2">{agent.progress}%</span>
              </div>
              <ProgressBar progress={agent.progress} />
            </div>

            <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1">
              <span>Tasks Completed: <strong className="text-slate-200">{agent.tasksCompleted}</strong></span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleInspect(agent.name, agent.role, agent.currentTask);
                }}
                className="text-cyan-400 hover:text-cyan-200 flex items-center space-x-1 cursor-pointer font-sans text-[11px] font-semibold"
              >
                <span>Inspect</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Simulated Agent Inspection Toast/Modal */}
      {inspectModalText && (
        <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-200 text-xs font-mono flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-purple-400 shrink-0" />
            <span>{inspectModalText}</span>
          </div>
          <button
            onClick={() => setInspectModalText(null)}
            className="text-slate-400 hover:text-slate-200 text-xs font-bold"
          >
            Dismiss
          </button>
        </div>
      )}
    </GlassCard>
  );
};

export default ActiveAgentsWidget;
