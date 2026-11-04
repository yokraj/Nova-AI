import { useState, useRef, useCallback, useEffect } from 'react';
import {
  WebTextToSpeechEngine,
  getTimeBasedGreeting,
  selectNovaVoice,
} from '../services/webSpeechEngine';
import { BackendTTSAudioPlayer } from '../services/backendTTSPlayer';
import { AudioCaptureService, MicrophoneError } from '../services/audioCapture';
import { CompositeSTTService } from '../services/sttProviders';
import { AudioChimeService } from '../services/audioChime';
import { VoiceActivityDetector } from '../services/vadService';
import { WakeWordDetector, WakeWordMatchResult } from '../services/wakeWordDetector';
import { SpeechPreparationService } from '../services/speechPreparation';
import {
  VoiceSettingsConfig,
  loadPersistedVoiceSettings,
  savePersistedVoiceSettings,
} from '../types/voiceSettings';
import { NovaCoreState } from '@/features/nova-core/types/novaCore';
import { UniversalCommand } from '@/features/universal-command/types/command';

export interface UseNovaVoiceAssistantOptions {
  onExecuteCommand?: (command: string) => Promise<UniversalCommand | null | void>;
  userName?: string;
  defaultWakePhrase?: string;
  initialHandsFree?: boolean;
}

// Interruption phrases that trigger barge-in during speech synthesis
const BARGE_IN_PHRASES = [
  'stop',
  'nova wait',
  'wait',
  'be quiet',
  'cancel',
  'cancel speaking',
  'halt',
  'quiet',
  'shut up',
  'hold on',
  'pause',
];

// Session exit phrases that end the multi-turn session
const SESSION_EXIT_PHRASES = [
  'goodbye nova',
  'goodbye',
  'bye nova',
  'bye',
  'exit session',
  'end conversation',
  'close conversation',
  'dismiss',
  "that's all",
  'thats all',
  'sleep',
  'go to sleep',
];

