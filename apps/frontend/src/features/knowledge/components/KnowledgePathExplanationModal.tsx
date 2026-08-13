import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Network, X, ArrowRight } from 'lucide-react';
import { cn } from '@/utils/cn';
import { KnowledgeEntity } from '../types/knowledge';

interface KnowledgePathExplanationModalProps {
  entity: KnowledgeEntity | null;
  onClose: () => void;
  className?: string;
}

export const KnowledgePathExplanationModal: React.FC<KnowledgePathExplanationModalProps> = ({
  entity,
  onClose,
  className,
}) => {
  if (!entity) return null;

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
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2 text-cyan-300 font-extrabold">
              <Network className="w-4 h-4 text-cyan-400" />
              <span className="uppercase tracking-wider">KNOWLEDGE PATH EXPLANATION</span>
            </div>
            <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-1">
            <h3 className="text-base font-bold font-sans text-slate-100">{entity.name}</h3>
            <p className="text-xs font-sans text-slate-300">{entity.description}</p>
          </div>

          {/* Visual Path Explanation Chain */}
          <div className="p-4 rounded-2xl bg-slate-900/90 border border-cyan-500/30 space-y-3">
            <div className="text-[11px] font-bold text-cyan-300 uppercase">WHY THESE ARE CONNECTED</div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <span className="px-2 py-1 rounded-lg bg-slate-950 text-slate-200 font-bold border border-slate-800">User Prompt</span>
                <ArrowRight className="w-3.5 h-3.5 text-cyan-400" />
                <span className="px-2 py-1 rounded-lg bg-slate-950 text-purple-300 font-bold border border-slate-800">Conversation Thread</span>
              </div>

              <div className="flex items-center space-x-2">
                <span className="px-2 py-1 rounded-lg bg-slate-950 text-purple-300 font-bold border border-slate-800">Conversation Thread</span>
                <ArrowRight className="w-3.5 h-3.5 text-cyan-400" />
                <span className="px-2 py-1 rounded-lg bg-slate-950 text-emerald-400 font-bold border border-slate-800">{entity.name} ({entity.type})</span>
              </div>
            </div>

            <p className="text-[11px] font-sans text-slate-400 leading-relaxed pt-1">
              This entity was indexed from conversation decisions and architectural blueprints. Nova uses this relationship path to inject grounding context during reasoning.
            </p>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-800">
            <span>Cluster: {entity.cluster}</span>
            <span>Importance: {entity.importance}/10</span>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default KnowledgePathExplanationModal;
