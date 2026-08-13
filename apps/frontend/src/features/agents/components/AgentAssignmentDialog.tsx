import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Sparkles, Check, X } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MOCK_AGENT_WORKFORCE } from '../mock/mockAgentData';

interface AgentAssignmentDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirmAssignment: (agentId: string, taskTitle: string) => void;
  className?: string;
}

export const AgentAssignmentDialog: React.FC<AgentAssignmentDialogProps> = ({
  isOpen,
  onClose,
  onConfirmAssignment,
  className,
}) => {
  const [taskTitle, setTaskTitle] = useState('Research offline LLM vector store indexing strategies');
  const [selectedAgentId, setSelectedAgentId] = useState<string>(MOCK_AGENT_WORKFORCE[0].id);

  if (!isOpen) return null;

  const recommended = MOCK_AGENT_WORKFORCE.find((a) => a.id === selectedAgentId) || MOCK_AGENT_WORKFORCE[0];

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
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span className="uppercase tracking-wider">NOVA AGENT ASSIGNMENT</span>
            </div>
            <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] text-slate-400 uppercase font-bold">Task Objective</label>
            <input
              type="text"
              value={taskTitle}
              onChange={(e) => setTaskTitle(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-sans focus:outline-none focus:border-cyan-500/50"
            />
          </div>

          {/* Recommended Agent Box */}
          <div className="p-4 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 space-y-2">
            <div className="flex items-center justify-between text-[11px] text-cyan-300 font-bold">
              <span>RECOMMENDED BY NOVA</span>
              <span>Match: 98%</span>
            </div>
            <div className="flex items-center space-x-2">
              <Bot className="w-5 h-5 text-cyan-400" />
              <span className="font-bold text-slate-100 font-sans text-sm">{recommended.name}</span>
            </div>
            <p className="text-[11px] font-sans text-slate-300">
              Reason: Requires web search, memory synthesis, and structural benchmark compilation.
            </p>
          </div>

          {/* Select Alternate Agent */}
          <div className="space-y-1.5">
            <label className="text-[10px] text-slate-400 uppercase font-bold">Or Select Specialized Agent</label>
            <select
              value={selectedAgentId}
              onChange={(e) => setSelectedAgentId(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-sans focus:outline-none"
            >
              {MOCK_AGENT_WORKFORCE.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.domain})
                </option>
              ))}
            </select>
          </div>

          {/* Confirm Actions */}
          <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
            <button onClick={onClose} className="px-3.5 py-2 rounded-xl bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800 font-bold transition-all cursor-pointer">
              Cancel
            </button>
            <button
              onClick={() => {
                onConfirmAssignment(selectedAgentId, taskTitle);
                onClose();
              }}
              className="px-4 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1"
            >
              <Check className="w-4 h-4" />
              <span>Assign Task</span>
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AgentAssignmentDialog;
