import React from 'react';
import { History, Search, FileCheck, Brain, ShieldCheck, Workflow } from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard } from '@/components/cards/Cards';
import { MOCK_ACTIVITY_TIMELINE } from '@/mock/mockDashboardData';

const iconMap: Record<string, React.ElementType> = {
  Search,
  FileCheck,
  Brain,
  ShieldCheck,
  Workflow,
};

export const ActivityTimelineWidget: React.FC<{ className?: string }> = ({ className }) => {
  const activities = MOCK_ACTIVITY_TIMELINE;

  return (
    <GlassCard className={cn('p-5 space-y-4', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <History className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Recent System Activity Stream
            </h3>
            <p className="text-xs text-slate-400">Audit timeline of agent actions, memory indexing & automation</p>
          </div>
        </div>
      </div>

      {/* Timeline Stream List */}
      <div className="relative pl-6 space-y-4 border-l border-slate-800">
        {activities.map((act) => {
          const Icon = iconMap[act.icon] || History;
          return (
            <div key={act.id} className="relative group">
              {/* Dot Icon Indicator on Timeline Axis */}
              <div className="absolute -left-[31px] top-0.5 p-1 rounded-full bg-slate-900 border border-cyan-500/40 text-cyan-400 group-hover:border-cyan-400 transition-all">
                <Icon className="w-3.5 h-3.5" />
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition-all space-y-1">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-100">{act.title}</h4>
                  <span className="text-[10px] font-mono text-slate-500">{act.timestamp}</span>
                </div>
                <p className="text-xs text-slate-400 font-sans leading-relaxed">{act.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </GlassCard>
  );
};

export default ActivityTimelineWidget;
