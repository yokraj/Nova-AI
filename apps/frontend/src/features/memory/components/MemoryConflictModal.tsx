import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, X } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MemoryConflictItem } from '../types/memory';

interface MemoryConflictModalProps {
  conflict: MemoryConflictItem | null;
  onClose: () => void;
  onResolve: (resolution: 'keep_a' | 'keep_b' | 'keep_both') => void;
  className?: string;
}

export const MemoryConflictModal: React.FC<MemoryConflictModalProps> = ({
  conflict,
  onClose,
  onResolve,
  className,
}) => {
  if (!conflict) return null;

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
          className={cn('w-full max-w-xl bg-slate-950 border border-amber-500/40 rounded-3xl p-6 space-y-4 text-xs font-mono shadow-2xl text-slate-100', className)}
        >
          <div className="flex items-center justify-between border-b border-amber-500/20 pb-3">
            <div className="flex items-center space-x-2 text-amber-300 font-extrabold">
              <ShieldAlert className="w-4 h-4 text-amber-400 animate-pulse" />
              <span className="uppercase tracking-wider">CONFLICT DETECTED • {conflict.topic}</span>
            </div>
            <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200">
              <X className="w-4 h-4" />
            </button>
          </div>

          <p className="text-xs font-sans text-slate-300">
            Nova detected contradictory memory records. Select which information Nova should retain in future reasoning:
          </p>

          {/* Option A vs Option B Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
            <div className="p-3.5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-2">
              <div className="text-[11px] font-bold text-cyan-300 uppercase">Memory A (Original)</div>
              <h5 className="font-sans font-bold text-slate-100 text-xs">{conflict.memoryA.title}</h5>
              <p className="text-[11px] text-slate-400 font-sans">{conflict.memoryA.summary}</p>
              <button
                onClick={() => onResolve('keep_a')}
                className="w-full py-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 font-bold transition-all cursor-pointer"
              >
                Keep Memory A
              </button>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-2">
              <div className="text-[11px] font-bold text-purple-300 uppercase">Memory B (Newer)</div>
              <h5 className="font-sans font-bold text-slate-100 text-xs">{conflict.memoryB.title}</h5>
              <p className="text-[11px] text-slate-400 font-sans">{conflict.memoryB.summary}</p>
              <button
                onClick={() => onResolve('keep_b')}
                className="w-full py-1.5 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 font-bold transition-all cursor-pointer"
              >
                Keep Memory B
              </button>
            </div>
          </div>

          <div className="pt-2 flex justify-center">
            <button
              onClick={() => onResolve('keep_both')}
              className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 font-bold transition-all cursor-pointer"
            >
              Keep Both as Contextual Variations
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default MemoryConflictModal;
