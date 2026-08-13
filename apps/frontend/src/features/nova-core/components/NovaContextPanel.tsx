import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Layers, Bot, Target, Monitor, Brain, Workflow, Activity, Bell } from 'lucide-react';
import { cn } from '@/utils/cn';
import { NovaContextDrawerType } from '../types/novaCore';
import ActiveAgentsWidget from '@/components/dashboard/ActiveAgentsWidget';
import RunningMissionsWidget from '@/components/dashboard/RunningMissionsWidget';
import DeviceCenterWidget from '@/components/dashboard/DeviceCenterWidget';
import MemoryActivityWidget from '@/components/dashboard/MemoryActivityWidget';
import AutomationCenterWidget from '@/components/dashboard/AutomationCenterWidget';
import SystemOverviewWidget from '@/components/dashboard/SystemOverviewWidget';
import NovaCoreServicesWidget from '@/components/dashboard/NovaCoreServicesWidget';
import NotificationsWidget from '@/components/dashboard/NotificationsWidget';

interface NovaContextPanelProps {
  activeDrawer: NovaContextDrawerType;
  onClose: () => void;
  className?: string;
}

export const NovaContextPanel: React.FC<NovaContextPanelProps> = ({
  activeDrawer,
  onClose,
  className,
}) => {
  if (activeDrawer === 'none') return null;

  const drawerTitles: Record<Exclude<NovaContextDrawerType, 'none'>, { title: string; icon: any }> = {
    agents: { title: 'Active Workforce Agents', icon: Bot },
    missions: { title: 'Autonomous Missions DAG', icon: Target },
    devices: { title: 'Cross-Platform Device Mesh', icon: Monitor },
    memory: { title: 'Semantic Vector Memory Store', icon: Brain },
    knowledge: { title: 'Ontological Knowledge Graph', icon: Brain },
    automation: { title: 'No-Code Automation Studio', icon: Workflow },
    telemetry: { title: 'System Hardware & Core Services', icon: Activity },
    notifications: { title: 'System Notifications & Alerts', icon: Bell },
  };

  const currentInfo = drawerTitles[activeDrawer as Exclude<NovaContextDrawerType, 'none'>];
  const Icon = currentInfo?.icon || Layers;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex justify-end"
        onClick={onClose}
      >
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          onClick={(e) => e.stopPropagation()}
          className={cn('w-full max-w-2xl h-full bg-slate-950 border-l border-slate-800 p-6 overflow-y-auto space-y-6 shadow-2xl', className)}
        >
          {/* Drawer Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Icon className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-extrabold text-slate-100 uppercase tracking-wider">
                  {currentInfo?.title}
                </h3>
                <p className="text-xs font-mono text-slate-400">Contextual inspection panel requested by user</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-100 hover:border-slate-700 transition-all cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Drawer Body Content */}
          <div className="space-y-6">
            {activeDrawer === 'agents' && <ActiveAgentsWidget />}
            {activeDrawer === 'missions' && <RunningMissionsWidget />}
            {activeDrawer === 'devices' && <DeviceCenterWidget />}
            {(activeDrawer === 'memory' || activeDrawer === 'knowledge') && <MemoryActivityWidget />}
            {activeDrawer === 'automation' && <AutomationCenterWidget />}
            {activeDrawer === 'telemetry' && (
              <div className="space-y-6">
                <SystemOverviewWidget />
                <NovaCoreServicesWidget />
              </div>
            )}
            {activeDrawer === 'notifications' && <NotificationsWidget />}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default NovaContextPanel;
