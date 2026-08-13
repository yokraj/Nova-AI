import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Activity,
  Cpu,
  Bell,
  CheckCircle2,
  TrendingUp,
  Clock,
  ShieldCheck,
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
          className="w-80 h-[calc(100vh-4rem)] border-l border-slate-800/80 bg-slate-950/90 backdrop-blur-xl p-4 overflow-y-auto space-y-5 z-20 flex-shrink-0"
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                Inspection Panel
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Card 1: System Status */}
          <div className="glass-panel p-3.5 rounded-xl space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span className="flex items-center space-x-1.5">
                <Zap className="w-3.5 h-3.5 text-cyan-400" />
                <span>System Status</span>
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                OPTIMAL
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 pt-1 text-xs">
              <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                <div className="text-[10px] text-slate-500">CPU Load</div>
                <div className="font-mono font-bold text-cyan-400">24.5%</div>
              </div>
              <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                <div className="text-[10px] text-slate-500">RAM Used</div>
                <div className="font-mono font-bold text-purple-400">4.1 GB</div>
              </div>
            </div>
          </div>

          {/* Card 2: AI Status */}
          <div className="glass-panel p-3.5 rounded-xl space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span className="flex items-center space-x-1.5">
                <Cpu className="w-3.5 h-3.5 text-purple-400" />
                <span>Inference Gateway</span>
              </span>
              <span className="text-[10px] font-mono text-cyan-400">Ollama/vLLM</span>
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Active Model:</span>
                <span className="font-mono text-slate-200">llama3.2</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>GPU VRAM:</span>
                <span className="font-mono text-slate-200">8.1 / 24 GB</span>
              </div>
            </div>
          </div>

          {/* Card 3: Recent Activity */}
          <div className="glass-panel p-3.5 rounded-xl space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span className="flex items-center space-x-1.5">
                <Clock className="w-3.5 h-3.5 text-blue-400" />
                <span>Recent Activity</span>
              </span>
            </div>
            <div className="space-y-2 text-xs">
              <div className="p-2 rounded-lg bg-slate-900/40 border border-slate-800/80">
                <div className="text-slate-200 font-medium">Memory Indexing Completed</div>
                <div className="text-[10px] text-slate-500">142,850 vector embeddings synced</div>
              </div>
            </div>
          </div>

          {/* Card 4: Notifications */}
          <div className="glass-panel p-3.5 rounded-xl space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span className="flex items-center space-x-1.5">
                <Bell className="w-3.5 h-3.5 text-amber-400" />
                <span>Notifications</span>
              </span>
              <span className="text-[10px] font-mono text-cyan-400">{MOCK_NOTIFICATIONS.length}</span>
            </div>
            <div className="space-y-2">
              {MOCK_NOTIFICATIONS.map((n) => (
                <div key={n.id} className="p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-xs space-y-0.5">
                  <div className="font-semibold text-slate-200">{n.title}</div>
                  <div className="text-slate-400 text-[11px]">{n.message}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Card 5: Today's Tasks */}
          <div className="glass-panel p-3.5 rounded-xl space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Today's Tasks</span>
              </span>
            </div>
            <div className="space-y-1.5 text-xs text-slate-400">
              <div className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span className="line-through text-slate-500">F1.1 Frontend Bootstrap</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
                <span className="text-cyan-300 font-medium">F1.2 Enterprise Layout System</span>
              </div>
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
};

export default RightPanel;
