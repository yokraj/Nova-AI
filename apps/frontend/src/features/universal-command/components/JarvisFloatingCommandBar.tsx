import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  Send,
  Mic,
  MicOff,
  Paperclip,
  Camera,
  X,
  Loader2,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Volume2,
  VolumeX,
  Square,
  FileText,
  Radio,
  Settings2,
  Power,
  Sliders,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { CommandVisualState, AttachedFile, AttachedVision } from '@/types/dashboard';

export interface JarvisFloatingCommandBarProps {
  onExecuteCommand?: (
    command: string,
    mode: 'text' | 'voice' | 'attachment' | 'vision',
    attachments?: { files: AttachedFile[]; vision?: AttachedVision }
  ) => void;
  state?: CommandVisualState;
  className?: string;
  onApprovePermission?: () => void;
  onRejectPermission?: () => void;
  permissionDetails?: {
    action: string;
    resource: string;
    riskLevel?: string;
  };
  executionResult?: {
    success: boolean;
    message: string;
    details?: string;
  };
  onCancel?: () => void;
  isListeningProp?: boolean;
  isSpeakingProp?: boolean;
  onToggleVoice?: () => void;
  onStopSpeaking?: () => void;
  voiceError?: string | null;
  onClearVoiceError?: () => void;
  externalTranscript?: string;
  handsFreeEnabled?: boolean;
  onToggleHandsFree?: () => void;
  isMuted?: boolean;
  onToggleMute?: () => void;
  onEndConversation?: () => void;
  wakePhrase?: string;
  onSetWakePhrase?: (phrase: string) => void;
  voiceState?: string;
  isConversationActive?: boolean;
  detectedLanguage?: string;
  activeVoiceName?: string;
  onOpenVoiceSettings?: () => void;
}

