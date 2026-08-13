import React from 'react';
import { Target, Users, ChevronRight } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MissionItem } from '../types/mission';
import MissionStatusBadge from './MissionStatusBadge';
import { ProgressBar } from '@/components/status/StatusIndicators';

interface MissionCardProps {
  mission: MissionItem;
  onSelect: () => void;
  className?: string;
}

export const MissionCard: React.FC<MissionCardProps> = ({
  mission,
  onSelect,
  className,
}) => {
  const isExecuting = mission.status === 'EXECUTING' || mission.status === 'PLANNING';

  return (
    <div
      onClick={onSelect}
      className={cn(
        'p-5 rounded-3xl bg-slate-900/80 border transition-all cursor-pointer space-y-3.5 group shadow-xl relative',
        isExecuting
          ? 'border-cyan-500/50 bg-slate-900 shadow-[0_0_20px_rgba(0,240,255,0.15)]'
          : 'border-slate-800/90 hover:border-slate-700 hover:bg-slate-900'
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Target className="w-5 h-5" />
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20 uppercase font-bold">
            Autonomy: {mission.autonomyLevel}
          </span>
        </div>

        <MissionStatusBadge status={mission.status} />
      </div>

      <div className="space-y-1">
        <h4 className="text-sm font-bold font-sans text-slate-100 group-hover:text-cyan-300 transition-colors">
          {mission.title}
        </h4>
        <p className="text-xs font-sans text-slate-300 line-clamp-2 leading-relaxed">
          {mission.goal}
        </p>
      </div>

      {/* Progress & Task Ratio */}
      <div className="space-y-1 pt-1 font-mono text-[11px]">
        <div className="flex justify-between text-slate-400">
          <span>Overall Progress</span>
          <span className="text-cyan-300 font-bold">
            {mission.completedTasksCount}/{mission.tasksCount} Tasks ({mission.progress}%)
          </span>
        </div>
        <ProgressBar progress={mission.progress} />
      </div>

      {/* Agents & Footer */}
      <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800">
        <div className="flex items-center space-x-1">
          <Users className="w-3.5 h-3.5 text-slate-500" />
          <span>{mission.assignedAgents.length} Agents Assigned</span>
        </div>
        <div className="flex items-center text-cyan-400 font-bold group-hover:translate-x-0.5 transition-transform">
          <span>Inspect DAG</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </div>
      </div>
    </div>
  );
};

export default MissionCard;
