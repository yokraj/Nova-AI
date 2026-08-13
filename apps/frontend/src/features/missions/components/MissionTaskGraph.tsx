import React from 'react';
import { motion } from 'framer-motion';
import { Network, ArrowRight } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MissionTask } from '../types/missionTask';

interface MissionTaskGraphProps {
  tasks: MissionTask[];
  onSelectTask?: (task: MissionTask) => void;
  className?: string;
}

export const MissionTaskGraph: React.FC<MissionTaskGraphProps> = ({
  tasks,
  onSelectTask,
  className,
}) => {
  return (
    <div className={cn('p-5 rounded-3xl bg-slate-950 border border-slate-800 space-y-4 shadow-2xl font-mono text-xs', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2 text-cyan-300 font-extrabold">
          <Network className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span className="uppercase tracking-wider">AUTONOMOUS MISSION TASK DAG</span>
        </div>
        <span className="text-slate-400 text-[10px]">{tasks.length} Nodes Rendered</span>
      </div>

      {/* Visual DAG Flow Stream */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-3 overflow-x-auto py-4 px-2">
        {tasks.map((t, idx) => {
          const isDone = t.status === 'COMPLETED';
          const isRunning = t.status === 'RUNNING';
          const isBlocked = t.status === 'BLOCKED';

          return (
            <React.Fragment key={t.id}>
              <motion.div
                whileHover={{ scale: 1.03 }}
                onClick={() => onSelectTask?.(t)}
                className={cn(
                  'p-3.5 rounded-2xl border transition-all cursor-pointer space-y-1.5 min-w-[180px] max-w-[220px]',
                  isDone
                    ? 'bg-slate-900 border-emerald-500/40 text-slate-200'
                    : isRunning
                    ? 'bg-slate-900 border-cyan-400 text-slate-100 shadow-[0_0_15px_rgba(0,240,255,0.2)]'
                    : 'bg-slate-950 border-slate-800 text-slate-400'
                )}
              >
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold uppercase text-purple-300">{t.assignedAgentName.split(' ')[0]}</span>
                  <span
                    className={cn(
                      'font-bold uppercase',
                      isDone ? 'text-emerald-400' : isRunning ? 'text-cyan-300 animate-pulse' : 'text-slate-500'
                    )}
                  >
                    {t.status}
                  </span>
                </div>
                <div className="font-sans font-bold text-xs truncate">{t.title}</div>
                <div className="text-[10px] text-slate-400 truncate">{t.description}</div>
              </motion.div>

              {idx < tasks.length - 1 && (
                <div className="text-slate-600 flex items-center justify-center">
                  <ArrowRight className="w-4 h-4 text-cyan-400/60 hidden md:block" />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

export default MissionTaskGraph;