export const JarvisFloatingCommandBar: React.FC<JarvisFloatingCommandBarProps> = ({
  onExecuteCommand,
  state = 'idle',
  className,
  onApprovePermission,
  onRejectPermission,
  permissionDetails,
  executionResult,
  onCancel,
  isListeningProp,
  isSpeakingProp = false,
  onToggleVoice,
  onStopSpeaking,
  voiceError,
  onClearVoiceError,
  externalTranscript,
  handsFreeEnabled = false,
  onToggleHandsFree,
  isMuted = false,
  onToggleMute,
  onEndConversation,
  wakePhrase = 'Hey Nova',
  onSetWakePhrase,
  voiceState = 'IDLE',
  isConversationActive = false,
  detectedLanguage = 'en-IN',
  activeVoiceName = 'NOVA — Indian Professional',
  onOpenVoiceSettings,
}) => {
  const [commandText, setCommandText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([]);
  const [attachedVision, setAttachedVision] = useState<AttachedVision | null>(null);
  const [isEditingWakePhrase, setIsEditingWakePhrase] = useState(false);
  const [tempWakePhrase, setTempWakePhrase] = useState(wakePhrase);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const listeningActive = isListeningProp !== undefined ? isListeningProp : isListening;

  // Sync external transcript from voice recognition
  useEffect(() => {
    if (externalTranscript && listeningActive) {
      setCommandText(externalTranscript);
    }
  }, [externalTranscript, listeningActive]);

  const handleToggleVoice = () => {
    if (onToggleVoice) {
      onToggleVoice();
      return;
    }

    if (listeningActive) {
      setIsListening(false);
      if (onCancel) onCancel();
    } else {
      setIsListening(true);
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        try {
          const SpeechRecognition =
            (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
          const recognition = new SpeechRecognition();
          recognition.continuous = false;
          recognition.interimResults = true;
          recognition.lang = 'en-US';
          recognition.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript;
            if (transcript) {
              setCommandText(transcript);
              if (event.results[0].isFinal) {
                setIsListening(false);
                onExecuteCommand?.(transcript, 'voice');
              }
            }
          };
          recognition.onerror = () => setIsListening(false);
          recognition.onend = () => setIsListening(false);
          recognition.start();
        } catch {
          setIsListening(false);
        }
      }
    }
  };

  const handleSend = () => {
    const text = commandText.trim();
    if (!text && attachedFiles.length === 0 && !attachedVision) return;

    const mode = listeningActive
      ? 'voice'
      : attachedVision
      ? 'vision'
      : attachedFiles.length > 0
      ? 'attachment'
      : 'text';
    onExecuteCommand?.(text || 'Inspect attached files', mode, {
      files: attachedFiles,
      vision: attachedVision || undefined,
    });

    setCommandText('');
    setAttachedFiles([]);
    setAttachedVision(null);
    setIsListening(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files).map((f) => ({
        id: `file-${Date.now()}-${f.name}`,
        name: f.name,
        size: f.size,
        type: f.name.endsWith('.py')
          ? ('code' as const)
          : f.name.endsWith('.pdf') || f.name.endsWith('.docx')
          ? ('document' as const)
          : f.type.startsWith('image/')
          ? ('image' as const)
          : ('document' as const),
      }));
      setAttachedFiles((prev) => [...prev, ...files]);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (event) => {
        setAttachedVision({
          id: `vision-${Date.now()}`,
          title: f.name,
          previewUrl: event.target?.result as string,
          timestamp: new Date().toLocaleTimeString(),
        });
      };
      reader.readAsDataURL(f);
    }
  };

  return (
    <div className={cn('w-full max-w-3xl mx-auto flex flex-col items-center space-y-2.5 z-20', className)}>
      {/* 1. Visible Voice Error Banner (if mic denied or unsupported) */}
      <AnimatePresence>
        {voiceError && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            className="w-full px-4 py-2.5 rounded-xl bg-rose-950/80 border border-rose-500/50 backdrop-blur-xl shadow-[0_0_20px_rgba(244,63,94,0.25)] flex items-center justify-between text-xs font-mono select-none"
          >
            <div className="flex items-center space-x-2 text-rose-300">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{voiceError}</span>
            </div>
            <button
              onClick={onClearVoiceError}
              className="text-slate-400 hover:text-white ml-3 cursor-pointer p-1"
              title="Dismiss warning"
              aria-label="Dismiss error"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </motion.div>
        )}

        {/* 2. Vocal Synthesis Active Banner (Speaking state with Halt Audio button) */}
        {isSpeakingProp && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            className="w-full px-4 py-2 rounded-xl bg-cyan-950/70 border border-cyan-400/50 backdrop-blur-md shadow-[0_0_25px_rgba(0,240,255,0.25)] flex items-center justify-between text-xs font-mono select-none"
          >
            <div className="flex items-center space-x-2.5 text-cyan-300">
              <Volume2 className="w-4 h-4 text-cyan-400 animate-pulse" />
              <span className="font-bold tracking-wider uppercase">NOVA VOCAL SYNTHESIS ACTIVE...</span>
            </div>
            <button
              onClick={onStopSpeaking}
              className="px-2.5 py-1 rounded-lg bg-cyan-950 border border-cyan-500/40 text-cyan-300 hover:text-white hover:bg-cyan-900/60 transition-colors text-[11px] font-semibold flex items-center space-x-1.5 cursor-pointer"
              title="Stop speech"
              aria-label="Stop speech"
            >
              <Square className="w-2.5 h-2.5 fill-cyan-400 text-cyan-400" />
              <span>Halt Audio</span>
            </button>
          </motion.div>
        )}

        {/* 3. In-Flight Execution Status or Permission Approval HUD Banner */}
        {state === 'waiting_for_permission' && permissionDetails && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.98 }}
            className="w-full p-4 rounded-2xl bg-amber-950/40 border border-amber-500/50 backdrop-blur-xl shadow-[0_0_30px_rgba(245,158,11,0.2)] flex flex-col sm:flex-row items-center justify-between gap-3 select-none"
          >
            <div className="flex items-center space-x-3 text-left">
              <div className="p-2 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-400">
                <ShieldAlert className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <span className="text-[10px] font-mono tracking-widest text-amber-400 font-bold uppercase">
                  SECURITY AUTHORIZATION REQUIRED
                </span>
                <p className="text-xs text-slate-200 font-medium">
                  Allow <span className="text-amber-300 font-mono font-bold">{permissionDetails.action}</span> on{' '}
                  <span className="text-slate-100 font-mono">{permissionDetails.resource}</span>?
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-2 shrink-0">
              <button
                onClick={onRejectPermission}
                className="px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 hover:text-white hover:border-slate-600 text-xs font-mono transition-all cursor-pointer"
              >
                Reject
              </button>
              <button
                onClick={onApprovePermission}
                className="px-4 py-1.5 rounded-xl bg-amber-500/20 border border-amber-400/60 text-amber-300 hover:bg-amber-500/30 font-mono text-xs font-bold transition-all shadow-[0_0_15px_rgba(245,158,11,0.3)] cursor-pointer"
              >
                Authorize & Execute
              </button>
            </div>
          </motion.div>
        )}

        {(state === 'processing' || state === 'executing') && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="w-full px-4 py-2 rounded-xl bg-cyan-950/40 border border-cyan-500/40 backdrop-blur-md shadow-[0_0_20px_rgba(0,240,255,0.15)] flex items-center justify-between text-xs font-mono select-none"
          >
            <div className="flex items-center space-x-2.5">
              <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />
              <span className="text-cyan-300 font-bold tracking-wider uppercase">
                {state === 'processing'
                  ? 'NEURAL SYNTHESIS IN PROGRESS...'
                  : 'PHYSICAL WORKSTATION DISPATCH ACTIVE...'}
              </span>
            </div>
            {onCancel && (
              <button
                onClick={onCancel}
                className="text-slate-400 hover:text-rose-400 text-[11px] underline cursor-pointer"
              >
                Cancel
              </button>
            )}
          </motion.div>
        )}

        {state === 'completed' && executionResult && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="w-full px-4 py-2.5 rounded-xl bg-emerald-950/40 border border-emerald-500/40 backdrop-blur-md shadow-[0_0_20px_rgba(16,185,129,0.15)] flex items-center justify-between text-xs font-mono select-none"
          >
            <div className="flex items-center space-x-2.5 text-left">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span className="text-emerald-300">
                {executionResult.message || 'Operation executed and verified.'}
              </span>
            </div>
            <button
              onClick={onCancel}
              className="text-slate-500 hover:text-slate-300 ml-2 cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 4. Attachment Chips Preview */}
      {(attachedFiles.length > 0 || attachedVision) && (
        <div className="w-full flex items-center flex-wrap gap-2 px-2">
          {attachedVision && (
            <div className="flex items-center space-x-2 px-2.5 py-1 rounded-xl bg-cyan-950/60 border border-cyan-500/40 text-cyan-300 text-xs font-mono">
              <Camera className="w-3.5 h-3.5" />
              <span className="truncate max-w-[140px]">{attachedVision.title}</span>
              <button
                onClick={() => setAttachedVision(null)}
                className="hover:text-white cursor-pointer ml-1"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}
          {attachedFiles.map((file) => (
            <div
              key={file.id}
              className="flex items-center space-x-2 px-2.5 py-1 rounded-xl bg-slate-900/80 border border-cyan-500/30 text-slate-300 text-xs font-mono"
            >
              <FileText className="w-3.5 h-3.5 text-cyan-400" />
              <span className="truncate max-w-[140px]">{file.name}</span>
              <button
                onClick={() => setAttachedFiles((prev) => prev.filter((f) => f.id !== file.id))}
                className="hover:text-rose-400 cursor-pointer ml-1"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* 4.5. Hands-Free Mode & Wake Word HUD Strip */}
      <div className="w-full flex items-center justify-between px-3 py-1.5 rounded-xl bg-[#030712]/90 border border-cyan-500/25 backdrop-blur-xl text-xs font-mono shadow-[0_0_15px_rgba(0,0,0,0.5)]">
        {/* Left: Hands-Free Switch & State Badge */}
        <div className="flex items-center space-x-2">
          <button
            onClick={onToggleHandsFree}
            className={cn(
              'px-2.5 py-1 rounded-lg flex items-center space-x-1.5 transition-all text-[11px] font-bold cursor-pointer select-none',
              handsFreeEnabled
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/60 shadow-[0_0_12px_rgba(0,240,255,0.3)]'
                : 'bg-slate-900/60 text-slate-400 border border-slate-700/50 hover:text-slate-200 hover:border-slate-600'
            )}
            title={handsFreeEnabled ? "Hands-Free Active (say 'Hey Nova')" : 'Enable Hands-Free Wake Word Mode'}
          >
            <Radio
              className={cn(
                'w-3.5 h-3.5',
                handsFreeEnabled ? 'text-cyan-400 animate-pulse' : 'text-slate-500'
              )}
            />
            <span>Hands-Free: {handsFreeEnabled ? 'ON' : 'OFF'}</span>
          </button>

          {/* Dynamic Voice State Badge */}
          {handsFreeEnabled ? (
            <div
              className={cn(
                'px-2 py-0.5 rounded-md text-[10px] font-bold tracking-wider uppercase border',
                voiceState === 'SLEEPING'
                  ? 'bg-cyan-950/60 text-cyan-400 border-cyan-500/40 animate-pulse shadow-[0_0_10px_rgba(0,240,255,0.2)]'
                  : voiceState === 'LISTENING'
                  ? 'bg-sky-950/70 text-sky-300 border-sky-400/60 shadow-[0_0_12px_rgba(56,189,248,0.5)] animate-pulse'
                  : voiceState === 'TRANSCRIBING'
                  ? 'bg-cyan-950/80 text-cyan-200 border-cyan-400/80 shadow-[0_0_15px_rgba(0,229,255,0.6)] animate-pulse'
                  : voiceState === 'THINKING'
                  ? 'bg-purple-950/70 text-purple-300 border-purple-400/60'
                  : voiceState === 'SPEAKING'
                  ? 'bg-cyan-950/70 text-cyan-300 border-cyan-400/60 animate-pulse'
                  : voiceState === 'INTERRUPTED'
                  ? 'bg-orange-950/70 text-orange-400 border-orange-500/60'
                  : 'bg-slate-900 text-slate-400 border-slate-700'
              )}
            >
              {voiceState === 'SLEEPING'
                ? `STANDBY: "${wakePhrase}"`
                : voiceState === 'LISTENING'
                ? 'LISTENING...'
                : voiceState === 'TRANSCRIBING'
                ? 'DECODING...'
                : voiceState === 'THINKING'
                ? 'REASONING...'
                : voiceState === 'SPEAKING'
                ? 'SPEAKING (Say "Stop")'
                : voiceState === 'INTERRUPTED'
                ? 'INTERRUPTED'
                : voiceState}
            </div>
          ) : (
            <span className="text-[11px] text-slate-500 font-mono hidden sm:inline">
              Push-to-talk mode ready
            </span>
          )}

          {/* Multilingual Status Pill */}
          <span className="text-[10px] px-2 py-0.5 rounded-md bg-slate-900/90 text-cyan-300 border border-cyan-500/30 hidden md:inline font-mono">
            LANG: {detectedLanguage.toUpperCase()}
          </span>
        </div>

        {/* Right: Wake Config, Mute, End Session */}
        <div className="flex items-center space-x-1.5">
          {handsFreeEnabled && (
            <>
              {/* Wake Phrase Config / Display */}
              {isEditingWakePhrase ? (
                <div className="flex items-center space-x-1">
                  <input
                    type="text"
                    value={tempWakePhrase}
                    onChange={(e) => setTempWakePhrase(e.target.value)}
                    placeholder="e.g. Hey Nova"
                    className="px-2 py-0.5 rounded bg-black border border-cyan-500/60 text-[11px] text-cyan-300 focus:outline-none w-28"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        onSetWakePhrase?.(tempWakePhrase);
                        setIsEditingWakePhrase(false);
                      } else if (e.key === 'Escape') {
                        setIsEditingWakePhrase(false);
                      }
                    }}
                  />
                  <button
                    onClick={() => {
                      onSetWakePhrase?.(tempWakePhrase);
                      setIsEditingWakePhrase(false);
                    }}
                    className="px-2 py-0.5 rounded bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-[10px] font-bold cursor-pointer"
                  >
                    Set
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => {
                    setTempWakePhrase(wakePhrase);
                    setIsEditingWakePhrase(true);
                  }}
                  className="px-2 py-0.5 rounded bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 text-[10px] border border-slate-700/60 flex items-center space-x-1 cursor-pointer transition-colors"
                  title="Configure Wake Phrase"
                >
                  <Settings2 className="w-3 h-3 text-cyan-400" />
                  <span>Wake: "{wakePhrase}"</span>
                </button>
              )}

              {/* Microphone Mute / Unmute */}
              <button
                onClick={onToggleMute}
                className={cn(
                  'p-1.5 rounded-lg transition-colors cursor-pointer',
                  isMuted
                    ? 'bg-rose-950/70 text-rose-300 border border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]'
                    : 'text-slate-400 hover:text-cyan-300 hover:bg-slate-900/80'
                )}
                title={isMuted ? 'Unmute Microphone' : 'Mute Microphone'}
              >
                {isMuted ? <MicOff className="w-3.5 h-3.5 text-rose-400" /> : <Mic className="w-3.5 h-3.5" />}
              </button>

              {/* End Active Conversation Session */}
              {isConversationActive && (
                <button
                  onClick={onEndConversation}
                  className="px-2 py-0.5 rounded bg-rose-950/50 text-rose-300 hover:bg-rose-900/70 hover:text-white border border-rose-500/40 text-[10px] font-bold flex items-center space-x-1 cursor-pointer transition-colors"
                  title="End Conversation Session (or say 'Goodbye Nova')"
                >
                  <Power className="w-3 h-3 text-rose-400" />
                  <span className="hidden sm:inline">End Session</span>
                </button>
              )}
            </>
          )}

          {/* Dedicated Voice Settings Dialog Toggle */}
          {onOpenVoiceSettings && (
            <button
              onClick={onOpenVoiceSettings}
              className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-300 hover:bg-slate-900/80 transition-colors cursor-pointer border border-transparent hover:border-cyan-500/30 ml-1"
              title="Nova Voice 2.0 Settings & Personality"
            >
              <Sliders className="w-3.5 h-3.5 text-cyan-400" />
            </button>
          )}
        </div>
      </div>

      {/* 5. Central Floating Glassmorphic Command Input Bar */}
      <div className="relative w-full rounded-2xl p-[1px] bg-gradient-to-r from-cyan-500/40 via-sky-500/20 to-blue-600/40 shadow-[0_8px_35px_rgba(0,0,0,0.8),0_0_25px_rgba(0,240,255,0.12)]">
        <div className="relative w-full flex items-center bg-[#030712]/90 backdrop-blur-2xl rounded-[15px] px-3 sm:px-4 py-2 border border-cyan-500/20">
          {/* Sparkles / Command Indicator */}
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shrink-0 mr-2 sm:mr-3">
            <Sparkles className="w-4 h-4" />
          </div>

          {/* Primary Text Input */}
          <input
            ref={inputRef}
            type="text"
            value={commandText}
            onChange={(e) => setCommandText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              listeningActive
                ? 'Listening to acoustic input...'
                : isSpeakingProp
                ? 'Nova is speaking (click mic to halt)...'
                : 'Ask Nova anything...'
            }
            className="w-full bg-transparent text-sm sm:text-base text-slate-100 placeholder-slate-500 focus:outline-none font-sans min-w-0"
            disabled={state === 'processing' || state === 'executing'}
          />

          {/* Action Button Strip */}
          <div className="flex items-center space-x-1.5 sm:space-x-2 shrink-0 ml-2">
            {/* Hidden File & Image Inputs */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              multiple
              className="hidden"
            />
            <input
              type="file"
              ref={imageInputRef}
              onChange={handleImageChange}
              accept="image/*"
              className="hidden"
            />

            {/* Document Attachment Button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-2 rounded-xl text-slate-400 hover:text-cyan-300 hover:bg-slate-900 border border-transparent hover:border-cyan-500/30 transition-all cursor-pointer focus:outline-none"
              title="Attach File or Document"
              aria-label="Attach file"
            >
              <Paperclip className="w-4 h-4" />
            </button>

            {/* Camera / Vision Button */}
            <button
              onClick={() => imageInputRef.current?.click()}
              className="p-2 rounded-xl text-slate-400 hover:text-cyan-300 hover:bg-slate-900 border border-transparent hover:border-cyan-500/30 transition-all cursor-pointer focus:outline-none"
              title="Attach Vision Screenshot or Image"
              aria-label="Attach vision"
            >
              <Camera className="w-4 h-4" />
            </button>

            {/* Live Microphone Voice Input Button */}
            <button
              onClick={handleToggleVoice}
              className={cn(
                'p-2 rounded-xl transition-all cursor-pointer focus:outline-none relative',
                listeningActive
                  ? 'bg-cyan-500/30 text-cyan-200 border border-cyan-400 shadow-[0_0_20px_rgba(0,240,255,0.7)] animate-pulse'
                  : isSpeakingProp
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-400/60 shadow-[0_0_15px_rgba(56,189,248,0.4)]'
                  : 'text-slate-400 hover:text-cyan-300 hover:bg-slate-900 border border-transparent hover:border-cyan-500/30'
              )}
              title={
                listeningActive
                  ? 'Stop Listening'
                  : isSpeakingProp
                  ? 'Stop Vocal Synthesis'
                  : 'Voice Command Input'
              }
              aria-label="Toggle voice input"
            >
              {listeningActive ? (
                <Mic className="w-4 h-4 animate-bounce text-cyan-300" />
              ) : isSpeakingProp ? (
                <VolumeX className="w-4 h-4 text-sky-300" />
              ) : (
                <Mic className="w-4 h-4" />
              )}
            </button>

            {/* Execute / Send Button */}
            <button
              onClick={handleSend}
              disabled={!commandText.trim() && attachedFiles.length === 0 && !attachedVision}
              className={cn(
                'px-3.5 py-2 rounded-xl flex items-center space-x-1.5 font-mono text-xs font-bold transition-all cursor-pointer focus:outline-none',
                commandText.trim() || attachedFiles.length > 0 || attachedVision
                  ? 'bg-cyan-500 text-slate-950 hover:bg-cyan-400 shadow-[0_0_20px_rgba(0,240,255,0.4)]'
                  : 'bg-slate-900/80 text-slate-600 border border-slate-800 cursor-not-allowed'
              )}
              aria-label="Execute command"
            >
              <span className="hidden sm:inline">Send</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JarvisFloatingCommandBar;
