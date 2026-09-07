import React from 'react';
import { cn } from '@/utils/cn';
import { MissionStatus } from '../types/mission.js';

interface MissionStatusBadgeProps {
  status: MissionStatus;
  className?: string;
}

export const MissionStatusBadge: React.FC<MissionStatusBadgeProps> = ({ status, className }) => {
  const styles: Record<MissionStatus, string> = {
    DRAFT: 'bg-slate-800 text-slate-400 border-slate-700',
    QUEUED: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
    PLANNING: 'bg-purple-500/20 text-purple-300 border-purple-500/30 animate-pulse',
    EXECUTING: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-bold animate-pulse',
    PAUSED: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
    AWAITING_APPROVAL: 'bg-amber-500/30 text-amber-200 border-amber-500/50 font-bold animate-pulse',
    RECOVERING: 'bg-orange-500/20 text-orange-300 border-orange-500/30 animate-pulse',
    REPLANNING: 'bg-purple-500/30 text-purple-200 border-purple-500/50 font-bold animate-pulse',
    COMPLETED: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold',
    FAILED: 'bg-rose-500/20 text-rose-300 border-rose-500/40 font-bold',
    CANCELLED: 'bg-slate-800 text-slate-500 border-slate-700',
    TIMED_OUT: 'bg-rose-900/30 text-rose-300 border-rose-800',
    RECOVERY_REQUIRED: 'bg-amber-600/30 text-amber-200 border-amber-600/50 font-bold animate-pulse',
  };

  const styleClass = styles[status] || 'bg-slate-800 text-slate-400 border-slate-700';

  return (
    <span className={cn('px-2.5 py-0.5 rounded-full text-[10px] font-mono border uppercase tracking-wider', styleClass, className)}>
      ● {status ? status.replace('_', ' ') : 'DRAFT'}
    </span>
  );
};

export default MissionStatusBadge;
