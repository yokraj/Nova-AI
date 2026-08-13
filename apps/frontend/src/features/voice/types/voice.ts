export type VoiceState =
  | 'IDLE'
  | 'LISTENING'
  | 'PROCESSING'
  | 'THINKING'
  | 'RESPONDING'
  | 'SPEAKING'
  | 'PAUSED'
  | 'STOPPED'
  | 'ERROR'
  | 'PERMISSION_REQUIRED';

export type MicrophonePermissionState = 'prompt' | 'granted' | 'denied' | 'unavailable';

export interface VoiceStateInfo {
  state: VoiceState;
  primaryLabel: string;
  subLabel: string;
  glowColor: string;
  orbScale: number[];
}
