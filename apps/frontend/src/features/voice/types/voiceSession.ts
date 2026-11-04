import { VoiceState } from './voice';

export interface VoiceSession {
  sessionId: string;
  state: VoiceState;
  liveTranscript: string;
  normalizedCommand?: string;
  spokenResponse?: string;
  playbackProgress: number; // 0 to 100
  durationSeconds: number;
  errorReason?: string;
}

export interface SpeechToTextProvider {
  startListening: (
    onTranscript?: (t: string) => void,
    onComplete?: (fullT: string) => void,
    onError?: (err: string) => void
  ) => void;
  stopListening: () => void;
  onTranscript?: (transcript: string) => void;
}

export type HandsFreeVoiceState =
  | 'SLEEPING'
  | 'IDLE'
  | 'LISTENING'
  | 'THINKING'
  | 'SPEAKING'
  | 'INTERRUPTED'
  | 'ERROR';

export interface HandsFreeConfig {
  enabled: boolean;
  wakePhrase: string;
  acknowledgmentType: 'chime' | 'spoken' | 'both';
  continuousConversation: boolean;
  silenceTimeoutMs: number;
  followupWindowMs: number;
  sensitivity: 'low' | 'medium' | 'high';
}

export interface TextToSpeechProvider {
  speak: (
    text: string,
    onProgress?: (pct: number) => void,
    onComplete?: () => void,
    onError?: (err: string) => void
  ) => void;
  stop: () => void;
  pause: () => void;
  resume: () => void;
}
