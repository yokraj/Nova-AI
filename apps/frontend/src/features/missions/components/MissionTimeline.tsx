import React from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MissionStatus } from '../types/mission';

interface MissionTimelineProps {
  status: MissionStatus;
  className?: string;
}

export const MissionTimeline: React.FC<MissionTimelineProps> = ({ status, className }) => {
  const stages = [
    { label: 'UNDERSTANDING', completed: true },
    { label: 'PLANNING', completed: true },
    { label: 'APPROVAL', completed: true },
    { label: 'EXECUTION', active: status === 'EXECUTING' || status === 'PLANNING' },
    { label: 'VERIFICATION', completed: status === 'COMPLETED' },
    { label: 'DELIVERY', completed: status === 'COMPLETED' },
  ];

  return (
    <div className={cn('flex items-center justify-between font-mono text-xs p-4 rounded-2xl bg-slate-950 border border-slate-800 overflow-x-auto', className)}>
      {stages.map((st, idx) => (
        <div key={idx} className="flex items-center space-x-2 shrink-0">
          <div
            className={cn(
              'w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] border',
              st.completed
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                : st.active
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 animate-pulse shadow-[0_0_10px_rgba(0,240,255,0.4)]'
                : 'bg-slate-900 text-slate-500 border-slate-800'
            )}
          >
            {st.completed ? <Check className="w-3.5 h-3.5" /> : idx + 1}
          </div>
          <span className={cn('text-[11px] font-bold', st.active ? 'text-cyan-300' : st.completed ? 'text-slate-200' : 'text-slate-500')}>
            {st.label}
          </span>
          {idx < stages.length - 1 && <span className="text-slate-700 font-bold mx-1.5">──</span>}
        </div>
      ))}
    </div>
  );
};

export default MissionTimeline;
