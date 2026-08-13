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
  startListening: (onTranscript?: (t: string) => void, onComplete?: (fullT: string) => void) => void;
  stopListening: () => void;
  onTranscript?: (transcript: string) => void;
}

export interface TextToSpeechProvider {
  speak: (text: string, onProgress: (pct: number) => void, onComplete: () => void) => void;
  stop: () => void;
  pause: () => void;
  resume: () => void;
}
