import React from 'react';
import { Users, CheckCircle2, AlertCircle, Loader2, StopCircle } from 'lucide-react';
import { SwarmStatus, SwarmTask } from '../types/swarm';
import { cn } from '@/utils/cn';

interface SwarmExecutionCardProps {
  goal: string;
  status: SwarmStatus;
  progress: number;
  agentCount: number;
  tasks: SwarmTask[];
  onCancel?: () => void;
  className?: string;
}

export const SwarmExecutionCard: React.FC<SwarmExecutionCardProps> = ({
  goal,
  status,
  progress,
  agentCount,
  tasks,
  onCancel,
  className,
}) => {
  const isRunning = status === 'RUNNING' || status === 'PLANNING' || status === 'SYNTHESIZING';

  return (
    <div className={cn('p-4 rounded-3xl border border-cyan-500/30 bg-slate-950/90 backdrop-blur-xl shadow-2xl space-y-3 font-mono text-xs text-slate-100', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-cyan-300 font-bold uppercase tracking-wider">
          <Users className="w-4 h-4 text-cyan-400" />
          <span>MULTI-AGENT SWARM COLLABORATION</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase border bg-purple-500/20 text-purple-300 border-purple-500/30">
            {agentCount} AGENTS ACTIVE
          </span>
          <span
            className={cn(
              'px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border',
              isRunning && 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 animate-pulse',
              status === 'COMPLETED' && 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
              status === 'FAILED' && 'bg-rose-500/20 text-rose-300 border-rose-500/40'
            )}
          >
            {status}
          </span>
        </div>
      </div>

      <div className="text-slate-200 text-xs font-sans">
        Swarm Goal: <strong className="text-cyan-200 font-mono">"{goal}"</strong>
      </div>

      <div className="space-y-1.5 pt-1">
        <div className="flex justify-between text-[11px] text-slate-400">
          <span>DAG Task Execution Progress</span>
          <span>{progress}% Completed</span>
        </div>
        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div className="h-full bg-cyan-400 transition-all duration-300" style={{ width: `${progress}%` }} />
        </div>

        <div className="space-y-1 pt-2">
          {tasks.map((task) => (
            <div key={task.taskId} className="flex items-center justify-between text-[11px] p-2 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="flex items-center space-x-2">
                {task.state === 'COMPLETED' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
                {task.state === 'RUNNING' && <Loader2 className="w-3.5 h-3.5 text-cyan-400 animate-spin shrink-0" />}
                {task.state === 'FAILED' && <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
                {task.state === 'DEPENDENCY_BLOCKED' && <div className="w-3.5 h-3.5 rounded-full border border-amber-500/40 shrink-0" />}
                <span className="text-slate-200">{task.title}</span>
              </div>
              <span className="text-[10px] text-slate-400">{task.assignedAgentName}</span>
            </div>
          ))}
        </div>
      </div>

      {isRunning && onCancel && (
        <div className="pt-1 flex justify-end">
          <button
            onClick={onCancel}
            className="flex items-center space-x-1.5 px-3 py-1 rounded-xl bg-rose-500/20 text-rose-300 border border-rose-500/40 hover:bg-rose-500/30 text-[11px]"
          >
            <StopCircle className="w-3.5 h-3.5" />
            <span>Cancel Swarm Mission</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default SwarmExecutionCard;
