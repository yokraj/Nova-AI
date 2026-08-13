import React from 'react';
import { Play, Pause, Square, Terminal, Activity } from 'lucide-react';
import { cn } from '@/utils/cn';
import { AgentExecutionTask } from '../types/agentExecution';
import AgentStatusBadge from './AgentStatusBadge';
import { ProgressBar } from '@/components/status/StatusIndicators';

interface AgentExecutionCardProps {
  task: AgentExecutionTask;
  onPause: (id: string) => void;
  onResume: (id: string) => void;
  onCancel: (id: string) => void;
  className?: string;
}

export const AgentExecutionCard: React.FC<AgentExecutionCardProps> = ({
  task,
  onPause,
  onResume,
  onCancel,
  className,
}) => {
  const isWorking = task.status === 'WORKING';
  const isPaused = task.status === 'PAUSED';

  return (
    <div className={cn('p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3 font-mono text-xs shadow-xl', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span className="font-bold text-slate-100">{task.agentName}</span>
        </div>
        <AgentStatusBadge status={task.status} />
      </div>

      <div>
        <h4 className="text-xs font-bold text-cyan-300 font-sans">{task.title}</h4>
        <p className="text-[11px] text-slate-400 font-sans mt-0.5">{task.description}</p>
      </div>

      <div className="space-y-1">
        <div className="flex justify-between text-[10px] text-slate-400">
          <span>{task.currentAction}</span>
          <span>{task.progress}%</span>
        </div>
        <ProgressBar progress={task.progress} />
      </div>

      {/* Output Stream Logs */}
      {task.outputLogs.length > 0 && (
        <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[10px] text-slate-300 space-y-1 max-h-24 overflow-y-auto">
          {task.outputLogs.map((log, idx) => (
            <div key={idx} className="flex items-start space-x-1.5">
              <Terminal className="w-3 h-3 text-cyan-400 shrink-0 mt-0.5" />
              <span>{log}</span>
            </div>
          ))}
        </div>
      )}

      {/* Control Buttons */}
      <div className="flex items-center justify-between pt-1">
        <div className="flex items-center space-x-2">
          {isWorking && (
            <button
              onClick={() => onPause(task.id)}
              className="px-3 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 text-[11px] font-bold border border-slate-800 transition-all cursor-pointer flex items-center space-x-1"
            >
              <Pause className="w-3 h-3" />
              <span>Pause</span>
            </button>
          )}

          {isPaused && (
            <button
              onClick={() => onResume(task.id)}
              className="px-3 py-1 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-[11px] font-bold transition-all cursor-pointer flex items-center space-x-1"
            >
              <Play className="w-3 h-3" />
              <span>Resume</span>
            </button>
          )}
        </div>

        <button
          onClick={() => onCancel(task.id)}
          className="px-3 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 text-[11px] font-bold transition-all cursor-pointer flex items-center space-x-1"
        >
          <Square className="w-3 h-3" />
          <span>Cancel Task</span>
        </button>
      </div>
    </div>
  );
};

export default AgentExecutionCard;
