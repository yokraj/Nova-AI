import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/utils/cn';
import { NovaCoreState } from '../types/novaCore';
import novaCoreImg from '@/assets/nova-core.png';

interface NovaCoreProps {
  state?: NovaCoreState;
  onClick?: () => void;
  className?: string;
}

export const NovaCore: React.FC<NovaCoreProps> = ({
  state = 'IDLE',
  onClick,
  className,
}) => {
  // Glow color mappings around the authoritative Nova Core image
  const haloGlowStyles: Record<NovaCoreState, string> = {
    IDLE: 'shadow-[0_0_60px_rgba(0,240,255,0.35)] border-cyan-500/30',
    LISTENING: 'shadow-[0_0_90px_rgba(0,240,255,0.7)] border-cyan-400',
    THINKING: 'shadow-[0_0_80px_rgba(168,85,247,0.6)] border-purple-500/50',
    PLANNING: 'shadow-[0_0_80px_rgba(59,130,246,0.6)] border-blue-500/50',
    EXECUTING: 'shadow-[0_0_90px_rgba(168,85,247,0.75)] border-purple-400',
    SPEAKING: 'shadow-[0_0_75px_rgba(0,240,255,0.6)] border-cyan-400/80',
    SUCCESS: 'shadow-[0_0_80px_rgba(16,185,129,0.7)] border-emerald-400',
    ERROR: 'shadow-[0_0_80px_rgba(244,63,94,0.7)] border-rose-500',
  };

  return (
    <div
      onClick={onClick}
      className={cn('relative flex items-center justify-center cursor-pointer group select-none', className)}
    >
      {/* Outer State Ring & Atmospheric Halo */}
      <motion.div
        animate={
          state === 'THINKING'
            ? { rotate: 360 }
            : state === 'PLANNING'
            ? { rotate: -360 }
            : state === 'LISTENING'
            ? { scale: [1, 1.06, 1] }
            : state === 'SPEAKING'
            ? { scale: [1, 1.04, 1] }
            : { scale: [1, 1.02, 1] }
        }
        transition={{
          rotate: { duration: state === 'THINKING' ? 12 : 8, repeat: Infinity, ease: 'linear' },
          scale: { duration: state === 'LISTENING' ? 1.2 : 3, repeat: Infinity, ease: 'easeInOut' },
        }}
        className={cn(
          'w-64 h-64 sm:w-80 sm:h-80 rounded-full border-2 transition-all duration-700 absolute pointer-events-none',
          haloGlowStyles[state]
        )}
      />

      {/* Secondary Audio-Reactive / Energy Orbital Ring for LISTENING, PLANNING, EXECUTING */}
      {(state === 'LISTENING' || state === 'PLANNING' || state === 'EXECUTING') && (
        <motion.div
          animate={{ rotate: 360, scale: [1, 1.08, 1] }}
          transition={{ rotate: { duration: 6, repeat: Infinity, ease: 'linear' }, scale: { duration: 1.5, repeat: Infinity } }}
          className="w-72 h-72 sm:w-96 sm:h-96 rounded-full border border-dashed border-cyan-400/40 absolute pointer-events-none"
        />
      )}

      {/* Authoritative Official Nova Core Image */}
      <motion.div
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.98 }}
        className="w-56 h-56 sm:w-72 sm:h-72 rounded-full overflow-hidden relative z-10 shadow-2xl flex items-center justify-center"
      >
        <img
          src={novaCoreImg}
          alt="Nova Core Universal Intelligence"
          className="w-full h-full object-cover rounded-full transition-all duration-500 filter drop-shadow-[0_0_25px_rgba(0,240,255,0.4)]"
        />
      </motion.div>
    </div>
  );
};

export default NovaCore;
