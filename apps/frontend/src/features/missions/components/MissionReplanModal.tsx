import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, ArrowRight, X } from 'lucide-react';
import { cn } from '@/utils/cn';

interface MissionReplanModalProps {
  isOpen: boolean;
  failedTaskTitle?: string;
  missionTitle?: string;
  failureReason: string;
  proposedPlan?: string[];
  onConfirmReplan: () => void;
  onClose?: () => void;
  onCancel?: () => void;
  className?: string;
}

export const MissionReplanModal: React.FC<MissionReplanModalProps> = ({
  isOpen,
  failedTaskTitle,
  missionTitle,
  failureReason,
  proposedPlan = ['Re-evaluate target state', 'Apply alternative tool strategy', 'Resume execution'],
  onConfirmReplan,
  onClose,
  onCancel,
  className,
}) => {
  if (!isOpen) return null;

  const handleClose = onClose || onCancel || (() => {});
  const displayTitle = failedTaskTitle || missionTitle || 'Mission Task Execution';

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className={cn('w-full max-w-lg bg-slate-950 border border-purple-500/40 rounded-3xl p-6 space-y-4 text-xs font-mono shadow-2xl text-slate-100', className)}
        >
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2 text-purple-300 font-extrabold">
              <RefreshCw className="w-4 h-4 text-purple-400 animate-spin" />
              <span className="uppercase tracking-wider">NOVA AUTONOMOUS REPLANNING</span>
            </div>
            <button onClick={handleClose} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 cursor-pointer">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="p-3 rounded-2xl bg-rose-500/10 border border-rose-500/30 space-y-1">
            <div className="text-[10px] text-rose-300 font-bold uppercase">Task Failed: {displayTitle}</div>
            <p className="text-xs font-sans text-slate-300">{failureReason}</p>
          </div>

          {/* Replanning Visual Stream */}
          <div className="p-4 rounded-2xl bg-slate-900/90 border border-purple-500/30 space-y-3">
            <div className="text-[11px] font-bold text-purple-300 uppercase">NOVA REPLANNING FLOW</div>

            <div className="space-y-1.5 pt-1">
              {proposedPlan.map((step, idx) => (
                <div key={idx} className="flex items-center space-x-2 text-[11px] text-slate-300">
                  <ArrowRight className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
            <button
              onClick={handleClose}
              className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-slate-100 font-bold cursor-pointer transition-all"
            >
              Cancel
            </button>
            <button
              onClick={onConfirmReplan}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-600 text-slate-950 font-bold flex items-center space-x-1.5 shadow-[0_0_15px_rgba(168,85,247,0.3)] hover:scale-[1.02] cursor-pointer transition-all"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Confirm & Resume Replan</span>
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default MissionReplanModal;
