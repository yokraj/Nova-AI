import React from 'react';
import { Wrench, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { ToolActivityData } from '../types/message';

export const ToolActivity: React.FC<{ data: ToolActivityData; className?: string }> = ({ data, className }) => {
  return (
    <div className={cn('my-2 p-3 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs font-mono space-y-1.5', className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Wrench className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-bold text-slate-200 uppercase">TOOL EXECUTION: {data.toolName}</span>
        </div>
        <div className="flex items-center space-x-1">
          {data.status === 'running' && <Loader2 className="w-3.5 h-3.5 text-cyan-400 animate-spin" />}
          {data.status === 'complete' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
          {data.status === 'error' && <AlertCircle className="w-3.5 h-3.5 text-rose-400" />}
          <span className="text-[10px] text-slate-400 uppercase">{data.status}</span>
        </div>
      </div>
      {data.input && <div className="text-[11px] text-slate-400">Input: {data.input}</div>}
      {data.output && <div className="text-[11px] text-cyan-300 font-sans">{data.output}</div>}
    </div>
  );
};

export default ToolActivity;
