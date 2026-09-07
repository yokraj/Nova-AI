import React, { useState, useEffect, useCallback } from 'react';
import { Send, Mic, MicOff, Eye, Sparkles, AlertCircle, Loader2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { CommandSource } from '../types/command';
import { useBrowserSpeechRecognition } from '@/features/voice/hooks/useBrowserSpeechRecognition';

export interface UniversalCommandSurfaceProps {
  onSubmitCommand: (input: string, source: CommandSource) => void;
  isListening?: boolean;
  onToggleVoice?: () => void;
  voiceStatusMessage?: string;
  className?: string;
}

export const UniversalCommandSurface: React.FC<UniversalCommandSurfaceProps> = ({
  onSubmitCommand,
  isListening: propIsListening,
  onToggleVoice,
  voiceStatusMessage,
  className,
}) => {
  const [input, setInput] = useState('');
  const [commandSource, setCommandSource] = useState<CommandSource>('TEXT');

  const {
    isSupported,
    voiceState,
    errorMessage,
    toggleListening,
    clearError,
  } = useBrowserSpeechRecognition({
    onResult: (transcriptText) => {
      setInput(transcriptText);
      setCommandSource('VOICE');
    },
    onError: (err) => {
      console.warn('Speech recognition notice:', err);
    },
  });

  const isCurrentlyListening =
    propIsListening !== undefined
      ? propIsListening
      : voiceState === 'LISTENING' || voiceState === 'TRANSCRIBING';

  const handleMicClick = useCallback(() => {
    if (onToggleVoice) {
      onToggleVoice();
    } else {
      if (voiceState === 'ERROR') {
        clearError();
      }
      toggleListening();
    }
  }, [onToggleVoice, voiceState, clearError, toggleListening]);


  const handleMicKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleMicClick();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSubmitCommand(input.trim(), commandSource);
    setInput('');
    setCommandSource('TEXT');
  };

  // Keyboard shortcut Alt+V to toggle microphone
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && (e.key === 'v' || e.key === 'V')) {
        e.preventDefault();
        handleMicClick();
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, [handleMicClick]);

  const samplePrompts = [
    'Open VS Code',
    'Summarize system status',
    'Run background workflow',
    'Research agent query',
  ];

  const getMicTitle = () => {
    if (!isSupported && !onToggleVoice) return 'Voice recognition is unavailable in this browser.';
    if (errorMessage) return errorMessage;
    if (isCurrentlyListening) return 'Listening... Click to stop';
    if (voiceState === 'TRANSCRIBING') return 'Transcribing...';
    return 'Voice command';
  };

  return (
    <div className={cn('w-full max-w-2xl mx-auto space-y-2 font-sans', className)}>
      <form
        onSubmit={handleSubmit}
        className="p-2 rounded-2xl bg-slate-900/95 border border-cyan-500/30 shadow-[0_0_25px_rgba(0,240,255,0.12)] flex items-center space-x-2 backdrop-blur-xl transition-all focus-within:border-cyan-400 focus-within:shadow-[0_0_35px_rgba(0,240,255,0.2)]"
      >
        <div className="pl-2.5 text-cyan-400">
          <Sparkles className="w-4 h-4 animate-pulse" />
        </div>

        <input
          type="text"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setCommandSource('TEXT');
          }}
          placeholder="Ask Nova anything..."
          className="flex-1 bg-transparent border-none text-slate-100 text-sm placeholder-slate-500 focus:outline-none focus:ring-0 px-2 py-1"
          aria-label="Ask Nova anything"
        />

        <div className="flex items-center space-x-1 pr-1">
          {/* ALWAYS VISIBLE MICROPHONE CONTROL BUTTON */}
          <button
            type="button"
            onClick={handleMicClick}
            onKeyDown={handleMicKeyDown}
            tabIndex={0}
            aria-label="Voice command"
            title={getMicTitle()}
            className={cn(
              'p-1.5 rounded-xl border transition-all cursor-pointer flex items-center justify-center min-w-[32px] min-h-[32px] focus:outline-none focus:ring-2 focus:ring-cyan-400',
              isCurrentlyListening
                ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 animate-pulse shadow-[0_0_15px_rgba(244,63,94,0.4)]'
                : voiceState === 'TRANSCRIBING'
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 animate-pulse'
                : voiceState === 'ERROR' || errorMessage
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/50'
                : 'bg-slate-950/80 text-slate-400 hover:text-cyan-300 border-slate-800'
            )}
          >
            {isCurrentlyListening ? (
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                <Mic className="w-3.5 h-3.5 text-rose-300" />
              </span>
            ) : voiceState === 'TRANSCRIBING' ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
            ) : voiceState === 'ERROR' || errorMessage ? (
              <MicOff className="w-3.5 h-3.5 text-amber-400" />
            ) : (
              <Mic className="w-3.5 h-3.5" />
            )}
          </button>

          <button
            type="button"
            className="p-1.5 rounded-xl bg-slate-950/80 text-slate-400 hover:text-purple-300 border border-slate-800 transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-purple-400"
            title="Attach Vision Target"
          >
            <Eye className="w-3.5 h-3.5" />
          </button>

          <button
            type="submit"
            disabled={!input.trim()}
            className={cn(
              'p-2 rounded-xl font-bold transition-all cursor-pointer flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-cyan-400',
              input.trim()
                ? 'bg-cyan-500 text-slate-950 hover:bg-cyan-400 shadow-[0_0_12px_rgba(0,240,255,0.4)]'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'
            )}
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </form>

      {/* Voice Status Badge / Error Indicator */}
      {(isCurrentlyListening || voiceState === 'TRANSCRIBING' || errorMessage || voiceStatusMessage) && (
        <div className="flex items-center justify-center text-xs space-x-2 py-0.5 px-2">
          {isCurrentlyListening && (
            <span className="inline-flex items-center space-x-1.5 text-rose-400 font-mono bg-rose-950/50 px-2.5 py-0.5 rounded-full border border-rose-800/50">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
              <span>Listening... Speak your command</span>
            </span>
          )}

          {voiceState === 'TRANSCRIBING' && (
            <span className="inline-flex items-center space-x-1.5 text-cyan-400 font-mono bg-cyan-950/50 px-2.5 py-0.5 rounded-full border border-cyan-800/50">
              <Loader2 className="w-3 h-3 animate-spin" />
              <span>Transcribing voice prompt...</span>
            </span>
          )}

          {(errorMessage || voiceStatusMessage) && !isCurrentlyListening && voiceState !== 'TRANSCRIBING' && (
            <span className="inline-flex items-center space-x-1.5 text-amber-400 font-mono bg-amber-950/50 px-2.5 py-0.5 rounded-full border border-amber-800/50">
              <AlertCircle className="w-3 h-3" />
              <span>{errorMessage || voiceStatusMessage}</span>
            </span>
          )}
        </div>
      )}

      {/* Subtle Suggestions */}
      <div className="flex items-center justify-center flex-wrap gap-1.5 pt-0.5">
        {samplePrompts.map((prompt, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSubmitCommand(prompt, 'TEXT')}
            className="px-2.5 py-0.5 rounded-full bg-slate-950/80 hover:bg-slate-900 border border-slate-800/80 text-[10px] font-mono text-slate-400 hover:text-cyan-300 transition-all cursor-pointer"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
};

export default UniversalCommandSurface;
