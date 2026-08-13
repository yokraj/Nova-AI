import React from 'react';
import { Terminal } from 'lucide-react';
import { cn } from '@/utils/cn';
import { UniversalCommand } from '../types/command';

interface CommandUnderstandingProps {
  command: UniversalCommand;
  className?: string;
}

export const CommandUnderstanding: React.FC<CommandUnderstandingProps> = ({
  command,
  className,
}) => {
  return (
    <div className={cn('p-4 rounded-3xl bg-slate-950/90 border border-cyan-500/40 space-y-3 font-mono text-xs shadow-2xl', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-cyan-300 font-extrabold uppercase tracking-wider">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span>UNDERSTANDING</span>
        </div>
        <span className="px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 text-[10px] border border-cyan-500/30 uppercase">
          {command.intent?.category}
        </span>
      </div>

      <div className="space-y-1">
        <div className="text-[10px] text-slate-500 uppercase font-bold">Input</div>
        <div className="text-sm font-bold font-sans text-slate-100">"{command.rawInput}"</div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[11px]">
        <div className="p-2 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-slate-500 block text-[10px]">Target</span>
          <span className="font-bold text-slate-200">{command.target}</span>
        </div>
        <div className="p-2 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-slate-500 block text-[10px]">Capability</span>
          <span className="font-bold text-purple-300">{command.capability?.name}</span>
        </div>
      </div>
    </div>
  );
};

export default CommandUnderstanding;
