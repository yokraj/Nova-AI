/**
 * Nova Voice 2.0 Settings Configuration and Persistence Layer.
 */

export type VoiceModeType = 'offline_female' | 'neural_female';
export type VoiceIdentityType =
  | 'nova-offline-female'
  | 'nova-neural-female'
  | 'nova-offline'
  | 'nova-indian-pro'
  | 'nova-tamil-pro'
  | 'nova-hindi-pro'
  | 'system-custom';
export type SupportedLanguageType = 'auto' | 'en' | 'ta' | 'hi';
export type ResponseLengthType = 'concise' | 'detailed';
export type VADSensitivityType = 'low' | 'medium' | 'high';

export interface InstalledSapiVoice {
  name: string;
  culture: string;
  gender: string;
  age: string;
  description: string;
  is_female: boolean;
  is_default?: boolean;
}

export interface VoiceSettingsConfig {
  voiceEnabled: boolean;
  autoPlayResponses: boolean;
  continuousConversation: boolean;
  pushToTalk: boolean;
  allowInterrupt: boolean;
  showLiveTranscript: boolean;
  voiceMode: VoiceModeType;
  offlineVoice: string;
  neuralVoice: string;
  voiceIdentity: VoiceIdentityType;
  selectedVoiceName: string;
  language: SupportedLanguageType;
  speakingRate: number;       // 0.8 to 1.4, default 1.05 (youthful natural speed)
  pitch: number;              // 0.8 to 1.3, default 1.08 (youthful elevated female pitch)
  volume: number;             // 0 to 100, default 100
  responseLength: ResponseLengthType;
  handsFreeEnabled: boolean;
  wakePhrase: string;
  vadSensitivity: VADSensitivityType;
}

export const DEFAULT_VOICE_SETTINGS: VoiceSettingsConfig = {
  voiceEnabled: true,
  autoPlayResponses: true,
  continuousConversation: true,
  pushToTalk: false,
  allowInterrupt: true,
  showLiveTranscript: true,
  voiceMode: 'offline_female',
  offlineVoice: 'Microsoft Zira Desktop',
  neuralVoice: 'en-IN-NeerjaNeural',
  voiceIdentity: 'nova-offline-female',
  selectedVoiceName: 'NOVA — Offline Female (Microsoft Zira)',
  language: 'auto',
  speakingRate: 1.05,
  pitch: 1.08,
  volume: 100,
  responseLength: 'concise',
  handsFreeEnabled: false,
  wakePhrase: 'Hey Nova',
  vadSensitivity: 'medium',
};

const STORAGE_KEY = 'nova_voice_settings_v2';

export function loadPersistedVoiceSettings(): VoiceSettingsConfig {
  if (typeof window === 'undefined') return DEFAULT_VOICE_SETTINGS;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_VOICE_SETTINGS;
    const parsed = JSON.parse(raw);
    return { ...DEFAULT_VOICE_SETTINGS, ...parsed };
  } catch {
    return DEFAULT_VOICE_SETTINGS;
  }
}

export function savePersistedVoiceSettings(settings: VoiceSettingsConfig): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  } catch (e) {
    console.warn('Failed to persist voice settings:', e);
  }
}
