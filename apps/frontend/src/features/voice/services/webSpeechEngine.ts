import { SpeechToTextProvider, TextToSpeechProvider } from '../types/voiceSession';
import { SpeechPreparationService, FormattedSpeechOutput } from './speechPreparation';

export interface NovaVoiceIdentity {
  id: string;
  name: string;
  language: 'en-IN' | 'ta-IN' | 'hi-IN' | 'auto';
  gender: 'male' | 'female';
  description: string;
  recommendedPitch: number;
  recommendedRate: number;
  isOffline?: boolean;
}

export const NOVA_VOICE_PROFILES: NovaVoiceIdentity[] = [
  {
    id: 'nova-offline-female',
    name: 'NOVA — Offline Female (Windows SAPI)',
    language: 'en-IN',
    gender: 'female',
    description: 'Natural youthful female voice using local Windows SAPI (Microsoft Zira). 100% offline, zero internet.',
    recommendedPitch: 1.08,
    recommendedRate: 1.05,
    isOffline: true,
  },
  {
    id: 'nova-neural-female',
    name: 'NOVA — Neural Female (Edge TTS)',
    language: 'en-IN',
    gender: 'female',
    description: 'High-definition young female voice via Microsoft Edge (Neerja / Pallavi / Swara). Optional online service.',
    recommendedPitch: 1.0,
    recommendedRate: 1.05,
    isOffline: false,
  },
  {
    id: 'nova-offline',
    name: 'NOVA — Offline Local Synthesizer',
    language: 'en-IN',
    gender: 'female',
    description: '100% offline local Windows speech synthesizer. Operates completely without internet.',
    recommendedPitch: 1.08,
    recommendedRate: 1.05,
    isOffline: true,
  },
  {
    id: 'nova-indian-female',
    name: 'NOVA — Indian Female (Neerja)',
    language: 'en-IN',
    gender: 'female',
    description: 'Natural Indian English feminine voice (Optional free online service).',
    recommendedPitch: 1.0,
    recommendedRate: 1.05,
    isOffline: false,
  },
  {
    id: 'nova-tamil-female',
    name: 'NOVA — Tamil Female (Pallavi)',
    language: 'ta-IN',
    gender: 'female',
    description: 'Natural Tamil feminine voice with Tanglish fluency (Optional free online service).',
    recommendedPitch: 1.0,
    recommendedRate: 1.05,
    isOffline: false,
  },
  {
    id: 'nova-hindi-female',
    name: 'NOVA — Hindi Female (Swara)',
    language: 'hi-IN',
    gender: 'female',
    description: 'Natural Hindi feminine voice with Hinglish fluency (Optional free online service).',
    recommendedPitch: 1.0,
    recommendedRate: 1.05,
    isOffline: false,
  },
];

/**
 * Clean text using SpeechPreparationService
 */
export function cleanTextForSpeech(rawText: string, language?: string): string {
  const formatted = SpeechPreparationService.formatResponse(rawText, language);
  return formatted.speechText;
}

/**
 * Returns composed, professional time-based greeting without robotic 'sir' repetition.
 */
export function getTimeBasedGreeting(userName?: string): string {
  const hour = new Date().getHours();
  const salutation =
    hour >= 5 && hour < 12
      ? 'Good morning.'
      : hour >= 12 && hour < 17
      ? 'Good afternoon.'
      : 'Good evening.';

  return `${salutation} Nova online. How can I assist you today?`;
}

/**
 * Select the optimal voice for Nova's Indian Professional profile based on target language.
 */
