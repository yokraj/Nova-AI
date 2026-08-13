import React from 'react';
import { cn } from '@/utils/cn';
import { MissionStatus } from '../types/mission';

interface MissionStatusBadgeProps {
  status: MissionStatus;
  className?: string;
}

export const MissionStatusBadge: React.FC<MissionStatusBadgeProps> = ({ status, className }) => {
  const styles: Record<MissionStatus, string> = {
    DRAFT: 'bg-slate-800 text-slate-400 border-slate-700',
    UNDERSTANDING: 'bg-blue-500/20 text-blue-300 border-blue-500/30 animate-pulse',
    PLANNING: 'bg-purple-500/20 text-purple-300 border-purple-500/30 animate-pulse',
    AWAITING_APPROVAL: 'bg-amber-500/30 text-amber-200 border-amber-500/50 font-bold animate-pulse',
    READY: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    EXECUTING: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-bold animate-pulse',
    PAUSED: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
    REPLANNING: 'bg-purple-500/30 text-purple-200 border-purple-500/50 font-bold animate-pulse',
    VERIFYING: 'bg-blue-500/20 text-blue-300 border-blue-500/30 animate-pulse',
    COMPLETED: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold',
    PARTIALLY_COMPLETED: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    FAILED: 'bg-rose-500/20 text-rose-300 border-rose-500/40 font-bold',
    CANCELLED: 'bg-slate-800 text-slate-500 border-slate-700',
  };

  return (
    <span className={cn('px-2.5 py-0.5 rounded-full text-[10px] font-mono border uppercase tracking-wider', styles[status], className)}>
      ● {status.replace('_', ' ')}
    </span>
  );
};

export default MissionStatusBadge;
