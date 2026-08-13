import React, { useState } from 'react';
import { Brain, Search, Clock, ShieldAlert } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MOCK_MEMORY_ITEMS_EXTENDED, MOCK_MEMORY_CONFLICTS } from '../mock/mockMemoryData';
import { MemoryItem, MemoryConflictItem } from '../types/memory';
import MemoryItemCard from './MemoryItemCard';
import MemoryTimeline from './MemoryTimeline';
import MemoryDetailModal from './MemoryDetailModal';
import MemoryConflictModal from './MemoryConflictModal';

export const MemoryWorkspace: React.FC = () => {
  const [memories, setMemories] = useState<MemoryItem[]>(MOCK_MEMORY_ITEMS_EXTENDED);
  const [conflicts, setConflicts] = useState<MemoryConflictItem[]>(MOCK_MEMORY_CONFLICTS);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'timeline'>('grid');
  const [activeItem, setActiveItem] = useState<MemoryItem | null>(null);
  const [activeConflict, setActiveConflict] = useState<MemoryConflictItem | null>(null);

  const categories = ['all', 'Decision', 'Architecture', 'Technology', 'Requirement'];

  const filtered = memories.filter((m) => {
    const matchesSearch =
      m.title.toLowerCase().includes(search.toLowerCase()) ||
      m.summary.toLowerCase().includes(search.toLowerCase()) ||
      m.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()));

    const matchesCategory = selectedCategory === 'all' || m.type === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  const handleForget = (id: string) => {
    setMemories((prev) => prev.filter((m) => m.id !== id));
  };

  const handlePin = (id: string) => {
    setMemories((prev) =>
      prev.map((m) => {
        if (m.id === id) {
          const nextStatus = m.status === 'pinned' ? 'active' : 'pinned';
          return { ...m, status: nextStatus };
        }
        return m;
      })
    );
  };

  const handleResolveConflict = (resolution: string) => {
    if (!activeConflict) return;
    setConflicts((prev) => prev.filter((c) => c.id !== activeConflict.id));
    if (resolution === 'keep_a') {
      setMemories((prev) => [activeConflict.memoryA, ...prev]);
    } else if (resolution === 'keep_b') {
      setMemories((prev) => [activeConflict.memoryB, ...prev]);
    } else {
      setMemories((prev) => [activeConflict.memoryA, activeConflict.memoryB, ...prev]);
    }
    setActiveConflict(null);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header Stat Panel */}
      <div className="p-6 rounded-3xl bg-slate-900/90 border border-purple-500/30 flex flex-col md:flex-row items-center justify-between gap-4 shadow-2xl">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Brain className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Nova Memory Store</h1>
            <p className="text-xs text-slate-400 font-mono">
              Semantic vector store & indexed workspace context • 142,850 stored vectors
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs">
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-cyan-400 font-bold">43</span> Decisions
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-purple-400 font-bold">18</span> Requirements
          </div>
        </div>
      </div>

      {/* Conflict Alert Banner (If pending conflicts exist) */}
      {conflicts.length > 0 && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 font-mono text-xs flex items-center justify-between">
          <div className="flex items-center space-x-2 text-amber-300 font-bold">
            <ShieldAlert className="w-4 h-4 text-amber-400 animate-pulse" />
            <span>{conflicts.length} Memory Conflict(s) Detected</span>
          </div>
          <button
            onClick={() => setActiveConflict(conflicts[0])}
            className="px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 font-bold transition-all cursor-pointer"
          >
            Resolve Conflict
          </button>
        </div>
      )}

      {/* Search & Category Filter Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search Nova's memory (e.g. 'frontend decisions')..."
            className="w-full bg-slate-950 border border-slate-800 rounded-2xl py-2 pl-9 pr-4 text-xs text-slate-100 placeholder-slate-500 font-sans focus:outline-none focus:border-cyan-500/50"
          />
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs">
          <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={cn(
                  'px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer capitalize',
                  selectedCategory === cat
                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                )}
              >
                {cat}
              </button>
            ))}
          </div>

          <button
            onClick={() => setViewMode(viewMode === 'grid' ? 'timeline' : 'grid')}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-cyan-300 transition-all cursor-pointer"
            title="Toggle Grid / Timeline View"
          >
            <Clock className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Memory Content Display */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((item) => (
            <MemoryItemCard
              key={item.id}
              item={item}
              onSelect={() => setActiveItem(item)}
              onForget={handleForget}
              onPin={handlePin}
            />
          ))}
        </div>
      ) : (
        <MemoryTimeline items={filtered} onSelect={(item) => setActiveItem(item)} />
      )}

      {/* Modals */}
      <MemoryDetailModal item={activeItem} onClose={() => setActiveItem(null)} onForget={handleForget} />

      <MemoryConflictModal
        conflict={activeConflict}
        onClose={() => setActiveConflict(null)}
        onResolve={handleResolveConflict}
      />
    </div>
  );
};

export default MemoryWorkspace;
