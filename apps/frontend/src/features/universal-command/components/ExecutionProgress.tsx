import React from 'react';
import { cn } from '@/utils/cn';
import { CommandExecutionState } from '../types/execution';

interface ExecutionProgressProps {
  state: CommandExecutionState;
  className?: string;
}

export const ExecutionProgress: React.FC<ExecutionProgressProps> = ({ state, className }) => {
  const steps: { label: string; key: CommandExecutionState }[] = [
    { label: 'UNDERSTAND', key: 'UNDERSTANDING' },
    { label: 'PLAN', key: 'PLANNING' },
    { label: 'CHECK PERMISSION', key: 'PERMISSION_CHECK' },
    { label: 'EXECUTE', key: 'EXECUTING' },
    { label: 'VERIFY', key: 'VERIFYING' },
  ];

  const getStateIndex = (s: CommandExecutionState) => {
    switch (s) {
      case 'UNDERSTANDING':
        return 0;
      case 'PLANNING':
        return 1;
      case 'CAPABILITY_SELECTED':
      case 'PERMISSION_CHECK':
      case 'AWAITING_APPROVAL':
        return 2;
      case 'EXECUTING':
        return 3;
      case 'VERIFYING':
        return 4;
      case 'COMPLETED':
        return 5;
      default:
        return 0;
    }
  };

  const currentIndex = getStateIndex(state);

  return (
    <div className={cn('p-4 rounded-3xl bg-slate-950/80 border border-slate-800 space-y-2 font-mono text-xs shadow-xl', className)}>
      <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">UNIVERSAL PIPELINE PROGRESS</div>
      <div className="flex items-center justify-between gap-1 overflow-x-auto py-1">
        {steps.map((st, idx) => {
          const isDone = currentIndex > idx;
          const isCurrent = currentIndex === idx;
          return (
            <div key={st.key} className="flex items-center space-x-1.5 shrink-0">
              <span
                className={cn(
                  'px-2.5 py-1 rounded-xl text-[10px] font-bold border transition-all',
                  isDone
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                    : isCurrent
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 animate-pulse'
                    : 'bg-slate-900 text-slate-600 border-slate-800'
                )}
              >
                {isDone ? '✓ ' : isCurrent ? '● ' : '○ '} {st.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ExecutionProgress;
