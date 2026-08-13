import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/utils/cn';
import { VoiceState } from '../types/voice';

interface VoiceWaveformProps {
  state: VoiceState;
  className?: string;
}

export const VoiceWaveform: React.FC<VoiceWaveformProps> = ({ state, className }) => {
  if (state !== 'LISTENING' && state !== 'SPEAKING' && state !== 'PROCESSING') {
    return null;
  }

  const bars = [16, 28, 44, 20, 36, 52, 24, 40, 18, 32, 48, 22];

  return (
    <div className={cn('flex items-center justify-center space-x-1.5 h-12 my-2', className)}>
      {bars.map((height, idx) => (
        <motion.div
          key={idx}
          animate={{
            height: state === 'LISTENING' ? [12, height, 12] : [8, height * 0.8, 8],
            opacity: [0.6, 1, 0.6],
          }}
          transition={{
            duration: 0.6 + (idx % 3) * 0.2,
            repeat: Infinity,
            repeatType: 'reverse',
            delay: idx * 0.05,
          }}
          className={cn(
            'w-1.5 rounded-full',
            state === 'LISTENING' ? 'bg-cyan-400 shadow-[0_0_8px_rgba(0,240,255,0.8)]' : 'bg-purple-400 shadow-[0_0_8px_rgba(168,85,247,0.8)]'
          )}
        />
      ))}
    </div>
  );
};

export default VoiceWaveform;
