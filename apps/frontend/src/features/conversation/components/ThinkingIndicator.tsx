import React from 'react';
import { motion } from 'framer-motion';
import { Brain } from 'lucide-react';
import novaCoreImg from '@/assets/nova-core.png';

interface ThinkingIndicatorProps {
  stage?: string;
  className?: string;
}

export const ThinkingIndicator: React.FC<ThinkingIndicatorProps> = ({
  stage = 'REASONING',
  className,
}) => {
  return (
    <div className="flex items-center space-x-3 my-3 p-3 rounded-2xl bg-slate-950/80 border border-cyan-500/30 text-xs font-mono max-w-md">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
        className="w-8 h-8 rounded-full overflow-hidden shrink-0 border border-cyan-400 shadow-[0_0_15px_rgba(0,240,255,0.4)]"
      >
        <img src={novaCoreImg} alt="Nova Core" className="w-full h-full object-cover" />
      </motion.div>

      <div className="space-y-0.5">
        <div className="flex items-center space-x-1.5 text-cyan-300 font-bold uppercase tracking-wider">
          <Brain className="w-3.5 h-3.5 animate-pulse" />
          <span>THINKING • {stage}</span>
        </div>
        <div className="text-[11px] text-slate-400 font-sans">Synthesizing intelligence response blocks...</div>
      </div>
    </div>
  );
};

export default ThinkingIndicator;
