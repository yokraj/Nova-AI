import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Cpu,
  Brain,
  Network,
  Layers,
  Bot,
  Workflow,
  Activity,
  ChevronRight,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { cn } from '@/utils/cn';

interface NovaIntelligenceCoreProps {
  className?: string;
  onNavigateSubsystem?: (subsystemId: string) => void;
}

export const NovaIntelligenceCore: React.FC<NovaIntelligenceCoreProps> = ({
  className,
  onNavigateSubsystem,
}) => {
  const [activeSubsystem, setActiveSubsystem] = useState<string>('Reasoning');
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  const subsystems = [
    {
      id: 'reasoning',
      name: 'Reasoning',
      icon: Cpu,
      value: 'Qwen 3 8B / DeepSeek',
      detail: 'Multi-Model Neural Reasoning Engine active with speculative early decoding & plan validation.',
      color: 'text-cyan-400 border-cyan-500/30 bg-cyan-500/10',
      badge: 'OLLAMA ACTIVE',
      specs: ['Local Model: qwen3:8b', 'Temperature: 0.2', 'Fallback: llama3.2:3b'],
    },
    {
      id: 'memory',
      name: 'Memory',
      icon: Brain,
      value: '142.8k Vectors',
      detail: 'Semantic memory store with continuous workspace indexing & high confidence RAG retrieval.',
      color: 'text-purple-400 border-purple-500/30 bg-purple-500/10',
      badge: 'HNSW INDEXED',
      specs: ['Vectors: 142,850', 'Search Latency: 4.2ms', 'Confidence Avg: 96.8%'],
    },
    {
      id: 'knowledge',
      name: 'Knowledge',
      icon: Network,
      value: '12.5k Graph Nodes',
      detail: 'Ontological graph linking biological, code, research & device relationships seamlessly.',
      color: 'text-blue-400 border-blue-500/30 bg-blue-500/10',
      badge: 'SYNCHRONIZED',
      specs: ['Entities: 12,480', 'Edges: 48,200', 'Ontologies: 6 active'],
    },
    {
      id: 'context',
      name: 'Context',
      icon: Layers,
      value: '128k Window',
      detail: 'Automated desktop window & browser URL context tracking engine active across workspaces.',
      color: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
      badge: 'TRACKING ON',
      specs: ['Window Size: 131,072', 'Active Focus: Nova-AI', 'Decay Rate: Low'],
    },
    {
      id: 'agents',
      name: 'Agents',
      icon: Bot,
      value: '67 Active Workforce',
      detail: '9 Engineering & Operations Divisions orchestrating parallel tasks with plan critic oversight.',
      color: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
      badge: '9 DIVISIONS',
      specs: ['Total Agents: 67', 'Online Pool: 18', 'Avg Latency: 12ms'],
    },
    {
      id: 'inference',
      name: 'Inference',
      icon: Workflow,
      value: 'Ollama 11434 Engine',
      detail: 'Local-first model router with dynamic VRAM throttling, temperature scaling & zero cloud leaks.',
      color: 'text-rose-400 border-rose-500/30 bg-rose-500/10',
      badge: 'PORT 11434',
      specs: ['Host: 127.0.0.1:11434', 'VRAM: 8.4 / 24 GB', 'Context: 32k'],
    },
  ];

  const currentInfo = subsystems.find((s) => s.name === activeSubsystem) || subsystems[0];

  return (
    <div
      className={cn(
        'glass-panel p-5 sm:p-6 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl space-y-5 relative overflow-hidden shadow-xl select-none',
        className
      )}
    >
      {/* Background Cyber Ambient Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3.5">
        <div className="flex items-center space-x-3">
          <div className="p-2 sm:p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shrink-0">
            <Activity className="w-4 h-4 sm:w-5 sm:h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm sm:text-base font-extrabold text-slate-100 uppercase tracking-wider font-sans">
              Nova Intelligence Core
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Autonomous Cognitive Neural Subsystems & Dynamic Router
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">
            ALL SYSTEMS NOMINAL
          </span>
        </div>
      </div>

      {/* Main Grid: Orbital Ring + 6 Subsystem Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
        {/* Left Side: Animated Core Orbital Rings (5 cols) */}
        <div className="lg:col-span-5 flex flex-col items-center justify-center relative py-6">
          {/* Outer Dashed Orbit Ring */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 24, repeat: Infinity, ease: 'linear' }}
            className="w-44 h-44 sm:w-48 sm:h-48 rounded-full border-2 border-dashed border-cyan-500/30 absolute pointer-events-none"
          />

          {/* Middle Counter-Rotating Gradient Ring */}
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 16, repeat: Infinity, ease: 'linear' }}
            className="w-32 h-32 sm:w-36 sm:h-36 rounded-full border-2 border-purple-500/40 border-t-cyan-400 border-b-purple-500 absolute pointer-events-none shadow-[0_0_20px_rgba(0,240,255,0.2)]"
          />

          {/* Central Pulsing Glowing Core Orb */}
          <motion.div
            animate={{ scale: [1, 1.06, 1], opacity: [0.92, 1, 0.92] }}
            transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
            className="w-24 h-24 rounded-full bg-gradient-to-tr from-cyan-500 via-blue-600 to-purple-600 flex flex-col items-center justify-center text-slate-950 shadow-[0_0_40px_rgba(0,240,255,0.6)] cursor-pointer z-10 hover:shadow-[0_0_50px_rgba(0,240,255,0.8)] transition-all"
            onClick={() => setActiveSubsystem('Reasoning')}
            title="Nova Core Central Intelligence"
          >
            <span className="text-xs font-black tracking-tighter text-slate-950 font-sans">NOVA</span>
            <span className="text-[9px] font-mono font-bold tracking-widest text-cyan-100">CORE</span>
          </motion.div>

          <div className="mt-28 text-center">
            <div className="text-xs font-mono font-bold text-cyan-300 tracking-wider">
              UNIVERSAL INTELLIGENCE ARCHITECTURE
            </div>
            <div className="text-[11px] text-slate-400 font-mono mt-0.5">
              LOCAL-FIRST • ZERO-LEAK • 67 AGENTS • 6 SUBSYSTEMS
            </div>
          </div>
        </div>

        {/* Right Side: 6 Subsystem Cards & Active Details (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
            {subsystems.map((sub) => {
              const SubIcon = sub.icon;
              const isSelected = activeSubsystem === sub.name;
              return (
                <button
                  key={sub.name}
                  onClick={() => setActiveSubsystem(sub.name)}
                  className={cn(
                    'p-3 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between space-y-2 focus:outline-none focus:ring-1 focus:ring-cyan-400',
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
          <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800/90 space-y-2">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center space-x-2">
                <span className={cn('text-xs font-mono font-bold px-2.5 py-0.5 rounded-full border', currentInfo.color)}>
                  {currentInfo.name} SUBSYSTEM
                </span>
                <span className="text-xs font-mono text-cyan-300 font-bold">{currentInfo.value}</span>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                {currentInfo.badge}
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed font-sans">{currentInfo.detail}</p>

            {/* Specifications list */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-2 border-t border-slate-800/80 text-[11px] font-mono text-slate-400">
              {currentInfo.specs.map((spec, idx) => (
                <div key={idx} className="flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3 h-3 text-cyan-400 shrink-0" />
                  <span className="truncate">{spec}</span>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between pt-1 text-xs">
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-cyan-400 hover:text-cyan-300 font-mono text-[11px] flex items-center space-x-1 cursor-pointer"
              >
                <span>{isExpanded ? 'Hide Architecture Blueprint' : 'View Architecture Blueprint'}</span>
                <ChevronRight className={cn('w-3 h-3 transition-transform', isExpanded && 'rotate-90')} />
              </button>

              {onNavigateSubsystem && (
                <button
                  onClick={() => onNavigateSubsystem(currentInfo.id)}
                  className="text-slate-400 hover:text-cyan-300 text-[11px] font-mono flex items-center space-x-1 cursor-pointer"
                >
                  <span>Open {currentInfo.name} Center</span>
                  <ExternalLink className="w-3 h-3" />
                </button>
              )}
            </div>

            {/* Expanded Blueprint Details */}
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="pt-2 text-xs text-slate-400 space-y-1 font-mono border-t border-slate-800/60"
                >
                  <div className="flex items-center space-x-2 text-slate-300">
                    <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
                    <span>Zero-Cost Local Inference Guarantee • No external API egress</span>
                  </div>
                  <p className="text-[11px] text-slate-500 font-sans leading-relaxed">
                    All reasoning graphs and vector computations execute directly on local hardware via Ollama and embedded FAISS / HNSW indices.
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NovaIntelligenceCore;
