import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Layers } from 'lucide-react';
import { cn } from '@/utils/cn';
import AgentWorkspace from '@/features/agents/components/AgentWorkspace';
import MissionWorkspace from '@/features/missions/components/MissionWorkspace';
import DeviceControlWorkspace from '@/features/device-control/components/DeviceControlWorkspace';
import MemoryWorkspace from '@/features/memory/components/MemoryWorkspace';
import KnowledgeWorkspace from '@/features/knowledge/components/KnowledgeWorkspace';

interface CommandContextDrawerProps {
  isOpen: boolean;
  domain: string | null;
  onClose: () => void;
  className?: string;
}

export const CommandContextDrawer: React.FC<CommandContextDrawerProps> = ({
  isOpen,
  domain,
  onClose,
  className,
}) => {
  if (!isOpen || !domain) return null;

  const renderDomainContent = () => {
    switch (domain) {
      case 'agents':
        return <AgentWorkspace />;
      case 'missions':
        return <MissionWorkspace />;
      case 'device-control':
      case 'devices':
        return <DeviceControlWorkspace />;
      case 'memory':
        return <MemoryWorkspace />;
      case 'knowledge':
        return <KnowledgeWorkspace />;
      default:
        return (
          <div className="p-8 text-center text-slate-400 font-mono text-sm">
            Subsystem details for domain "{domain}" available in dedicated workspace.
          </div>
        );
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex justify-end"
      >
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className={cn(
            'w-full max-w-2xl bg-slate-950 border-l border-cyan-500/30 h-full flex flex-col shadow-2xl overflow-hidden',
            className
          )}
        >
          {/* Drawer Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/60 font-mono text-xs">
            <div className="flex items-center space-x-2 text-cyan-300 font-bold uppercase tracking-wider">
              <Layers className="w-4 h-4 text-cyan-400" />
              <span>CONTEXTUAL SUBSYSTEM DRAWER: {domain}</span>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-xl bg-slate-900 text-slate-400 hover:text-slate-100 border border-slate-800 transition-all cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Drawer Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 font-sans text-slate-100">
            {renderDomainContent()}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default CommandContextDrawer;
