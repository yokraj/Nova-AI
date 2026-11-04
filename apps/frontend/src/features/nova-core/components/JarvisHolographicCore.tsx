import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { cn } from '@/utils/cn';
import { NovaCoreState } from '../types/novaCore';
import novaCoreImg from '@/assets/nova-core.png';
import { Sparkles, Activity, ShieldCheck, Cpu } from 'lucide-react';

interface JarvisHolographicCoreProps {
  state?: NovaCoreState;
  userName?: string;
  onClick?: () => void;
  className?: string;
  voiceLevel?: number;
}

export const JarvisHolographicCore: React.FC<JarvisHolographicCoreProps> = ({
  state = 'IDLE',
  userName = 'Commander',
  onClick,
  className,
  voiceLevel = 0,
}) => {
  const shouldReduceMotion = useReducedMotion();

  // Dynamic time-based greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  // State-based glowing colors and parameters
  const stateTheme: Record<
    NovaCoreState,
    {
      primary: string;
      glow: string;
      halo: string;
      orbitSpeed: number;
      label: string;
      subtext: string;
    }
  > = {
    IDLE: {
      primary: '#00f0ff',
      glow: 'rgba(0, 240, 255, 0.35)',
      halo: 'shadow-[0_0_80px_rgba(0,240,255,0.25)]',
      orbitSpeed: 24,
      label: 'SYSTEM ONLINE',
      subtext: 'Core standing by for instruction',
    },
    SLEEPING: {
      primary: '#00f0ff',
      glow: 'rgba(0, 240, 255, 0.4)',
      halo: 'shadow-[0_0_90px_rgba(0,240,255,0.3)]',
      orbitSpeed: 30,
      label: 'WAKE WORD STANDBY',
      subtext: 'Listening for "Hey Nova"...',
    },
    INTERRUPTED: {
      primary: '#f97316',
      glow: 'rgba(249, 115, 22, 0.65)',
      halo: 'shadow-[0_0_100px_rgba(249,115,22,0.5)]',
      orbitSpeed: 10,
      label: 'SPEECH HALTED',
      subtext: 'Interrupted by operator',
    },
    LISTENING: {
      primary: '#38bdf8',
      glow: 'rgba(56, 189, 248, 0.65)',
      halo: 'shadow-[0_0_110px_rgba(56,189,248,0.55)]',
      orbitSpeed: 8,
      label: 'VOICE RECEPTIVE',
      subtext: 'Listening to acoustic input...',
    },
    TRANSCRIBING: {
      primary: '#00e5ff',
      glow: 'rgba(0, 229, 255, 0.65)',
      halo: 'shadow-[0_0_110px_rgba(0,229,255,0.5)]',
      orbitSpeed: 6,
      label: 'ACOUSTIC DECODING',
      subtext: 'Transcribing speech & identifying language...',
    },
    THINKING: {
      primary: '#a855f7',
      glow: 'rgba(168, 85, 247, 0.6)',
      halo: 'shadow-[0_0_100px_rgba(168,85,247,0.45)]',
      orbitSpeed: 10,
      label: 'SYNTACTIC REASONING',
      subtext: 'Analyzing request parameters...',
    },
    PLANNING: {
      primary: '#3b82f6',
      glow: 'rgba(59, 130, 246, 0.6)',
      halo: 'shadow-[0_0_100px_rgba(59,130,246,0.45)]',
      orbitSpeed: 12,
      label: 'TASK DECOMPOSITION',
      subtext: 'Generating tool execution plan...',
    },
    EXECUTING: {
      primary: '#ffaa00',
      glow: 'rgba(255, 170, 0, 0.7)',
      halo: 'shadow-[0_0_120px_rgba(255,170,0,0.5)]',
      orbitSpeed: 6,
      label: 'PHYSICAL DISPATCH',
      subtext: 'Executing verified operation...',
    },
    AWAITING_APPROVAL: {
      primary: '#f59e0b',
      glow: 'rgba(245, 158, 11, 0.75)',
      halo: 'shadow-[0_0_110px_rgba(245,158,11,0.55)]',
      orbitSpeed: 16,
      label: 'AUTHORIZATION REQUIRED',
      subtext: 'Operator confirmation requested',
    },
    COMPLETED: {
      primary: '#10b981',
      glow: 'rgba(16, 185, 129, 0.65)',
      halo: 'shadow-[0_0_100px_rgba(16,185,129,0.45)]',
      orbitSpeed: 20,
      label: 'OPERATION VERIFIED',
      subtext: 'State verified successfully',
    },
    FAILED: {
      primary: '#f43f5e',
      glow: 'rgba(244, 63, 94, 0.65)',
      halo: 'shadow-[0_0_100px_rgba(244,63,94,0.45)]',
      orbitSpeed: 20,
      label: 'OPERATION HALTED',
      subtext: 'Execution encountered exception',
    },
    SPEAKING: {
      primary: '#00f0ff',
      glow: 'rgba(0, 240, 255, 0.5)',
      halo: 'shadow-[0_0_90px_rgba(0,240,255,0.35)]',
      orbitSpeed: 12,
      label: 'VOCAL SYNTHESIS',
      subtext: 'Streaming auditory response...',
    },
    SUCCESS: {
      primary: '#10b981',
      glow: 'rgba(16, 185, 129, 0.65)',
      halo: 'shadow-[0_0_100px_rgba(16,185,129,0.45)]',
      orbitSpeed: 20,
      label: 'COMPLETED',
      subtext: 'Result verified',
    },
    ERROR: {
      primary: '#f43f5e',
      glow: 'rgba(244, 63, 94, 0.65)',
      halo: 'shadow-[0_0_100px_rgba(244,63,94,0.45)]',
      orbitSpeed: 20,
      label: 'ERROR',
      subtext: 'Execution error',
    },
  };

  const currentTheme = stateTheme[state] || stateTheme.IDLE;

  // Pulse scaling
  const coreScale =
    state === 'LISTENING'
      ? [1, 1.05 + voiceLevel * 0.15, 1]
      : state === 'TRANSCRIBING'
      ? [1, 1.05, 1]
      : state === 'SPEAKING'
      ? [1, 1.08, 1]
      : state === 'SLEEPING'
      ? [1, 1.03, 1]
      : state === 'INTERRUPTED'
      ? [1, 1.06, 1]
      : state === 'EXECUTING'
      ? [1, 1.04, 1]
      : state === 'AWAITING_APPROVAL'
      ? [1, 1.06, 1]
      : [1, 1.02, 1];

  return (
    <div className={cn('flex flex-col items-center justify-center select-none relative', className)}>
      {/* 1. Header Cinematic Greeting */}
      <div className="text-center mb-3 sm:mb-4 space-y-1 z-10 max-w-xl">
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center space-x-2 px-3 py-0.5 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 font-mono text-[10px] tracking-widest uppercase mb-1 shadow-[0_0_15px_rgba(0,240,255,0.15)]"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
          <span>{currentTheme.label}</span>
          <span className="text-slate-500">•</span>
          <span className="text-slate-400">{currentTheme.subtext}</span>
        </motion.div>

        <h1 className="text-xl sm:text-2xl md:text-3xl font-extrabold tracking-tight text-white">
          {getGreeting()},{' '}
          <span className="bg-gradient-to-r from-cyan-300 via-sky-400 to-blue-500 bg-clip-text text-transparent drop-shadow-[0_0_12px_rgba(0,240,255,0.5)]">
            {userName}
          </span>
        </h1>

        <p className="text-xs sm:text-xs font-mono text-cyan-400/80 tracking-wide">
          I'm Nova, your personal AI operating system.
        </p>
      </div>

      {/* 2. Visual Centerpiece: Holographic AI Core */}
      <div
        onClick={onClick}
        className="relative flex items-center justify-center cursor-pointer group my-1 sm:my-1.5"
        role="button"
        tabIndex={0}
        aria-label={`Nova Holographic Core: ${state}`}
      >
        {/* Ambient Halo Glow */}
        <motion.div
          animate={shouldReduceMotion ? {} : { scale: coreScale }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
          className={cn(
            'w-48 h-48 sm:w-56 sm:h-56 md:w-64 md:h-64 rounded-full blur-[50px] pointer-events-none transition-all duration-700 absolute',
            currentTheme.halo
          )}
          style={{ backgroundColor: currentTheme.glow }}
        />

        {/* Ring 1: Outermost Tachymeter Tech Ring with Degree Ticks */}
        <motion.div
          animate={shouldReduceMotion ? {} : { rotate: 360 }}
          transition={{ duration: currentTheme.orbitSpeed * 2, repeat: Infinity, ease: 'linear' }}
          className="w-48 h-48 sm:w-56 sm:h-56 md:w-60 md:h-60 rounded-full border border-cyan-500/25 absolute pointer-events-none flex items-center justify-center"
        >
          {/* Degree Ticks */}
          {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
            <div
              key={deg}
              className="absolute w-full h-full flex items-start justify-center"
              style={{ transform: `rotate(${deg}deg)` }}
            >
              <div className="w-[1px] h-1.5 bg-cyan-400/50 mt-1" />
            </div>
          ))}
          {/* 4 Radial Corner Markers */}
          <span className="absolute top-0 text-[7px] font-mono text-cyan-400/60 tracking-tighter">000°</span>
          <span className="absolute right-0 text-[7px] font-mono text-cyan-400/60 tracking-tighter rotate-90">090°</span>
          <span className="absolute bottom-0 text-[7px] font-mono text-cyan-400/60 tracking-tighter">180°</span>
          <span className="absolute left-0 text-[7px] font-mono text-cyan-400/60 tracking-tighter -rotate-90">270°</span>
        </motion.div>

        {/* Ring 2: Counter-Rotating Segmented Cyan HUD Arc Ring */}
        <motion.div
          animate={shouldReduceMotion ? {} : { rotate: -360 }}
          transition={{ duration: currentTheme.orbitSpeed * 1.4, repeat: Infinity, ease: 'linear' }}
          className="w-40 h-40 sm:w-48 sm:h-48 md:w-52 md:h-52 rounded-full border border-dashed border-cyan-400/40 absolute pointer-events-none flex items-center justify-center"
          style={{ borderColor: currentTheme.primary }}
        >
          {/* Orbiting Tech Nodes */}
          <div className="w-full h-full relative">
            <span
              className="w-2 h-2 rounded-full absolute -top-1 left-1/2 -translate-x-1/2 shadow-[0_0_10px_#00f0ff]"
              style={{ backgroundColor: currentTheme.primary }}
            />
            <span
              className="w-1.5 h-1.5 rounded-full absolute -bottom-1 left-1/2 -translate-x-1/2 shadow-[0_0_8px_#00f0ff]"
              style={{ backgroundColor: currentTheme.primary }}
            />
            <span
              className="w-1.5 h-1.5 rounded-full absolute top-1/2 -left-1 -translate-y-1/2 shadow-[0_0_8px_#00f0ff]"
              style={{ backgroundColor: currentTheme.primary }}
            />
          </div>
        </motion.div>

        {/* Ring 3: Elliptical Orbital Ring with Electron Node */}
        <motion.div
          animate={shouldReduceMotion ? {} : { rotate: [0, 360], scale: [0.98, 1.02, 0.98] }}
          transition={{
            rotate: { duration: currentTheme.orbitSpeed, repeat: Infinity, ease: 'linear' },
            scale: { duration: 4, repeat: Infinity, ease: 'easeInOut' },
          }}
          className="w-36 h-36 sm:w-44 sm:h-44 md:w-48 md:h-48 rounded-full border border-cyan-500/30 absolute pointer-events-none"
        >
          <div className="w-full h-full relative">
            <div className="w-2 rounded-full bg-cyan-300 absolute top-2 right-5 shadow-[0_0_12px_#00f0ff] animate-ping" />
            <div className="w-2 h-2 rounded-full bg-cyan-400 absolute top-2 right-5 shadow-[0_0_12px_#00f0ff]" />
          </div>
        </motion.div>

        {/* Ring 4: Inner Radar Pulse Arc (Active when listening/executing/speaking/thinking) */}
        {(state === 'LISTENING' || state === 'EXECUTING' || state === 'THINKING' || state === 'SPEAKING') && (
          <motion.div
            animate={shouldReduceMotion ? {} : { scale: [1, 1.18, 1], opacity: [0.6, 0.1, 0.6] }}
            transition={{ duration: 1.8, repeat: Infinity, ease: 'easeOut' }}
            className="w-32 h-32 sm:w-36 sm:h-36 rounded-full border-2 border-cyan-400/60 absolute pointer-events-none shadow-[0_0_20px_rgba(0,240,255,0.4)]"
          />
        )}

        {/* Central Core Holographic Sphere (Asset + High-tech Glass Frame) */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.97 }}
          animate={shouldReduceMotion ? {} : { scale: coreScale }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
          className="w-28 h-28 sm:w-36 sm:h-36 md:w-40 md:h-40 rounded-full overflow-hidden relative z-10 shadow-2xl flex items-center justify-center border-2 border-cyan-500/40 group-hover:border-cyan-300 transition-colors bg-black"
        >
          {/* Holographic Image Asset */}
          <img
            src={novaCoreImg}
            alt="Nova Universal Holographic Core"
            className="w-full h-full object-cover rounded-full filter drop-shadow-[0_0_25px_rgba(0,240,255,0.5)] group-hover:drop-shadow-[0_0_35px_rgba(0,240,255,0.8)] transition-all"
          />

          {/* Core HUD Overlay */}
          <div className="absolute inset-0 bg-radial from-transparent via-cyan-950/20 to-black/60 pointer-events-none rounded-full" />

          {/* Central Holographic NOVA Branding Inside the Core */}
          <div className="absolute flex flex-col items-center justify-center pointer-events-none">
            <span className="font-mono text-[9px] tracking-widest text-cyan-300/80 font-bold uppercase drop-shadow-[0_0_6px_#00f0ff]">
              NOVA
            </span>
            <span className="w-6 h-[1px] bg-cyan-400/60 my-0.5" />
            <span className="font-mono text-[7px] text-cyan-400/60 tracking-wider">
              AI CORE
            </span>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default JarvisHolographicCore;
