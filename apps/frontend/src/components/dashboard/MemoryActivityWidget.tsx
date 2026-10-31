import React, { useState } from 'react';
import {
  Brain,
  Network,
  Share2,
  Search,
  RefreshCw,
  X,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { MOCK_MEMORY_ITEMS } from '@/mock/mockMemory';

const DEFAULT_KNOWLEDGE_UPDATES = [
  { entity: 'FastAPI Microservice', type: 'Framework', relation: 'implements', target: 'REST API Gateway', time: '5m ago' },
  { entity: 'PostgreSQL DB', type: 'Database', relation: 'stores', target: 'User & System Telemetry', time: '18m ago' },
  { entity: 'Qwen 3 8B', type: 'AI Model', relation: 'powers', target: 'Universal Intelligence Core', time: '42m ago' },
  { entity: 'Agent Runtime', type: 'Subsystem', relation: 'orchestrates', target: 'TaskGraph & PlanCritic', time: '1h ago' },
];

export const MemoryActivityWidget: React.FC<{ className?: string }> = ({ className }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | 'memory' | 'knowledge'>('all');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const filteredMemories = MOCK_MEMORY_ITEMS.filter((mem) => {
    if (!searchQuery) return true;
    return (
      mem.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mem.workspace.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mem.type.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  const filteredKnowledge = DEFAULT_KNOWLEDGE_UPDATES.filter((item) => {
    if (!searchQuery) return true;
    return (
      item.entity.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.target.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.relation.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 800);
  };

  return (
    <div
      className={cn(
        'glass-panel p-5 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl space-y-4 shadow-xl select-none',
        className
      )}
    >
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-3 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20 shrink-0">
            <Brain className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
              Memory & Knowledge Intelligence
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Vector memory store & ontological entity graph activity
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-300 transition-all cursor-pointer disabled:opacity-50"
            title="Re-index Memory"
            aria-label="Refresh memory activity"
          >
            <RefreshCw className={cn('w-3.5 h-3.5', isRefreshing && 'animate-spin text-purple-400')} />
          </button>

          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-purple-500/15 border border-purple-500/30 text-purple-300 text-xs font-mono font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-ping" />
            <span>HNSW INDEXED</span>
          </span>
        </div>
      </div>

      {/* Toolbar: Search & Tab Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div className="relative flex-1 max-w-sm">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search memories and entities..."
            className="w-full pl-9 pr-8 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500/50 transition-all font-sans"
            aria-label="Search memory"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-[11px] font-mono">
          {(['all', 'memory', 'knowledge'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                'px-2.5 py-1 rounded-lg uppercase tracking-wider transition-all cursor-pointer',
                activeTab === tab
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              )}
            >
              {tab === 'all' ? 'All' : tab === 'memory' ? 'Vector Memory' : 'Knowledge Graph'}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid: Vector Memory & Knowledge Graph */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Sub-panel 1: MEMORY */}
        {(activeTab === 'all' || activeTab === 'memory') && (
          <div className="space-y-3 p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Brain className="w-4 h-4 text-purple-400" />
                <h4 className="text-xs font-bold text-slate-100 uppercase tracking-wider font-sans">
                  Semantic Memory Activity
                </h4>
              </div>
              <span className="text-[10px] font-mono text-purple-300 font-bold">142,850 Stored</span>
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
              <div className="text-[11px] font-mono font-semibold text-slate-400">
                Recent Semantic Vectors ({filteredMemories.length})
              </div>
              {filteredMemories.length === 0 ? (
                <div className="p-4 text-center text-xs font-mono text-slate-500">
                  No memories match search.
                </div>
              ) : (
                filteredMemories.map((mem) => (
                  <div key={mem.id} className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                    <div className="flex items-center justify-between text-[10px] font-mono">
                      <span className="px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                        {mem.type}
                      </span>
                      <span className="text-slate-400">{mem.workspace}</span>
                    </div>
                    <p className="text-xs text-slate-200 line-clamp-2 leading-relaxed font-sans">{mem.content}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Sub-panel 2: KNOWLEDGE GRAPH */}
        {(activeTab === 'all' || activeTab === 'knowledge') && (
          <div className="space-y-3 p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Network className="w-4 h-4 text-blue-400" />
                <h4 className="text-xs font-bold text-slate-100 uppercase tracking-wider font-sans">
                  Knowledge Graph
                </h4>
              </div>
              <span className="text-[10px] font-mono text-blue-300 font-bold">12,480 Entities</span>
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
              <div className="text-[11px] font-mono font-semibold text-slate-400">
                Recent Graph Updates ({filteredKnowledge.length})
              </div>
              {filteredKnowledge.length === 0 ? (
                <div className="p-4 text-center text-xs font-mono text-slate-500">
                  No relationships match search.
                </div>
              ) : (
                filteredKnowledge.map((item, idx) => (
                  <div key={idx} className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1 text-xs">
                    <div className="flex items-center justify-between font-mono text-[10px]">
                      <span className="text-slate-200 font-bold">{item.entity}</span>
                      <span className="text-slate-500">{item.time}</span>
                    </div>
                    <div className="flex items-center space-x-1.5 font-mono text-[11px] text-slate-400">
                      <span className="text-cyan-400">{item.relation}</span>
                      <Share2 className="w-3 h-3 text-slate-600 shrink-0" />
                      <span className="text-purple-300 truncate">{item.target}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MemoryActivityWidget;
