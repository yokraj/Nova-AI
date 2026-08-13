import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/utils/cn';
import { VoiceState } from '../types/voice';

interface VoiceStatusProps {
  state: VoiceState;
  className?: string;
}

export const VoiceStatus: React.FC<VoiceStatusProps> = ({ state, className }) => {
  const labels: Record<VoiceState, { primary: string; secondary: string; color: string }> = {
    IDLE: { primary: 'NOVA VOICE', secondary: 'Click mic or hold Spacebar to speak', color: 'text-cyan-400' },
    LISTENING: { primary: 'LISTENING', secondary: '"I\'m listening..."', color: 'text-cyan-300 animate-pulse' },
    PROCESSING: { primary: 'PROCESSING', secondary: 'Transcribing speech & reasoning...', color: 'text-blue-300' },
    THINKING: { primary: 'THINKING', secondary: 'Synthesizing response...', color: 'text-purple-300' },
    RESPONDING: { primary: 'RESPONDING', secondary: 'Preparing audio output...', color: 'text-cyan-300' },
    SPEAKING: { primary: 'NOVA SPEAKING', secondary: 'Audio playback output active', color: 'text-cyan-300' },
    PAUSED: { primary: 'PAUSED', secondary: 'Audio playback paused', color: 'text-yellow-400' },
    STOPPED: { primary: 'STOPPED', secondary: 'Speech output stopped', color: 'text-slate-400' },
    ERROR: { primary: 'VOICE ERROR', secondary: 'Encountered a problem', color: 'text-rose-400' },
    PERMISSION_REQUIRED: { primary: 'PERMISSION REQUIRED', secondary: 'Microphone access is needed', color: 'text-amber-400' },
  };

  const current = labels[state];

  return (
    <div className={cn('text-center space-y-1 select-none font-mono', className)}>
      <AnimatePresence mode="wait">
        <motion.div
          key={state}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          className="space-y-0.5"
        >
          <div className={cn('text-xs font-extrabold tracking-widest uppercase', current.color)}>
            {current.primary}
          </div>
          <div className="text-xs text-slate-400 font-sans">{current.secondary}</div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default VoiceStatus;
