import { SpeechToTextProvider, TextToSpeechProvider } from '../types/voiceSession';
import { MockSpeechToTextEngine, MockTextToSpeechEngine } from '../mock/mockVoiceEngine';

/**
 * Real Web Speech STT Engine with fallback to Mock engine if browser lacks speech API.
 */
export class WebSpeechToTextEngine implements SpeechToTextProvider {
  private recognition: any = null;
  private fallbackEngine = new MockSpeechToTextEngine();
  private isListening = false;

  constructor() {
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';
      }
    }
  }

  isSupported(): boolean {
    return this.recognition !== null;
  }

  startListening(
    onTranscript?: (partial: string) => void,
    onComplete?: (full: string) => void
  ): void {
    if (!this.recognition) {
      this.fallbackEngine.startListening(onTranscript, onComplete);
      return;
    }

    try {
      this.isListening = true;
      let finalTranscript = '';

      this.recognition.onresult = (event: any) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const transcriptPiece = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcriptPiece;
          } else {
            interimTranscript += transcriptPiece;
          }
        }
        const currentText = (finalTranscript + ' ' + interimTranscript).trim();
        onTranscript?.(currentText);
      };

      this.recognition.onerror = (event: any) => {
        if (event.error === 'no-speech') return;
        this.stopListening();
        if (finalTranscript.trim()) {
          onComplete?.(finalTranscript.trim());
        }
      };

      this.recognition.onend = () => {
        if (this.isListening) {
          if (finalTranscript.trim()) {
            onComplete?.(finalTranscript.trim());
          }
          this.isListening = false;
        }
      };

      this.recognition.start();
    } catch {
      this.fallbackEngine.startListening(onTranscript, onComplete);
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
    } else {
      this.fallbackEngine.stopListening();
    }
  }
}

/**
 * Real Web Speech Synthesis Engine with barge-in interruption and progress tracking.
 */
export class WebTextToSpeechEngine implements TextToSpeechProvider {
  private fallbackEngine = new MockTextToSpeechEngine();
  private currentUtterance: SpeechSynthesisUtterance | null = null;

  isSupported(): boolean {
    return typeof window !== 'undefined' && 'speechSynthesis' in window;
  }

  speak(text: string, onProgress: (pct: number) => void, onComplete: () => void): void {
    if (!this.isSupported()) {
      this.fallbackEngine.speak(text, onProgress, onComplete);
      return;
    }

    try {
      // Immediate cancellation of any prior speech for clean barge-in
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      this.currentUtterance = utterance;
      utterance.rate = 1.0;
      utterance.pitch = 1.0;

      const totalChars = Math.max(1, text.length);

      utterance.onboundary = (e: SpeechSynthesisEvent) => {
        if (e.charIndex) {
          const pct = Math.min(100, Math.round((e.charIndex / totalChars) * 100));
          onProgress(pct);
        }
      };

      utterance.onend = () => {
        this.currentUtterance = null;
        onProgress(100);
        onComplete();
      };

      utterance.onerror = () => {
        this.currentUtterance = null;
        onComplete();
      };

      window.speechSynthesis.speak(utterance);
    } catch {
      this.fallbackEngine.speak(text, onProgress, onComplete);
    }
  }

  stop(): void {
    if (this.isSupported()) {
      window.speechSynthesis.cancel();
      this.currentUtterance = null;
    } else {
      this.fallbackEngine.stop();
    }
  }

  pause(): void {
    if (this.isSupported()) {
      window.speechSynthesis.pause();
    } else {
      this.fallbackEngine.pause();
    }
  }

  resume(): void {
    if (this.isSupported()) {
      window.speechSynthesis.resume();
    } else {
      this.fallbackEngine.resume();
    }
  }
}

