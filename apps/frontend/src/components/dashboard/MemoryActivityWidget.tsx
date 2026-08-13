import React from 'react';
import { Brain, Network, Database, Sparkles, Clock, Share2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard } from '@/components/cards/Cards';
import { StatusBadge } from '@/components/status/StatusIndicators';
import { MOCK_MEMORY_ITEMS } from '@/mock/mockMemory';

export const MemoryActivityWidget: React.FC<{ className?: string }> = ({ className }) => {
  const knowledgeUpdates = [
    { entity: 'FastAPI Microservice', type: 'Framework', relation: 'implements', target: 'REST API Gateway', time: '5m ago' },
    { entity: 'PostgreSQL DB', type: 'Database', relation: 'stores', target: 'User & System Telemetry', time: '18m ago' },
    { entity: 'Qwen 3 8B', type: 'AI Model', relation: 'powers', target: 'Universal Intelligence Core', time: '42m ago' },
  ];

  return (
    <GlassCard className={cn('p-5 space-y-4', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Brain className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Memory & Knowledge Intelligence
            </h3>
            <p className="text-xs text-slate-400">Vector memory store & ontological entity graph activity</p>
          </div>
        </div>
        <StatusBadge label="INDEXED" variant="purple" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Sub-panel 1: MEMORY */}
        <div className="space-y-3 p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="w-4 h-4 text-purple-400" />
              <h4 className="text-xs font-bold text-slate-100 uppercase tracking-wider">Memory Activity</h4>
            </div>
            <span className="text-[10px] font-mono text-purple-300">142,850 Stored</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800">
              <div className="text-[10px] text-slate-400">Retrieved Today</div>
              <div className="text-sm font-bold text-cyan-300">3,412</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800">
              <div className="text-[10px] text-slate-400">Confidence Avg</div>
              <div className="text-sm font-bold text-emerald-400">96.8%</div>
            </div>
          </div>

          <div className="space-y-2 pt-1">
            <div className="text-[11px] font-mono font-semibold text-slate-400">Recent Semantic Memories</div>
            {MOCK_MEMORY_ITEMS.map((mem) => (
              <div key={mem.id} className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                <div className="flex items-center justify-between text-[10px] font-mono">
                  <StatusBadge label={mem.type} variant="cyan" />
                  <span className="text-slate-400">{mem.workspace}</span>
                </div>
                <p className="text-xs text-slate-200 line-clamp-2 leading-relaxed">{mem.content}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Sub-panel 2: KNOWLEDGE GRAPH */}
        <div className="space-y-3 p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Network className="w-4 h-4 text-blue-400" />
              <h4 className="text-xs font-bold text-slate-100 uppercase tracking-wider">Knowledge Graph</h4>
            </div>
            <span className="text-[10px] font-mono text-blue-300">12,480 Entities</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800">
              <div className="text-[10px] text-slate-400">Relationships</div>
              <div className="text-sm font-bold text-blue-300">48,200</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800">
              <div className="text-[10px] text-slate-400">Ontology Status</div>
              <div className="text-sm font-bold text-emerald-400">SYNCHRONIZED</div>
            </div>
          </div>

          <div className="space-y-2 pt-1">
            <div className="text-[11px] font-mono font-semibold text-slate-400">Recent Graph Relationships</div>
            {knowledgeUpdates.map((item, idx) => (
              <div key={idx} className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1 text-xs">
                <div className="flex items-center justify-between font-mono text-[10px]">
                  <span className="text-slate-200 font-bold">{item.entity}</span>
                  <span className="text-slate-500">{item.time}</span>
                </div>
                <div className="flex items-center space-x-1.5 font-mono text-[11px] text-slate-400">
                  <span className="text-cyan-400">{item.relation}</span>
                  <Share2 className="w-3 h-3 text-slate-600" />
                  <span className="text-purple-300">{item.target}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </GlassCard>
  );
};

export default MemoryActivityWidget;
