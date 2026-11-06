import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Compass, LayoutGrid } from 'lucide-react';
import { cn } from '@/utils/cn';
import { useAuthStore } from '@/stores/useAuthStore';
import { useDashboardData } from '@/hooks/useDashboardData';
import { useUniversalCommand } from '@/features/universal-command/hooks/useUniversalCommand';
import { useNovaVoiceAssistant } from '@/features/voice/hooks/useNovaVoiceAssistant';
import { NovaCoreState } from '@/features/nova-core/types/novaCore';
import { CommandVisualState } from '@/types/dashboard';

// JARVIS-Inspired Cockpit Components
import JarvisHolographicCore from '@/features/nova-core/components/JarvisHolographicCore';
import IntelligenceCapabilities from '@/features/nova-core/components/IntelligenceCapabilities';
import JarvisFloatingCommandBar from '@/features/universal-command/components/JarvisFloatingCommandBar';
import JarvisRightContextPanels from '@/components/dashboard/JarvisRightContextPanels';
import JarvisBottomQuickActions from '@/components/dashboard/JarvisBottomQuickActions';
import CommandContextDrawer from '@/features/universal-command/components/CommandContextDrawer';
import { VoiceSettings } from '@/features/voice/components/VoiceSettings';

// Execution Pipeline Views for active in-flight multi-step operations
import ExecutionProgress from '@/features/universal-command/components/ExecutionProgress';
import CommandUnderstanding from '@/features/universal-command/components/CommandUnderstanding';
import CommandPlanView from '@/features/universal-command/components/CommandPlan';
import PermissionPreview from '@/features/universal-command/components/PermissionPreview';
import ExecutionResult from '@/features/universal-command/components/ExecutionResult';

// Comprehensive Operations Grid (14 Standardized Widgets)
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

