import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Bot, Target, Monitor, Brain, Workflow } from 'lucide-react';
import NovaCore from '@/features/nova-core/components/NovaCore';
import NovaStatus from '@/features/nova-core/components/NovaStatus';
import { useUniversalCommand } from '@/features/universal-command/hooks/useUniversalCommand';
import UniversalCommandSurface from '@/features/universal-command/components/UniversalCommandSurface';
import CommandUnderstanding from '@/features/universal-command/components/CommandUnderstanding';
import CommandPlanView from '@/features/universal-command/components/CommandPlan';
import PermissionPreview from '@/features/universal-command/components/PermissionPreview';
import ExecutionProgress from '@/features/universal-command/components/ExecutionProgress';
import ExecutionResult from '@/features/universal-command/components/ExecutionResult';
import CommandContextDrawer from '@/features/universal-command/components/CommandContextDrawer';

export const DashboardPage: React.FC = () => {
  const {
    currentCommand,
    processCommand,
    approveCurrentCommand,
    isDrawerOpen,
    drawerDomain,
    openDrawer,
    closeDrawer,
  } = useUniversalCommand();

  const getCoreState = () => {
    if (!currentCommand) return 'IDLE';
    if (currentCommand.executionState === 'EXECUTING') return 'EXECUTING';
    if (currentCommand.executionState === 'UNDERSTANDING' || currentCommand.executionState === 'PLANNING') return 'THINKING';
    return 'IDLE';
  };

  return (
    <div className="min-h-[85vh] flex flex-col items-center justify-between py-6 px-4 relative overflow-hidden select-none">
      {/* Background Cyber Ambient Glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Top Header */}
      <div className="w-full max-w-4xl flex items-center justify-between z-10">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
          <span className="text-xs font-mono font-bold text-cyan-300 tracking-wider uppercase">
            NOVA CORE • UNIVERSAL ASSISTANT
          </span>
        </div>
      </div>

      {/* Center Dominant Official Nova Core Visual Identity */}
      <div className="flex flex-col items-center justify-center space-y-6 my-6 z-10 max-w-2xl text-center">
        <NovaCore
          state={getCoreState()}
          onClick={() => processCommand('What can Nova do?', 'TEXT')}
        />

        <NovaStatus
          state={getCoreState()}
          customText={currentCommand?.executionState || 'Ready for universal commands.'}
        />
      </div>

      {/* Dynamic Execution Pipeline Display */}
      <AnimatePresence>
        {currentCommand && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="w-full max-w-3xl z-10 space-y-3 my-4"
          >
            <ExecutionProgress state={currentCommand.executionState} />

            {currentCommand.executionState === 'UNDERSTANDING' && (
              <CommandUnderstanding command={currentCommand} />
            )}

            {currentCommand.plan && currentCommand.executionState === 'PLANNING' && (
              <CommandPlanView plan={currentCommand.plan} />
            )}

            {currentCommand.permission && currentCommand.executionState === 'AWAITING_APPROVAL' && (
              <PermissionPreview
                permission={currentCommand.permission}
                onApprove={approveCurrentCommand}
              />
            )}

            {currentCommand.result && (
              <ExecutionResult
                result={currentCommand.result}
                onOpenContextDrawer={openDrawer}
              />
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Universal Command Surface */}
      <div className="w-full max-w-3xl z-10 space-y-4">
        <UniversalCommandSurface
          onSubmitCommand={(cmd, src) => processCommand(cmd, src)}
        />

        {/* Subdued Contextual Trigger Chips */}
        <div className="flex items-center justify-center flex-wrap gap-2 text-xs font-mono pt-2">
          {[
            { id: 'agents', label: 'Agents', icon: Bot },
            { id: 'missions', label: 'Missions', icon: Target },
            { id: 'device-control', label: 'Devices', icon: Monitor },
            { id: 'memory', label: 'Memory', icon: Brain },
            { id: 'knowledge', label: 'Knowledge', icon: Workflow },
          ].map((chip) => {
            const ChipIcon = chip.icon;
            return (
              <button
                key={chip.id}
                onClick={() => openDrawer(chip.id)}
                className="px-3 py-1.5 rounded-xl bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-cyan-500/40 text-slate-400 hover:text-cyan-300 transition-all cursor-pointer flex items-center space-x-1.5"
              >
                <ChipIcon className="w-3.5 h-3.5 text-cyan-400" />
                <span>{chip.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Contextual Subsystem Slide-Over Drawer */}
      <CommandContextDrawer
        isOpen={isDrawerOpen}
        domain={drawerDomain}
        onClose={closeDrawer}
      />
    </div>
  );
};

export default DashboardPage;
