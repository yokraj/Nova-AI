import React, { useState } from 'react';
import { Send, Mic, Eye, Sparkles } from 'lucide-react';
import { cn } from '@/utils/cn';
import { CommandSource } from '../types/command';

interface UniversalCommandSurfaceProps {
  onSubmitCommand: (input: string, source: CommandSource) => void;
  isListening?: boolean;
  onToggleVoice?: () => void;
  className?: string;
}

export const UniversalCommandSurface: React.FC<UniversalCommandSurfaceProps> = ({
  onSubmitCommand,
  isListening = false,
  onToggleVoice,
  className,
}) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSubmitCommand(input.trim(), 'TEXT');
    setInput('');
  };

  const samplePrompts = [
    'Open Visual Studio Code',
    'Turn on bedroom light',
    'Build my portfolio',
    'What do you remember about the frontend?',
    'Ask the research agent to investigate local LLMs',
  ];

  return (
    <div className={cn('w-full max-w-3xl mx-auto space-y-3 font-sans', className)}>
      <form
        onSubmit={handleSubmit}
        className="p-2.5 rounded-3xl bg-slate-900/90 border border-cyan-500/40 shadow-[0_0_30px_rgba(0,240,255,0.15)] flex items-center space-x-2 backdrop-blur-xl transition-all focus-within:border-cyan-400"
      >
        <div className="pl-3 text-cyan-400">
          <Sparkles className="w-5 h-5 animate-pulse" />
        </div>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Nova anything (e.g. 'Open VS Code', 'Build my portfolio', 'Turn on light')..."
          className="flex-1 bg-transparent border-none text-slate-100 text-sm placeholder-slate-500 focus:outline-none focus:ring-0 px-2 py-1.5"
        />

        <div className="flex items-center space-x-1 pr-1">
          <button
            type="button"
            onClick={onToggleVoice}
            className={cn(
              'p-2 rounded-2xl border transition-all cursor-pointer',
              isListening
                ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 animate-pulse'
                : 'bg-slate-950/80 text-slate-400 hover:text-cyan-300 border-slate-800'
            )}
            title="Voice Command"
          >
            <Mic className="w-4 h-4" />
          </button>

          <button
            type="button"
            className="p-2 rounded-2xl bg-slate-950/80 text-slate-400 hover:text-purple-300 border border-slate-800 transition-all cursor-pointer"
            title="Attach Vision File"
          >
            <Eye className="w-4 h-4" />
          </button>

          <button
            type="submit"
            disabled={!input.trim()}
            className={cn(
              'p-2.5 rounded-2xl font-bold transition-all cursor-pointer flex items-center justify-center',
              input.trim()
                ? 'bg-cyan-500 text-slate-950 hover:bg-cyan-400 shadow-[0_0_15px_rgba(0,240,255,0.4)]'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'
            )}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>

      {/* Suggested Quick Commands */}
      <div className="flex items-center justify-center flex-wrap gap-1.5 pt-1">
        {samplePrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => onSubmitCommand(prompt, 'TEXT')}
            className="px-3 py-1 rounded-full bg-slate-950/80 hover:bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-400 hover:text-cyan-300 transition-all cursor-pointer"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
};

export default UniversalCommandSurface;
