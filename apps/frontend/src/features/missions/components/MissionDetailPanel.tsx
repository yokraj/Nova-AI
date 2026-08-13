import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Target, Play, Pause, RefreshCw } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MissionItem } from '../types/mission';
import { MissionTask } from '../types/missionTask';
import MissionStatusBadge from './MissionStatusBadge';
import MissionTimeline from './MissionTimeline';
import MissionTaskGraph from './MissionTaskGraph';

interface MissionDetailPanelProps {
  mission: MissionItem | null;
  tasks: MissionTask[];
  onClose: () => void;
  onPause: (id: string) => void;
  onResume: (id: string) => void;
  onCancel: (id: string) => void;
  onReplan?: (id: string) => void;
  className?: string;
}

export const MissionDetailPanel: React.FC<MissionDetailPanelProps> = ({
  mission,
  tasks,
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
              <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Goal & Outcome */}
          <p className="text-xs font-sans text-slate-300 leading-relaxed p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800">
            {mission.goal}
          </p>

          {/* Mission Progress Timeline */}
          <MissionTimeline status={mission.status} />

          {/* Mission Task DAG Graph */}
          <MissionTaskGraph tasks={tasks} />

          {/* Controls Footer */}
          <div className="flex items-center justify-between pt-3 border-t border-slate-800">
            <div className="flex items-center space-x-2">
              {mission.status === 'EXECUTING' && (
                <button
                  onClick={() => onPause(mission.id)}
                  className="px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white font-bold transition-all cursor-pointer flex items-center space-x-1"
                >
                  <Pause className="w-3.5 h-3.5" />
                  <span>Pause</span>
                </button>
              )}

              {mission.status === 'PAUSED' && (
                <button
                  onClick={() => onResume(mission.id)}
                  className="px-3.5 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Resume</span>
                </button>
              )}

              {onReplan && (
                <button
                  onClick={() => onReplan(mission.id)}
                  className="px-3.5 py-1.5 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Replan Mission</span>
                </button>
              )}
            </div>

            <button
              onClick={() => onCancel(mission.id)}
              className="px-3.5 py-1.5 rounded-xl bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold transition-all cursor-pointer"
            >
              Cancel Mission
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default MissionDetailPanel;
