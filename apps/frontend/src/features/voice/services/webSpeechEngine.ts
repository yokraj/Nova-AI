import { SpeechToTextProvider, TextToSpeechProvider } from '../types/voiceSession';

/**
 * Clean markdown, code blocks, thinking tags, and URLs before sending to SpeechSynthesis
 * so Nova speaks crisp, natural English without reciting syntax aloud.
 */
export function cleanTextForSpeech(rawText: string): string {
  if (!rawText) return '';
  let cleaned = rawText;

  // Strip <think>...</think> tags and internal thinking text
  cleaned = cleaned.replace(/<think>[\s\S]*?<\/think>/gi, '');

  // Strip code blocks ```language ... ```
  cleaned = cleaned.replace(/```[\s\S]*?```/g, ' Code block omitted. ');

  // Strip inline code backticks `code`
  cleaned = cleaned.replace(/`([^`]+)`/g, '$1');

  // Strip markdown bold/italics
  cleaned = cleaned.replace(/(\*\*|__)(.*?)\1/g, '$2');
  cleaned = cleaned.replace(/(\*|_)(.*?)\1/g, '$2');

  // Strip markdown headers #, ##, etc.
  cleaned = cleaned.replace(/^#+\s+/gm, '');

  // Strip markdown links [text](url) -> text
  cleaned = cleaned.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

  // Strip standalone URLs
  cleaned = cleaned.replace(/https?:\/\/\S+/g, '');

  // Strip markdown list bullets -, *, +
  cleaned = cleaned.replace(/^\s*[-*+]\s+/gm, '');

  // Collapse multiple spaces/newlines
  cleaned = cleaned.replace(/\s+/g, ' ').trim();

  return cleaned;
}

/**
 * Returns dynamic greeting based on user's local time:
 * - Morning (05:00 - 11:59): "Good morning, sir. I'm Nova. How may I assist you?"
 * - Afternoon (12:00 - 16:59): "Good afternoon, sir. I'm Nova. How may I assist you?"
 * - Evening (17:00 - 20:59): "Good evening, sir. I'm Nova. How may I assist you?"
 * - Night (21:00 - 04:59): "Good evening, sir. I'm Nova. How may I assist you?"
 */
export function getTimeBasedGreeting(userName?: string): string {
  const hour = new Date().getHours();
  let salutation = 'Good morning, sir.';
  if (hour >= 12 && hour < 17) {
    salutation = 'Good afternoon, sir.';
  } else if (hour >= 17 && hour < 21) {
    salutation = 'Good evening, sir.';
  } else if (hour >= 21 || hour < 5) {
    salutation = 'Good evening, sir.';
  }
  return `${salutation} I'm Nova. How may I assist you?`;
}

/**
 * Select natural, high-quality English voice (JARVIS style) from browser voices.
 */
export function selectNaturalEnglishVoice(voices: SpeechSynthesisVoice[]): SpeechSynthesisVoice | null {
  if (!voices || voices.length === 0) return null;

  const jarvisPriority = [
    'Google UK English Male',
    'Microsoft George Online (Natural)',
    'Microsoft George',
    'Microsoft Ryan Online (Natural)',
    'Microsoft Christopher Online (Natural)',
    'Microsoft Guy Online (Natural)',
    'Daniel',
    'Oliver',
    'Google US English',
    'Microsoft David',
  ];

  for (const name of jarvisPriority) {
    const match = voices.find(
      (v) => v.name.toLowerCase().includes(name.toLowerCase()) && v.lang.startsWith('en')
    );
    if (match) return match;
  }

  // Any English voice with "Natural" or "Online"
  const naturalEn = voices.find(
    (v) => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Online'))
  );
  if (naturalEn) return naturalEn;

  // Any English voice
  const anyEn = voices.find((v) => v.lang.startsWith('en'));
  if (anyEn) return anyEn;

  return voices[0] || null;
}

