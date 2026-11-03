import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  Send,
  Mic,
  MicOff,
  Paperclip,
  Camera,
  Terminal,
  MessageSquare,
  CheckCircle2,
  XCircle,
  Loader2,
  ShieldAlert,
  AlertTriangle,
  RotateCcw,
  X,
  FileCode,
  FileText,
  Image as ImageIcon,
  StopCircle,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { CommandVisualState, AttachedFile, AttachedVision } from '@/types/dashboard';

export interface UniversalCommandAreaProps {
  onExecuteCommand?: (command: string, mode: 'text' | 'voice' | 'attachment' | 'vision', attachments?: { files: AttachedFile[]; vision?: AttachedVision }) => void;
  state?: CommandVisualState;
  className?: string;
  // External control props
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
    outcomeData?: Record<string, any>;
  };
  errorMessage?: string;
  onCancel?: () => void;
  onRetry?: () => void;
  isListeningProp?: boolean;
}

export const UniversalCommandArea: React.FC<UniversalCommandAreaProps> = ({
  onExecuteCommand,
  state: externalState,
  className,
  onApprovePermission,
  onRejectPermission,
  permissionDetails,
  executionResult,
  errorMessage: externalErrorMessage,
  onCancel,
  onRetry,
  isListeningProp,
}) => {
  // Internal state machine when not externally controlled
  const [internalState, setInternalState] = useState<CommandVisualState>('idle');
  const currentState = externalState || internalState;

  const [inputMode, setInputMode] = useState<'text' | 'voice' | 'attachment' | 'vision'>('text');
  const [commandText, setCommandText] = useState('');
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([]);
  const [attachedVision, setAttachedVision] = useState<AttachedVision | null>(null);
  const [activeStepText, setActiveStepText] = useState<string>('Initializing plan...');
  const [stepProgress, setStepProgress] = useState<number>(0);
  const [localError, setLocalError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const commandSuggestions = [
    'Analyze Nova monorepo architecture',
    'Synthesize research on FastAPI vs Go',
    'Run background security vulnerability scan',
    'Audit Docker container topology',
    'Summarize vector memory growth',
    'Schedule morning standup automation',
  ];

  // Voice recording toggle
  const isListening = isListeningProp !== undefined ? isListeningProp : currentState === 'listening';

  const handleToggleVoice = () => {
    if (isListening) {
      if (onCancel) onCancel();
      setInternalState('idle');
    } else {
      setInputMode('voice');
      setInternalState('listening');
      setCommandText('');

      if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        try {
          const SpeechRecognitionClass = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
          const rec = new SpeechRecognitionClass();
          rec.continuous = false;
          rec.interimResults = true;
          rec.lang = 'en-US';
          rec.onresult = (e: any) => {
            const transcript = e.results[0][0].transcript;
            if (transcript) {
              setCommandText(transcript);
              if (e.results[0].isFinal) {
                setInternalState('processing');
                handleCommandSubmit(transcript);
              }
            }
          };
          rec.onerror = () => setInternalState('idle');
          rec.onend = () => setInternalState('idle');
          rec.start();
        } catch {
          setInternalState('idle');
        }
      }
    }
  };

  // Handle Command Submit
  const handleCommandSubmit = useCallback((overrideText?: string) => {
    const textToRun = (overrideText || commandText).trim();
    if (!textToRun && attachedFiles.length === 0 && !attachedVision) return;

    setLocalError(null);

    if (onExecuteCommand) {
      onExecuteCommand(textToRun, inputMode, {
        files: attachedFiles,
        vision: attachedVision || undefined,
      });
    }

    // If no external controller manages states, advance internal state
    if (!externalState) {
      setInternalState('processing');
      setTimeout(() => {
        setInternalState('executing');
        setActiveStepText('Allocating autonomous reasoning agents...');
        setStepProgress(35);

        setTimeout(() => {
          setStepProgress(70);
          setActiveStepText('Synthesizing workspace context & dependencies...');

          setTimeout(() => {
            setStepProgress(100);
            setInternalState('completed');
          }, 1200);
        }, 1200);
      }, 1000);
    }
  }, [commandText, attachedFiles, attachedVision, onExecuteCommand, inputMode, externalState]);

  // File Attachment Handling
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles: AttachedFile[] = Array.from(e.target.files).map((file) => ({
        id: `file-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
        name: file.name,
        size: file.size,
        type: file.type || 'application/octet-stream',
      }));
      setAttachedFiles((prev) => [...prev, ...newFiles]);
      setInputMode('attachment');
      e.target.value = '';
    }
  };

  const removeFile = (id: string) => {
    setAttachedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  // Vision / Screenshot Attachment Handling
  const handleCaptureScreenshot = () => {
    const mockVision: AttachedVision = {
      id: `vis-${Date.now()}`,
      title: 'Active Desktop Display (1920x1080)',
      previewUrl: '',
      timestamp: new Date().toLocaleTimeString(),
    };
    setAttachedVision(mockVision);
    setInputMode('vision');
    if (!commandText) {
      setCommandText('Inspect UI elements in active window and report anomalies');
    }
  };

  const removeVision = () => {
    setAttachedVision(null);
  };

  // Cancellation
  const handleCancelClick = () => {
    if (onCancel) {
      onCancel();
    }
    setInternalState('cancelled');
  };

  // Reset
  const handleReset = () => {
    setInternalState('idle');
    setCommandText('');
    setAttachedFiles([]);
    setAttachedVision(null);
    setLocalError(null);
    if (onRetry) onRetry();
  };

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileIcon = (type: string) => {
    if (type.includes('image')) return ImageIcon;
    if (type.includes('code') || type.includes('typescript') || type.includes('javascript') || type.includes('json')) return FileCode;
    return FileText;
  };

  return (
    <div
      className={cn(
        'glass-panel p-5 sm:p-6 rounded-2xl sm:rounded-3xl border border-cyan-500/30 relative overflow-hidden shadow-[0_0_30px_rgba(0,240,255,0.1)] select-none transition-all',
        currentState === 'listening' && 'border-purple-500/60 shadow-[0_0_40px_rgba(168,85,247,0.25)]',
        currentState === 'waiting_for_permission' && 'border-amber-500/60 shadow-[0_0_40px_rgba(245,158,11,0.2)]',
        currentState === 'failed' && 'border-rose-500/60 shadow-[0_0_40px_rgba(244,63,94,0.2)]',
        currentState === 'completed' && 'border-emerald-500/50 shadow-[0_0_35px_rgba(16,185,129,0.2)]',
        className
      )}
    >
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        multiple
        className="hidden"
        aria-label="Upload file attachment"
      />

      {/* Subtle ambient cyber gradient */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-cyan-500/10 via-purple-600/10 to-transparent rounded-full blur-3xl pointer-events-none" />

      {/* Header bar with greeting & state pill */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 sm:mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 sm:p-3 bg-gradient-to-tr from-cyan-500/20 to-purple-500/20 rounded-2xl text-cyan-300 border border-cyan-500/40 shadow-[0_0_15px_rgba(0,240,255,0.2)] shrink-0">
            <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 animate-pulse" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-extrabold text-slate-100 tracking-tight flex items-center gap-2">
              <span>Universal Command Center</span>
            </h2>
            <p className="text-xs text-slate-400 font-mono">
              TEXT • VOICE • VISION • MULTIMODAL AUTONOMOUS ORCHESTRATION
            </p>
          </div>
        </div>

        {/* State Badge Indicator */}
        <div className="flex items-center space-x-2">
          {currentState === 'idle' && (
            <span className="inline-flex items-center space-x-1.5 text-[11px] font-mono font-bold px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <span>CORE READY</span>
            </span>
          )}

          {currentState === 'listening' && (
            <span className="inline-flex items-center space-x-1.5 text-[11px] font-mono font-bold px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/50 animate-pulse">
              <span className="w-2 h-2 rounded-full bg-purple-400 animate-ping" />
              <span>VOICE: LISTENING</span>
            </span>
          )}

          {currentState === 'processing' && (
            <span className="inline-flex items-center space-x-1.5 text-[11px] font-mono font-bold px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/50">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
              <span>SYNTHESIZING INTENT</span>
            </span>
          )}

          {currentState === 'executing' && (
            <span className="inline-flex items-center space-x-1.5 text-[11px] font-mono font-bold px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/50">
              <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
              <span>EXECUTING MISSION</span>
            </span>
          )}

          {currentState === 'waiting_for_permission' && (
            <span className="inline-flex items-center space-x-1.5 text-[11px] font-mono font-bold px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/50">
              <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
              <span>AWAITING APPROVAL</span>
            </span>
          )}

          {currentState === 'completed' && (
            <span className="inline-flex items-center space-x-1.5 text-[11px] font-mono font-bold px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/50">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>COMPLETED</span>
            </span>
          )}

          {currentState === 'failed' && (
            <span className="inline-flex items-center space-x-1.5 text-[11px] font-mono font-bold px-3 py-1 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/50">
              <XCircle className="w-3.5 h-3.5 text-rose-400" />
              <span>FAILED</span>
            </span>
          )}

          {currentState === 'cancelled' && (
            <span className="inline-flex items-center space-x-1.5 text-[11px] font-mono font-bold px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              <X className="w-3.5 h-3.5 text-slate-400" />
              <span>CANCELLED</span>
            </span>
          )}
        </div>
      </div>

      {/* Interaction Mode Selector Tabs */}
      <div className="flex items-center space-x-1 mb-3 bg-slate-900/90 p-1 rounded-xl border border-slate-800/90 w-fit overflow-x-auto max-w-full">
        <button
          onClick={() => setInputMode('text')}
          className={cn(
            'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer whitespace-nowrap focus:outline-none focus:ring-1 focus:ring-cyan-400',
            inputMode === 'text'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          )}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Text Command</span>
        </button>

        <button
          onClick={handleToggleVoice}
          className={cn(
            'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer whitespace-nowrap focus:outline-none focus:ring-1 focus:ring-purple-400',
            inputMode === 'voice' || currentState === 'listening'
              ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          )}
        >
          <Mic className="w-3.5 h-3.5" />
          <span>Voice Mode</span>
        </button>

        <button
          onClick={() => {
            setInputMode('attachment');
            fileInputRef.current?.click();
          }}
          className={cn(
            'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer whitespace-nowrap focus:outline-none focus:ring-1 focus:ring-blue-400',
            inputMode === 'attachment' || attachedFiles.length > 0
              ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40 shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          )}
        >
          <Paperclip className="w-3.5 h-3.5" />
          <span>Attachments {attachedFiles.length > 0 && `(${attachedFiles.length})`}</span>
        </button>

        <button
          onClick={() => {
            setInputMode('vision');
            if (!attachedVision) handleCaptureScreenshot();
          }}
          className={cn(
            'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer whitespace-nowrap focus:outline-none focus:ring-1 focus:ring-emerald-400',
            inputMode === 'vision' || attachedVision
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          )}
        >
          <Camera className="w-3.5 h-3.5" />
          <span>Vision / Screen</span>
        </button>
      </div>

      {/* Attachment Previews */}
      {(attachedFiles.length > 0 || attachedVision) && (
        <div className="mb-3 flex items-center flex-wrap gap-2 pt-1 pb-1">
          {/* Vision Screenshot Badge */}
          {attachedVision && (
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-mono">
              <Camera className="w-3.5 h-3.5 text-emerald-400" />
              <span>{attachedVision.title}</span>
              <button
                onClick={removeVision}
                className="hover:text-emerald-100 p-0.5 rounded cursor-pointer"
                title="Remove vision context"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}

          {/* Files Badges */}
          {attachedFiles.map((file) => {
            const FileIcon = getFileIcon(file.type);
            return (
              <div
                key={file.id}
                className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs font-mono"
              >
                <FileIcon className="w-3.5 h-3.5 text-blue-400" />
                <span className="truncate max-w-[160px]">{file.name}</span>
                <span className="text-slate-500 text-[10px]">({formatFileSize(file.size)})</span>
                <button
                  onClick={() => removeFile(file.id)}
                  className="hover:text-blue-100 p-0.5 rounded cursor-pointer"
                  title="Remove attachment"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Voice Wave Visualizer when Listening */}
      <AnimatePresence>
        {currentState === 'listening' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-3 p-3.5 rounded-2xl bg-purple-950/40 border border-purple-500/40 flex items-center justify-between"
          >
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 rounded-full bg-rose-500 animate-ping" />
              <span className="text-xs font-mono text-purple-200 font-semibold">
                Listening for spoken instructions... (VAD active)
              </span>
            </div>

            {/* Simulated Animated Waveform Bars */}
            <div className="flex items-center space-x-1 h-5">
              {[4, 12, 18, 10, 16, 22, 14, 8, 19, 11].map((h, i) => (
                <motion.div
                  key={i}
                  animate={{ height: [4, h, 6] }}
                  transition={{
                    duration: 0.6 + (i % 3) * 0.2,
                    repeat: Infinity,
                    repeatType: 'reverse',
                  }}
                  className="w-1 bg-purple-400 rounded-full"
                />
              ))}
            </div>

            <button
              onClick={handleToggleVoice}
              className="px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 text-xs font-mono transition-all cursor-pointer flex items-center space-x-1"
            >
              <StopCircle className="w-3.5 h-3.5" />
              <span>Stop</span>
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Input Box */}
      <div className="relative group">
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cyan-500/20 via-blue-600/20 to-purple-600/20 blur-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
        <div className="relative flex items-center bg-slate-950/95 rounded-2xl border border-slate-800 group-hover:border-cyan-500/50 transition-all p-2 shadow-inner focus-within:border-cyan-400">
          <Terminal className="w-5 h-5 text-cyan-400 ml-3 mr-2 shrink-0" />

          <input
            ref={inputRef}
            type="text"
            value={commandText}
            onChange={(e) => setCommandText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleCommandSubmit();
              }
            }}
            disabled={currentState === 'processing' || currentState === 'executing'}
            placeholder={
              currentState === 'listening'
                ? 'Listening... speak now or type to override...'
                : inputMode === 'voice'
                ? 'Speak into microphone or enter voice command...'
                : inputMode === 'attachment'
                ? 'Enter instructions for attached files...'
                : inputMode === 'vision'
                ? 'Enter vision analysis prompt...'
                : 'Ask Nova anything or enter system command...'
            }
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none py-2 px-1 font-sans disabled:opacity-50"
            aria-label="Command input"
          />

          <div className="flex items-center space-x-1.5 mr-1 shrink-0">
            {/* Attachment Button */}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                'p-2 rounded-xl border transition-all cursor-pointer',
                attachedFiles.length > 0
                  ? 'bg-blue-500/20 text-blue-300 border-blue-500/40'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-cyan-300 hover:border-slate-700'
              )}
              title="Attach Document or Code File"
              aria-label="Attach File"
            >
              <Paperclip className="w-4 h-4" />
            </button>

            {/* Vision Button */}
            <button
              type="button"
              onClick={handleCaptureScreenshot}
              className={cn(
                'p-2 rounded-xl border transition-all cursor-pointer',
                attachedVision
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-cyan-300 hover:border-slate-700'
              )}
              title="Add Screenshot Context"
              aria-label="Vision input"
            >
              <Camera className="w-4 h-4" />
            </button>

            {/* Voice Mic Button */}
            <motion.button
              type="button"
              whileTap={{ scale: 0.95 }}
              onClick={handleToggleVoice}
              className={cn(
                'p-2 rounded-xl transition-all cursor-pointer border flex items-center justify-center',
                currentState === 'listening'
                  ? 'bg-rose-500 text-white border-rose-400 animate-pulse shadow-[0_0_15px_rgba(244,63,94,0.6)]'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-purple-300 hover:border-purple-500/40'
              )}
              title={currentState === 'listening' ? 'Stop Listening' : 'Activate Voice Command'}
              aria-label="Toggle Voice"
            >
              {currentState === 'listening' ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </motion.button>

            {/* Execute / Send Button */}
            <button
              type="button"
              disabled={
                currentState === 'processing' ||
                currentState === 'executing' ||
                (!commandText.trim() && attachedFiles.length === 0 && !attachedVision)
              }
              onClick={() => handleCommandSubmit()}
              className={cn(
                'px-4 py-2 rounded-xl font-bold text-xs font-mono transition-all cursor-pointer flex items-center space-x-1.5 focus:outline-none focus:ring-2 focus:ring-cyan-400',
                currentState === 'processing' || currentState === 'executing'
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : commandText.trim() || attachedFiles.length > 0 || attachedVision
                  ? 'bg-cyan-500 text-slate-950 hover:bg-cyan-400 shadow-[0_0_15px_rgba(0,240,255,0.4)]'
                  : 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed'
              )}
            >
              {currentState === 'processing' || currentState === 'executing' ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>RUNNING</span>
                </>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" />
                  <span>EXECUTE</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Suggestion Chips (Visible when idle) */}
      {currentState === 'idle' && (
        <div className="mt-3.5 flex items-center space-x-2 overflow-x-auto pb-1 scrollbar-none">
          <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider shrink-0 mr-1">
            Suggestions:
          </span>
          {commandSuggestions.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => {
                setCommandText(suggestion);
                handleCommandSubmit(suggestion);
              }}
              className="px-3 py-1 rounded-xl bg-slate-900/90 text-slate-300 hover:text-cyan-300 hover:bg-cyan-500/10 border border-slate-800 hover:border-cyan-500/30 text-xs transition-all whitespace-nowrap cursor-pointer shrink-0 font-sans"
            >
              + {suggestion}
            </button>
          ))}
        </div>
      )}

      {/* ACTIVE STATE NOTIFICATION BANNERS */}
      <AnimatePresence mode="wait">
        {/* 1. Processing State */}
        {currentState === 'processing' && (
          <motion.div
            key="processing-banner"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="mt-4 p-4 rounded-2xl bg-cyan-950/40 border border-cyan-500/40 flex items-center justify-between text-xs font-mono"
          >
            <div className="flex items-center space-x-3 text-cyan-300">
              <Loader2 className="w-4 h-4 animate-spin text-cyan-400 shrink-0" />
              <span>Nova Intelligence Core is decomposing goal and routing capabilities...</span>
            </div>
            <button
              onClick={handleCancelClick}
              className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs hover:text-rose-300 transition-all cursor-pointer"
            >
              Cancel
            </button>
          </motion.div>
        )}

        {/* 2. Executing State */}
        {currentState === 'executing' && (
          <motion.div
            key="executing-banner"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="mt-4 p-4 rounded-2xl bg-blue-950/40 border border-blue-500/40 space-y-2 text-xs font-mono"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-blue-300 font-semibold">
                <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
                <span>Executing Mission Pipeline: {activeStepText}</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-cyan-300 font-bold">{stepProgress}%</span>
                <button
                  onClick={handleCancelClick}
                  className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-rose-300 text-xs transition-all cursor-pointer"
                >
                  Cancel
                </button>
              </div>
            </div>
            {/* Progress Bar */}
            <div className="w-full h-1.5 rounded-full bg-slate-900 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${stepProgress}%` }}
                className="h-full bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full"
              />
            </div>
          </motion.div>
        )}

        {/* 3. Waiting for Permission State */}
        {currentState === 'waiting_for_permission' && (
          <motion.div
            key="permission-banner"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="mt-4 p-4 rounded-2xl bg-amber-950/40 border border-amber-500/50 space-y-3 text-xs"
          >
            <div className="flex items-start space-x-3">
              <div className="p-2 rounded-xl bg-amber-500/20 text-amber-300 border border-amber-500/30 shrink-0">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-amber-200">Execution Permission Required</h4>
                <p className="text-slate-300 leading-relaxed font-sans">
                  The mission requires execution privileges for action:
                  <strong className="text-amber-300 font-mono ml-1">
                    {permissionDetails?.action || 'Execute System Action'}
                  </strong>{' '}
                  on target:
                  <strong className="text-cyan-300 font-mono ml-1">
                    {permissionDetails?.resource || 'System Resources'}
                  </strong>
                </p>
                <div className="text-[11px] font-mono text-slate-400">
                  Risk Level: <span className="uppercase text-amber-400 font-bold">{permissionDetails?.riskLevel || 'Medium'}</span> • ToolPermissionGuard active
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 pt-1 border-t border-amber-500/20">
              <button
                onClick={onRejectPermission || handleCancelClick}
                className="px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-rose-300 border border-slate-700 text-xs font-mono transition-all cursor-pointer"
              >
                Deny & Cancel
              </button>
              <button
                onClick={onApprovePermission || (() => setInternalState('executing'))}
                className="px-4 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs font-mono transition-all cursor-pointer shadow-[0_0_12px_rgba(245,158,11,0.4)]"
              >
                Approve & Execute
              </button>
            </div>
          </motion.div>
        )}

        {/* 4. Completed State */}
        {currentState === 'completed' && (
          <motion.div
            key="completed-banner"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="mt-4 p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 space-y-2 text-xs font-mono"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-emerald-300 font-semibold">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>
                  {executionResult?.message ||
                    `Mission executed successfully: "${commandText || 'Command'}" completed.`}
                </span>
              </div>
              <button
                onClick={handleReset}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-100 cursor-pointer"
                title="Dismiss"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {executionResult?.details && (
              <p className="text-slate-300 font-sans text-xs leading-relaxed pl-6">
                {executionResult.details}
              </p>
            )}

            <div className="flex items-center justify-end pt-1">
              <button
                onClick={handleReset}
                className="px-3 py-1 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs transition-all cursor-pointer"
              >
                New Command
              </button>
            </div>
          </motion.div>
        )}

        {/* 5. Failed State */}
        {currentState === 'failed' && (
          <motion.div
            key="failed-banner"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="mt-4 p-4 rounded-2xl bg-rose-950/40 border border-rose-500/40 space-y-2 text-xs font-mono"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-rose-300 font-semibold">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>
                  Execution Failed: {externalErrorMessage || localError || 'Agent runtime encountered an error.'}
                </span>
              </div>
              <button
                onClick={handleReset}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-100 cursor-pointer"
                title="Dismiss"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-slate-400 font-sans text-xs pl-6">
              Check model connection, resource permissions, or retry with adjusted parameters.
            </p>

            <div className="flex items-center justify-end space-x-2 pt-1">
              <button
                onClick={handleReset}
                className="px-3 py-1 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 text-xs transition-all cursor-pointer"
              >
                Dismiss
              </button>
              <button
                onClick={onRetry || (() => handleCommandSubmit())}
                className="px-3 py-1 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 text-xs transition-all cursor-pointer flex items-center space-x-1"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Retry</span>
              </button>
            </div>
          </motion.div>
        )}

        {/* 6. Cancelled State */}
        {currentState === 'cancelled' && (
          <motion.div
            key="cancelled-banner"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="mt-4 p-3.5 rounded-2xl bg-slate-900/90 border border-slate-800 flex items-center justify-between text-xs font-mono text-slate-300"
          >
            <div className="flex items-center space-x-2">
              <XCircle className="w-4 h-4 text-slate-400 shrink-0" />
              <span>Command execution was cancelled by user.</span>
            </div>
            <button
              onClick={handleReset}
              className="px-3 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs transition-all cursor-pointer"
            >
              Reset
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UniversalCommandArea;
