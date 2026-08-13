import React from 'react';
import { Clock } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MemoryItem } from '../types/memory';

interface MemoryTimelineProps {
  items: MemoryItem[];
  onSelect: (item: MemoryItem) => void;
  className?: string;
}

export const MemoryTimeline: React.FC<MemoryTimelineProps> = ({ items, onSelect, className }) => {
  return (
    <div className={cn('space-y-4 relative pl-4 border-l border-slate-800 font-mono text-xs', className)}>
      {items.map((item) => (
        <div key={item.id} className="relative group">
          {/* Dot */}
          <div className="w-3 h-3 rounded-full bg-cyan-400 border-2 border-slate-950 absolute -left-[23px] top-1 shadow-[0_0_8px_rgba(0,240,255,0.8)]" />

          <div
            onClick={() => onSelect(item)}
            className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 transition-all cursor-pointer space-y-1.5 shadow-md"
          >
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span className="flex items-center space-x-1.5">
                <Clock className="w-3.5 h-3.5 text-cyan-400" />
                <span>{item.createdAt}</span>
              </span>
              <span className="text-cyan-300 font-bold">{item.type}</span>
            </div>

            <h5 className="text-xs font-bold text-slate-100 font-sans group-hover:text-cyan-300 transition-colors">
              {item.title}
            </h5>
            <p className="text-[11px] text-slate-300 font-sans line-clamp-2 leading-relaxed">{item.summary}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MemoryTimeline;