export function selectNovaVoice(
  voices: SpeechSynthesisVoice[],
  targetLang: string = 'en-IN'
): { voice: SpeechSynthesisVoice | null; voiceName: string; isExactLocale: boolean } {
  if (!voices || voices.length === 0) {
    return { voice: null, voiceName: 'System Default', isExactLocale: false };
  }

  const langLower = targetLang.toLowerCase();

  // 1. TAMIL (ta, ta-IN)
  if (langLower.startsWith('ta')) {
    const tamilPriorities = [
      'Microsoft Valluvar Online (Natural) - Tamil (India)',
      'Microsoft Valluvar',
      'Google தமிழ்',
      'Tamil India',
      'Tamil',
    ];
    for (const name of tamilPriorities) {
      const match = voices.find(
        (v) => v.lang.toLowerCase().includes('ta') && v.name.toLowerCase().includes(name.toLowerCase())
      );
      if (match) return { voice: match, voiceName: match.name, isExactLocale: true };
    }
    const anyTamil = voices.find((v) => v.lang.toLowerCase().startsWith('ta'));
    if (anyTamil) return { voice: anyTamil, voiceName: anyTamil.name, isExactLocale: true };
  }

  // 2. HINDI (hi, hi-IN)
  if (langLower.startsWith('hi')) {
    const hindiPriorities = [
      'Microsoft Madhur Online (Natural) - Hindi (India)',
      'Microsoft Madhur',
      'Microsoft Hemant',
      'Google हिन्दी',
      'Hindi India',
      'Hindi',
    ];
    for (const name of hindiPriorities) {
      const match = voices.find(
        (v) => v.lang.toLowerCase().includes('hi') && v.name.toLowerCase().includes(name.toLowerCase())
      );
      if (match) return { voice: match, voiceName: match.name, isExactLocale: true };
    }
    const anyHindi = voices.find((v) => v.lang.toLowerCase().startsWith('hi'));
    if (anyHindi) return { voice: anyHindi, voiceName: anyHindi.name, isExactLocale: true };
  }

  // 3. INDIAN ENGLISH (en-IN) - Primary Identity
  const indianEnglishPriorities = [
    'Microsoft Prabhat Online (Natural) - English (India)',
    'Microsoft Prabhat',
    'Google English (India)',
    'Microsoft Ravi Online (Natural) - English (India)',
    'Microsoft Ravi',
    'Microsoft Heera',
    'Rishi',
    'en-IN',
    'English (India)',
  ];

  for (const name of indianEnglishPriorities) {
    const match = voices.find(
      (v) =>
        (v.lang.toLowerCase() === 'en-in' || v.name.toLowerCase().includes('india')) &&
        v.name.toLowerCase().includes(name.toLowerCase())
    );
    if (match) return { voice: match, voiceName: match.name, isExactLocale: true };
  }

  // Any en-IN voice
  const anyIndianEn = voices.find(
    (v) => v.lang.toLowerCase() === 'en-in' || v.name.toLowerCase().includes('india')
  );
  if (anyIndianEn) return { voice: anyIndianEn, voiceName: anyIndianEn.name, isExactLocale: true };

  // Fallback: Male / Natural English voice with composed timbre
  const composedEnPriorities = [
    'Google UK English Male',
    'Microsoft George Online (Natural)',
    'Microsoft George',
    'Microsoft Ryan Online (Natural)',
    'Microsoft David',
  ];
  for (const name of composedEnPriorities) {
    const match = voices.find(
      (v) => v.lang.toLowerCase().startsWith('en') && v.name.toLowerCase().includes(name.toLowerCase())
    );
    if (match) return { voice: match, voiceName: match.name, isExactLocale: false };
  }

  const anyEnglish = voices.find((v) => v.lang.toLowerCase().startsWith('en'));
  if (anyEnglish) return { voice: anyEnglish, voiceName: anyEnglish.name, isExactLocale: false };

  return { voice: voices[0], voiceName: voices[0].name, isExactLocale: false };
}

/**
 * Real Web Speech STT Engine using native browser SpeechRecognition API.
 */
export class WebSpeechToTextEngine implements SpeechToTextProvider {
  private recognition: any = null;
  private isListening = false;
  private activeLanguage = 'en-IN';

  constructor(language: string = 'en-IN') {
    this.activeLanguage = language;
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = this.activeLanguage;
      }
    }
  }

  setLanguage(lang: string): void {
    this.activeLanguage = lang;
    if (this.recognition) {
      this.recognition.lang = lang;
    }
  }

  isSupported(): boolean {
    return (
      typeof window !== 'undefined' &&
      Boolean((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition)
    );
  }

  startListening(
    onTranscript?: (partial: string) => void,
    onComplete?: (full: string) => void,
    onError?: (error: string) => void
  ): void {
    if (!this.isSupported()) {
      onError?.('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    try {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = this.activeLanguage;

      this.isListening = true;
      let finalTranscript = '';
      let latestInterim = '';

      this.recognition.onresult = (event: any) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const piece = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += piece;
          } else {
            interimTranscript += piece;
          }
        }
        latestInterim = interimTranscript;
        const currentText = (finalTranscript + ' ' + interimTranscript).trim();
        onTranscript?.(currentText);
      };

      this.recognition.onerror = (event: any) => {
        this.isListening = false;
        let errMsg = 'Speech recognition error occurred.';
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          errMsg = 'Microphone permission denied. Please allow microphone access in your browser.';
        } else if (event.error === 'no-speech') {
          errMsg = 'No speech detected.';
        } else if (event.error === 'audio-capture') {
          errMsg = 'No microphone hardware found or input was interrupted.';
        } else if (event.error === 'network') {
          errMsg = 'Network error during voice recognition.';
        }
        onError?.(errMsg);
      };

      this.recognition.onend = () => {
        const fullText = (finalTranscript || latestInterim).trim();
        this.isListening = false;
        if (fullText) {
          onComplete?.(fullText);
        }
      };

      this.recognition.start();
    } catch (err: any) {
      this.isListening = false;
      onError?.(err?.message || 'Failed to start speech recognition.');
    }
  }

  stopListening(): void {
    this.isListening = false;
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch {}
      this.recognition = null;
    }
  }
}

