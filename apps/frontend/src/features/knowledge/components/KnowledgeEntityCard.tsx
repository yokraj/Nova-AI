import React from 'react';
import { Share2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { KnowledgeEntity } from '../types/knowledge';

interface KnowledgeEntityCardProps {
  entity: KnowledgeEntity;
  onSelect: () => void;
  className?: string;
}

export const KnowledgeEntityCard: React.FC<KnowledgeEntityCardProps> = ({
  entity,
  onSelect,
  className,
}) => {
  return (
    <div
      onClick={onSelect}
      className={cn('p-4 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-900 transition-all cursor-pointer space-y-2.5 group shadow-xl', className)}
    >
      <div className="flex items-center justify-between">
        <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-blue-500/10 text-blue-300 border border-blue-500/20">
          {entity.type}
        </span>
        <span className="text-[10px] font-mono text-cyan-400 font-bold">
          Importance: {entity.importance}/10
        </span>
      </div>

      <div>
        <h4 className="text-sm font-bold font-sans text-slate-100 group-hover:text-cyan-300 transition-colors">
          {entity.name}
        </h4>
        <p className="text-xs font-sans text-slate-300 line-clamp-2 leading-relaxed mt-1">
          {entity.description}
        </p>
      </div>

      <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800">
        <span className="text-purple-300">Cluster: {entity.cluster}</span>
        <div className="flex items-center space-x-1">
          <Share2 className="w-3.5 h-3.5 text-slate-500" />
          <span>Inspect Connections</span>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeEntityCard;
