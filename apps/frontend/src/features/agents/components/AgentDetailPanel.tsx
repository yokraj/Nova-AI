import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Bot, Shield, Wrench, Brain, Play } from 'lucide-react';
import { cn } from '@/utils/cn';
import { AgentItem } from '../types/agent';
import AgentStatusBadge from './AgentStatusBadge';

interface AgentDetailPanelProps {
  agent: AgentItem | null;
  onClose: () => void;
  onStartTask?: (agentId: string) => void;
  className?: string;
}

export const AgentDetailPanel: React.FC<AgentDetailPanelProps> = ({
  agent,
  onClose,
  onStartTask,
  className,
}) => {
  if (!agent) return null;

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
          className={cn('w-full max-w-2xl bg-slate-950 border border-slate-800 rounded-3xl p-6 space-y-5 text-xs font-mono shadow-2xl text-slate-100 max-h-[90vh] overflow-y-auto', className)}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Bot className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold font-sans text-slate-100">{agent.name}</h3>
                <span className="text-[11px] text-purple-300">{agent.domain} Domain • Model: {agent.model}</span>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <AgentStatusBadge status={agent.status} />
              <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          <p className="text-xs font-sans text-slate-300 leading-relaxed p-3 rounded-2xl bg-slate-900/80 border border-slate-800">
            {agent.description}
          </p>

          {/* Performance Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-[10px] text-slate-500">Tasks Completed</div>
              <div className="font-bold text-cyan-300 text-sm">{agent.performance.tasksCompleted}</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-[10px] text-slate-500">Success Rate</div>
              <div className="font-bold text-emerald-400 text-sm">{Math.round(agent.performance.successRate * 100)}%</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-[10px] text-slate-500">Avg Duration</div>
              <div className="font-bold text-purple-300 text-sm">{agent.performance.averageDurationSeconds}s</div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-[10px] text-slate-500">Workload</div>
              <div className="font-bold text-amber-300 text-sm">{agent.performance.currentWorkload}%</div>
            </div>
          </div>

          {/* Permissions Matrix */}
          <div className="space-y-2 pt-1">
            <div className="flex items-center space-x-1.5 text-slate-300 font-bold">
              <Shield className="w-4 h-4 text-cyan-400" />
              <span>Permission Security Matrix</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {Object.entries(agent.permissions).map(([permKey, isAllowed]) => (
                <div key={permKey} className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-[10px]">
                  <span className="capitalize text-slate-300">{permKey.replace(/([A-Z])/g, ' $1')}</span>
                  <span className={cn('font-bold', isAllowed ? 'text-emerald-400' : 'text-rose-400')}>
                    {isAllowed ? '✓ ALLOWED' : '✕ DENIED'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Tools & Capabilities */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            <div className="space-y-1.5">
              <div className="flex items-center space-x-1.5 text-slate-300 font-bold">
                <Wrench className="w-4 h-4 text-cyan-400" />
                <span>Authorized Tools</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {agent.tools.map((tool, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded-md bg-slate-900 text-cyan-300 border border-slate-800 text-[10px]">
                    {tool}
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center space-x-1.5 text-slate-300 font-bold">
                <Brain className="w-4 h-4 text-purple-400" />
                <span>Specialized Capabilities</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {agent.capabilities.map((cap, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded-md bg-slate-900 text-purple-300 border border-slate-800 text-[10px]">
                    {cap}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Footer Action */}
          <div className="flex items-center justify-between pt-3 border-t border-slate-800">
            <span className="text-[10px] text-slate-500">Created: {agent.createdAt}</span>
            {onStartTask && (
              <button
                onClick={() => {
                  onStartTask(agent.id);
                  onClose();
                }}
                className="px-4 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1.5"
              >
                <Play className="w-4 h-4" />
                <span>Assign Task to Agent</span>
              </button>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AgentDetailPanel;
