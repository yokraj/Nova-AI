import React, { useState, useMemo } from 'react';
import {
  MessageSquarePlus,
  Mic,
  Search,
  FileText,
  FileSearch,
  Play,
  Terminal,
  Users,
  Brain,
  Network,
  Laptop,
  Workflow,
  Zap,
  Filter,
  X,
  CheckCircle2,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { QuickActionItem } from '@/types/dashboard';
import { MOCK_QUICK_ACTIONS } from '@/mock/mockDashboardData';

const iconMap: Record<string, React.ElementType> = {
  MessageSquarePlus,
  Mic,
  Search,
  FileText,
  FileSearch,
  Play,
  Terminal,
  Users,
  Brain,
  Network,
  Laptop,
  Workflow,
  Zap,
};

export interface QuickActionsWidgetProps {
  onSelectAction?: (commandSuggestion: string) => void;
  className?: string;
  actions?: QuickActionItem[];
}

export const QuickActionsWidget: React.FC<QuickActionsWidgetProps> = ({
  onSelectAction,
  className,
  actions = MOCK_QUICK_ACTIONS,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'create' | 'run' | 'navigate'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const filteredActions = useMemo(() => {
    return actions.filter((act) => {
      const matchesCategory = selectedCategory === 'all' || act.category === selectedCategory;
      const matchesSearch =
        act.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        act.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [actions, selectedCategory, searchQuery]);

  const handleActionClick = (action: QuickActionItem) => {
    if (action.commandSuggestion) {
      setToastMessage(`Routing action: "${action.title}" to Universal Command Core.`);
      setTimeout(() => setToastMessage(null), 3000);
      if (onSelectAction) {
        onSelectAction(action.commandSuggestion);
      }
    }
  };

  return (
    <div
      className={cn(
        'glass-panel p-5 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl space-y-4 shadow-xl select-none',
        className
      )}
    >
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800/80 pb-3 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 shrink-0">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
              Quick System Actions & Commands
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              One-click AI OS capabilities, macros & workspace shortcuts
            </p>
          </div>
        </div>

        {/* Status Pill */}
        <div className="flex items-center space-x-2 shrink-0">
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-mono font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            <span>{filteredActions.length} ACTIONS READY</span>
          </span>
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
            placeholder="Search shortcuts and actions..."
            className="w-full pl-9 pr-8 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/50 transition-all font-sans"
            aria-label="Search quick actions"
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
        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-[11px] font-mono overflow-x-auto scrollbar-none">
          <Filter className="w-3 h-3 text-slate-500 ml-1 mr-0.5 shrink-0" />
          {(['all', 'create', 'run', 'navigate'] as const).map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={cn(
                'px-2.5 py-1 rounded-lg uppercase tracking-wider transition-all cursor-pointer whitespace-nowrap',
                selectedCategory === cat
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              )}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Grid of Quick Action Cards */}
      {filteredActions.length === 0 ? (
        <div className="p-8 text-center rounded-2xl bg-slate-900/40 border border-slate-800/80 text-xs font-mono text-slate-500">
          No quick actions match the selected filter.
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
          {filteredActions.map((act) => {
            const Icon = iconMap[act.iconName] || Zap;
            return (
              <button
                key={act.id}
                onClick={() => handleActionClick(act)}
                className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 hover:border-cyan-500/50 hover:bg-slate-900 hover:shadow-[0_0_15px_rgba(0,240,255,0.15)] transition-all text-left group cursor-pointer flex flex-col justify-between space-y-2 focus:outline-none focus:ring-1 focus:ring-cyan-400"
              >
                <div className="flex items-center justify-between">
                  <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 group-hover:bg-cyan-500/20 group-hover:text-cyan-300 border border-cyan-500/20 transition-all shrink-0">
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase group-hover:text-cyan-400">
                    {act.category}
                  </span>
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-100 group-hover:text-cyan-300 transition-colors">
                    {act.title}
                  </div>
                  <div className="text-[11px] text-slate-400 truncate mt-0.5 font-sans leading-tight">
                    {act.description}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* Action Toast Feedback */}
      {toastMessage && (
        <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs font-mono flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-amber-400 shrink-0" />
            <span>{toastMessage}</span>
          </div>
          <button
            onClick={() => setToastMessage(null)}
            className="text-slate-400 hover:text-slate-200 text-xs cursor-pointer font-bold"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
};

export default QuickActionsWidget;
