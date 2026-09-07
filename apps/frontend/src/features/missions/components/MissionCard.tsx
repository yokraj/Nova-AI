import React from 'react';
import { Target, Users, ChevronRight, Play, Pause, XCircle } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MissionItem } from '../types/mission.js';
import MissionStatusBadge from './MissionStatusBadge.js';
import { ProgressBar } from '@/components/status/StatusIndicators.js';

interface MissionCardProps {
  mission: MissionItem;
  onClick?: () => void;
  onSelect?: () => void;
  onPause?: () => void;
  onResume?: () => void;
  onCancel?: () => void;
  className?: string;
}

export const MissionCard: React.FC<MissionCardProps> = ({
  mission,
  onClick,
  onSelect,
  onPause,
  onResume,
  onCancel,
  className,
}) => {
  const isExecuting = mission.status === 'EXECUTING' || mission.status === 'PLANNING';
  const isPaused = mission.status === 'PAUSED';

  const handleClick = () => {
    if (onClick) onClick();
    else if (onSelect) onSelect();
  };

  return (
    <div
      onClick={handleClick}
      className={cn(
        'p-5 rounded-3xl bg-slate-900/80 border transition-all cursor-pointer space-y-3.5 group shadow-xl relative',
        isExecuting
          ? 'border-cyan-500/50 bg-slate-900 shadow-[0_0_20px_rgba(0,240,255,0.15)]'
          : 'border-slate-800/90 hover:border-slate-700 hover:bg-slate-900',
        className
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

      {/* Action Toolbar */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 font-mono text-xs">
        <div className="flex items-center space-x-2 text-slate-400">
          <Users className="w-3.5 h-3.5 text-cyan-400" />
          <span>{mission.assignedAgents.length} Agents</span>
        </div>

        <div className="flex items-center space-x-1.5" onClick={(e) => e.stopPropagation()}>
          {isExecuting && onPause && (
            <button
              onClick={onPause}
              className="p-1.5 rounded-lg bg-yellow-500/20 text-yellow-300 border border-yellow-500/30 hover:bg-yellow-500/30 transition-all cursor-pointer"
              title="Pause Mission"
            >
              <Pause className="w-3.5 h-3.5" />
            </button>
          )}

          {isPaused && onResume && (
            <button
              onClick={onResume}
              className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 transition-all cursor-pointer"
              title="Resume Mission"
            >
              <Play className="w-3.5 h-3.5" />
            </button>
          )}

          {onCancel && (
            <button
              onClick={onCancel}
              className="p-1.5 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/30 hover:bg-rose-500/30 transition-all cursor-pointer"
              title="Cancel Mission"
            >
              <XCircle className="w-3.5 h-3.5" />
            </button>
          )}

          <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all" />
        </div>
      </div>
    </div>
  );
};

export default MissionCard;
