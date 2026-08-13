import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/utils/cn';
import { VoiceState } from '../types/voice';
import novaCoreImg from '@/assets/nova-core.png';

interface VoiceOrbProps {
  state: VoiceState;
  onClick?: () => void;
  className?: string;
}

export const VoiceOrb: React.FC<VoiceOrbProps> = ({ state, onClick, className }) => {
  const stateHaloStyles: Record<VoiceState, string> = {
    IDLE: 'shadow-[0_0_60px_rgba(0,240,255,0.35)] border-cyan-500/30',
    LISTENING: 'shadow-[0_0_90px_rgba(0,240,255,0.8)] border-cyan-400',
    PROCESSING: 'shadow-[0_0_70px_rgba(59,130,246,0.7)] border-blue-400/80',
    THINKING: 'shadow-[0_0_80px_rgba(168,85,247,0.7)] border-purple-500/60',
    RESPONDING: 'shadow-[0_0_75px_rgba(0,240,255,0.6)] border-cyan-400',
    SPEAKING: 'shadow-[0_0_95px_rgba(0,240,255,0.8)] border-cyan-300',
    PAUSED: 'shadow-[0_0_50px_rgba(234,179,8,0.5)] border-yellow-500/50',
    STOPPED: 'shadow-[0_0_40px_rgba(148,163,184,0.4)] border-slate-600',
    ERROR: 'shadow-[0_0_80px_rgba(244,63,94,0.75)] border-rose-500',
    PERMISSION_REQUIRED: 'shadow-[0_0_80px_rgba(245,158,11,0.7)] border-amber-500',
  };

  return (
    <div
      onClick={onClick}
      className={cn('relative flex items-center justify-center cursor-pointer select-none group', className)}
    >
      {/* State-Driven Outer Glow Ring */}
      <motion.div
        animate={
          state === 'LISTENING'
            ? { scale: [1, 1.08, 1] }
            : state === 'SPEAKING'
            ? { scale: [1, 1.06, 1] }
            : state === 'THINKING'
            ? { rotate: 360 }
            : { scale: [1, 1.03, 1] }
        }
        transition={{
          rotate: { duration: 10, repeat: Infinity, ease: 'linear' },
          scale: { duration: state === 'LISTENING' ? 1.2 : 2.5, repeat: Infinity, ease: 'easeInOut' },
        }}
        className={cn(
          'w-64 h-64 sm:w-80 sm:h-80 rounded-full border-2 transition-all duration-500 absolute pointer-events-none',
          stateHaloStyles[state]
        )}
      />

      {/* Official Nova Core Image */}
      <motion.div
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        className="w-56 h-56 sm:w-72 sm:h-72 rounded-full overflow-hidden relative z-10 shadow-2xl flex items-center justify-center"
      >
        <img
          src={novaCoreImg}
          alt="Nova Core Visual Identity"
          className="w-full h-full object-cover rounded-full"
        />
      </motion.div>
    </div>
  );
};

export default VoiceOrb;
