import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Cpu, Brain, Network, Layers, Bot, Workflow, Activity } from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard } from '@/components/cards/Cards';

export const NovaIntelligenceCore: React.FC<{ className?: string }> = ({ className }) => {
  const [activeSubsystem, setActiveSubsystem] = useState<string | null>('Reasoning');

  const subsystems = [
    {
      name: 'Reasoning',
      icon: Cpu,
      value: 'Qwen 3 8B / DeepSeek',
      detail: 'Multi-Model Neural Reasoning Engine active with speculative early decoding',
      color: 'text-cyan-400 border-cyan-500/30 bg-cyan-500/10',
    },
    {
      name: 'Memory',
      icon: Brain,
      value: '142.8k Vectors',
      detail: 'Semantic memory store with continuous workspace indexing & high confidence',
      color: 'text-purple-400 border-purple-500/30 bg-purple-500/10',
    },
    {
      name: 'Knowledge',
      icon: Network,
      value: '12.5k Graph Nodes',
      detail: 'Ontological graph linking biological, code, research & device relationships',
      color: 'text-blue-400 border-blue-500/30 bg-blue-500/10',
    },
    {
      name: 'Context',
      icon: Layers,
      value: '128k Context Window',
      detail: 'Automated desktop window & browser URL context tracking engine active',
      color: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
    },
    {
      name: 'Agents',
      icon: Bot,
      value: '67 Active Workforce',
      detail: '9 Engineering & Operations Divisions orchestrating parallel tasks',
      color: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
    },
    {
      name: 'Inference',
      icon: Workflow,
      value: 'Ollama 11434 Engine',
      detail: 'Local-first model router with dynamic VRAM throttling & fallbacks',
      color: 'text-rose-400 border-rose-500/30 bg-rose-500/10',
    },
  ];

  const currentInfo = subsystems.find((s) => s.name === activeSubsystem) || subsystems[0];

  return (
    <GlassCard className={cn('p-6 space-y-6 relative overflow-hidden', className)}>
      {/* Background Cyber Ambient Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Activity className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-extrabold text-slate-100 uppercase tracking-wider">
              Nova Intelligence Core
            </h3>
            <p className="text-xs text-slate-400">Autonomous Cognitive Neural Network & Multi-Model Engine</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-xs font-mono font-bold text-emerald-400 uppercase">SYSTEM ONLINE</span>
        </div>
      </div>

      {/* Central Animated Core Ring & Subsystem Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
        {/* Left Side: Animated Core Orbital Rings */}
        <div className="md:col-span-5 flex flex-col items-center justify-center relative py-4">
          {/* Outer Dotted Ring */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 24, repeat: Infinity, ease: 'linear' }}
            className="w-48 h-48 rounded-full border-2 border-dashed border-cyan-500/30 absolute pointer-events-none"
          />

          {/* Middle Counter-Rotating Gradient Ring */}
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 16, repeat: Infinity, ease: 'linear' }}
            className="w-36 h-36 rounded-full border-2 border-purple-500/40 border-t-cyan-400 border-b-purple-500 absolute pointer-events-none shadow-[0_0_20px_rgba(0,240,255,0.2)]"
          />

          {/* Central Pulsing Glowing Core Orb */}
          <motion.div
            animate={{ scale: [1, 1.08, 1], opacity: [0.9, 1, 0.9] }}
            transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
            className="w-24 h-24 rounded-full bg-gradient-to-tr from-cyan-500 via-blue-600 to-purple-600 flex flex-col items-center justify-center text-slate-950 shadow-[0_0_40px_rgba(0,240,255,0.6)] cursor-pointer z-10"
            onClick={() => setActiveSubsystem('Reasoning')}
          >
            <span className="text-xs font-black tracking-tighter text-slate-950">NOVA</span>
            <span className="text-[9px] font-mono font-bold tracking-widest text-cyan-100">CORE</span>
          </motion.div>

          <div className="mt-28 text-center">
            <div className="text-xs font-mono font-bold text-cyan-300">UNIVERSAL INTELLIGENCE</div>
            <div className="text-[11px] text-slate-400 font-mono mt-0.5">LOCAL-FIRST • VOICE-FIRST • 67 AGENTS</div>
          </div>
        </div>

        {/* Right Side: 6 Core Subsystem Chips & Details */}
        <div className="md:col-span-7 space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
            {subsystems.map((sub) => {
              const SubIcon = sub.icon;
              const isSelected = activeSubsystem === sub.name;
              return (
                <button
                  key={sub.name}
                  onClick={() => setActiveSubsystem(sub.name)}
                  className={cn(
                    'p-3 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between space-y-2',
                    isSelected
                      ? 'bg-slate-900 border-cyan-500/60 shadow-[0_0_15px_rgba(0,240,255,0.2)] scale-[1.02]'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/50'
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-200">{sub.name}</span>
                    <SubIcon className={cn('w-4 h-4', isSelected ? 'text-cyan-400' : 'text-slate-500')} />
                  </div>
                  <div className="text-[11px] font-mono font-semibold text-slate-400 truncate">
                    {sub.value}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Active Subsystem Detail Card */}
          <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-1">
            <div className="flex items-center space-x-2">
              <span className={cn('text-xs font-mono font-bold px-2 py-0.5 rounded-full border', currentInfo.color)}>
                {currentInfo.name} SUBSYSTEM
              </span>
              <span className="text-xs font-mono text-cyan-300 font-bold">{currentInfo.value}</span>
            </div>
            <p className="text-xs text-slate-300 pt-1 leading-relaxed">{currentInfo.detail}</p>
          </div>
        </div>
      </div>
    </GlassCard>
  );
};

export default NovaIntelligenceCore;
