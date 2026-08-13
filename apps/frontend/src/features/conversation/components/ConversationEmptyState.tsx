import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Code, Cpu, ShieldCheck } from 'lucide-react';
import novaCoreImg from '@/assets/nova-core.png';

interface ConversationEmptyStateProps {
  onSelectPrompt: (prompt: string) => void;
  className?: string;
}

export const ConversationEmptyState: React.FC<ConversationEmptyStateProps> = ({
  onSelectPrompt,
  className,
}) => {
  const suggestions = [
    { title: 'Explain quantum computing', subtitle: 'Physics & Superposition Theory', icon: Sparkles },
    { title: 'Write a Python program to sort a list', subtitle: 'QuickSort Algorithms & Benchmarks', icon: Code },
    { title: 'Analyze my Nova project', subtitle: 'Multi-Agent Monorepo Architecture', icon: Cpu },
    { title: 'Turn on my lights', subtitle: 'Smart Home Device Control & Approval UX', icon: ShieldCheck },
  ];

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 space-y-6 text-center select-none">
      {/* Official Nova Core Mini Visual Authority */}
      <motion.div
        animate={{ scale: [1, 1.04, 1] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        className="w-36 h-36 rounded-full overflow-hidden border-2 border-cyan-400 shadow-[0_0_50px_rgba(0,240,255,0.4)] flex items-center justify-center cursor-pointer"
      >
        <img src={novaCoreImg} alt="Nova Core" className="w-full h-full object-cover rounded-full" />
      </motion.div>

      <div className="space-y-2">
        <h2 className="text-2xl font-extrabold text-slate-100 tracking-tight">What shall we explore?</h2>
        <p className="text-xs text-slate-400 font-mono max-w-md">
          Ask Nova about science, coding, architecture, device orchestration, or project automation
        </p>
      </div>

      {/* 4 Capability Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full text-left font-sans">
        {suggestions.map((s, idx) => {
          const Icon = s.icon;
          return (
            <div
              key={idx}
              onClick={() => onSelectPrompt(s.title)}
              className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/90 hover:border-cyan-500/50 hover:bg-slate-900 transition-all cursor-pointer space-y-1.5 group shadow-xl"
            >
              <div className="flex items-center space-x-2 text-cyan-400 group-hover:text-cyan-300 font-bold text-xs">
                <Icon className="w-4 h-4" />
                <span>{s.title}</span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">{s.subtitle}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ConversationEmptyState;