export function useNovaVoiceAssistant({
  onExecuteCommand,
  userName = 'sir',
  defaultWakePhrase = 'Hey Nova',
  initialHandsFree = false,
}: UseNovaVoiceAssistantOptions = {}) {
  // Voice Settings & Persistence
  const [voiceSettings, setVoiceSettingsState] = useState<VoiceSettingsConfig>(() =>
    loadPersistedVoiceSettings()
  );

  const [voiceState, setVoiceState] = useState<NovaCoreState>('IDLE');
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string>('');
  const [detectedLanguage, setDetectedLanguage] = useState<string>('en-IN');
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [voiceLevel, setVoiceLevel] = useState<number>(0);
  const [activeVoiceInfo, setActiveVoiceInfo] = useState<{
    name: string;
    lang: string;
    isExactLocale: boolean;
  }>({
    name: 'NOVA — Indian Professional',
    lang: 'en-IN',
    isExactLocale: true,
  });

  // Hands-free controls
  const [handsFreeEnabled, setHandsFreeEnabled] = useState<boolean>(
    voiceSettings.handsFreeEnabled || initialHandsFree
  );
  const [wakePhrase, setWakePhraseState] = useState<string>(
    voiceSettings.wakePhrase || defaultWakePhrase
  );
  const [isConversationActive, setIsConversationActive] = useState<boolean>(false);

  // Core Service Refs
  const backendTTSPlayerRef = useRef<BackendTTSAudioPlayer | null>(null);
  const ttsEngineRef = useRef<WebTextToSpeechEngine | null>(null);
  const audioCaptureRef = useRef<AudioCaptureService | null>(null);
  const sttServiceRef = useRef<CompositeSTTService | null>(null);
  const chimeRef = useRef<AudioChimeService | null>(null);
  const vadRef = useRef<VoiceActivityDetector | null>(null);
  const wakeWordRef = useRef<WakeWordDetector | null>(null);
  const recognitionRef = useRef<any>(null);

  // Lifecycle control refs
  const voiceStateRef = useRef<NovaCoreState>('IDLE');
  const handsFreeRef = useRef<boolean>(handsFreeEnabled);
  const isSpeakingRef = useRef<boolean>(false);
  const isListeningRef = useRef<boolean>(false);
  const isProcessingRef = useRef<boolean>(false);
  const followupTimerRef = useRef<any>(null);
  const voiceSettingsRef = useRef<VoiceSettingsConfig>(voiceSettings);

  // Sync state refs
  useEffect(() => {
    voiceStateRef.current = voiceState;
  }, [voiceState]);

  useEffect(() => {
    handsFreeRef.current = handsFreeEnabled;
  }, [handsFreeEnabled]);

  useEffect(() => {
    isSpeakingRef.current = isSpeaking;
  }, [isSpeaking]);

  useEffect(() => {
    isListeningRef.current = isListening;
  }, [isListening]);

  useEffect(() => {
    voiceSettingsRef.current = voiceSettings;
  }, [voiceSettings]);

  const updateVoiceSettings = useCallback((newSettings: VoiceSettingsConfig) => {
    setVoiceSettingsState(newSettings);
    savePersistedVoiceSettings(newSettings);
    setHandsFreeEnabled(newSettings.handsFreeEnabled);
    setWakePhraseState(newSettings.wakePhrase);
    wakeWordRef.current?.setWakePhrase(newSettings.wakePhrase);
    ttsEngineRef.current?.configureVoiceParameters(
      newSettings.pitch,
      newSettings.speakingRate,
      newSettings.volume / 100
    );
  }, []);

  const clearVoiceError = useCallback(() => {
    setVoiceError(null);
    if (voiceStateRef.current === 'ERROR') {
      const nextState = handsFreeRef.current ? 'SLEEPING' : 'IDLE';
      setVoiceState(nextState);
    }
  }, []);

  const clearFollowupTimer = useCallback(() => {
    if (followupTimerRef.current) {
      clearTimeout(followupTimerRef.current);
      followupTimerRef.current = null;
    }
  }, []);

  // Stop active speech playback immediately
  const stopSpeaking = useCallback(() => {
    if (backendTTSPlayerRef.current) {
      backendTTSPlayerRef.current.stop();
    }
    if (ttsEngineRef.current) {
      ttsEngineRef.current.stop();
    }
    setIsSpeaking(false);
    isSpeakingRef.current = false;
  }, []);

  // Update wake phrase
  const setWakePhrase = useCallback((newPhrase: string) => {
    if (newPhrase && newPhrase.trim()) {
      const clean = newPhrase.trim();
      setWakePhraseState(clean);
      wakeWordRef.current?.setWakePhrase(clean);
      updateVoiceSettings({ ...voiceSettingsRef.current, wakePhrase: clean });
    }
  }, [updateVoiceSettings]);

  /**
   * Speak arbitrary text aloud using Nova Indian Professional voice identity
   * and natural speech preparation.
   * Prioritizes the genuine neural backend TTS engine (Edge-TTS) with browser synthesis fallback.
   */
  const speakText = useCallback(
    (text: string, onEnd?: () => void, languageOverride?: string) => {
      setVoiceError(null);

      const targetLang = languageOverride || detectedLanguage || 'en-IN';
      const settings = voiceSettingsRef.current;

      // 1. Prioritize Genuine Backend Neural TTS Engine
      if (backendTTSPlayerRef.current?.isSupported()) {
        setVoiceState('SPEAKING');
        setIsSpeaking(true);
        isSpeakingRef.current = true;

        const isOfflineProfile =
          settings.voiceMode === 'offline_female' ||
          settings.voiceIdentity === 'nova-offline-female' ||
          settings.voiceIdentity === 'nova-offline';

        const chosenVoice = isOfflineProfile
          ? (settings.offlineVoice || 'Microsoft Zira Desktop')
          : targetLang.startsWith('ta')
          ? 'ta-IN-PallaviNeural'
          : targetLang.startsWith('hi')
          ? 'hi-IN-SwaraNeural'
          : (settings.neuralVoice || 'en-IN-NeerjaNeural');

        const langLabel = isOfflineProfile
          ? `NOVA Offline Female (${chosenVoice}) [100% Local]`
          : `NOVA Neural Female (${chosenVoice}) [ONLINE]`;

        setActiveVoiceInfo({
          name: langLabel,
          lang: targetLang,
          isExactLocale: true,
        });

        backendTTSPlayerRef.current.synthesizeAndPlay(
          text,
          {
            language: targetLang,
            voice: chosenVoice,
            mode: isOfflineProfile ? 'offline' : 'neural',
            pitch: settings.pitch,
            speakingRate: settings.speakingRate,
            volume: settings.volume,
            offlineOnly: isOfflineProfile,
          },
          () => {
            // onStart
            setVoiceState('SPEAKING');
            setIsSpeaking(true);
            isSpeakingRef.current = true;
          },
          () => {
            // onEnd
            setIsSpeaking(false);
            isSpeakingRef.current = false;
            onEnd?.();
          },
          (backendErr) => {
            console.warn('Backend TTS error, falling back to browser speech synthesis:', backendErr);
            // 2. Fallback to WebSpeech if backend synthesis fails
            if (ttsEngineRef.current && ttsEngineRef.current.isSupported()) {
              ttsEngineRef.current.configureVoiceParameters(
                settings.pitch,
                settings.speakingRate,
                settings.volume / 100
              );
              const info = ttsEngineRef.current.getActiveVoiceInfo(targetLang);
              setActiveVoiceInfo(info);

              ttsEngineRef.current.speak(
                text,
                undefined,
                () => {
                  setIsSpeaking(false);
                  isSpeakingRef.current = false;
                  onEnd?.();
                },
                (webErr) => {
                  setIsSpeaking(false);
                  isSpeakingRef.current = false;
                  setVoiceError(webErr);
                  setVoiceState('ERROR');
                  onEnd?.();
                },
                targetLang
              );
            } else {
              setIsSpeaking(false);
              isSpeakingRef.current = false;
              setVoiceError(backendErr.message || 'Speech synthesis failed.');
              setVoiceState('ERROR');
              onEnd?.();
            }
          }
        );
        return;
      }

      // 3. Direct Browser WebSpeech fallback if Audio element unsupported
      if (!ttsEngineRef.current || !ttsEngineRef.current.isSupported()) {
        const err = 'Speech synthesis is not supported in this browser environment.';
        setVoiceError(err);
        setVoiceState('ERROR');
        onEnd?.();
        return;
      }

      setVoiceState('SPEAKING');
      setIsSpeaking(true);
      isSpeakingRef.current = true;

      ttsEngineRef.current.configureVoiceParameters(
        settings.pitch,
        settings.speakingRate,
        settings.volume / 100
      );

      const info = ttsEngineRef.current.getActiveVoiceInfo(targetLang);
      setActiveVoiceInfo(info);

      ttsEngineRef.current.speak(
        text,
        undefined,
        () => {
          setIsSpeaking(false);
          isSpeakingRef.current = false;
          onEnd?.();
        },
        (err) => {
          setIsSpeaking(false);
          isSpeakingRef.current = false;
          setVoiceError(err);
          setVoiceState('ERROR');
          onEnd?.();
        },
        targetLang
      );
    },
    [detectedLanguage]
  );

  /**
   * Process a recognized prompt through the real inference/conversation engine
   * and speak the result aloud.
   */
  const handleDispatchVoiceCommand = useCallback(
    async (recognizedPrompt: string, promptLanguage?: string) => {
      const cleanPrompt = recognizedPrompt.trim();
      if (!cleanPrompt) {
        setVoiceState(handsFreeRef.current ? 'SLEEPING' : 'IDLE');
        return;
      }

      // Check for session exit command
      const lower = cleanPrompt.toLowerCase();
      const isExit = SESSION_EXIT_PHRASES.some(
        (phrase) => lower === phrase || lower.startsWith(phrase)
      );
      if (isExit) {
        clearFollowupTimer();
        setIsConversationActive(false);
        chimeRef.current?.playSessionEndTone();
        speakText('Goodbye. Nova standing by.', () => {
          setVoiceState(handsFreeRef.current ? 'SLEEPING' : 'IDLE');
        });
        return;
      }

      // Check for interruption/stop commands
      const isStop = BARGE_IN_PHRASES.some(
        (phrase) => lower === phrase || lower.startsWith(phrase)
      );
      if (isStop) {
        stopSpeaking();
        chimeRef.current?.playInterruptedTone();
        setVoiceState('INTERRUPTED');
        setTimeout(() => {
          setVoiceState(handsFreeRef.current ? 'SLEEPING' : 'IDLE');
        }, 1200);
        return;
      }

      // State: THINKING
      setVoiceState('THINKING');
      isProcessingRef.current = true;

      try {
        if (!onExecuteCommand) {
          setVoiceState(handsFreeRef.current ? 'SLEEPING' : 'IDLE');
          isProcessingRef.current = false;
          return;
        }

        const cmd = await onExecuteCommand(cleanPrompt);

        if (cmd && cmd.executionState === 'AWAITING_APPROVAL') {
          speakText('Authorization is required for this action.', () => {
            if (handsFreeRef.current) {
              startFollowupWindow();
            } else {
              setVoiceState('IDLE');
            }
          });
          return;
        }

        const rawResponse =
          cmd?.result?.message || 'Operation executed and verified successfully.';

        // Format speech using speech preparation layer
        const targetLang = promptLanguage || detectedLanguage || 'en-IN';
        const formatted = SpeechPreparationService.formatResponse(rawResponse, targetLang);

        speakText(
          formatted.speechText,
          () => {
            if (handsFreeRef.current) {
              startFollowupWindow();
            } else {
              setVoiceState('IDLE');
            }
          },
          formatted.detectedLanguage
        );
      } catch (err: any) {
        const errorMsg = err?.message || 'Encountered an exception executing voice command.';
        setVoiceError(errorMsg);
        setVoiceState('ERROR');
        speakText('I encountered an error executing that command.', () => {
          setVoiceState(handsFreeRef.current ? 'SLEEPING' : 'IDLE');
        });
      } finally {
        isProcessingRef.current = false;
      }
    },
    [onExecuteCommand, speakText, stopSpeaking, clearFollowupTimer, detectedLanguage]
  );

  /**
   * Finalize recording slice and send audio to local Whisper STT engine.
   * State: TRANSCRIBING -> THINKING -> SPEAKING
   */
  const stopListeningAndTranscribe = useCallback(async () => {
    setIsListening(false);
    isListeningRef.current = false;

    // Stop interim speech recognition if active
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
      recognitionRef.current = null;
    }

    if (!audioCaptureRef.current) {
      setVoiceState(handsFreeRef.current ? 'SLEEPING' : 'IDLE');
      return;
    }

    const audioBlob = await audioCaptureRef.current.stopRecordingSlice();
    if (!audioBlob || audioBlob.size < 200) {
      setVoiceState(handsFreeRef.current ? 'SLEEPING' : 'IDLE');
      return;
    }

    // STATE: TRANSCRIBING (decoding audio & language identification)
    setVoiceState('TRANSCRIBING');

    try {
      if (!sttServiceRef.current) {
        throw new Error('STT Service uninitialized.');
      }

      // Transcribe via Local Multilingual faster-whisper
      const currentLanguageSetting = voiceSettingsRef.current.language;
      const result = await sttServiceRef.current.transcribeAudioBlob(
        audioBlob,
        currentLanguageSetting
      );
      const recognized = result.transcript.trim();

      if (!recognized) {
        setVoiceState(handsFreeRef.current ? 'SLEEPING' : 'IDLE');
        return;
      }

      // Detect language from result or script
      const langCode = result.language || SpeechPreparationService.detectScriptLanguage(recognized);
      setDetectedLanguage(langCode === 'ta' ? 'ta-IN' : langCode === 'hi' ? 'hi-IN' : 'en-IN');

      // Strip wake phrase if user spoke "Hey Nova, ..." together
      const stripped = wakeWordRef.current?.matchInText(recognized).strippedCommand || recognized;
      const finalPrompt = stripped.trim() || recognized;

      setTranscript(finalPrompt);
      await handleDispatchVoiceCommand(finalPrompt, langCode);
    } catch (err: any) {
      console.warn('Speech recognition error:', err);
      const msg = err.message || 'Speech recognition failed.';
      setVoiceError(msg);
      setVoiceState('ERROR');
    }
  }, [handleDispatchVoiceCommand]);

  /**
   * Continuous multi-turn conversation follow-up window.
   */
  const startFollowupWindow = useCallback(() => {
    clearFollowupTimer();
    setIsConversationActive(true);
    setVoiceState('LISTENING');
    setIsListening(true);
    isListeningRef.current = true;

    audioCaptureRef.current?.startRecordingSlice().catch(() => {});

    followupTimerRef.current = setTimeout(() => {
      if (voiceStateRef.current === 'LISTENING') {
        audioCaptureRef.current?.stopRecordingSlice().catch(() => {});
        setIsListening(false);
        isListeningRef.current = false;
        setIsConversationActive(false);
        setVoiceState('SLEEPING');
      }
    }, 8000);
  }, [clearFollowupTimer]);

  /**
   * Starts active microphone listening.
   */
  const startListening = useCallback(async () => {
    clearFollowupTimer();
    setVoiceError(null);
    setTranscript('');

    if (isSpeakingRef.current || backendTTSPlayerRef.current?.isSpeaking() || ttsEngineRef.current?.isSpeaking()) {
      stopSpeaking();
    }

    if (!audioCaptureRef.current?.isSupported()) {
      const err = 'Microphone recording is not supported in this browser.';
      setVoiceError(err);
      setVoiceState('ERROR');
      return;
    }

    try {
      await audioCaptureRef.current.startRecordingSlice();
      setIsListening(true);
      isListeningRef.current = true;
      setVoiceState('LISTENING');

      // Optional browser interim preview
      if (typeof window !== 'undefined') {
        const SpeechRecognition =
          (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (SpeechRecognition) {
          try {
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang =
              voiceSettingsRef.current.language === 'ta'
                ? 'ta-IN'
                : voiceSettingsRef.current.language === 'hi'
                ? 'hi-IN'
                : 'en-IN';

            recognition.onresult = (event: any) => {
              let liveText = '';
              for (let i = event.resultIndex; i < event.results.length; ++i) {
                liveText += event.results[i][0].transcript;
              }
              if (liveText.trim()) {
                const clean = liveText.trim();
                setTranscript(clean);

                // Live barge-in interruption check
                if (isSpeakingRef.current && voiceSettingsRef.current.allowInterrupt) {
                  const lower = clean.toLowerCase();
                  if (BARGE_IN_PHRASES.some((p) => lower.includes(p))) {
                    handleBargeInInterruption();
                  }
                }
              }
            };

            recognition.onerror = () => {};
            recognition.start();
            recognitionRef.current = recognition;
          } catch {}
        }
      }
    } catch (err: any) {
      setIsListening(false);
      isListeningRef.current = false;
      setVoiceState('ERROR');
      if (err instanceof MicrophoneError) {
        setVoiceError(err.message);
      } else {
        setVoiceError(err?.message || 'Failed to access microphone.');
      }
    }
  }, [stopSpeaking, clearFollowupTimer]);

  /**
   * Barge-in interruption handler.
   */
  const handleBargeInInterruption = useCallback(() => {
    stopSpeaking();
    chimeRef.current?.playInterruptedTone();
    setVoiceState('INTERRUPTED');

    setTimeout(() => {
      if (handsFreeRef.current) {
        startListening();
      } else {
        setVoiceState('IDLE');
      }
    }, 700);
  }, [stopSpeaking, startListening]);

  /**
   * Wake-Word Activation Trigger Callback
   */
  const handleWakeWordDetected = useCallback(
    (match: WakeWordMatchResult) => {
      if (isProcessingRef.current || voiceStateRef.current === 'THINKING') {
        return;
      }

      if (isSpeakingRef.current) {
        handleBargeInInterruption();
        return;
      }

      chimeRef.current?.playWakeAcknowledgment();
      setIsConversationActive(true);

      if (match.strippedCommand && match.strippedCommand.trim().length > 1) {
        setTranscript(match.strippedCommand);
        handleDispatchVoiceCommand(match.strippedCommand);
        return;
      }

      startListening();
    },
    [handleBargeInInterruption, handleDispatchVoiceCommand, startListening]
  );

  /**
   * Enable Hands-Free Mode
   */
  const enableHandsFreeMode = useCallback(async () => {
    clearVoiceError();

    if (!audioCaptureRef.current?.isSupported()) {
      setVoiceError('Audio recording is not supported in this browser environment.');
      setVoiceState('ERROR');
      return;
    }

    try {
      const stream = await audioCaptureRef.current.acquireContinuousStream();

      if (vadRef.current) {
        vadRef.current.start(stream);
      }

      setHandsFreeEnabled(true);
      handsFreeRef.current = true;
      updateVoiceSettings({ ...voiceSettingsRef.current, handsFreeEnabled: true });
      setVoiceState('SLEEPING');
    } catch (err: any) {
      setHandsFreeEnabled(false);
      handsFreeRef.current = false;
      setVoiceState('ERROR');
      setVoiceError(err.message || 'Microphone permission denied for hands-free mode.');
    }
  }, [clearVoiceError, updateVoiceSettings]);

  /**
   * Disable Hands-Free Mode
   */
  const disableHandsFreeMode = useCallback(() => {
    clearFollowupTimer();
    stopSpeaking();

    vadRef.current?.stop();
    audioCaptureRef.current?.releaseResources();

    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {}
      recognitionRef.current = null;
    }

    setHandsFreeEnabled(false);
    handsFreeRef.current = false;
    updateVoiceSettings({ ...voiceSettingsRef.current, handsFreeEnabled: false });
    setIsListening(false);
    isListeningRef.current = false;
    setIsConversationActive(false);
    setVoiceLevel(0);
    setVoiceState('IDLE');
  }, [clearFollowupTimer, stopSpeaking, updateVoiceSettings]);

  const toggleHandsFree = useCallback(() => {
    if (handsFreeEnabled) {
      disableHandsFreeMode();
    } else {
      enableHandsFreeMode();
    }
  }, [handsFreeEnabled, disableHandsFreeMode, enableHandsFreeMode]);

  const toggleMute = useCallback(() => {
    if (!audioCaptureRef.current) return;
    if (isMuted) {
      audioCaptureRef.current.unmute();
      setIsMuted(false);
    } else {
      audioCaptureRef.current.mute();
      setIsMuted(true);
    }
  }, [isMuted]);

  const endConversationSession = useCallback(() => {
    clearFollowupTimer();
    stopSpeaking();
    setIsConversationActive(false);
    chimeRef.current?.playSessionEndTone();

    if (handsFreeEnabled) {
      setVoiceState('SLEEPING');
    } else {
      setVoiceState('IDLE');
    }
    setIsListening(false);
    isListeningRef.current = false;
  }, [clearFollowupTimer, stopSpeaking, handsFreeEnabled]);

  const speakGreeting = useCallback(() => {
    setVoiceError(null);

    if (
      isSpeaking ||
      isSpeakingRef.current ||
      backendTTSPlayerRef.current?.isSpeaking() ||
      ttsEngineRef.current?.isSpeaking()
    ) {
      stopSpeaking();
      return;
    }

    if (isListening) {
      audioCaptureRef.current?.cancel();
      setIsListening(false);
    }

    if (
      !backendTTSPlayerRef.current?.isSupported() &&
      (!ttsEngineRef.current || !ttsEngineRef.current.isSupported())
    ) {
      const err = 'Speech synthesis is not supported in this browser.';
      setVoiceError(err);
      setVoiceState('ERROR');
      return;
    }

    const greetingText = getTimeBasedGreeting(userName);
    speakText(greetingText, () => {
      if (handsFreeRef.current) {
        startFollowupWindow();
      } else {
        setVoiceState('IDLE');
      }
    });
  }, [isSpeaking, isListening, userName, stopSpeaking, speakText, startFollowupWindow]);

  const toggleVoice = useCallback(() => {
    if (
      isSpeaking ||
      isSpeakingRef.current ||
      backendTTSPlayerRef.current?.isSpeaking() ||
      ttsEngineRef.current?.isSpeaking()
    ) {
      stopSpeaking();
      return;
    }

    if (isListening) {
      stopListeningAndTranscribe();
      return;
    }

    startListening();
  }, [isSpeaking, isListening, stopSpeaking, stopListeningAndTranscribe, startListening]);

  // Initial setup
  useEffect(() => {
    backendTTSPlayerRef.current = new BackendTTSAudioPlayer();
    ttsEngineRef.current = new WebTextToSpeechEngine();
    audioCaptureRef.current = new AudioCaptureService();
    sttServiceRef.current = new CompositeSTTService();
    chimeRef.current = new AudioChimeService();

    // Configure initial voice parameters from persisted settings
    ttsEngineRef.current.configureVoiceParameters(
      voiceSettings.pitch,
      voiceSettings.speakingRate,
      voiceSettings.volume / 100
    );

    // Refresh initial voice info
    const info = ttsEngineRef.current.getActiveVoiceInfo(voiceSettings.language);
    setActiveVoiceInfo(info);

    // Initialize Wake Word Detector
    wakeWordRef.current = new WakeWordDetector({
      wakePhrase: voiceSettings.wakePhrase || defaultWakePhrase,
      onWakeWordDetected: (res) => handleWakeWordDetected(res),
    });

    // Initialize Voice Activity Detector
    vadRef.current = new VoiceActivityDetector({
      sensitivity: voiceSettings.vadSensitivity || 'medium',
      silenceHangoverMs: 1200,
      onSpeechStart: () => {
        if (voiceStateRef.current === 'SLEEPING' && handsFreeRef.current) {
          audioCaptureRef.current?.startRecordingSlice().catch(() => {});
        }
        if (isSpeakingRef.current && voiceSettingsRef.current.allowInterrupt) {
          handleBargeInInterruption();
        }
      },
      onSpeechEnd: () => {
        if (voiceStateRef.current === 'SLEEPING' && handsFreeRef.current) {
          audioCaptureRef.current?.stopRecordingSlice().then((blob) => {
            if (blob && blob.size > 200) {
              wakeWordRef.current?.evaluateAudioBlob(blob);
            }
          });
        }
        if (voiceStateRef.current === 'LISTENING') {
          stopListeningAndTranscribe();
        }
      },
      onVolumeChange: (vol) => {
        setVoiceLevel(vol);
      },
    });

    if (handsFreeEnabled) {
      enableHandsFreeMode();
    }

    return () => {
      clearFollowupTimer();
      backendTTSPlayerRef.current?.stop();
      ttsEngineRef.current?.stop();
      vadRef.current?.stop();
      chimeRef.current?.dispose();
      audioCaptureRef.current?.releaseResources();
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {}
      }
    };
  }, []);

  return {
    voiceState,
    voiceError,
    transcript,
    detectedLanguage,
    activeVoiceInfo,
    voiceSettings,
    updateVoiceSettings,
    isListening,
    isSpeaking,
    isMuted,
    voiceLevel,
    handsFreeEnabled,
    wakePhrase,
    isConversationActive,
    enableHandsFreeMode,
    disableHandsFreeMode,
    toggleHandsFree,
    toggleMute,
    setWakePhrase,
    endConversationSession,
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
