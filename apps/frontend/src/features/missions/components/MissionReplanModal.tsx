import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, ArrowRight, X } from 'lucide-react';
import { cn } from '@/utils/cn';

interface MissionReplanModalProps {
  isOpen: boolean;
  failedTaskTitle: string;
  failureReason: string;
  onConfirmReplan: () => void;
  onClose: () => void;
  className?: string;
}

export const MissionReplanModal: React.FC<MissionReplanModalProps> = ({
  isOpen,
  failedTaskTitle,
  failureReason,
  onConfirmReplan,
  onClose,
  className,
}) => {
  if (!isOpen) return null;

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
            <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="p-3 rounded-2xl bg-rose-500/10 border border-rose-500/30 space-y-1">
            <div className="text-[10px] text-rose-300 font-bold uppercase">Task Failed: {failedTaskTitle}</div>
            <p className="text-xs font-sans text-slate-300">{failureReason}</p>
          </div>

          {/* Replanning Visual Stream */}
          <div className="p-4 rounded-2xl bg-slate-900/90 border border-purple-500/30 space-y-3">
            <div className="text-[11px] font-bold text-purple-300 uppercase">NOVA REPLANNING FLOW</div>

            <div className="flex items-center space-x-2">
              <span className="px-2 py-1 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">Failed Operation</span>
              <ArrowRight className="w-3.5 h-3.5 text-purple-400" />
              <span className="px-2 py-1 rounded-lg bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold">Nova Replanning Engine</span>
              <ArrowRight className="w-3.5 h-3.5 text-purple-400" />
              <span className="px-2 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">Alternative Plan</span>
            </div>

            <p className="text-[11px] font-sans text-slate-300 leading-relaxed pt-1">
              Nova will automatically bypass the unavailable credential dependency by preparing a local deployment artifact package.
            </p>
          </div>

          <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
            <button onClick={onClose} className="px-3.5 py-2 rounded-xl bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800 font-bold transition-all cursor-pointer">
              Cancel
            </button>
            <button
              onClick={onConfirmReplan}
              className="px-4 py-2 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Execute Alternative Plan</span>
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default MissionReplanModal;
