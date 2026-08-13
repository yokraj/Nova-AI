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
      title: 'NOVA',
      subtitle: 'UNIVERSAL INTELLIGENCE • LOCAL-FIRST • VOICE-FIRST',
      color: 'text-cyan-400',
    },
    LISTENING: {
      title: 'LISTENING',
      subtitle: '"I\'m listening..."',
      color: 'text-cyan-300 animate-pulse',
    },
    THINKING: {
      title: 'THINKING',
      subtitle: '"Understanding your request..."',
      color: 'text-purple-400',
    },
    PLANNING: {
      title: 'PLANNING',
      subtitle: '"Preparing the best approach..."',
      color: 'text-blue-400',
    },
    EXECUTING: {
      title: 'EXECUTING',
      subtitle: '"Working on it..."',
      color: 'text-purple-300',
    },
    SPEAKING: {
      title: 'SPEAKING',
      subtitle: '"Nova Speaking..."',
      color: 'text-cyan-300',
    },
    SUCCESS: {
      title: 'COMPLETE',
      subtitle: '"Done."',
      color: 'text-emerald-400',
    },
    ERROR: {
      title: 'I ENCOUNTERED A PROBLEM',
      subtitle: '"Let me explain."',
      color: 'text-rose-400',
    },
  };

  const current = statusInfo[state];

  return (
    <div className={cn('text-center space-y-1.5 select-none', className)}>
      <AnimatePresence mode="wait">
        <motion.div
          key={state}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          className="space-y-1"
        >
          <div className={cn('text-xs font-mono font-extrabold tracking-widest uppercase', current.color)}>
            {current.title}
          </div>
          <div className="text-sm font-sans font-medium text-slate-300">
            {customText || current.subtitle}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default NovaStatus;
