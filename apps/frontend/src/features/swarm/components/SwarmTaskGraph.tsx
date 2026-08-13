import React from 'react';
import { SwarmTask } from '../types/swarm';
import { Network } from 'lucide-react';
import { cn } from '@/utils/cn';

interface SwarmTaskGraphProps {
  tasks: SwarmTask[];
  className?: string;
}

export const SwarmTaskGraph: React.FC<SwarmTaskGraphProps> = ({ tasks, className }) => {
  return (
    <div className={cn('p-4 rounded-3xl border border-slate-800 bg-slate-950/80 backdrop-blur-xl space-y-3 font-mono text-xs text-slate-100', className)}>
      <div className="flex items-center space-x-2 text-cyan-300 font-bold border-b border-slate-800 pb-2">
        <Network className="w-4 h-4 text-cyan-400" />
        <span>SWARM TASK DEPENDENCY GRAPH (DAG)</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {tasks.map((task, idx) => (
          <div key={task.taskId} className="p-3 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <div className="flex justify-between items-center text-[11px]">
              <span className="font-bold text-cyan-300">T{idx + 1}: {task.title}</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">{task.state}</span>
            </div>
            <div className="text-[10px] text-slate-400">Assigned: {task.assignedAgentName}</div>
            {task.dependencies.length > 0 && (
              <div className="text-[10px] text-amber-300">Dependencies: [{task.dependencies.length} upstream task(s)]</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SwarmTaskGraph;
