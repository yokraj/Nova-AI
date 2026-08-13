import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Settings, Globe } from 'lucide-react';
import { cn } from '@/utils/cn';
import { VoiceSettingsConfig } from '../types/voiceSettings';

interface VoiceSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  settings: VoiceSettingsConfig;
  onUpdateSettings: (newSettings: VoiceSettingsConfig) => void;
  className?: string;
}

export const VoiceSettings: React.FC<VoiceSettingsProps> = ({
  isOpen,
  onClose,
  settings,
  onUpdateSettings,
  className,
}) => {
  if (!isOpen) return null;

  const languages = ['English', 'Tamil', 'Hindi', 'Malayalam', 'Kannada', 'Telugu'];

  const toggleConfigKey = (key: keyof VoiceSettingsConfig) => {
    onUpdateSettings({
      ...settings,
      [key]: !settings[key],
    });
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className={cn('w-full max-w-md bg-slate-950 border border-slate-800 rounded-3xl p-6 space-y-5 text-xs font-mono shadow-2xl text-slate-100', className)}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2 text-cyan-300 font-extrabold">
              <Settings className="w-4 h-4 text-cyan-400" />
              <span className="uppercase tracking-wider">Nova Voice Settings</span>
            </div>
            <button onClick={onClose} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Toggle Switches */}
          <div className="space-y-3">
            {[
              { key: 'voiceEnabled', label: 'Voice Enabled', sub: 'Enable Nova Voice Input & Synthesis' },
              { key: 'autoPlayResponses', label: 'Auto-Play Voice Responses', sub: 'Automatically synthesize voice when Nova responds' },
              { key: 'continuousConversation', label: 'Continuous Conversation Mode', sub: 'Return to listening automatically after speaking' },
              { key: 'pushToTalk', label: 'Push-To-Talk (Hold Spacebar)', sub: 'Require Spacebar key press to speak' },
              { key: 'allowInterrupt', label: 'Allow Voice Interruption', sub: 'Interrupt Nova speech playback anytime' },
              { key: 'showLiveTranscript', label: 'Show Live Speech Transcript', sub: 'Display real-time speech transcription' },
            ].map((item) => {
              const value = Boolean(settings[item.key as keyof VoiceSettingsConfig]);
              return (
                <div
                  key={item.key}
                  onClick={() => toggleConfigKey(item.key as keyof VoiceSettingsConfig)}
                  className="flex items-center justify-between p-3 rounded-2xl bg-slate-900/80 border border-slate-800/90 hover:border-slate-700 transition-all cursor-pointer"
                >
                  <div>
                    <div className="font-bold text-slate-200">{item.label}</div>
                    <div className="text-[10px] text-slate-500 font-sans">{item.sub}</div>
                  </div>
                  <div
                    className={cn(
                      'w-10 h-6 rounded-full border p-0.5 transition-colors flex items-center',
                      value ? 'bg-cyan-500/20 border-cyan-500 justify-end' : 'bg-slate-950 border-slate-800 justify-start'
                    )}
                  >
                    <div className={cn('w-4.5 h-4.5 rounded-full', value ? 'bg-cyan-400' : 'bg-slate-600')} />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Language Selection */}
          <div className="space-y-2 pt-2 border-t border-slate-800">
            <div className="flex items-center space-x-2 text-slate-300 font-bold">
              <Globe className="w-4 h-4 text-cyan-400" />
              <span>Language Preference Foundation</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {languages.map((lang) => (
                <button
                  key={lang}
                  onClick={() => onUpdateSettings({ ...settings, language: lang as any })}
                  className={cn(
                    'px-2.5 py-1.5 rounded-xl border text-[11px] font-bold transition-all cursor-pointer text-center',
                    settings.language === lang
                      ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                      : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                  )}
                >
                  {lang}
                </button>
              ))}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default VoiceSettings;
