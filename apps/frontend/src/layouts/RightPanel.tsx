import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Activity,
  Cpu,
  CheckCircle2,
  Clock,
  Zap,
} from 'lucide-react';
import { MOCK_NOTIFICATIONS } from '@/mock/mockNotifications';

interface RightPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RightPanel: React.FC<RightPanelProps> = ({ isOpen, onClose }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.aside
          initial={{ x: 320, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 320, opacity: 0 }}
          transition={{ duration: 0.2, ease: 'easeInOut' }}
          className="fixed right-0 top-16 bottom-8 w-80 border-l border-zinc-800/80 bg-black/95 backdrop-blur-2xl p-4 overflow-y-auto space-y-4 z-40 shadow-2xl select-none"
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <h2 className="text-xs font-bold text-slate-100 uppercase tracking-wider font-mono">
                INSPECTION PANEL
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-zinc-800 text-slate-400 hover:text-slate-200 cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Card 1: System Status */}
          <div className="glass-panel p-3 rounded-xl space-y-2 font-mono text-xs">
            <div className="flex items-center justify-between font-semibold text-slate-300">
              <span className="flex items-center space-x-1.5">
                <Zap className="w-3.5 h-3.5 text-cyan-400" />
                <span>System Health</span>
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                OPTIMAL
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 pt-1 text-xs">
              <div className="bg-zinc-900/80 p-2 rounded-lg border border-zinc-800">
                <div className="text-[10px] text-slate-500">CPU Load</div>
                <div className="font-bold text-cyan-400">18.2%</div>
              </div>
              <div className="bg-zinc-900/80 p-2 rounded-lg border border-zinc-800">
                <div className="text-[10px] text-slate-500">RAM Used</div>
                <div className="font-bold text-purple-400">3.8 GB</div>
              </div>
            </div>
          </div>

          {/* Card 2: AI Status */}
          <div className="glass-panel p-3 rounded-xl space-y-2 text-xs font-mono">
            <div className="flex items-center justify-between font-semibold text-slate-300">
              <span className="flex items-center space-x-1.5">
                <Cpu className="w-3.5 h-3.5 text-purple-400" />
                <span>Inference Gateway</span>
              </span>
              <span className="text-[10px] text-cyan-400">Local Ollama</span>
            </div>
            <div className="space-y-1 text-[11px]">
              <div className="flex justify-between text-slate-400">
                <span>Active Model:</span>
                <span className="text-slate-200">llama3.2:latest</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Native Bridge:</span>
                <span className="text-emerald-400 font-bold">127.0.0.1:3001</span>
              </div>
            </div>
          </div>

          {/* Card 3: Recent Activity */}
          <div className="glass-panel p-3 rounded-xl space-y-2 text-xs">
            <div className="flex items-center justify-between font-semibold text-slate-300 font-mono">
              <span className="flex items-center space-x-1.5">
                <Clock className="w-3.5 h-3.5 text-blue-400" />
                <span>Recent Audit Events</span>
              </span>
            </div>
            <div className="space-y-2 text-[11px]">
              {MOCK_NOTIFICATIONS.slice(0, 3).map((item) => (
                <div key={item.id} className="p-2 rounded-lg bg-zinc-900/80 border border-zinc-800 space-y-1">
                  <div className="flex items-center justify-between text-slate-300">
                    <span className="font-medium truncate">{item.title}</span>
                    <CheckCircle2 className="w-3 h-3 text-emerald-400 flex-shrink-0" />
                  </div>
                  <div className="text-[10px] text-slate-500 truncate">{item.timestamp}</div>
                </div>
              ))}
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
};

export default RightPanel;
