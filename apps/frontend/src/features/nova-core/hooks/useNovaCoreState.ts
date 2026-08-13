import { useState } from 'react';
import { NovaCoreState, NovaVoiceState, NovaContextDrawerType } from '../types/novaCore';
import { NovaResponse } from '../types/novaCommand';

export function useNovaCoreState() {
  const [coreState, setCoreState] = useState<NovaCoreState>('IDLE');
  const [voiceState, setVoiceState] = useState<NovaVoiceState>('MIC_READY');
  const [activeDrawer, setActiveDrawer] = useState<NovaContextDrawerType>('none');
  const [latestResponse, setLatestResponse] = useState<NovaResponse | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>('LOCAL-FIRST • VOICE-FIRST');

  const openDrawer = (drawer: NovaContextDrawerType) => {
    setActiveDrawer(drawer);
  };

  const closeDrawer = () => {
    setActiveDrawer('none');
  };

  const resetToIdle = () => {
    setCoreState('IDLE');
    setVoiceState('MIC_READY');
    setStatusMessage('LOCAL-FIRST • VOICE-FIRST');
    setLatestResponse(null);
  };

  return {
    coreState,
    setCoreState,
    voiceState,
    setVoiceState,
    activeDrawer,
    openDrawer,
    closeDrawer,
    latestResponse,
    setLatestResponse,
    statusMessage,
    setStatusMessage,
    resetToIdle,
  };
}
