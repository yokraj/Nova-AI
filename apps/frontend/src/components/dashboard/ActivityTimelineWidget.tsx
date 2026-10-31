import React, { useState } from 'react';
import {
  History,
  FileCheck,
  Brain,
  ShieldCheck,
  Workflow,
  Cpu,
  Filter,
  Clock,
  Search,
  X,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { ActivityTimelineItem } from '@/types/dashboard';
import { MOCK_ACTIVITY_TIMELINE } from '@/mock/mockDashboardData';

const iconMap: Record<string, React.ElementType> = {
  Search,
  FileCheck,
  Brain,
  ShieldCheck,
  Workflow,
  Cpu,
};

interface ActivityTimelineWidgetProps {
  className?: string;
  activities?: ActivityTimelineItem[];
}

export const ActivityTimelineWidget: React.FC<ActivityTimelineWidgetProps> = ({
  className,
  activities = MOCK_ACTIVITY_TIMELINE,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const categories = ['all', 'agent', 'memory', 'security', 'automation'];

  const filteredActivities = activities.filter((act) => {
    const matchesCategory = selectedCategory === 'all' || act.category === selectedCategory;
    const matchesSearch =
      act.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      act.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

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
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shrink-0">
            <History className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
              Recent System Activity Stream
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Audit timeline of agent actions, memory indexing & automation
            </p>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div className="relative flex-1 max-w-sm">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search activity events..."
            className="w-full pl-9 pr-8 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 transition-all font-sans"
            aria-label="Search activities"
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

        {/* Category Filters */}
        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-[11px] font-mono">
          <Filter className="w-3 h-3 text-slate-500 ml-1 mr-0.5 shrink-0" />
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={cn(
                'px-2.5 py-1 rounded-lg uppercase tracking-wider transition-all cursor-pointer',
                selectedCategory === cat
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              )}
            >
              {cat === 'all' ? 'All' : cat}
            </button>
          ))}
        </div>
      </div>

      {/* Timeline Stream List */}
      {filteredActivities.length === 0 ? (
        <div className="p-8 text-center rounded-2xl bg-slate-900/40 border border-slate-800/80 text-xs font-mono text-slate-500">
          No audit activities found for category "{selectedCategory}".
        </div>
      ) : (
        <div className="relative pl-6 space-y-3.5 border-l border-slate-800 ml-2">
          {filteredActivities.map((act) => {
            const Icon = iconMap[act.icon] || History;
            return (
              <div key={act.id} className="relative group">
                {/* Dot Icon Indicator on Timeline Axis */}
                <div className="absolute -left-[31px] top-1 p-1 rounded-full bg-slate-900 border border-cyan-500/40 text-cyan-400 group-hover:border-cyan-400 group-hover:bg-cyan-500/10 transition-all">
                  <Icon className="w-3.5 h-3.5" />
                </div>

                <div className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition-all space-y-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-slate-100 group-hover:text-cyan-300 transition-colors">
                      {act.title}
                    </h4>
                    <span className="text-[10px] font-mono text-slate-500 flex items-center space-x-1 shrink-0">
                      <Clock className="w-3 h-3" />
                      <span>{act.timestamp}</span>
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 font-sans leading-relaxed">{act.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ActivityTimelineWidget;
