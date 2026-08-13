import React from 'react';
import { Mic, MicOff, Square, Radio } from 'lucide-react';
import { cn } from '@/utils/cn';
import { NovaVoiceState } from '../types/novaCore';

interface NovaVoiceControlProps {
  voiceState: NovaVoiceState;
  onToggleMic: () => void;
  onStopSpeaking?: () => void;
  className?: string;
}

export const NovaVoiceControl: React.FC<NovaVoiceControlProps> = ({
  voiceState,
  onToggleMic,
  onStopSpeaking,
  className,
}) => {
  const getVoiceStateLabel = () => {
    switch (voiceState) {
      case 'LISTENING':
        return 'LISTENING • Speak now...';
      case 'PROCESSING':
        return 'PROCESSING • Transcribing & Reasoning...';
      case 'NOVA_SPEAKING':
        return 'NOVA SPEAKING • Rhythmic Audio Output...';
      case 'STOPPED':
        return 'STOPPED • Voice muted';
      default:
        return 'MIC READY • Press to speak';
    }
  };

  return (
    <div className={cn('flex items-center space-x-3 bg-slate-900/90 px-4 py-2 rounded-2xl border border-slate-800 text-xs font-mono', className)}>
      <div className="flex items-center space-x-2">
        <Radio className={cn('w-4 h-4', voiceState === 'LISTENING' ? 'text-cyan-400 animate-pulse' : 'text-slate-500')} />
        <span className="text-slate-300 font-semibold">{getVoiceStateLabel()}</span>
      </div>

      <div className="flex items-center space-x-2 ml-auto">
        {voiceState === 'NOVA_SPEAKING' ? (
          <button
            onClick={onStopSpeaking}
            className="p-1.5 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/30 hover:bg-rose-500/30 text-xs transition-all cursor-pointer flex items-center space-x-1"
          >
            <Square className="w-3.5 h-3.5" />
            <span>Stop</span>
          </button>
        ) : (
          <button
            onClick={onToggleMic}
            className={cn(
              'p-1.5 rounded-lg border text-xs transition-all cursor-pointer flex items-center space-x-1',
              voiceState === 'LISTENING'
                ? 'bg-rose-500 text-white border-rose-400 animate-pulse'
                : 'bg-slate-800 text-slate-300 hover:text-cyan-300 border-slate-700'
            )}
          >
            {voiceState === 'LISTENING' ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
            <span>{voiceState === 'LISTENING' ? 'Mute' : 'Voice'}</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default NovaVoiceControl;
