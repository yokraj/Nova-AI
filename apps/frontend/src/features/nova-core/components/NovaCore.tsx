import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { cn } from '@/utils/cn';
import { NovaCoreState } from '../types/novaCore';
import novaCoreImg from '@/assets/nova-core.png';

interface NovaCoreProps {
  state?: NovaCoreState;
  onClick?: () => void;
  className?: string;
  voiceLevel?: number; // 0..1 optional audio activity indicator
}

export const NovaCore: React.FC<NovaCoreProps> = ({
  state = 'IDLE',
  onClick,
  className,
  voiceLevel = 0,
}) => {
  const shouldReduceMotion = useReducedMotion();

  // Color mapping per visual state
  const stateGlowStyles: Record<NovaCoreState, { halo: string; border: string; particleColor: string }> = {
    IDLE: {
      halo: 'shadow-[0_0_70px_rgba(0,240,255,0.25)] bg-cyan-500/10',
      border: 'border-cyan-500/30',
      particleColor: '#00f0ff',
    },
    LISTENING: {
      halo: 'shadow-[0_0_100px_rgba(0,240,255,0.65)] bg-cyan-400/20',
      border: 'border-cyan-400',
      particleColor: '#38bdf8',
    },
    THINKING: {
      halo: 'shadow-[0_0_90px_rgba(168,85,247,0.55)] bg-purple-500/20',
      border: 'border-purple-500/40',
      particleColor: '#c084fc',
    },
    PLANNING: {
      halo: 'shadow-[0_0_90px_rgba(59,130,246,0.55)] bg-blue-500/20',
      border: 'border-blue-400/50',
      particleColor: '#60a5fa',
    },
    EXECUTING: {
      halo: 'shadow-[0_0_110px_rgba(168,85,247,0.7)] bg-purple-600/25',
      border: 'border-purple-400',
      particleColor: '#e879f9',
    },
    AWAITING_APPROVAL: {
      halo: 'shadow-[0_0_95px_rgba(245,158,11,0.6)] bg-amber-500/20',
      border: 'border-amber-400',
      particleColor: '#fbbf24',
    },
    COMPLETED: {
      halo: 'shadow-[0_0_90px_rgba(16,185,129,0.65)] bg-emerald-500/20',
      border: 'border-emerald-400',
      particleColor: '#34d399',
    },
    FAILED: {
      halo: 'shadow-[0_0_85px_rgba(244,63,94,0.55)] bg-rose-500/20',
      border: 'border-rose-400/60',
      particleColor: '#fb7185',
    },
    SPEAKING: {
      halo: 'shadow-[0_0_85px_rgba(0,240,255,0.5)] bg-cyan-500/20',
      border: 'border-cyan-400/80',
      particleColor: '#38bdf8',
    },
    SUCCESS: {
      halo: 'shadow-[0_0_90px_rgba(16,185,129,0.65)] bg-emerald-500/20',
      border: 'border-emerald-400',
      particleColor: '#34d399',
    },
    ERROR: {
      halo: 'shadow-[0_0_85px_rgba(244,63,94,0.55)] bg-rose-500/20',
      border: 'border-rose-400/60',
      particleColor: '#fb7185',
    },
  };

  const currentStateStyle = stateGlowStyles[state] || stateGlowStyles.IDLE;

  // Speed scaling per state
  const rotationDuration =
    state === 'THINKING' ? 8 : state === 'EXECUTING' ? 6 : state === 'PLANNING' ? 12 : state === 'LISTENING' ? 10 : 20;

  const pulseScale =
    state === 'LISTENING'
      ? [1, 1.05 + voiceLevel * 0.08, 1]
      : state === 'EXECUTING'
      ? [1, 1.04, 1]
      : state === 'AWAITING_APPROVAL'
      ? [1, 1.06, 1]
      : [1, 1.02, 1];

  const pulseDuration =
    state === 'LISTENING' ? 1.2 : state === 'EXECUTING' ? 1.5 : state === 'AWAITING_APPROVAL' ? 2 : 4;

  return (
    <div
      onClick={onClick}
      className={cn('relative flex items-center justify-center cursor-pointer group select-none py-4', className)}
      role="button"
      tabIndex={0}
      aria-label={`Nova Core State: ${state}`}
    >
      {/* Background Cyber Ambient Glow */}
      <motion.div
        animate={shouldReduceMotion ? {} : { scale: pulseScale }}
        transition={{ duration: pulseDuration, repeat: Infinity, ease: 'easeInOut' }}
        className={cn(
          'w-64 h-64 sm:w-80 sm:h-80 md:w-96 md:h-96 rounded-full blur-[60px] pointer-events-none transition-all duration-700 absolute',
          currentStateStyle.halo
        )}
      />

      {/* Layer 1: Outer Rotating Ring with Tech Dots */}
      <motion.div
        animate={shouldReduceMotion ? {} : { rotate: 360 }}
        transition={{ duration: rotationDuration, repeat: Infinity, ease: 'linear' }}
        className={cn(
          'w-64 h-64 sm:w-80 sm:h-80 rounded-full border transition-all duration-700 absolute pointer-events-none flex items-center justify-center',
          currentStateStyle.border
        )}
      >
        <div className="w-full h-full relative">
          <span className="w-2 h-2 rounded-full bg-cyan-400 absolute -top-1 left-1/2 -translate-x-1/2 shadow-[0_0_8px_#00f0ff]" />
          <span className="w-1.5 h-1.5 rounded-full bg-purple-400 absolute -bottom-1 left-1/2 -translate-x-1/2" />
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400 absolute top-1/2 -left-1 -translate-y-1/2" />
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 absolute top-1/2 -right-1 -translate-y-1/2" />
        </div>
      </motion.div>

      {/* Layer 2: Counter-Rotating Dashed Orbital Ring (Active during THINKING, PLANNING, EXECUTING, AWAITING_APPROVAL) */}
      {(state === 'THINKING' || state === 'PLANNING' || state === 'EXECUTING' || state === 'AWAITING_APPROVAL' || state === 'LISTENING') && (
        <motion.div
          animate={shouldReduceMotion ? {} : { rotate: -360, scale: [0.98, 1.03, 0.98] }}
          transition={{
            rotate: { duration: rotationDuration * 1.2, repeat: Infinity, ease: 'linear' },
            scale: { duration: 2.5, repeat: Infinity, ease: 'easeInOut' },
          }}
          className="w-72 h-72 sm:w-[22rem] sm:h-[22rem] rounded-full border border-dashed border-cyan-400/40 absolute pointer-events-none"
        />
      )}

      {/* Layer 3: Floating Particle Orbiters */}
      {!shouldReduceMotion && (
        <div className="w-72 h-72 sm:w-88 sm:h-88 absolute pointer-events-none flex items-center justify-center">
          {[0, 45, 90, 135, 180, 225, 270, 315].map((angle, i) => (
            <motion.div
              key={i}
              animate={{
                rotate: [angle, angle + 360],
              }}
              transition={{
                duration: rotationDuration * (1 + (i % 3) * 0.2),
                repeat: Infinity,
                ease: 'linear',
              }}
              className="w-full h-full absolute top-0 left-0 flex items-center justify-center"
            >
              <div
                className="w-1.5 h-1.5 rounded-full absolute"
                style={{
                  top: '10%',
                  backgroundColor: currentStateStyle.particleColor,
                  boxShadow: `0 0 6px ${currentStateStyle.particleColor}`,
                  opacity: 0.4 + (i % 4) * 0.15,
                }}
              />
            </motion.div>
          ))}
        </div>
      )}

      {/* Central Official Nova Core Visual Asset */}
      <motion.div
        whileHover={{ scale: 1.04 }}
        whileTap={{ scale: 0.97 }}
        animate={
          shouldReduceMotion
            ? {}
            : {
                rotate: 360,
                scale: pulseScale,
              }
        }
        transition={{
          rotate: { duration: rotationDuration * 2.5, repeat: Infinity, ease: 'linear' },
          scale: { duration: pulseDuration, repeat: Infinity, ease: 'easeInOut' },
        }}
        className="w-48 h-48 sm:w-64 sm:h-64 rounded-full overflow-hidden relative z-10 shadow-2xl flex items-center justify-center border-2 border-slate-700/60 group-hover:border-cyan-400/80 transition-colors"
      >
        <img
          src={novaCoreImg}
          alt="Nova Core Universal Intelligence"
          className="w-full h-full object-cover rounded-full filter drop-shadow-[0_0_20px_rgba(0,240,255,0.4)]"
        />
      </motion.div>
    </div>
  );
};

export default NovaCore;
