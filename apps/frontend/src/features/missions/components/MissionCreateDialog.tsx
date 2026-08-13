import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Target, Sparkles, X } from 'lucide-react';
import { cn } from '@/utils/cn';
import { AutonomyLevel } from '../types/mission';

interface MissionCreateDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateMission: (goal: string, autonomyLevel: AutonomyLevel) => void;
  className?: string;
}

export const MissionCreateDialog: React.FC<MissionCreateDialogProps> = ({
  isOpen,
  onClose,
  onCreateMission,
  className,
}) => {
  const [goal, setGoal] = useState('Build a complete portfolio website for my business.');
  const [autonomyLevel, setAutonomyLevel] = useState<AutonomyLevel>('SUPERVISED');

  if (!isOpen) return null;

  const autonomyDescriptions: Record<AutonomyLevel, { title: string; sub: string }> = {
    ASSISTED: { title: 'Assisted Autonomy', sub: 'Nova asks before major actions and confirms every step.' },
    SUPERVISED: { title: 'Supervised Autonomy (Recommended)', sub: 'Nova executes routine tasks automatically and requests approval for sensitive actions.' },
    AUTONOMOUS: { title: 'Autonomous Mode', sub: 'Nova executes complete DAG missions within predefined system permissions.' },
  };

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
          className={cn('w-full max-w-lg bg-slate-950 border border-cyan-500/40 rounded-3xl p-6 space-y-4 text-xs font-mono shadow-2xl text-slate-100', className)}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2 text-cyan-300 font-extrabold">
              <Target className="w-4 h-4 text-cyan-400" />
              <span className="uppercase tracking-wider">NEW AUTONOMOUS MISSION</span>
            </div>
            <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] text-slate-400 uppercase font-bold">What would you like Nova to accomplish?</label>
            <textarea
              rows={3}
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="e.g. 'Build a complete website', 'Research local LLMs', 'Analyze my repository'..."
              className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-3 text-xs text-slate-100 font-sans focus:outline-none focus:border-cyan-500/50 leading-relaxed resize-none"
            />
          </div>

          {/* Autonomy Level Radio Group */}
          <div className="space-y-2 pt-1">
            <label className="text-[10px] text-slate-400 uppercase font-bold">Select Autonomy Level</label>
            <div className="space-y-2">
              {(['ASSISTED', 'SUPERVISED', 'AUTONOMOUS'] as AutonomyLevel[]).map((level) => {
                const info = autonomyDescriptions[level];
                const isSelected = autonomyLevel === level;
                return (
                  <div
                    key={level}
                    onClick={() => setAutonomyLevel(level)}
                    className={cn(
                      'p-3 rounded-2xl border transition-all cursor-pointer space-y-0.5',
                      isSelected
                        ? 'bg-cyan-500/10 border-cyan-500 text-slate-100 shadow-[0_0_15px_rgba(0,240,255,0.15)]'
                        : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
                    )}
                  >
                    <div className="font-bold text-xs">{info.title}</div>
                    <div className="text-[10px] font-sans text-slate-400">{info.sub}</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
            <button onClick={onClose} className="px-3.5 py-2 rounded-xl bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800 font-bold transition-all cursor-pointer">
              Cancel
            </button>
            <button
              onClick={() => {
                onCreateMission(goal, autonomyLevel);
                onClose();
              }}
              className="px-4 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1"
            >
              <Sparkles className="w-4 h-4" />
              <span>Start Autonomous Mission</span>
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default MissionCreateDialog;
