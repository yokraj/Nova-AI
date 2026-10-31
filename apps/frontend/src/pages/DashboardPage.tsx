import React, { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Sparkles,
  LayoutDashboard,
  Bot,
  Target,
  Monitor,
  Brain,
  BookOpen,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import NovaCore from '@/features/nova-core/components/NovaCore';
import NovaStatus from '@/features/nova-core/components/NovaStatus';
import { useUniversalCommand } from '@/features/universal-command/hooks/useUniversalCommand';
import CommandUnderstanding from '@/features/universal-command/components/CommandUnderstanding';
import CommandPlanView from '@/features/universal-command/components/CommandPlan';
import PermissionPreview from '@/features/universal-command/components/PermissionPreview';
import ExecutionProgress from '@/features/universal-command/components/ExecutionProgress';
import ExecutionResult from '@/features/universal-command/components/ExecutionResult';
import CommandContextDrawer from '@/features/universal-command/components/CommandContextDrawer';
import { NovaCoreState } from '@/features/nova-core/types/novaCore';

// The 14 Polished Dashboard Components
import NovaHeader from '@/components/dashboard/NovaHeader';
import UniversalCommandArea from '@/components/dashboard/UniversalCommandArea';
import NovaIntelligenceCore from '@/components/dashboard/NovaIntelligenceCore';
import SystemOverviewWidget from '@/components/dashboard/SystemOverviewWidget';
import NovaCoreServicesWidget from '@/components/dashboard/NovaCoreServicesWidget';
import ActiveAgentsWidget from '@/components/dashboard/ActiveAgentsWidget';
import RunningMissionsWidget from '@/components/dashboard/RunningMissionsWidget';
import MemoryActivityWidget from '@/components/dashboard/MemoryActivityWidget';
import DeviceCenterWidget from '@/components/dashboard/DeviceCenterWidget';
import AutomationCenterWidget from '@/components/dashboard/AutomationCenterWidget';
import QuickActionsWidget from '@/components/dashboard/QuickActionsWidget';
import ActivityTimelineWidget from '@/components/dashboard/ActivityTimelineWidget';
import DashboardAnalyticsWidget from '@/components/dashboard/DashboardAnalyticsWidget';
import NotificationsWidget from '@/components/dashboard/NotificationsWidget';
import { CommandVisualState } from '@/types/dashboard';

import { useDashboardData } from '@/hooks/useDashboardData';

export const DashboardPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<'overview' | 'core'>('overview');

  const {
    data: dashboardData,
    isLoading: isDashboardLoading,
    isRefreshing: isDashboardRefreshing,
    connectionStatus,
    refresh: refreshDashboard,
    pauseMission,
    resumeMission,
    cancelMission,
    approveMission,
    executeAutomation,
    cancelAutomation,
    markNotificationRead,
    deleteNotification,
    pingDevice,
  } = useDashboardData();

  const {
    currentCommand,
    processCommand,
    approveCurrentCommand,
    rejectCurrentCommand,
    cancelCommand,
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

  const mapToVisualState = (): CommandVisualState => {
    if (!currentCommand) return 'idle';
    switch (currentCommand.executionState) {
      case 'UNDERSTANDING':
      case 'PLANNING':
        return 'processing';
      case 'AWAITING_APPROVAL':
        return 'waiting_for_permission';
      case 'EXECUTING':
      case 'VERIFYING':
        return 'executing';
      case 'COMPLETED':
        return 'completed';
      case 'FAILED':
        return 'failed';
      default:
        return 'idle';
    }
  };

  return (
    <div className="w-full max-w-7xl mx-auto min-w-0 min-h-screen flex flex-col py-4 px-3 sm:px-6 space-y-6 select-none font-sans text-slate-100">
      {/* Top View Switcher Header Bar */}
      <div className="w-full flex items-center justify-between pb-1 border-b border-zinc-800/80">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span className="text-[11px] font-mono font-bold text-cyan-300 tracking-wider uppercase">
            NOVA CORE • UNIVERSAL COMMAND CENTER
          </span>
        </div>

        {/* View Mode Segmented Control */}
        <div className="flex items-center space-x-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800 text-xs font-mono">
          <button
            onClick={() => setViewMode('overview')}
            className={cn(
              'px-3 py-1 rounded-lg flex items-center space-x-1.5 transition-all cursor-pointer',
              viewMode === 'overview'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            )}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Dashboard Overview</span>
          </button>

          <button
            onClick={() => setViewMode('core')}
            className={cn(
              'px-3 py-1 rounded-lg flex items-center space-x-1.5 transition-all cursor-pointer',
              viewMode === 'core'
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            )}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Core Focus Mode</span>
          </button>
        </div>
      </div>

      {/* VIEW MODE 1: FULL DASHBOARD OVERVIEW */}
      {viewMode === 'overview' && (
        <div className="space-y-6">
          {/* 1. Nova Header Widget */}
          <NovaHeader
            isConnected={connectionStatus === 'connected'}
            onRefresh={refreshDashboard}
            isRefreshing={isDashboardRefreshing}
          />

          {/* 2. Universal Command Area */}
          <UniversalCommandArea
            state={mapToVisualState()}
            onExecuteCommand={(cmd, mode, attachments) =>
              processCommand(
                cmd,
                mode === 'voice' ? 'VOICE' : mode === 'vision' ? 'VISION' : 'TEXT',
                attachments
              )
            }
            onApprovePermission={approveCurrentCommand}
            onRejectPermission={rejectCurrentCommand}
            onCancel={cancelCommand}
            permissionDetails={
              currentCommand?.permission
                ? {
                    action: currentCommand.permission.requiredCapability || currentCommand.permission.scope,
                    resource: currentCommand.permission.scope || 'System Resources',
                    riskLevel: currentCommand.permission.riskLevel,
                  }
                : undefined
            }
            executionResult={
              currentCommand?.result
                ? {
                    success: currentCommand.result.success,
                    message: currentCommand.result.message,
                    details: currentCommand.result.errorReason || currentCommand.result.suggestedNextStep,
                  }
                : undefined
            }
          />

          {/* Dynamic Execution Pipeline View (If active command in flight) */}
          <AnimatePresence>
            {currentCommand && currentCommand.executionState !== 'IDLE' && (
              <motion.div
                initial={{ opacity: 0, y: 8, height: 0 }}
                animate={{ opacity: 1, y: 0, height: 'auto' }}
                exit={{ opacity: 0, y: -8, height: 0 }}
                className="w-full space-y-3"
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

          {/* 3. Nova Intelligence Core Subsystem Widget */}
          <NovaIntelligenceCore
            onNavigateSubsystem={(subsystemId) => openDrawer(subsystemId)}
          />

          {/* 4. Telemetry Hardware & Core Microservices */}
          <div className="space-y-6">
            <SystemOverviewWidget
              telemetry={dashboardData?.telemetry}
              onRefresh={refreshDashboard}
              isLoading={isDashboardLoading || isDashboardRefreshing}
            />
            <NovaCoreServicesWidget
              services={dashboardData?.services}
              onRestartService={refreshDashboard}
            />
          </div>

          {/* 5. Telemetry Analytics & Workload Distribution */}
          <DashboardAnalyticsWidget data={dashboardData?.analytics} />

          {/* 6. Active Agent Workforce & Autonomous Missions DAG */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
            <ActiveAgentsWidget agents={dashboardData?.agents} />
            <RunningMissionsWidget
              missions={dashboardData?.missions}
              onPauseMission={pauseMission}
              onResumeMission={resumeMission}
              onCancelMission={cancelMission}
              onApproveMission={approveMission}
            />
          </div>

          {/* 7. Memory Activity & Device Mesh Center */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
            <MemoryActivityWidget />
            <DeviceCenterWidget
              devices={dashboardData?.devices}
              onPingDevice={pingDevice}
            />
          </div>

          {/* 8. Automation Studio & Quick System Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
            <AutomationCenterWidget
              automations={dashboardData?.automations}
              onTriggerAutomation={executeAutomation}
              onCancelAutomation={cancelAutomation}
            />
            <QuickActionsWidget onSelectAction={(cmd) => processCommand(cmd, 'TEXT')} />
          </div>

          {/* 9. Activity Timeline Stream & System Notifications */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
            <ActivityTimelineWidget activities={dashboardData?.timeline} />
            <NotificationsWidget
              initialNotifications={dashboardData?.notifications}
              onMarkRead={markNotificationRead}
              onDeleteNotification={deleteNotification}
            />
          </div>
        </div>
      )}

      {/* VIEW MODE 2: MINIMALIST NOVA CORE ORB FOCUS */}
      {viewMode === 'core' && (
        <div className="w-full max-w-4xl mx-auto flex flex-col items-center justify-between py-6 px-2 relative min-h-[75vh]">
          {/* Dominant Nova Core Orb */}
          <div className="flex flex-col items-center justify-center space-y-4 my-6 z-10 max-w-xl text-center w-full">
            <NovaCore
              state={getCoreState()}
              onClick={() => processCommand('What can Nova do?', 'TEXT')}
            />

            <NovaStatus
              state={getCoreState()}
              customText={currentCommand?.executionState ? `Executing: ${currentCommand.rawInput}` : undefined}
            />
          </div>

          {/* Dynamic Execution Pipeline Display */}
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

          {/* Universal Command Area */}
          <div className="w-full max-w-2xl z-10 space-y-3 pt-4">
            <UniversalCommandArea
              state={mapToVisualState()}
              onExecuteCommand={(cmd, mode, attachments) =>
                processCommand(
                  cmd,
                  mode === 'voice' ? 'VOICE' : mode === 'vision' ? 'VISION' : 'TEXT',
                  attachments
                )
              }
              onApprovePermission={approveCurrentCommand}
              onRejectPermission={rejectCurrentCommand}
              onCancel={cancelCommand}
              permissionDetails={
                currentCommand?.permission
                  ? {
                      action: currentCommand.permission.requiredCapability || currentCommand.permission.scope,
                      resource: currentCommand.permission.scope || 'System Resources',
                      riskLevel: currentCommand.permission.riskLevel,
                    }
                  : undefined
              }
              executionResult={
                currentCommand?.result
                  ? {
                      success: currentCommand.result.success,
                      message: currentCommand.result.message,
                      details: currentCommand.result.errorReason || currentCommand.result.suggestedNextStep,
                    }
                  : undefined
              }
            />

            {/* Subdued Contextual Trigger Chips */}
            <div className="flex items-center justify-center flex-wrap gap-2 text-xs font-mono pt-2">
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
        </div>
      )}

      {/* Slide-Over Contextual Subsystem Drawer */}
      <CommandContextDrawer
        isOpen={isDrawerOpen}
        domain={drawerDomain}
        onClose={closeDrawer}
      />
    </div>
  );
};

export default DashboardPage;