export type DashboardViewMode = 'cockpit' | 'operations';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [rightPanelsOpen, setRightPanelsOpen] = useState(true);
  const [isVoiceSettingsOpen, setIsVoiceSettingsOpen] = useState(false);

  // Safe preference-based state persistence for selected view mode
  const [activeView, setActiveView] = useState<DashboardViewMode>(() => {
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem('nova_dashboard_active_view');
        if (saved === 'cockpit' || saved === 'operations') return saved;
      } catch {
        // Fallback to cockpit if localStorage is blocked
      }
    }
    return 'cockpit';
  });

  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem('nova_dashboard_active_view', activeView);
      } catch {
        // Ignore storage write issues in sandboxed iframes
      }
    }
  }, [activeView]);

  // Unified Live Real Data Hook (Single source of truth shared by both views)
  const {
    data: dashboardData,
    connectionStatus,
    refresh: refreshDashboard,
    isRefreshing,
  } = useDashboardData();

  // Unified Universal Command Pipeline
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

  // Unified Voice Interaction Assistant (SpeechSynthesis + SpeechRecognition)
  const voiceAssistant = useNovaVoiceAssistant({
    onExecuteCommand: async (cmdText) => {
      return await processCommand(cmdText, 'VOICE');
    },
    userName: user?.name || 'sir',
  });

  // Map execution and voice state to central holographic core state
  const getCoreState = (): NovaCoreState => {
    if (voiceAssistant.voiceState !== 'IDLE') {
      return voiceAssistant.voiceState;
    }
    if (!currentCommand) return 'IDLE';
    switch (currentCommand.executionState) {
      case 'UNDERSTANDING':
        return 'THINKING';
      case 'PLANNING':
        return 'PLANNING';
      case 'AWAITING_APPROVAL':
        return 'AWAITING_APPROVAL';
      case 'EXECUTING':
      case 'VERIFYING':
        return 'EXECUTING';
      case 'COMPLETED':
        return 'COMPLETED';
      case 'FAILED':
        return 'FAILED';
      default:
        return 'IDLE';
    }
  };

  const mapToVisualState = (): CommandVisualState => {
    if (voiceAssistant.isListening) return 'listening';
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

  // Handle Intelligence Capability clicks
  const handleSelectCapability = (cap: 'think' | 'see' | 'do' | 'control') => {
    switch (cap) {
      case 'think':
        navigate('/chat');
        break;
      case 'see':
        navigate('/knowledge');
        break;
      case 'do':
        navigate('/automation');
        break;
      case 'control':
        navigate('/computer-control');
        break;
    }
  };

  // Handle Bottom Quick Actions
  const handleQuickAction = (actionType: 'open_app' | 'run_task' | 'automate' | 'create', defaultPrompt: string) => {
    switch (actionType) {
      case 'open_app':
      case 'run_task':
      case 'create':
        processCommand(defaultPrompt, 'TEXT');
        break;
      case 'automate':
        navigate('/automation');
        break;
    }
  };

  return (
    <div className="w-full min-h-full max-w-[1920px] mx-auto flex flex-col min-w-0 jarvis-bg-grid relative overflow-x-hidden px-3 sm:px-6 py-2 sm:py-3 lg:py-4 space-y-3">
      {/* View Switcher Header Bar */}
      <div className="w-full flex items-center justify-between pb-2 border-b border-slate-800/80 shrink-0">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider hidden sm:inline">
            Nova AI OS • Command Viewport
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full border border-slate-700 bg-slate-900/60 text-slate-400">
            {activeView === 'cockpit' ? 'CINEMATIC COCKPIT' : 'OPERATIONS GRID (14 WIDGETS)'}
          </span>
        </div>

        {/* View Switcher Controls: [ JARVIS Cockpit | Operations Grid ] */}
        <div
          role="tablist"
          aria-label="Dashboard View Switcher"
          className="flex items-center space-x-1 p-1 rounded-xl bg-slate-900/90 border border-slate-800/90 backdrop-blur-md text-xs font-mono select-none"
        >
          <button
            role="tab"
            aria-selected={activeView === 'cockpit'}
            onClick={() => setActiveView('cockpit')}
            className={cn(
              'flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition-all cursor-pointer font-bold focus:outline-none focus:ring-1 focus:ring-cyan-400',
              activeView === 'cockpit'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(0,240,255,0.2)]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
            )}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>JARVIS Cockpit</span>
          </button>

          <button
            role="tab"
            aria-selected={activeView === 'operations'}
            onClick={() => setActiveView('operations')}
            className={cn(
              'flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition-all cursor-pointer font-bold focus:outline-none focus:ring-1 focus:ring-cyan-400',
              activeView === 'operations'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(0,240,255,0.2)]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
            )}
          >
            <LayoutGrid className="w-3.5 h-3.5" />
            <span>Operations Grid</span>
          </button>
        </div>
      </div>

      {/* Main View Container */}
      <AnimatePresence mode="wait">
        {activeView === 'cockpit' ? (
          /* =========================================================================
             VIEW 1: JARVIS COCKPIT (Cinematic HUD + Floating Command Pipeline)
             ========================================================================= */
          <motion.div
            key="cockpit-view"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2 }}
            className="w-full flex flex-1 min-w-0"
          >
            {/* Central Command Stage */}
            <div className="flex-1 flex flex-col items-center justify-center min-w-0 max-w-5xl mx-auto space-y-2.5 sm:space-y-3.5 z-10">
              {/* 1. Central Holographic Core & Greeting */}
              <div className="w-full flex flex-col items-center justify-center pt-0.5 sm:pt-1">
                <JarvisHolographicCore
                  state={getCoreState()}
                  userName={user?.name || 'Commander'}
                  voiceLevel={voiceAssistant.voiceLevel}
                  onClick={() => {
                    if (voiceAssistant.isSpeaking) {
                      voiceAssistant.stopSpeaking();
                    } else {
                      voiceAssistant.speakGreeting();
                    }
                  }}
                />
              </div>

              {/* 2. Four Surrounding Compact Intelligence Capabilities */}
              <div className="w-full max-w-4xl px-2">
                <IntelligenceCapabilities onSelectCapability={handleSelectCapability} />
              </div>

              {/* 3. Universal Floating Command Interface */}
              <div className="w-full max-w-3xl px-2">
                <JarvisFloatingCommandBar
                  state={mapToVisualState()}
                  isListeningProp={voiceAssistant.isListening}
                  isSpeakingProp={voiceAssistant.isSpeaking}
                  onToggleVoice={voiceAssistant.toggleVoice}
                  onStopSpeaking={voiceAssistant.stopSpeaking}
                  voiceError={voiceAssistant.voiceError}
                  onClearVoiceError={voiceAssistant.clearVoiceError}
                  externalTranscript={voiceAssistant.transcript}
                  handsFreeEnabled={voiceAssistant.handsFreeEnabled}
                  onToggleHandsFree={voiceAssistant.toggleHandsFree}
                  isMuted={voiceAssistant.isMuted}
                  onToggleMute={voiceAssistant.toggleMute}
                  onEndConversation={voiceAssistant.endConversationSession}
                  wakePhrase={voiceAssistant.wakePhrase}
                  onSetWakePhrase={voiceAssistant.setWakePhrase}
                  voiceState={voiceAssistant.voiceState}
                  isConversationActive={voiceAssistant.isConversationActive}
                  detectedLanguage={voiceAssistant.detectedLanguage}
                  activeVoiceName={voiceAssistant.activeVoiceInfo.name}
                  onOpenVoiceSettings={() => setIsVoiceSettingsOpen(true)}
                  onExecuteCommand={(cmd, mode, attachments) =>
                    processCommand(
                      cmd,
                      mode === 'voice' ? 'VOICE' : mode === 'vision' ? 'VISION' : 'TEXT',
                      attachments
                    )
                  }
                  onApprovePermission={approveCurrentCommand}
                  onRejectPermission={rejectCurrentCommand}
                  onCancel={() => {
                    voiceAssistant.stopListening();
                    voiceAssistant.stopSpeaking();
                    cancelCommand();
                  }}
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
              </div>

              {/* 4. Active In-Flight Multi-Step Execution Pipeline */}
              <AnimatePresence>
                {currentCommand && currentCommand.executionState !== 'IDLE' && (
                  <motion.div
                    initial={{ opacity: 0, y: 10, height: 0 }}
                    animate={{ opacity: 1, y: 0, height: 'auto' }}
                    exit={{ opacity: 0, y: -10, height: 0 }}
                    className="w-full max-w-3xl px-2 space-y-3"
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

              {/* 5. Bottom Quick Actions */}
              <div className="w-full max-w-3xl px-2">
                <JarvisBottomQuickActions onActionClick={handleQuickAction} />
              </div>
            </div>

            {/* Right-Side Collapsible Context Panels */}
            <div className="hidden lg:flex ml-4 shrink-0 h-[calc(100vh-8rem)] sticky top-2">
              <JarvisRightContextPanels
                telemetry={dashboardData?.telemetry}
                agents={dashboardData?.agents}
                activities={dashboardData?.timeline}
                isConnected={connectionStatus === 'connected'}
                isCollapsed={!rightPanelsOpen}
                onToggleCollapse={() => setRightPanelsOpen(!rightPanelsOpen)}
              />
            </div>
          </motion.div>
        ) : (
          /* =========================================================================
             VIEW 2: OPERATIONS GRID (Comprehensive 14-Widget Enterprise Dashboard)
             ========================================================================= */
          <motion.div
            key="operations-grid-view"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2 }}
            className="w-full space-y-5 pb-8"
          >
            {/* 1. Header Widget */}
            <NovaHeader
              isConnected={connectionStatus === 'connected'}
              onRefresh={() => refreshDashboard(true)}
              isRefreshing={isRefreshing}
            />

            {/* 2. Universal Command Execution Pipeline (Task 1 Integrated) */}
            <UniversalCommandArea
              state={mapToVisualState()}
              isListeningProp={voiceAssistant.isListening}
              isSpeakingProp={voiceAssistant.isSpeaking}
              onToggleVoice={voiceAssistant.toggleVoice}
              onStopSpeaking={voiceAssistant.stopSpeaking}
              voiceError={voiceAssistant.voiceError}
              onClearVoiceError={voiceAssistant.clearVoiceError}
              externalTranscript={voiceAssistant.transcript}
              voiceLevel={voiceAssistant.voiceLevel}
              onExecuteCommand={(cmd, mode, attachments) =>
                processCommand(
                  cmd,
                  mode === 'voice' ? 'VOICE' : mode === 'vision' ? 'VISION' : 'TEXT',
                  attachments
                )
              }
              onApprovePermission={approveCurrentCommand}
              onRejectPermission={rejectCurrentCommand}
              onCancel={() => {
                voiceAssistant.stopListening();
                voiceAssistant.stopSpeaking();
                cancelCommand();
              }}
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

            {/* 3. Nova Intelligence Core (Task 2 Holographic Visualizer & Subsystems) */}
            <NovaIntelligenceCore
              state={getCoreState()}
              voiceLevel={voiceAssistant.voiceLevel}
              userName={user?.name || 'Operator'}
              onCoreClick={() => {
                if (voiceAssistant.isSpeaking) {
                  voiceAssistant.stopSpeaking();
                } else {
                  voiceAssistant.speakGreeting();
                }
              }}
            />

            {/* 4. Hardware Telemetry & Core Services Health (Task 3 Standardized) */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
              <SystemOverviewWidget
                telemetry={dashboardData?.telemetry}
                connectionStatus={connectionStatus}
                backendHealth={dashboardData?.health}
                lastUpdated={dashboardData?.lastUpdated}
                onRefresh={() => refreshDashboard(true)}
                isLoading={isRefreshing}
              />
              <NovaCoreServicesWidget
                services={dashboardData?.services}
                connectionStatus={connectionStatus}
                lastUpdated={dashboardData?.lastUpdated}
                onRefresh={() => refreshDashboard(true)}
                isLoading={isRefreshing}
              />
            </div>

            {/* 5. Agent Workforce & Autonomous Missions */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
              <ActiveAgentsWidget
                agents={dashboardData?.agents}
                onRefresh={() => refreshDashboard(true)}
                isLoading={isRefreshing}
              />
              <RunningMissionsWidget
                missions={dashboardData?.missions}
                onRefresh={() => refreshDashboard(true)}
                isLoading={isRefreshing}
              />
            </div>

            {/* 6. Semantic Memory & Workload Analytics */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
              <MemoryActivityWidget
                onRefresh={() => refreshDashboard(true)}
                isLoading={isRefreshing}
              />
              <DashboardAnalyticsWidget
                data={dashboardData?.analytics}
                onRefresh={() => refreshDashboard(true)}
                isLoading={isRefreshing}
              />
            </div>

            {/* 7. Device Mesh & Automation Studio */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
              <DeviceCenterWidget
                devices={dashboardData?.devices}
                onRefresh={() => refreshDashboard(true)}
                isLoading={isRefreshing}
              />
              <AutomationCenterWidget
                automations={dashboardData?.automations}
                onRefresh={() => refreshDashboard(true)}
                isLoading={isRefreshing}
              />
            </div>

            {/* 8. Quick Actions, Activity Stream & Notifications */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              <QuickActionsWidget
                onSelectAction={(cmd) => processCommand(cmd, 'TEXT')}
              />
              <ActivityTimelineWidget
                activities={dashboardData?.timeline}
                onRefresh={() => refreshDashboard(true)}
                isLoading={isRefreshing}
              />
              <NotificationsWidget
                initialNotifications={dashboardData?.notifications}
                onRefresh={() => refreshDashboard(true)}
                isLoading={isRefreshing}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Shared Slide-Over Contextual Subsystem Drawer */}
      <CommandContextDrawer
        isOpen={isDrawerOpen}
        domain={drawerDomain}
        onClose={closeDrawer}
      />

      {/* Shared Voice 2.0 Settings Modal */}
      <VoiceSettings
        isOpen={isVoiceSettingsOpen}
        onClose={() => setIsVoiceSettingsOpen(false)}
        settings={voiceAssistant.voiceSettings}
        onUpdateSettings={voiceAssistant.updateVoiceSettings}
        activeVoiceInfo={voiceAssistant.activeVoiceInfo}
      />
    </div>
  );
};

export default DashboardPage;
