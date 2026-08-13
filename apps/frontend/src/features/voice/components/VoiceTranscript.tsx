import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic } from 'lucide-react';
import { cn } from '@/utils/cn';

interface VoiceTranscriptProps {
  transcript: string;
  isListening: boolean;
  className?: string;
}

export const VoiceTranscript: React.FC<VoiceTranscriptProps> = ({
  transcript,
  isListening,
  className,
}) => {
  if (!transcript && !isListening) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        className={cn('w-full max-w-xl mx-auto p-4 rounded-2xl bg-slate-950/90 border border-cyan-500/40 text-slate-100 shadow-xl font-mono text-xs space-y-2', className)}
      >
        <div className="flex items-center justify-between text-[11px] text-cyan-400 font-bold border-b border-slate-800 pb-1.5">
          <div className="flex items-center space-x-1.5">
            <Mic className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            <span>LIVE SPEECH TRANSCRIPTION</span>
          </div>
          {isListening && <span className="text-emerald-400 text-[10px]">CAPTURING...</span>}
        </div>

        <div className="text-sm font-sans font-medium text-slate-200 min-h-[2rem] flex items-center leading-relaxed">
          {transcript ? `"${transcript}"` : <span className="text-slate-500 italic">Listening for speech...</span>}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default VoiceTranscript;
