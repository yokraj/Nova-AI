import React from 'react';
import { Play, Pause, Square, Volume2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { ProgressBar } from '@/components/status/StatusIndicators';
import { VoiceState } from '../types/voice';

interface VoiceResponseProps {
  text: string;
  state: VoiceState;
  progress: number;
  onPause: () => void;
  onResume: () => void;
  onInterrupt: () => void;
  className?: string;
}

export const VoiceResponse: React.FC<VoiceResponseProps> = ({
  text,
  state,
  progress,
  onPause,
  onResume,
  onInterrupt,
  className,
}) => {
  if (!text) return null;

  const isSpeaking = state === 'SPEAKING';
  const isPaused = state === 'PAUSED';

  return (
    <div className={cn('w-full max-w-xl mx-auto p-4 rounded-2xl bg-slate-900/90 border border-cyan-500/40 text-slate-100 shadow-xl font-mono text-xs space-y-3', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-cyan-300 font-bold">
          <Volume2 className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span>NOVA VOICE RESPONSE</span>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 uppercase font-bold">
          {state}
        </span>
      </div>

      <p className="text-sm font-sans font-medium text-slate-200 leading-relaxed">"{text}"</p>

      {/* Progress Bar */}
      <div className="space-y-1 pt-1">
        <div className="flex justify-between text-[10px] text-slate-400">
          <span>Audio Output</span>
          <span>{progress}%</span>
        </div>
        <ProgressBar progress={progress} />
      </div>

      {/* Controls: Pause / Resume / Interrupt */}
      <div className="flex items-center justify-between pt-1">
        <div className="flex items-center space-x-2">
          {isSpeaking && (
            <button
              onClick={onPause}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition-all cursor-pointer flex items-center space-x-1"
            >
              <Pause className="w-3.5 h-3.5" />
              <span>Pause</span>
            </button>
          )}

          {isPaused && (
            <button
              onClick={onResume}
              className="px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-bold transition-all cursor-pointer flex items-center space-x-1"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Resume</span>
            </button>
          )}
        </div>

        <button
          onClick={onInterrupt}
          className="px-3.5 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 text-xs font-bold font-mono transition-all cursor-pointer flex items-center space-x-1"
        >
          <Square className="w-3.5 h-3.5" />
          <span>INTERRUPT SPEECH</span>
        </button>
      </div>
    </div>
  );
};

export default VoiceResponse;
