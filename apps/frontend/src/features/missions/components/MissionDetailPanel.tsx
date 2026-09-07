import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Target, Play, Pause, RefreshCw, XCircle } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MissionItem } from '../types/mission.js';
import { MissionTask } from '../types/missionTask.js';
import MissionStatusBadge from './MissionStatusBadge.js';
import MissionTimeline from './MissionTimeline.js';
import MissionTaskGraph from './MissionTaskGraph.js';

interface MissionDetailPanelProps {
  mission: MissionItem | null;
  tasks?: MissionTask[];
  onClose: () => void;
  onPause: (id: string) => void;
  onResume: (id: string) => void;
  onCancel: (id: string) => void;
  onReplan?: (id: string) => void;
  className?: string;
}

export const MissionDetailPanel: React.FC<MissionDetailPanelProps> = ({
  mission,
  tasks = [],
  onClose,
  onPause,
  onResume,
  onCancel,
  onReplan,
  className,
}) => {
  if (!mission) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className={cn('w-full max-w-3xl bg-slate-950 border border-slate-800 rounded-3xl p-6 space-y-5 text-xs font-mono shadow-2xl text-slate-100 max-h-[90vh] overflow-y-auto', className)}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Target className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold font-sans text-slate-100">{mission.title}</h3>
                <span className="text-[11px] text-purple-300">Autonomy Level: {mission.autonomyLevel}</span>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <MissionStatusBadge status={mission.status} />
              <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 cursor-pointer">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Goal & Description */}
          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <div className="text-[10px] text-slate-400 font-bold uppercase">Mission Goal</div>
            <p className="text-xs text-slate-200 font-sans leading-relaxed">{mission.goal}</p>
          </div>

          {/* Action Bar */}
          <div className="flex items-center space-x-2 pt-1">
            {mission.status === 'EXECUTING' && (
              <button
                onClick={() => onPause(mission.id)}
                className="px-3.5 py-1.5 rounded-xl bg-yellow-500/20 text-yellow-300 border border-yellow-500/30 font-bold flex items-center space-x-1.5 hover:bg-yellow-500/30 transition-all cursor-pointer"
              >
                <Pause className="w-3.5 h-3.5" />
                <span>Pause Mission</span>
              </button>
            )}

            {mission.status === 'PAUSED' && (
              <button
                onClick={() => onResume(mission.id)}
                className="px-3.5 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold flex items-center space-x-1.5 hover:bg-emerald-500/30 transition-all cursor-pointer"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Resume Mission</span>
              </button>
            )}

            {onReplan && (
              <button
                onClick={() => onReplan(mission.id)}
                className="px-3.5 py-1.5 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold flex items-center space-x-1.5 hover:bg-purple-500/30 transition-all cursor-pointer"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Trigger Replan</span>
              </button>
            )}

            <button
              onClick={() => onCancel(mission.id)}
              className="px-3.5 py-1.5 rounded-xl bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold flex items-center space-x-1.5 hover:bg-rose-500/30 transition-all cursor-pointer"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>Cancel Mission</span>
            </button>
          </div>

          {/* DAG Task Graph & Timeline */}
          {tasks.length > 0 && (
            <div className="space-y-3">
              <div className="text-[11px] font-bold text-cyan-400 uppercase">Execution Task Graph</div>
              <MissionTaskGraph tasks={tasks} />
            </div>
          )}

          <div className="space-y-3 pt-2">
            <div className="text-[11px] font-bold text-purple-300 uppercase">Mission Timeline Logs</div>
            <MissionTimeline status={mission.status} />
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default MissionDetailPanel;
