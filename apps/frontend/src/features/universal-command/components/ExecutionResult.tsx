import React from 'react';
import { CheckCircle2, AlertCircle, Clock, ExternalLink } from 'lucide-react';
import { cn } from '@/utils/cn';
import { CommandResult as ResultType } from '../types/commandResult';

interface ExecutionResultProps {
  result: ResultType;
  onOpenContextDrawer?: (domain?: string) => void;
  className?: string;
}

export const ExecutionResult: React.FC<ExecutionResultProps> = ({
  result,
  onOpenContextDrawer,
  className,
}) => {
  return (
    <div
      className={cn(
        'p-4.5 rounded-3xl border space-y-2 font-mono text-xs shadow-2xl transition-all',
        result.success
          ? 'bg-slate-950/90 border-emerald-500/40 text-slate-100'
          : 'bg-slate-950/90 border-rose-500/40 text-rose-200',
        className
      )}
    >
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 font-bold font-sans text-sm">
          {result.success ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-400" />
          )}
          <span>{result.success ? 'Command Executed' : 'Execution Failed'}</span>
        </div>
        <div className="flex items-center space-x-1 text-[10px] text-slate-400">
          <Clock className="w-3 h-3" />
          <span>{result.durationSeconds}s</span>
        </div>
      </div>

      <div className="text-xs font-sans text-slate-200">{result.message}</div>

      {result.targetDomain && onOpenContextDrawer && (
        <div className="pt-2 border-t border-slate-800 flex justify-end">
          <button
            onClick={() => onOpenContextDrawer(result.targetDomain)}
            className="px-3 py-1 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-[11px] font-bold transition-all cursor-pointer flex items-center space-x-1"
          >
            <span>View {result.targetDomain} Subsystem</span>
            <ExternalLink className="w-3 h-3" />
          </button>
        </div>
      )}
    </div>
  );
};

export default ExecutionResult;
