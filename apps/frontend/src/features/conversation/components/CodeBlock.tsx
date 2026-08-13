import React, { useState } from 'react';
import { Check, Copy, Code, ChevronDown, ChevronUp, WrapText } from 'lucide-react';
import { cn } from '@/utils/cn';
import { CodeBlockData } from '../types/message';

interface CodeBlockProps {
  data: CodeBlockData;
  className?: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ data, className }) => {
  const [copied, setCopied] = useState(false);
  const [isWrapped, setIsWrapped] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(data.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={cn('my-3 rounded-2xl bg-slate-950 border border-slate-800/90 overflow-hidden text-xs font-mono shadow-xl', className)}>
      {/* Code Header Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-900/90 border-b border-slate-800 text-slate-400">
        <div className="flex items-center space-x-2">
          <Code className="w-4 h-4 text-cyan-400" />
          <span className="font-bold text-slate-200 uppercase">{data.language}</span>
          {data.filename && <span className="text-[11px] text-slate-500 font-mono">({data.filename})</span>}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsWrapped(!isWrapped)}
            className={cn('p-1.5 rounded-lg border text-[11px] transition-all cursor-pointer flex items-center space-x-1', isWrapped ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30' : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200')}
            title="Toggle Line Wrap"
          >
            <WrapText className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Wrap</span>
          </button>

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg bg-slate-950 text-slate-400 border border-slate-800 hover:text-slate-200 text-[11px] transition-all cursor-pointer flex items-center space-x-1"
            title={isCollapsed ? 'Expand Code' : 'Collapse Code'}
          >
            {isCollapsed ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
          </button>

          <button
            onClick={handleCopy}
            className={cn('px-2.5 py-1.5 rounded-lg border text-[11px] font-bold font-mono transition-all cursor-pointer flex items-center space-x-1', copied ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30 hover:bg-cyan-500/20')}
          >
            {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'COPIED' : 'COPY'}</span>
          </button>
        </div>
      </div>

      {/* Code Body */}
      {!isCollapsed && (
        <div className={cn('p-4 overflow-x-auto text-slate-200 bg-slate-950 leading-relaxed font-mono', isWrapped && 'whitespace-pre-wrap break-words')}>
          <code>{data.code}</code>
        </div>
      )}
    </div>
  );
};

export default CodeBlock;
