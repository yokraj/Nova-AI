import React from 'react';
import { Brain, Clock, Pin, Trash2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MemoryItem } from '../types/memory';

interface MemoryItemCardProps {
  item: MemoryItem;
  onSelect: () => void;
  onForget: (id: string) => void;
  onPin?: (id: string) => void;
  className?: string;
}

export const MemoryItemCard: React.FC<MemoryItemCardProps> = ({
  item,
  onSelect,
  onForget,
  onPin,
  className,
}) => {
  const importanceBadges = {
    Low: 'bg-slate-800 text-slate-400 border-slate-700',
    Normal: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    High: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    Critical: 'bg-rose-500/20 text-rose-300 border-rose-500/40 font-bold',
  };

  return (
    <div
      onClick={onSelect}
      className={cn(
        'p-4 rounded-2xl bg-slate-900/80 border transition-all cursor-pointer space-y-3 group shadow-xl relative',
        item.status === 'pinned'
          ? 'border-cyan-500/50 bg-slate-900 shadow-[0_0_15px_rgba(0,240,255,0.15)]'
          : 'border-slate-800/90 hover:border-slate-700 hover:bg-slate-900'
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
            {item.type}
          </span>
          <span className={cn('px-2 py-0.5 rounded-full text-[10px] font-mono border', importanceBadges[item.importance])}>
            {item.importance}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-[10px] font-mono text-emerald-400 font-bold">
            {Math.round(item.confidence * 100)}% Confidence
          </span>
          {onPin && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onPin(item.id);
              }}
              className={cn('p-1 rounded-lg text-slate-400 hover:text-cyan-300', item.status === 'pinned' && 'text-cyan-300')}
              title="Pin Memory"
            >
              <Pin className="w-3.5 h-3.5" />
            </button>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onForget(item.id);
            }}
            className="p-1 rounded-lg text-slate-400 hover:text-rose-400"
            title="Forget Memory"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="space-y-1">
        <h4 className="text-sm font-bold text-slate-100 group-hover:text-cyan-300 transition-colors font-sans">
          {item.title}
        </h4>
        <p className="text-xs text-slate-300 font-sans leading-relaxed line-clamp-2">
          {item.summary}
        </p>
      </div>

      {/* Provenance & Tags Footer */}
      <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1 border-t border-slate-800/60">
        <div className="flex items-center space-x-1.5">
          <Brain className="w-3.5 h-3.5 text-cyan-400" />
          <span>Source: <strong className="text-slate-200">{item.source.origin}</strong></span>
        </div>
        <div className="flex items-center space-x-1">
          <Clock className="w-3 h-3 text-slate-500" />
          <span>{item.createdAt}</span>
        </div>
      </div>
    </div>
  );
};

export default MemoryItemCard;
