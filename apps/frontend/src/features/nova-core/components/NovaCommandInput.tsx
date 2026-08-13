import React, { useState } from 'react';
import { Send, Mic, MicOff, Paperclip, Camera, Terminal } from 'lucide-react';
import { cn } from '@/utils/cn';
import { PrimaryButton, IconButton } from '@/components/ui/Buttons';
import { NovaCommandMode } from '../types/novaCommand';

interface NovaCommandInputProps {
  onSendCommand: (prompt: string, mode: NovaCommandMode) => void;
  onToggleMic: () => void;
  isRecording: boolean;
  className?: string;
}

export const NovaCommandInput: React.FC<NovaCommandInputProps> = ({
  onSendCommand,
  onToggleMic,
  isRecording,
  className,
}) => {
  const [mode, setMode] = useState<NovaCommandMode>('text');
  const [prompt, setPrompt] = useState('');

  const commandSuggestions = [
    'Explain quantum computing',
    'Analyze my project',
    'Research AI agents',
    'Open VS Code',
    'Remember this',
    'Check my devices',
    'Create a report',
  ];

  const handleSend = () => {
    if (!prompt.trim()) return;
    onSendCommand(prompt, mode);
  };

  const handleSuggestionClick = (s: string) => {
    setPrompt(s);
    onSendCommand(s, mode);
  };

  return (
    <div className={cn('w-full max-w-3xl mx-auto space-y-3', className)}>
      {/* Primary Input Container */}
      <div className="relative group">
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cyan-500/20 via-blue-600/20 to-purple-600/20 blur-md opacity-50 group-hover:opacity-100 transition-opacity pointer-events-none" />
        <div className="relative flex items-center bg-slate-950/95 rounded-2xl border border-slate-800 group-hover:border-cyan-500/50 transition-all p-2 shadow-2xl">
          <Terminal className="w-5 h-5 text-cyan-400 ml-3 mr-2 shrink-0" />

          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={
              mode === 'voice'
                ? 'Speak voice prompt...'
                : mode === 'vision'
                ? 'Point camera at screen/document or enter visual request...'
                : mode === 'file'
                ? 'Attach file or type document prompt...'
                : mode === 'command'
                ? 'Enter system automation command...'
                : 'Ask Nova anything...'
            }
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none py-2 px-1 font-sans"
            aria-label="Ask Nova anything"
          />

          <div className="flex items-center space-x-2 mr-1">
            <IconButton
              icon={Paperclip}
              size="sm"
              className={cn('text-slate-400 hover:text-cyan-300', mode === 'file' && 'text-cyan-300 bg-cyan-500/20')}
              title="Attach File"
              onClick={() => setMode('file')}
            />
            <IconButton
              icon={Camera}
              size="sm"
              className={cn('text-slate-400 hover:text-cyan-300', mode === 'vision' && 'text-cyan-300 bg-cyan-500/20')}
              title="Camera / Vision Feed"
              onClick={() => setMode('vision')}
            />
            <button
              onClick={onToggleMic}
              className={cn(
                'p-2 rounded-xl transition-all cursor-pointer border flex items-center justify-center',
                isRecording
                  ? 'bg-rose-500 text-white border-rose-400 animate-pulse shadow-[0_0_15px_rgba(244,63,94,0.6)]'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-purple-300 hover:border-purple-500/40'
              )}
              title={isRecording ? 'Stop Recording' : 'Microphone Voice Input'}
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>
            <PrimaryButton
              size="md"
              disabled={!prompt.trim()}
              onClick={handleSend}
              icon={Send}
            >
              Ask Nova
            </PrimaryButton>
          </div>
        </div>
      </div>

      {/* Clickable Suggested Prompt Chips */}
      <div className="flex items-center justify-center flex-wrap gap-2 text-xs font-sans">
        <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider shrink-0">Try:</span>
        {commandSuggestions.map((suggestion, idx) => (
          <button
            key={idx}
            onClick={() => handleSuggestionClick(suggestion)}
            className="px-3 py-1 rounded-xl bg-slate-900/90 text-slate-300 hover:text-cyan-300 hover:bg-cyan-500/10 border border-slate-800 hover:border-cyan-500/30 transition-all cursor-pointer"
          >
            + {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
};

export default NovaCommandInput;
