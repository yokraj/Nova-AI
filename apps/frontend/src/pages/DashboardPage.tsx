import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Bot, Target, Monitor, Brain, BookOpen } from 'lucide-react';
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
import { NovaCoreState } from '@/features/nova-core/types/novaCore';

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

  const getCoreState = (): NovaCoreState => {
    if (!currentCommand) return 'IDLE';
    if (currentCommand.executionState === 'AWAITING_APPROVAL') return 'AWAITING_APPROVAL';
    if (currentCommand.executionState === 'COMPLETED') return 'COMPLETED';
    if (currentCommand.executionState === 'FAILED') return 'FAILED';
    if (currentCommand.executionState === 'EXECUTING' || currentCommand.executionState === 'VERIFYING') return 'EXECUTING';
    if (currentCommand.executionState === 'PLANNING') return 'PLANNING';
    if (currentCommand.executionState === 'UNDERSTANDING') return 'THINKING';
    return 'IDLE';
  };

  return (
    <div className="w-full max-w-4xl mx-auto min-w-0 min-h-[80vh] flex flex-col items-center justify-between py-4 px-2 relative select-none">
      {/* Top Header Label */}
      <div className="w-full flex items-center justify-between z-10 py-1">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span className="text-[11px] font-mono font-bold text-cyan-300 tracking-wider uppercase">
            NOVA CORE • UNIVERSAL INTELLIGENCE
          </span>
        </div>
      </div>

      {/* Dominant Nova Core Orb */}
      <div className="flex flex-col items-center justify-center space-y-4 my-4 z-10 max-w-xl text-center w-full">
        <NovaCore
          state={getCoreState()}
          onClick={() => processCommand('What can Nova do?', 'TEXT')}
        />

        <NovaStatus
          state={getCoreState()}
          customText={currentCommand?.executionState ? `Executing: ${currentCommand.rawInput}` : undefined}
        />
      </div>

      {/* Dynamic Execution Pipeline & Compact Cards (Only visible when command active) */}
      <AnimatePresence mode="wait">
        {currentCommand && currentCommand.executionState !== 'IDLE' && (
          <motion.div
            initial={{ opacity: 0, y: 8, height: 0 }}
            animate={{ opacity: 1, y: 0, height: 'auto' }}
            exit={{ opacity: 0, y: -8, height: 0 }}
            className="w-full max-w-2xl z-10 space-y-3 my-2"
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

      {/* Main Command Input Surface */}
      <div className="w-full max-w-2xl z-10 space-y-3 pt-2">
        <UniversalCommandSurface
          onSubmitCommand={(cmd, src) => processCommand(cmd, src)}
        />

        {/* Subdued Contextual Action Chips */}
        <div className="flex items-center justify-center flex-wrap gap-2 text-xs font-mono pt-1">
          {[
            { id: 'agents', label: 'Agents', icon: Bot },
            { id: 'missions', label: 'Missions', icon: Target },
            { id: 'devices', label: 'Devices', icon: Monitor },
            { id: 'memory', label: 'Memory', icon: Brain },
            { id: 'knowledge', label: 'Knowledge', icon: BookOpen },
          ].map((chip) => {
            const ChipIcon = chip.icon;
            return (
              <button
                key={chip.id}
                onClick={() => openDrawer(chip.id)}
                className="px-2.5 py-1 rounded-xl bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-cyan-500/40 text-slate-400 hover:text-cyan-300 transition-all cursor-pointer flex items-center space-x-1.5 text-[11px]"
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
