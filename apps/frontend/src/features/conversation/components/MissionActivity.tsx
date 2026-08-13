import React from 'react';
import { Target } from 'lucide-react';
import { cn } from '@/utils/cn';
import { ProgressBar } from '@/components/status/StatusIndicators';
import { MissionActivityData } from '../types/message';

export const MissionActivity: React.FC<{ data: MissionActivityData; className?: string }> = ({ data, className }) => {
  return (
    <div className={cn('my-3 p-4 rounded-2xl bg-slate-950/90 border border-purple-500/40 text-xs font-mono space-y-3 shadow-xl', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2">
          <Target className="w-4 h-4 text-purple-400 animate-pulse" />
          <span className="font-bold text-slate-100 uppercase">{data.title}</span>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold">
          {data.missionId}
        </span>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-400">
        <span>Category: <strong className="text-slate-200">{data.category}</strong></span>
        <span>Subtasks: <strong className="text-cyan-300">{data.subtasksCompleted}/{data.subtasksTotal}</strong></span>
      </div>

      <div className="space-y-1">
        <div className="flex justify-between items-center text-[10px]">
          <span className="text-slate-400">DAG Progress</span>
          <span className="text-cyan-300 font-bold">{data.progress}%</span>
        </div>
        <ProgressBar progress={data.progress} />
      </div>
    </div>
  );
};

export default MissionActivity;
