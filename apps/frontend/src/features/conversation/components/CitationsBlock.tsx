import React from 'react';
import { ExternalLink, BookOpen } from 'lucide-react';
import { cn } from '@/utils/cn';
import { CitationData } from '../types/message';

interface CitationsBlockProps {
  citations: CitationData[];
  className?: string;
}

export const CitationsBlock: React.FC<CitationsBlockProps> = ({ citations, className }) => {
  if (!citations || citations.length === 0) return null;

  return (
    <div className={cn('my-3 p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2.5 text-xs font-mono', className)}>
      <div className="flex items-center space-x-2 text-cyan-400 font-bold border-b border-slate-800 pb-2">
        <BookOpen className="w-4 h-4" />
        <span className="uppercase tracking-wider">Citations & Research Sources</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {citations.map((c, idx) => (
          <div key={c.id || idx} className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800/80 space-y-1 hover:border-cyan-500/40 transition-all">
            <div className="flex items-center justify-between text-slate-200 font-bold">
              <span className="truncate">[{idx + 1}] {c.title}</span>
              <ExternalLink className="w-3 h-3 text-slate-500 shrink-0 ml-1" />
            </div>
            <div className="text-[10px] text-cyan-300 truncate">{c.source}</div>
            {c.snippet && <p className="text-[11px] text-slate-400 font-sans line-clamp-2 leading-relaxed">{c.snippet}</p>}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CitationsBlock;
