import React from 'react';
import { Monitor, MousePointer, CheckCircle2, Loader2 } from 'lucide-react';
import { cn } from '@/utils/cn';

interface ComputerExecutionCardProps {
  applicationName: string;
  currentAction: string;
  targetElement: string;
  confidence: number; // 0.0 to 1.0
  status: 'EXECUTING' | 'VERIFYING' | 'COMPLETED' | 'FAILED' | 'AWAITING_APPROVAL';
  className?: string;
}

export const ComputerExecutionCard: React.FC<ComputerExecutionCardProps> = ({
  applicationName,
  currentAction,
  targetElement,
  confidence,
  status,
  className,
}) => {
  const confidencePercent = Math.round(confidence * 100);

  return (
    <div className={cn('p-4 rounded-3xl border border-cyan-500/30 bg-slate-950/90 backdrop-blur-xl shadow-2xl space-y-3 font-mono text-xs text-slate-100', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-cyan-300 font-bold uppercase tracking-wider">
          <Monitor className="w-4 h-4 text-cyan-400" />
          <span>REAL COMPUTER CONTROL</span>
        </div>
        <span
          className={cn(
            'px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border',
            status === 'EXECUTING' && 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 animate-pulse',
            status === 'VERIFYING' && 'bg-purple-500/20 text-purple-300 border-purple-500/40',
            status === 'COMPLETED' && 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
            status === 'FAILED' && 'bg-rose-500/20 text-rose-300 border-rose-500/40',
            status === 'AWAITING_APPROVAL' && 'bg-amber-500/20 text-amber-300 border-amber-500/40'
          )}
        >
          {status}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[11px] pt-1">
        <div className="p-2 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-slate-400 text-[10px]">Target Application</div>
          <div className="font-bold text-cyan-200">{applicationName}</div>
        </div>
        <div className="p-2 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-slate-400 text-[10px]">Active Action</div>
          <div className="font-bold text-purple-200">{currentAction}</div>
        </div>
      </div>

      <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
        <div className="flex items-center justify-between text-[11px]">
          <div className="flex items-center space-x-1.5 text-slate-300">
            <MousePointer className="w-3.5 h-3.5 text-cyan-400" />
            <span>Target: <strong className="text-cyan-200">{targetElement}</strong></span>
          </div>
          <span className="text-[10px] text-emerald-400 font-bold">{confidencePercent}% Confidence</span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-1 border-t border-slate-800/80 text-[10px] text-slate-400">
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1"><CheckCircle2 className="w-3 h-3 text-emerald-400" /> Observed</span>
          <span className="flex items-center space-x-1"><CheckCircle2 className="w-3 h-3 text-emerald-400" /> Resolved</span>
          <span className="flex items-center space-x-1">
            {status === 'EXECUTING' ? <Loader2 className="w-3 h-3 text-cyan-400 animate-spin" /> : <CheckCircle2 className="w-3 h-3 text-emerald-400" />} Action
          </span>
        </div>
      </div>
    </div>
  );
};

export default ComputerExecutionCard;
