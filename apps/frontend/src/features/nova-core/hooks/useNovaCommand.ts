import { useNovaCoreState } from './useNovaCoreState';
import { simulateNovaCommandEngine } from '../mock/mockNovaEngine';
import { NovaCommandMode } from '../types/novaCommand';

export function useNovaCommand() {
  const coreState = useNovaCoreState();

  const handleSendCommand = (prompt: string, mode: NovaCommandMode = 'text') => {
    if (!prompt.trim()) return;

    coreState.setCoreState('THINKING');
    coreState.setStatusMessage(`Processing: "${prompt}"`);

    simulateNovaCommandEngine(
      prompt,
      (step) => {
        coreState.setCoreState(step.state);
        coreState.setStatusMessage(step.text);
        if (step.responsePayload) {
          coreState.setLatestResponse({
            commandId: `cmd_${Date.now()}`,
            prompt,
            state: step.state,
            executionStage: 'COMPLETE',
            spokenText: step.responsePayload.spokenText || step.text,
            detailedOutput: step.responsePayload.detailedOutput,
            assignedAgent: step.responsePayload.assignedAgent,
            missionId: step.responsePayload.missionId,
            securityApprovalRequired: step.responsePayload.securityApprovalRequired,
            securityActionTitle: step.responsePayload.securityActionTitle,
            securityRiskLevel: step.responsePayload.securityRiskLevel,
            suggestedDrawer: step.responsePayload.suggestedDrawer,
          });
        }
      },
      (drawer) => {
        coreState.openDrawer(drawer);
      }
    );
  };

  const handleToggleMic = () => {
    if (coreState.voiceState === 'LISTENING') {
      coreState.setVoiceState('MIC_READY');
      coreState.setCoreState('IDLE');
      coreState.setStatusMessage('Voice muted');
    } else {
      coreState.setVoiceState('LISTENING');
      coreState.setCoreState('LISTENING');
      coreState.setStatusMessage('Listening for voice prompt...');
      setTimeout(() => {
        handleSendCommand('Hey Nova, analyze my project architecture');
      }, 2500);
    }
  };

  const handleApproveSecurity = () => {
    coreState.setCoreState('EXECUTING');
    coreState.setStatusMessage('Security Gate Approved • Executing Action...');
    setTimeout(() => {
      coreState.setCoreState('SUCCESS');
      coreState.setStatusMessage('Action completed successfully under owner approval.');
      if (coreState.latestResponse) {
        coreState.setLatestResponse({
          ...coreState.latestResponse,
          securityApprovalRequired: false,
          spokenText: 'Action approved and executed nominal.',
        });
      }
    }, 1200);
  };

  const handleRejectSecurity = () => {
    coreState.setCoreState('ERROR');
    coreState.setStatusMessage('Security Gate Blocked • Action Rejected by User.');
    if (coreState.latestResponse) {
      coreState.setLatestResponse({
        ...coreState.latestResponse,
        securityApprovalRequired: false,
        spokenText: 'Action was rejected and cancelled.',
      });
    }
  };

  return {
    ...coreState,
    handleSendCommand,
    handleToggleMic,
    handleApproveSecurity,
    handleRejectSecurity,
  };
}
