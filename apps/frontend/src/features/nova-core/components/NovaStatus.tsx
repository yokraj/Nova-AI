import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/utils/cn';
import { NovaCoreState } from '../types/novaCore';

interface NovaStatusProps {
  state: NovaCoreState;
  customText?: string;
  className?: string;
}

export const NovaStatus: React.FC<NovaStatusProps> = ({
  state,
  customText,
  className,
}) => {
  const statusInfo: Record<NovaCoreState, { title: string; subtitle: string; color: string }> = {
    IDLE: {
      title: 'NOVA CORE',
      subtitle: 'READY FOR COMMANDS',
      color: 'text-cyan-400',
    },
    LISTENING: {
      title: 'LISTENING',
      subtitle: '"I\'m listening..."',
      color: 'text-cyan-300 animate-pulse',
    },
    THINKING: {
      title: 'THINKING',
      subtitle: '"Understanding request..."',
      color: 'text-purple-400',
    },
    PLANNING: {
      title: 'PLANNING',
      subtitle: '"Structuring execution steps..."',
      color: 'text-blue-400',
    },
    EXECUTING: {
      title: 'EXECUTING',
      subtitle: '"Running task..."',
      color: 'text-purple-300',
    },
    AWAITING_APPROVAL: {
      title: 'AUTHORIZATION REQUIRED',
      subtitle: '"High-risk step requires your approval."',
      color: 'text-amber-400 animate-pulse',
    },
    COMPLETED: {
      title: 'TASK COMPLETE',
      subtitle: '"Action verified successfully."',
      color: 'text-emerald-400',
    },
    FAILED: {
      title: 'EXECUTION HALTED',
      subtitle: '"Review execution details below."',
      color: 'text-rose-400',
    },
    SPEAKING: {
      title: 'SPEAKING',
      subtitle: '"Nova Speaking..."',
      color: 'text-cyan-300',
    },
    SUCCESS: {
      title: 'TASK COMPLETE',
      subtitle: '"Done."',
      color: 'text-emerald-400',
    },
    ERROR: {
      title: 'EXECUTION HALTED',
      subtitle: '"Let me explain."',
      color: 'text-rose-400',
    },
  };

  const current = statusInfo[state] || statusInfo.IDLE;

  return (
    <div className={cn('text-center space-y-1 select-none font-sans', className)}>
      <AnimatePresence mode="wait">
        <motion.div
          key={state}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.2 }}
          className="space-y-0.5"
        >
          <div className={cn('text-xs font-mono font-extrabold tracking-widest uppercase', current.color)}>
            {current.title}
          </div>
          <div className="text-sm font-medium text-slate-300 max-w-md mx-auto truncate">
            {customText || current.subtitle}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default NovaStatus;
