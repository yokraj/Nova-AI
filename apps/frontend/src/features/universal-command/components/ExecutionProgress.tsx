import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/utils/cn';
import { CommandExecutionState } from '../types/execution';

interface ExecutionProgressProps {
  state: CommandExecutionState;
  className?: string;
}

export const ExecutionProgress: React.FC<ExecutionProgressProps> = ({ state, className }) => {
  if (state === 'IDLE') return null;

  const steps: { label: string; key: CommandExecutionState }[] = [
    { label: 'UNDERSTAND', key: 'UNDERSTANDING' },
    { label: 'PLAN', key: 'PLANNING' },
    { label: 'PERMISSION', key: 'PERMISSION_CHECK' },
    { label: 'EXECUTE', key: 'EXECUTING' },
    { label: 'OBSERVE', key: 'OBSERVING' },
    { label: 'VERIFY', key: 'VERIFYING' },
    { label: 'RECOVER', key: 'RECOVERING' },
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
      case 'OBSERVING':
        return 4;
      case 'VERIFYING':
        return 5;
      case 'RECOVERING':
        return 6;
      case 'COMPLETED':
        return 7;
      case 'FAILED':
      case 'DENIED':
        return 3;
      default:
        return 0;
    }
  };


  const isErrorState = state === 'FAILED' || state === 'DENIED';
  const currentIndex = getStateIndex(state);

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      className={cn('p-3 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-2 font-mono text-xs shadow-xl', className)}
    >
      <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-wider">
        <span>PIPELINE EXECUTION</span>
        <span className={isErrorState ? 'text-rose-400 font-bold' : 'text-cyan-400'}>{state}</span>
      </div>

      <div className="flex items-center justify-between gap-1 overflow-x-auto py-0.5">
        {steps.map((st, idx) => {
          const isDone = currentIndex > idx;
          const isCurrent = currentIndex === idx;
          const isFailedStep = isErrorState && isCurrent;

          return (
            <div key={st.key} className="flex items-center space-x-1 shrink-0">
              <span
                className={cn(
                  'px-2 py-0.5 rounded-lg text-[10px] font-bold border transition-all',
                  isFailedStep
                    ? 'bg-rose-500/20 text-rose-300 border-rose-500/50'
                    : isDone
                    ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                    : isCurrent
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400/50 animate-pulse shadow-[0_0_10px_rgba(0,240,255,0.2)]'
                    : 'bg-slate-950 text-slate-600 border-slate-850'
                )}
              >
                {isFailedStep ? '✗ ' : isDone ? '✓ ' : isCurrent ? '● ' : '○ '} {st.label}
              </span>
              {idx < steps.length - 1 && <span className="text-slate-700 text-[10px]">›</span>}
            </div>
          );
        })}
      </div>
    </motion.div>
  );
};

export default ExecutionProgress;
