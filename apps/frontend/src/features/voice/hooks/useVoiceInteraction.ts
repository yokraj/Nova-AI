import { useState, useRef } from 'react';
import { useVoiceState } from './useVoiceState';
import { MockSpeechToTextEngine, MockTextToSpeechEngine, getMockVoiceResponse } from '../mock/mockVoiceEngine';
import { DEFAULT_VOICE_SETTINGS, VoiceSettingsConfig } from '../types/voiceSettings';

export function useVoiceInteraction(onSendToConversation?: (prompt: string) => void) {
  const vState = useVoiceState();
  const [settings, setSettings] = useState<VoiceSettingsConfig>(DEFAULT_VOICE_SETTINGS);
  const sttEngineRef = useRef(new MockSpeechToTextEngine());
  const ttsEngineRef = useRef(new MockTextToSpeechEngine());

  const startListeningSession = () => {
    if (vState.permissionState === 'denied') {
      vState.setVoiceState('PERMISSION_REQUIRED');
      return;
    }

    vState.setVoiceState('LISTENING');
    vState.setLiveTranscript('');
    vState.setPlaybackProgress(0);

    sttEngineRef.current.startListening(
      (partial) => {
        vState.setLiveTranscript(partial);
      },
      (fullTranscript) => {
        vState.setLiveTranscript(fullTranscript);
        vState.setVoiceState('PROCESSING');

        // Pass to conversation thread
        onSendToConversation?.(fullTranscript);

        // Transition to Thinking
        setTimeout(() => {
          vState.setVoiceState('THINKING');

          // Generate response & speak
          setTimeout(() => {
            const resp = getMockVoiceResponse(fullTranscript);
            vState.setLastSpokenText(resp);

            if (settings.autoPlayResponses) {
              vState.setVoiceState('SPEAKING');
              ttsEngineRef.current.speak(
                resp,
                (pct) => vState.setPlaybackProgress(pct),
                () => {
                  if (settings.continuousConversation) {
                    startListeningSession();
                  } else {
                    vState.resetToIdle();
                  }
                }
              );
            } else {
              vState.resetToIdle();
            }
          }, 800);
        }, 500);
      }
    );
  };

  const stopListeningSession = () => {
    sttEngineRef.current.stopListening();
    vState.resetToIdle();
  };

  const interruptSpeech = () => {
    ttsEngineRef.current.stop();
    vState.setVoiceState('STOPPED');
    setTimeout(() => {
      vState.resetToIdle();
    }, 400);
  };

  const pausePlayback = () => {
    ttsEngineRef.current.pause();
    vState.setVoiceState('PAUSED');
  };

  const resumePlayback = () => {
    vState.setVoiceState('SPEAKING');
    ttsEngineRef.current.speak(
      vState.lastSpokenText || 'Resuming Nova voice output...',
      (pct) => vState.setPlaybackProgress(pct),
      () => vState.resetToIdle()
    );
  };

  return {
    ...vState,
    settings,
    setSettings,
    startListeningSession,
    stopListeningSession,
    interruptSpeech,
    pausePlayback,
    resumePlayback,
  };
}
