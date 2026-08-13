import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Check } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MicrophonePermissionState } from '../types/voice';

interface VoicePermissionDialogProps {
  permissionState: MicrophonePermissionState;
  onGrantPermission: () => void;
  onDenyPermission: () => void;
  className?: string;
}

export const VoicePermissionDialog: React.FC<VoicePermissionDialogProps> = ({
  permissionState,
  onGrantPermission,
  onDenyPermission,
  className,
}) => {
  if (permissionState !== 'prompt' && permissionState !== 'denied') return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className={cn('w-full max-w-md bg-slate-950 border border-cyan-500/40 rounded-3xl p-6 space-y-4 text-xs font-mono shadow-2xl text-slate-100', className)}
        >
          <div className="flex items-center space-x-2 text-cyan-300 font-extrabold border-b border-slate-800 pb-3">
            <Mic className="w-5 h-5 text-cyan-400 animate-pulse" />
            <span className="uppercase tracking-wider">Microphone Permission Required</span>
          </div>

          <p className="text-sm font-sans font-medium text-slate-200 leading-relaxed">
            Nova AI Operating System requires microphone access to enable voice-first speech understanding, continuous conversation, and push-to-talk.
          </p>

          <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400 space-y-1">
            <div className="font-bold text-slate-200">Local-First Security Guarantee:</div>
            <div>Speech transcription is processed locally without sending audio to untrusted cloud servers.</div>
          </div>

          <div className="flex items-center justify-end space-x-2 pt-2">
            <button
              onClick={onDenyPermission}
              className="px-4 py-2 rounded-xl bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800 font-bold transition-all cursor-pointer"
            >
              Deny
            </button>
            <button
              onClick={onGrantPermission}
              className="px-4 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1"
            >
              <Check className="w-4 h-4" />
              <span>Grant Microphone Access</span>
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default VoicePermissionDialog;
