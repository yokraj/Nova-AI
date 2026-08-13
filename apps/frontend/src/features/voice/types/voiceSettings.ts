export interface VoiceSettingsConfig {
  voiceEnabled: boolean;
  autoPlayResponses: boolean;
  continuousConversation: boolean;
  pushToTalk: boolean;
  responseSpeed: number; // 0.8 to 1.5
  voiceVolume: number; // 0 to 100
  allowInterrupt: boolean;
  showLiveTranscript: boolean;
  language: 'English' | 'Tamil' | 'Hindi' | 'Malayalam' | 'Kannada' | 'Telugu';
  selectedVoice: string;
}

export const DEFAULT_VOICE_SETTINGS: VoiceSettingsConfig = {
  voiceEnabled: true,
  autoPlayResponses: true,
  continuousConversation: false,
  pushToTalk: false,
  responseSpeed: 1.0,
  voiceVolume: 90,
  allowInterrupt: true,
  showLiveTranscript: true,
  language: 'English',
  selectedVoice: 'Nova Neural Voice (Cyan Core)',
};
