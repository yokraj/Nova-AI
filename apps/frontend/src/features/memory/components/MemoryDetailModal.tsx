import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Brain, Trash2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MemoryItem } from '../types/memory';

interface MemoryDetailModalProps {
  item: MemoryItem | null;
  onClose: () => void;
  onForget: (id: string) => void;
  className?: string;
}

export const MemoryDetailModal: React.FC<MemoryDetailModalProps> = ({
  item,
  onClose,
  onForget,
  className,
}) => {
  if (!item) return null;

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
          className={cn('w-full max-w-xl bg-slate-950 border border-slate-800 rounded-3xl p-6 space-y-4 text-xs font-mono shadow-2xl text-slate-100', className)}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2 text-cyan-300 font-extrabold">
              <Brain className="w-4 h-4 text-cyan-400" />
              <span className="uppercase tracking-wider">MEMORY DETAIL ({item.type})</span>
            </div>
            <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200">
              <X className="w-4 h-4" />
            </button>
          </div>

          <h3 className="text-base font-bold font-sans text-slate-100">{item.title}</h3>

          <p className="text-xs font-sans text-slate-300 leading-relaxed p-3 rounded-2xl bg-slate-900/80 border border-slate-800">
            {item.content}
          </p>

          {/* Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2">
            <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="text-[10px] text-slate-500">Source Origin</div>
              <div className="font-bold text-cyan-300">{item.source.origin}</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="text-[10px] text-slate-500">Importance</div>
              <div className="font-bold text-purple-300">{item.importance}</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="text-[10px] text-slate-500">Confidence</div>
              <div className="font-bold text-emerald-400">{Math.round(item.confidence * 100)}%</div>
            </div>
          </div>

          {/* Tags */}
          <div className="flex items-center space-x-1.5 flex-wrap pt-1">
            <span className="text-[10px] text-slate-500 uppercase font-bold">Tags:</span>
            {item.tags.map((t, idx) => (
              <span key={idx} className="px-2 py-0.5 rounded-md bg-slate-900 text-slate-300 border border-slate-800 text-[10px]">
                #{t}
              </span>
            ))}
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-between pt-3 border-t border-slate-800">
            <div className="text-[10px] text-slate-500">Workspace: {item.workspace}</div>
            <button
              onClick={() => {
                onForget(item.id);
                onClose();
              }}
              className="px-3.5 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Forget Memory</span>
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default MemoryDetailModal;
