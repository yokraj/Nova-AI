import { useState, useEffect, useRef, useCallback } from 'react';

export type VoiceState = 'IDLE' | 'LISTENING' | 'TRANSCRIBING' | 'READY' | 'ERROR';

// Declare Web Speech API types for TypeScript
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message?: string;
}

interface SpeechRecognitionInstance extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onstart: ((this: SpeechRecognitionInstance, ev: Event) => any) | null;
  onresult: ((this: SpeechRecognitionInstance, ev: SpeechRecognitionEvent) => any) | null;
  onerror: ((this: SpeechRecognitionInstance, ev: SpeechRecognitionErrorEvent) => any) | null;
  onend: ((this: SpeechRecognitionInstance, ev: Event) => any) | null;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognitionInstance;
}

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

interface UseBrowserSpeechRecognitionOptions {
  onResult?: (transcript: string, isFinal: boolean) => void;
  onError?: (errorMessage: string) => void;
}

export function useBrowserSpeechRecognition(options?: UseBrowserSpeechRecognitionOptions) {
  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE');
  const [transcript, setTranscript] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);

  const isSupported =
    typeof window !== 'undefined' &&
    Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        // Ignore stop errors if already stopped
      }
      recognitionRef.current = null;
    }
    setVoiceState((prev) => (prev === 'LISTENING' || prev === 'TRANSCRIBING' ? 'IDLE' : prev));
  }, []);

  const startListening = useCallback(() => {
    setErrorMessage(null);

    if (!isSupported) {
      const err = 'Voice recognition is unavailable in this browser.';
      setErrorMessage(err);
      setVoiceState('ERROR');
      options?.onError?.(err);
      return;
    }

    const SpeechRecognitionClass = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognitionClass) return;

    try {
      const recognition = new SpeechRecognitionClass();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setVoiceState('LISTENING');
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        setVoiceState('TRANSCRIBING');
        let currentTranscript = '';
        let isFinal = false;

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const res = event.results[i];
          currentTranscript += res[0].transcript;
          if (res.isFinal) {
            isFinal = true;
          }
        }

        setTranscript(currentTranscript);
        options?.onResult?.(currentTranscript, isFinal);

        if (isFinal) {
          setVoiceState('READY');
        }
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        let msg = 'Speech recognition error occurred.';
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          msg = 'Microphone permission denied';
        } else if (event.error === 'no-speech') {
          msg = 'No speech detected';
        } else if (event.error === 'audio-capture') {
          msg = 'No microphone hardware found';
        }
        setErrorMessage(msg);
        setVoiceState('ERROR');
        options?.onError?.(msg);
        recognitionRef.current = null;
      };

      recognition.onend = () => {
        setVoiceState((prev) => {
          if (prev === 'LISTENING' || prev === 'TRANSCRIBING') {
            return 'READY';
          }
          return prev;
        });
        recognitionRef.current = null;
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (e: any) {
      const msg = e?.message || 'Failed to initialize speech recognition.';
      setErrorMessage(msg);
      setVoiceState('ERROR');
      options?.onError?.(msg);
    }
  }, [isSupported, options]);

  const toggleListening = useCallback(() => {
    if (voiceState === 'LISTENING' || voiceState === 'TRANSCRIBING') {
      stopListening();
    } else {
      startListening();
    }
  }, [voiceState, startListening, stopListening]);

  const clearError = useCallback(() => {
    setErrorMessage(null);
    if (voiceState === 'ERROR') {
      setVoiceState('IDLE');
    }
  }, [voiceState]);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // cleanup
        }
      }
    };
  }, []);

  return {
    isSupported,
    voiceState,
    setVoiceState,
    transcript,
    setTranscript,
    errorMessage,
    setErrorMessage,
    startListening,
    stopListening,
    toggleListening,
    clearError,
  };
}

export default useBrowserSpeechRecognition;
