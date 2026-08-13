import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Network, ZoomIn, ZoomOut, RefreshCw, ArrowRight } from 'lucide-react';
import { cn } from '@/utils/cn';
import { KnowledgeEntity, KnowledgeRelationship } from '../types/knowledge';

interface KnowledgeGraphViewProps {
  entities: KnowledgeEntity[];
  relationships: KnowledgeRelationship[];
  onSelectEntity: (entity: KnowledgeEntity) => void;
  className?: string;
}

export const KnowledgeGraphView: React.FC<KnowledgeGraphViewProps> = ({
  entities,
  relationships,
  onSelectEntity,
  className,
}) => {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [selectedCluster, setSelectedCluster] = useState<string>('all');

  const clusters = ['all', 'Core', 'Frontend', 'Backend', 'Inference', 'Memory', 'Agents'];

  const filteredEntities = entities.filter(
    (e) => selectedCluster === 'all' || e.cluster === selectedCluster
  );

  return (
    <div className={cn('p-5 rounded-3xl bg-slate-950 border border-slate-800 space-y-4 shadow-2xl relative overflow-hidden', className)}>
      {/* Graph Control Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3 font-mono text-xs">
        <div className="flex items-center space-x-2 text-cyan-300 font-extrabold">
          <Network className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span className="uppercase tracking-wider">ONTOLOGICAL GRAPH VISUALIZER</span>
        </div>

        <div className="flex items-center space-x-2">
          {/* Cluster Filter */}
          <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
            {clusters.map((c) => (
              <button
                key={c}
                onClick={() => setSelectedCluster(c)}
                className={cn(
                  'px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer capitalize',
                  selectedCluster === c ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'
                )}
              >
                {c}
              </button>
            ))}
          </div>

          <button onClick={() => setZoomLevel(Math.min(zoomLevel + 0.15, 1.5))} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <ZoomIn className="w-4 h-4" />
          </button>
          <button onClick={() => setZoomLevel(Math.max(zoomLevel - 0.15, 0.7))} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <ZoomOut className="w-4 h-4" />
          </button>
          <button onClick={() => setZoomLevel(1)} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Graph Node Canvas Simulation */}
      <div
        className="min-h-[360px] relative p-6 rounded-2xl bg-slate-900/40 border border-slate-800/80 flex flex-wrap gap-4 items-center justify-center transition-transform duration-300"
        style={{ transform: `scale(${zoomLevel})` }}
      >
        {filteredEntities.map((ent) => (
          <motion.div
            key={ent.id}
            whileHover={{ scale: 1.05 }}
            onClick={() => onSelectEntity(ent)}
            className="p-3.5 rounded-2xl bg-slate-900 border border-cyan-500/40 hover:border-cyan-400 shadow-[0_0_20px_rgba(0,240,255,0.15)] cursor-pointer space-y-1.5 max-w-[200px]"
          >
            <div className="flex items-center justify-between text-[10px] font-mono">
              <span className="text-cyan-400 font-bold">{ent.type}</span>
              <span className="text-purple-300">{ent.cluster}</span>
            </div>
            <div className="text-xs font-bold text-slate-100 truncate">{ent.name}</div>
            <div className="text-[10px] text-slate-400 line-clamp-1">{ent.description}</div>
          </motion.div>
        ))}
      </div>

      {/* Connection Relationships Stream */}
      <div className="space-y-2 pt-2 border-t border-slate-800 font-mono text-xs">
        <div className="text-[11px] text-slate-400 font-bold uppercase">Active Relationships ({relationships.length})</div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {relationships.slice(0, 4).map((rel) => (
            <div key={rel.id} className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-[11px]">
              <span className="text-slate-200 font-bold truncate max-w-[120px]">{rel.sourceId}</span>
              <div className="flex items-center space-x-1 text-cyan-400 font-bold">
                <span>{rel.type}</span>
                <ArrowRight className="w-3 h-3 text-slate-500" />
              </div>
              <span className="text-purple-300 font-bold truncate max-w-[120px]">{rel.targetId}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeGraphView;
