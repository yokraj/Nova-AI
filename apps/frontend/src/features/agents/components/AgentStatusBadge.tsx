import React from 'react';
import { cn } from '@/utils/cn';
import { AgentStatus } from '../types/agent';

interface AgentStatusBadgeProps {
  status: AgentStatus;
  className?: string;
}

export const AgentStatusBadge: React.FC<AgentStatusBadgeProps> = ({ status, className }) => {
  const styles: Record<AgentStatus, string> = {
    IDLE: 'bg-slate-800 text-slate-400 border-slate-700',
    AVAILABLE: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold',
    ASSIGNED: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    PLANNING: 'bg-purple-500/20 text-purple-300 border-purple-500/30 animate-pulse',
    WORKING: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-bold animate-pulse',
    WAITING: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    AWAITING_APPROVAL: 'bg-amber-500/30 text-amber-200 border-amber-500/50 font-bold animate-pulse',
    COMPLETED: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    FAILED: 'bg-rose-500/20 text-rose-300 border-rose-500/40 font-bold',
    PAUSED: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
    CANCELLED: 'bg-slate-800 text-slate-500 border-slate-700',
  };

  return (
    <span className={cn('px-2.5 py-0.5 rounded-full text-[10px] font-mono border uppercase tracking-wider', styles[status], className)}>
      ● {status.replace('_', ' ')}
    </span>
  );
};

export default AgentStatusBadge;
