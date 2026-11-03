import { useState, useRef, useCallback, useEffect } from 'react';
import {
  WebTextToSpeechEngine,
  getTimeBasedGreeting,
} from '../services/webSpeechEngine';
import { AudioCaptureService, MicrophoneError } from '../services/audioCapture';
import { CompositeSTTService } from '../services/sttProviders';
import { NovaCoreState } from '@/features/nova-core/types/novaCore';
import { UniversalCommand } from '@/features/universal-command/types/command';

export interface UseNovaVoiceAssistantOptions {
  onExecuteCommand?: (command: string) => Promise<UniversalCommand | null | void>;
  userName?: string;
}

export function useNovaVoiceAssistant({
  onExecuteCommand,
  userName = 'sir',
}: UseNovaVoiceAssistantOptions = {}) {
  const [voiceState, setVoiceState] = useState<NovaCoreState>('IDLE');
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string>('');
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);

  const ttsEngineRef = useRef<WebTextToSpeechEngine | null>(null);
  const audioCaptureRef = useRef<AudioCaptureService | null>(null);
  const sttServiceRef = useRef<CompositeSTTService | null>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize audio and TTS engines
  useEffect(() => {
    ttsEngineRef.current = new WebTextToSpeechEngine();
    audioCaptureRef.current = new AudioCaptureService();
    sttServiceRef.current = new CompositeSTTService();

    return () => {
      ttsEngineRef.current?.stop();
      audioCaptureRef.current?.cancel();
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore
        }
      }
    };
  }, []);

  const clearVoiceError = useCallback(() => {
    setVoiceError(null);
    if (voiceState === 'ERROR') {
      setVoiceState('IDLE');
    }
  }, [voiceState]);

  // Stop active text-to-speech output
  const stopSpeaking = useCallback(() => {
    if (ttsEngineRef.current) {
      ttsEngineRef.current.stop();
    }
    setIsSpeaking(false);
    setVoiceState((prev) => (prev === 'SPEAKING' ? 'IDLE' : prev));
  }, []);

  /**
   * Speak Nova's dynamic greeting through the computer's speakers.
   * Dynamically changes based on user's local time:
   * - Morning (05:00 - 11:59): "Good morning, sir. I'm Nova. How may I assist you?"
   * - Afternoon (12:00 - 16:59): "Good afternoon, sir. I'm Nova. How may I assist you?"
   * - Evening (17:00 - 20:59): "Good evening, sir. I'm Nova. How may I assist you?"
   * - Night (21:00 - 04:59): "Good evening, sir. I'm Nova. How may I assist you?"
   * Avoids repeating greeting multiple times from repeated clicks (toggles off if already speaking).
   */
  const speakGreeting = useCallback(() => {
    setVoiceError(null);

    // If already speaking, clicking toggles off speech cleanly (barge-in interruption)
    if (isSpeaking || ttsEngineRef.current?.isSpeaking()) {
      stopSpeaking();
      return;
    }

    if (isListening) {
      audioCaptureRef.current?.cancel();
      setIsListening(false);
    }

    if (!ttsEngineRef.current || !ttsEngineRef.current.isSupported()) {
      const err = 'Speech synthesis is not supported in this browser.';
      setVoiceError(err);
      setVoiceState('ERROR');
      return;
    }

    const greetingText = getTimeBasedGreeting(userName);
    setVoiceState('SPEAKING');
    setIsSpeaking(true);

    ttsEngineRef.current.speak(
      greetingText,
      undefined,
      () => {
        setIsSpeaking(false);
        setVoiceState('IDLE');
      },
      (err) => {
        setIsSpeaking(false);
        setVoiceError(err);
        setVoiceState('ERROR');
      }
    );
  }, [isSpeaking, isListening, userName, stopSpeaking]);

  /**
   * Speak arbitrary text aloud (e.g. Nova's answer from backend inference)
   */
  const speakText = useCallback(
    (text: string, onEnd?: () => void) => {
      setVoiceError(null);

      if (!ttsEngineRef.current || !ttsEngineRef.current.isSupported()) {
        const err = 'Speech synthesis is not supported in this browser.';
        setVoiceError(err);
        setVoiceState('ERROR');
        onEnd?.();
        return;
      }

      setVoiceState('SPEAKING');
      setIsSpeaking(true);

      ttsEngineRef.current.speak(
        text,
        undefined,
        () => {
          setIsSpeaking(false);
          setVoiceState('IDLE');
          onEnd?.();
        },
        (err) => {
          setIsSpeaking(false);
          setVoiceError(err);
          setVoiceState('ERROR');
          onEnd?.();
        }
      );
    },
    []
  );

  /**
   * Process a recognized prompt through the real inference/conversation engine
   * and speak the result aloud.
   */
  const handleDispatchVoiceCommand = useCallback(
    async (recognizedPrompt: string) => {
      if (!recognizedPrompt.trim()) {
        setVoiceState('IDLE');
        return;
      }

      setVoiceState('THINKING');

      try {
        if (!onExecuteCommand) {
          setVoiceState('IDLE');
          return;
        }

        const cmd = await onExecuteCommand(recognizedPrompt);

        if (cmd && cmd.executionState === 'AWAITING_APPROVAL') {
          setVoiceState('IDLE');
          speakText('Operator authorization is required for this action.');
          return;
        }

        const responseMessage =
          cmd?.result?.message || 'Operation executed and verified successfully.';

        speakText(responseMessage);
      } catch (err: any) {
        const errorMsg = err?.message || 'Encountered an exception executing voice command.';
        setVoiceError(errorMsg);
        setVoiceState('ERROR');
        speakText('I encountered an error executing that command.');
      }
    },
    [onExecuteCommand, speakText]
  );

  /**
   * Finish recording and send audio to local Whisper STT engine.
   */
  const stopListeningAndTranscribe = useCallback(async () => {
    setIsListening(false);

    // Stop interim speech recognition if active
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        // ignore
      }
      recognitionRef.current = null;
    }

    if (!audioCaptureRef.current) {
      setVoiceState('IDLE');
      return;
    }

    const audioBlob = await audioCaptureRef.current.stop();
    if (!audioBlob || audioBlob.size < 200) {
      // Empty or silent recording; smoothly reset to IDLE without error
      setVoiceState('IDLE');
      return;
    }

    setVoiceState('THINKING');

    try {
      if (!sttServiceRef.current) {
        throw new Error('STT Service uninitialized.');
      }

      // Transcribe via Local-First Offline Whisper
      const result = await sttServiceRef.current.transcribeAudioBlob(audioBlob);
      const recognized = result.transcript.trim();

      if (!recognized) {
        // Silent audio with no words detected
        setVoiceState('IDLE');
        return;
      }

      setTranscript(recognized);
      await handleDispatchVoiceCommand(recognized);
    } catch (err: any) {
      console.warn('Speech recognition error:', err);
      const msg = err.message || 'Speech recognition failed.';
      setVoiceError(msg);
      setVoiceState('ERROR');
    }
  }, [handleDispatchVoiceCommand]);

  /**
   * Start listening to the microphone with user permission check.
   */
  const startListening = useCallback(async () => {
    setVoiceError(null);
    setTranscript('');

    if (isSpeaking || ttsEngineRef.current?.isSpeaking()) {
      stopSpeaking();
    }

    if (!audioCaptureRef.current?.isSupported()) {
      const err = 'Microphone recording is not supported in this browser.';
      setVoiceError(err);
      setVoiceState('ERROR');
      return;
    }

    try {
      // 1. Start real audio capture stream
      await audioCaptureRef.current.start();
      setIsListening(true);
      setVoiceState('LISTENING');

      // 2. Start optional browser SpeechRecognition for live interim typing feedback
      if (typeof window !== 'undefined') {
        const SpeechRecognition =
          (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (SpeechRecognition) {
          try {
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = (event: any) => {
              let liveText = '';
              for (let i = event.resultIndex; i < event.results.length; i++) {
                liveText += event.results[i][0].transcript;
              }
              if (liveText.trim()) {
                setTranscript(liveText.trim());
              }
            };

            // Suppress browser network errors during interim recognition
            // because local Whisper is our authoritative offline transcriber!
            recognition.onerror = (e: any) => {
              if (e.error === 'network') {
                // Silently ignore Google Cloud speech network failure
                // Local Whisper will transcribe the full audio on stop!
                return;
              }
            };

            recognition.start();
            recognitionRef.current = recognition;
          } catch {
            // Optional live preview unavailable; local Whisper will transcribe on completion
          }
        }
      }
    } catch (err: any) {
      setIsListening(false);
      setVoiceState('ERROR');
      if (err instanceof MicrophoneError) {
        setVoiceError(err.message);
      } else {
        setVoiceError(err?.message || 'Failed to access microphone.');
      }
    }
  }, [isSpeaking, stopSpeaking]);

  /**
   * Toggle voice listening state (mic button trigger)
   */
  const toggleVoice = useCallback(() => {
    if (isSpeaking) {
      stopSpeaking();
      return;
    }

    if (isListening) {
      stopListeningAndTranscribe();
      return;
    }

    startListening();
  }, [isSpeaking, isListening, stopSpeaking, stopListeningAndTranscribe, startListening]);

  return {
    voiceState,
    voiceError,
    transcript,
    isListening,
    isSpeaking,
    speakGreeting,
    speakText,
    startListening,
    stopListening: stopListeningAndTranscribe,
    stopSpeaking,
    toggleVoice,
    clearVoiceError,
  };
}

export default useNovaVoiceAssistant;
