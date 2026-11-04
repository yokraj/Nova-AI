import { useState, useRef, useCallback } from 'react';
import { useVoiceState } from './useVoiceState';
import { WebSpeechToTextEngine, WebTextToSpeechEngine } from '../services/webSpeechEngine';
import { executeRealStreamingResponse } from '@/features/conversation/services/realConversationEngine';
import { DEFAULT_VOICE_SETTINGS, VoiceSettingsConfig, loadPersistedVoiceSettings } from '../types/voiceSettings';

export function useVoiceInteraction(onSendToConversation?: (prompt: string) => void) {
  const vState = useVoiceState();
  const [settings, setSettings] = useState<VoiceSettingsConfig>(() => loadPersistedVoiceSettings());
  const [isMuted, setIsMuted] = useState(false);
  const [isPushToTalkActive, setIsPushToTalkActive] = useState(false);

  const sttEngineRef = useRef(new WebSpeechToTextEngine());
  const ttsEngineRef = useRef(new WebTextToSpeechEngine());

  const startListeningSession = useCallback(() => {
    if (isMuted) return;
    if (vState.permissionState === 'denied') {
      vState.setVoiceState('PERMISSION_REQUIRED');
      return;
    }

    // Immediate cancellation of any prior speech output (barge-in interruption)
    ttsEngineRef.current.stop();

    vState.setVoiceState('LISTENING');
    vState.setLiveTranscript('');
    vState.setPlaybackProgress(0);

    sttEngineRef.current.startListening(
      (partial) => {
        vState.setLiveTranscript(partial);
      },
      (fullTranscript) => {
        if (!fullTranscript.trim()) {
          vState.resetToIdle();
          return;
        }

        vState.setLiveTranscript(fullTranscript);
        vState.setVoiceState('PROCESSING');

        // Pass to conversation thread & execution pipeline
        onSendToConversation?.(fullTranscript);

        vState.setVoiceState('THINKING');

        executeRealStreamingResponse(
          fullTranscript,
          (update) => {
            if (update.streamingContent) {
              vState.setLiveTranscript(update.streamingContent);
            }
            if (update.isComplete) {
              const resp =
                update.blocks && update.blocks[0]?.content
                  ? update.blocks[0].content
                  : update.streamingContent || 'Execution verified.';
              vState.setLastSpokenText(resp);

              if (settings.autoPlayResponses && !isMuted) {
                vState.setVoiceState('SPEAKING');
                ttsEngineRef.current.speak(
                  resp,
                  (pct) => vState.setPlaybackProgress(pct),
                  () => {
                    if (settings.continuousConversation && !isMuted) {
                      startListeningSession();
                    } else {
                      vState.resetToIdle();
                    }
                  }
                );
              } else {
                vState.resetToIdle();
              }
            }
          }
        );
      }
    );
  }, [isMuted, onSendToConversation, settings.autoPlayResponses, settings.continuousConversation, vState]);

  const stopListeningSession = useCallback(() => {
    sttEngineRef.current.stopListening();
    setIsPushToTalkActive(false);
    vState.resetToIdle();
  }, [vState]);

  // Barge-in interruption
  const interruptSpeech = useCallback(() => {
    ttsEngineRef.current.stop();
    vState.setVoiceState('STOPPED');
    setTimeout(() => {
      vState.resetToIdle();
    }, 300);
  }, [vState]);

  const pausePlayback = useCallback(() => {
    ttsEngineRef.current.pause();
    vState.setVoiceState('PAUSED');
  }, [vState]);

  const resumePlayback = useCallback(() => {
    vState.setVoiceState('SPEAKING');
    ttsEngineRef.current.speak(
      vState.lastSpokenText || 'Resuming Nova voice output...',
      (pct) => vState.setPlaybackProgress(pct),
      () => vState.resetToIdle()
    );
  }, [vState]);

  const toggleMute = useCallback(() => {
    setIsMuted((prev) => {
      const next = !prev;
      if (next) {
        ttsEngineRef.current.stop();
        sttEngineRef.current.stopListening();
        vState.resetToIdle();
      }
      return next;
    });
  }, [vState]);

  const handlePushToTalkStart = useCallback(() => {
    if (isMuted) return;
    setIsPushToTalkActive(true);
    startListeningSession();
  }, [isMuted, startListeningSession]);

  const handlePushToTalkEnd = useCallback(() => {
    setIsPushToTalkActive(false);
    stopListeningSession();
  }, [stopListeningSession]);

  return {
    ...vState,
    settings,
    setSettings,
    isMuted,
    toggleMute,
    isPushToTalkActive,
    handlePushToTalkStart,
    handlePushToTalkEnd,
    startListeningSession,
    stopListeningSession,
    interruptSpeech,
    pausePlayback,
    resumePlayback,
  };
}
