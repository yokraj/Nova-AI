import React from 'react';
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
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard } from '@/components/cards/Cards';
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
};

interface QuickActionsWidgetProps {
  onSelectAction?: (commandSuggestion: string) => void;
  className?: string;
}

export const QuickActionsWidget: React.FC<QuickActionsWidgetProps> = ({
  onSelectAction,
  className,
}) => {
  const actions = MOCK_QUICK_ACTIONS;

  return (
    <GlassCard className={cn('p-5 space-y-4', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Quick System Actions
            </h3>
            <p className="text-xs text-slate-400">One-click AI OS capabilities & workspace shortcuts</p>
          </div>
        </div>
      </div>

      {/* Grid of 12 Quick Action Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
        {actions.map((act) => {
          const Icon = iconMap[act.iconName] || Zap;
          return (
            <button
              key={act.id}
              onClick={() => act.commandSuggestion && onSelectAction?.(act.commandSuggestion)}
              className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 hover:border-cyan-500/50 hover:bg-slate-900 hover:shadow-[0_0_15px_rgba(0,240,255,0.15)] transition-all text-left group cursor-pointer flex flex-col justify-between space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 group-hover:bg-cyan-500/20 group-hover:text-cyan-300 border border-cyan-500/20 transition-all">
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
                <div className="text-[11px] text-slate-400 truncate mt-0.5">{act.description}</div>
              </div>
            </button>
          );
        })}
      </div>
    </GlassCard>
  );
};

export default QuickActionsWidget;
