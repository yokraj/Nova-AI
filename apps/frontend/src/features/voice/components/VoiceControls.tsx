import React from 'react';
import { Mic, MicOff, Settings, RefreshCw, MessageSquare } from 'lucide-react';
import { cn } from '@/utils/cn';
import { VoiceState } from '../types/voice';

interface VoiceControlsProps {
  state: VoiceState;
  onToggleMic: () => void;
  onOpenSettings: () => void;
  onSwitchToText?: () => void;
  continuousMode: boolean;
  onToggleContinuous: () => void;
  className?: string;
}

export const VoiceControls: React.FC<VoiceControlsProps> = ({
  state,
  onToggleMic,
  onOpenSettings,
  onSwitchToText,
  continuousMode,
  onToggleContinuous,
  className,
}) => {
  const isListening = state === 'LISTENING';

  return (
    <div className={cn('flex flex-col items-center space-y-4 font-mono text-xs', className)}>
      {/* Central Microphone Button */}
      <button
        onClick={onToggleMic}
        className={cn(
          'w-20 h-20 rounded-full flex items-center justify-center transition-all cursor-pointer shadow-2xl border-2',
          isListening
            ? 'bg-rose-500 text-white border-rose-400 animate-pulse shadow-[0_0_40px_rgba(244,63,94,0.7)]'
            : 'bg-slate-900 border-cyan-500/50 text-cyan-400 hover:border-cyan-400 hover:bg-cyan-500/20 shadow-[0_0_30px_rgba(0,240,255,0.2)]'
        )}
        title={isListening ? 'Stop Listening' : 'Start Voice Input (Hold Spacebar or Click)'}
      >
        {isListening ? <MicOff className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
      </button>

      {/* Auxiliary Controls */}
      <div className="flex items-center space-x-3 text-slate-400">
        {onSwitchToText && (
          <button
            onClick={onSwitchToText}
            className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:text-cyan-300 hover:border-slate-700 transition-all cursor-pointer flex items-center space-x-1.5"
          >
            <MessageSquare className="w-3.5 h-3.5 text-cyan-400" />
            <span>Type Instead</span>
          </button>
        )}

        <button
          onClick={onToggleContinuous}
          className={cn(
            'px-3 py-1.5 rounded-xl border text-xs transition-all cursor-pointer flex items-center space-x-1.5',
            continuousMode
              ? 'bg-purple-500/20 text-purple-300 border-purple-500/40 font-bold'
              : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
          )}
          title="Continuous Conversation Mode"
        >
          <RefreshCw className={cn('w-3.5 h-3.5', continuousMode && 'animate-spin')} />
          <span>Continuous: {continuousMode ? 'ON' : 'OFF'}</span>
        </button>

        <button
          onClick={onOpenSettings}
          className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:text-slate-200 hover:border-slate-700 transition-all cursor-pointer"
          title="Voice Settings"
        >
          <Settings className="w-4 h-4" />
        </button>
      </div>

      <div className="text-[11px] text-slate-500">Hold Spacebar to speak • Esc to cancel</div>
    </div>
  );
};

export default VoiceControls;
