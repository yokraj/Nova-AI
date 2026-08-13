import React from 'react';
import { Bot, Wrench, Activity, ChevronRight } from 'lucide-react';
import { cn } from '@/utils/cn';
import { AgentItem } from '../types/agent';
import AgentStatusBadge from './AgentStatusBadge';
import { ProgressBar } from '@/components/status/StatusIndicators';

interface AgentCardProps {
  agent: AgentItem;
  onSelect: () => void;
  onAssign?: () => void;
  className?: string;
}

export const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  onSelect,
  onAssign,
  className,
}) => {
  const isWorking = agent.status === 'WORKING' || agent.status === 'PLANNING';

  return (
    <div
      onClick={onSelect}
      className={cn(
        'p-4 rounded-2xl bg-slate-900/80 border transition-all cursor-pointer space-y-3 group shadow-xl relative',
        isWorking
          ? 'border-cyan-500/50 bg-slate-900 shadow-[0_0_20px_rgba(0,240,255,0.15)]'
          : 'border-slate-800/90 hover:border-slate-700 hover:bg-slate-900'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold font-sans text-slate-100 group-hover:text-cyan-300 transition-colors">
              {agent.name}
            </h4>
            <span className="text-[10px] font-mono text-purple-300">{agent.domain}</span>
          </div>
        </div>

        <AgentStatusBadge status={agent.status} />
      </div>

      <p className="text-xs font-sans text-slate-300 line-clamp-2 leading-relaxed">
        {agent.description}
      </p>

      {/* Current Task Stream */}
      {agent.currentTask && (
        <div className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1 font-mono text-[11px]">
          <div className="flex items-center justify-between text-slate-400">
            <span className="flex items-center space-x-1">
              <Activity className="w-3 h-3 text-cyan-400 animate-pulse" />
              <span>Current Task</span>
            </span>
            <span className="text-cyan-300 font-bold">{agent.performance.currentWorkload}% Workload</span>
          </div>
          <div className="text-slate-200 truncate">{agent.currentTask}</div>
          {isWorking && <ProgressBar progress={agent.performance.currentWorkload} />}
        </div>
      )}

      {/* Tools & Capabilities */}
      <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1 border-t border-slate-800">
        <div className="flex items-center space-x-1">
          <Wrench className="w-3.5 h-3.5 text-slate-500" />
          <span>{agent.tools.slice(0, 3).join(', ')}</span>
        </div>
        <div className="flex items-center text-cyan-400 font-bold group-hover:translate-x-0.5 transition-transform">
          <span>Details</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </div>
      </div>
    </div>
  );
};

export default AgentCard;