/**
 * Nova Indian Professional Multilingual Text-To-Speech Engine.
 * Features:
 * - Specific voice selection for Indian English (en-IN), Tamil (ta-IN), and Hindi (hi-IN).
 * - Segmented breath-pause synthesis for responsive playback.
 * - Calibrated pitch (0.92) and pacing (1.0) for mature, composed delivery.
 * - Immediate barge-in audio halt.
 */
export class WebTextToSpeechEngine implements TextToSpeechProvider {
  private activeVoices: SpeechSynthesisVoice[] = [];
  private isSynthesizing = false;
  private cancelRequested = false;
  private currentLanguage = 'en-IN';
  private currentPitch = 0.92; // Medium-deep pitch for Nova Indian Professional
  private currentRate = 1.0;
  private currentVolume = 1.0;

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.loadVoices();
      window.speechSynthesis.onvoiceschanged = () => {
        this.loadVoices();
      };
    }
  }

  private loadVoices(): void {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;
    this.activeVoices = window.speechSynthesis.getVoices();
  }

  isSupported(): boolean {
    return typeof window !== 'undefined' && 'speechSynthesis' in window;
  }

  isSpeaking(): boolean {
    return this.isSynthesizing || (typeof window !== 'undefined' && Boolean(window.speechSynthesis?.speaking));
  }

  configureVoiceParameters(pitch: number = 0.92, rate: number = 1.0, volume: number = 1.0): void {
    this.currentPitch = Math.max(0.5, Math.min(1.5, pitch));
    this.currentRate = Math.max(0.5, Math.min(1.5, rate));
    this.currentVolume = Math.max(0.0, Math.min(1.0, volume));
  }

  setLanguage(language: string): void {
    this.currentLanguage = language;
  }

  getActiveVoiceInfo(targetLang?: string): { name: string; lang: string; isExactLocale: boolean } {
    this.loadVoices();
    const lang = targetLang || this.currentLanguage;
    const { voice, voiceName, isExactLocale } = selectNovaVoice(this.activeVoices, lang);
    return {
      name: voiceName,
      lang: voice?.lang || lang,
      isExactLocale,
    };
  }

  getAllInstalledVoices(): SpeechSynthesisVoice[] {
    this.loadVoices();
    return this.activeVoices;
  }

  /**
   * Synthesize text with natural speech preparation and sequential chunk playback.
   */
  speak(
    text: string,
    onProgress?: (progressPct: number) => void,
    onComplete?: () => void,
    onError?: (error: string) => void,
    overrideLanguage?: string
  ): void {
    if (!this.isSupported()) {
      onError?.('Speech synthesis is not supported in this browser environment.');
      return;
    }

    this.stop();
    this.cancelRequested = false;
    this.isSynthesizing = true;

    const lang = overrideLanguage || this.currentLanguage;
    const formatted = SpeechPreparationService.formatResponse(text, lang);
    const chunks = formatted.speechChunks;

    if (!chunks || chunks.length === 0 || !chunks[0]) {
      this.isSynthesizing = false;
      onComplete?.();
      return;
    }

    const { voice } = selectNovaVoice(this.activeVoices, formatted.detectedLanguage);

    let currentChunkIdx = 0;

    const speakNextChunk = () => {
      if (this.cancelRequested || currentChunkIdx >= chunks.length) {
        this.isSynthesizing = false;
        if (!this.cancelRequested) {
          onProgress?.(100);
          onComplete?.();
        }
        return;
      }

      const chunkText = chunks[currentChunkIdx];
      const utterance = new SpeechSynthesisUtterance(chunkText);

      if (voice) {
        utterance.voice = voice;
      }

      // Map language code to utterance
      if (formatted.detectedLanguage === 'ta') {
        utterance.lang = 'ta-IN';
      } else if (formatted.detectedLanguage === 'hi') {
        utterance.lang = 'hi-IN';
      } else {
        utterance.lang = 'en-IN';
      }

      utterance.pitch = this.currentPitch;
      utterance.rate = this.currentRate;
      utterance.volume = this.currentVolume;

      utterance.onstart = () => {
        const pct = Math.round((currentChunkIdx / chunks.length) * 100);
        onProgress?.(pct);
      };

      utterance.onend = () => {
        currentChunkIdx++;
        speakNextChunk();
      };

      utterance.onerror = (e) => {
        if (this.cancelRequested || e.error === 'canceled' || e.error === 'interrupted') {
          this.isSynthesizing = false;
          return;
        }
        this.isSynthesizing = false;
        onError?.(`Voice synthesis error: ${e.error}`);
      };

      try {
        window.speechSynthesis.speak(utterance);
      } catch (err: any) {
        this.isSynthesizing = false;
        onError?.(err?.message || 'Failed to dispatch speech synthesis utterance.');
      }
    };

    speakNextChunk();
  }

  stop(): void {
    this.cancelRequested = true;
    this.isSynthesizing = false;
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
      } catch {}
    }
  }

  pause(): void {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      try {
        window.speechSynthesis.pause();
      } catch {}
    }
  }

  resume(): void {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      try {
        window.speechSynthesis.resume();
      } catch {}
    }
  }
}