/**
 * Real Web Speech STT Engine using native browser SpeechRecognition API.
 */
export class WebSpeechToTextEngine implements SpeechToTextProvider {
  private recognition: any = null;
  private isListening = false;

  constructor() {
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';
      }
    }
  }

  isSupported(): boolean {
    return (
      typeof window !== 'undefined' &&
      Boolean((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition)
    );
  }

  async requestMicrophonePermission(): Promise<boolean> {
    if (typeof navigator === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
      return true;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
      return true;
    } catch {
      return false;
    }
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
      this.recognition.lang = 'en-US';

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
      } catch {
        // Ignored
      }
      this.recognition = null;
    }
  }
}

/**
 * Real Web Speech Synthesis Engine with natural voice selection,
 * time-based greeting, barge-in cancellation, and clean text preprocessing.
 */
export class WebTextToSpeechEngine implements TextToSpeechProvider {
  private currentUtterance: SpeechSynthesisUtterance | null = null;
  private cachedVoice: SpeechSynthesisVoice | null = null;

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.initVoice();
      window.speechSynthesis.onvoiceschanged = () => {
        this.initVoice();
      };
    }
  }

  private initVoice(): void {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;
    const voices = window.speechSynthesis.getVoices();
    this.cachedVoice = selectNaturalEnglishVoice(voices);
  }

  isSupported(): boolean {
    return typeof window !== 'undefined' && 'speechSynthesis' in window;
  }

  isSpeaking(): boolean {
    return (
      typeof window !== 'undefined' &&
      'speechSynthesis' in window &&
      (window.speechSynthesis.speaking || Boolean(this.currentUtterance))
    );
  }

  speak(
    text: string,
    onProgress?: (pct: number) => void,
    onComplete?: () => void,
    onError?: (err: string) => void
  ): void {
    if (!this.isSupported()) {
      onError?.('Speech synthesis is not supported in this browser.');
      return;
    }

    try {
      // Cancel any ongoing speech for immediate barge-in response
      window.speechSynthesis.cancel();

      const spokenText = cleanTextForSpeech(text);
      if (!spokenText) {
        onComplete?.();
        return;
      }

      const utterance = new SpeechSynthesisUtterance(spokenText);
      this.currentUtterance = utterance;

      // Select natural English voice
      if (!this.cachedVoice) {
        this.initVoice();
      }
      if (this.cachedVoice) {
        utterance.voice = this.cachedVoice;
      }

      utterance.rate = 1.0;
      utterance.pitch = 1.0;

      const totalChars = Math.max(1, spokenText.length);

      utterance.onboundary = (e: SpeechSynthesisEvent) => {
        if (e.charIndex && onProgress) {
          const pct = Math.min(100, Math.round((e.charIndex / totalChars) * 100));
          onProgress(pct);
        }
      };

      utterance.onend = () => {
        this.currentUtterance = null;
        onProgress?.(100);
        onComplete?.();
      };

      utterance.onerror = (e) => {
        this.currentUtterance = null;
        if (e.error !== 'canceled' && e.error !== 'interrupted') {
          onError?.(`Speech synthesis error: ${e.error}`);
        } else {
          onComplete?.();
        }
      };

      window.speechSynthesis.speak(utterance);
    } catch (err: any) {
      this.currentUtterance = null;
      onError?.(err?.message || 'Speech synthesis failed to execute.');
    }
  }

  speakGreeting(
    onComplete?: () => void,
    onError?: (err: string) => void
  ): void {
    const greeting = getTimeBasedGreeting();
    this.speak(greeting, undefined, onComplete, onError);
  }

  stop(): void {
    if (this.isSupported()) {
      window.speechSynthesis.cancel();
      this.currentUtterance = null;
    }
  }

  pause(): void {
    if (this.isSupported()) {
      window.speechSynthesis.pause();
    }
  }

  resume(): void {
    if (this.isSupported()) {
      window.speechSynthesis.resume();
    }
  }
}
