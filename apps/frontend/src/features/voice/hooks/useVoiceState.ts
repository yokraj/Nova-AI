import { useState } from 'react';
import { VoiceState, MicrophonePermissionState } from '../types/voice';

export function useVoiceState() {
  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE');
  const [permissionState, setPermissionState] = useState<MicrophonePermissionState>('granted');
  const [liveTranscript, setLiveTranscript] = useState<string>('');
  const [playbackProgress, setPlaybackProgress] = useState<number>(0);
  const [lastSpokenText, setLastSpokenText] = useState<string>('');

  const resetToIdle = () => {
    setVoiceState('IDLE');
    setLiveTranscript('');
    setPlaybackProgress(0);
  };

  return {
    voiceState,
    setVoiceState,
    permissionState,
    setPermissionState,
    liveTranscript,
    setLiveTranscript,
    playbackProgress,
    setPlaybackProgress,
    lastSpokenText,
    setLastSpokenText,
    resetToIdle,
  };
}
