import React, { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';
import { useDashboardData } from '@/hooks/useDashboardData';
import { useUniversalCommand } from '@/features/universal-command/hooks/useUniversalCommand';
import { useNovaVoiceAssistant } from '@/features/voice/hooks/useNovaVoiceAssistant';
import { NovaCoreState } from '@/features/nova-core/types/novaCore';
import { CommandVisualState } from '@/types/dashboard';

// JARVIS-Inspired Core Components
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

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [rightPanelsOpen, setRightPanelsOpen] = useState(true);
  const [isVoiceSettingsOpen, setIsVoiceSettingsOpen] = useState(false);

  // Live real data hooks
  const {
    data: dashboardData,
    connectionStatus,
    refresh: refreshDashboard,
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

  // Real voice interaction assistant (SpeechSynthesis + SpeechRecognition)
  const voiceAssistant = useNovaVoiceAssistant({
    onExecuteCommand: async (cmdText) => {
      return await processCommand(cmdText, 'VOICE');
    },
    userName: user?.name || 'sir',
  });

  // Map execution and voice state to central holographic core state
  const getCoreState = (): NovaCoreState => {
    // 1. Voice interaction states take visual precedence on the core
    if (voiceAssistant.voiceState !== 'IDLE') {
      return voiceAssistant.voiceState;
    }

    // 2. Command execution states
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
        processCommand(defaultPrompt, 'TEXT');
        break;
      case 'run_task':
        processCommand(defaultPrompt, 'TEXT');
        break;
      case 'automate':
        navigate('/automation');
        break;
      case 'create':
        processCommand(defaultPrompt, 'TEXT');
        break;
    }
  };

  return (
    <div className="w-full min-h-full max-w-[1920px] mx-auto flex min-w-0 jarvis-bg-grid relative overflow-x-hidden px-3 sm:px-6 py-2 sm:py-3 lg:py-4">
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

        {/* 2. Four Surrounding Compact Intelligence Capabilities (THINK, SEE, DO, CONTROL) */}
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

        {/* 4. Active In-Flight Multi-Step Execution Pipeline (When active task in progress) */}
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

        {/* 5. Bottom Quick Actions (Open App, Run Task, Automate, Create) */}
        <div className="w-full max-w-3xl px-2">
          <JarvisBottomQuickActions onActionClick={handleQuickAction} />
        </div>
      </div>

      {/* Right-Side Collapsible Context Panels (System Status, Active Agents, Live Activity) */}
      <div className="hidden lg:flex ml-4 shrink-0 h-[calc(100vh-6.5rem)] sticky top-2">
        <JarvisRightContextPanels
          telemetry={dashboardData?.telemetry}
          agents={dashboardData?.agents}
          activities={dashboardData?.timeline}
          isConnected={connectionStatus === 'connected'}
          isCollapsed={!rightPanelsOpen}
          onToggleCollapse={() => setRightPanelsOpen(!rightPanelsOpen)}
        />
      </div>

      {/* Slide-Over Contextual Subsystem Drawer (Preserved for full detail inspection) */}
      <CommandContextDrawer
        isOpen={isDrawerOpen}
        domain={drawerDomain}
        onClose={closeDrawer}
      />

      {/* Nova Voice 2.0 Intelligence & Personality Settings Modal */}
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
