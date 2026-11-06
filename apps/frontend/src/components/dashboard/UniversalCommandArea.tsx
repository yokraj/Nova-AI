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
  Volume2,
  VolumeX,
  UploadCloud,
  Eye,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { CommandVisualState, AttachedFile, AttachedVision } from '@/types/dashboard';
import { useUniversalCommand } from '@/features/universal-command/hooks/useUniversalCommand';

export interface UniversalCommandAreaProps {
  onExecuteCommand?: (
    command: string,
    mode: 'text' | 'voice' | 'attachment' | 'vision',
    attachments?: { files: AttachedFile[]; vision?: AttachedVision }
  ) => void | Promise<any>;
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
  // Unified voice props from useNovaVoiceAssistant
  isListeningProp?: boolean;
  isSpeakingProp?: boolean;
  onToggleVoice?: () => void;
  onStopSpeaking?: () => void;
  externalTranscript?: string;
  voiceLevel?: number;
  voiceError?: string | null;
  onClearVoiceError?: () => void;
  // Runtime metadata
  isLiveExecution?: boolean;
  activeModelName?: string;
}

const MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024; // 20 MB

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
  isSpeakingProp = false,
  onToggleVoice,
  onStopSpeaking,
  externalTranscript,
  voiceLevel = 0,
  voiceError,
  onClearVoiceError,
  isLiveExecution = false,
  activeModelName = 'qwen3:8b',
}) => {
  // Built-in universal command engine for standalone operation
  const internalCommandEngine = useUniversalCommand();

  // Internal state when not externally managed
  const [internalState, setInternalState] = useState<CommandVisualState>('idle');
  const currentState = externalState || internalState;

  const [inputMode, setInputMode] = useState<'text' | 'voice' | 'attachment' | 'vision'>('text');
  const [commandText, setCommandText] = useState('');
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([]);
  const [attachedVision, setAttachedVision] = useState<AttachedVision | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const [previewModalUrl, setPreviewModalUrl] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const commandSuggestions = [
    'Analyze Nova monorepo architecture',
    'Explain Python decorators with an example',
    'Write a Python program to check whether a number is prime',
    'Audit Docker container topology',
    'Inspect vector memory embeddings growth',
    'Check Ollama local inference health',
  ];

  // Voice state
  const isListening = isListeningProp !== undefined ? isListeningProp : currentState === 'listening';

  // Synchronize external voice transcript
  useEffect(() => {
    if (externalTranscript && isListening) {
      setCommandText(externalTranscript);
    }
  }, [externalTranscript, isListening]);

  // Voice Toggle Handler
  const handleToggleVoice = () => {
    setLocalError(null);
    if (onToggleVoice) {
      onToggleVoice();
      return;
    }
    // If no parent voice assistant is hooked, report clear state
    if (isListening) {
      if (onCancel) onCancel();
      setInternalState('idle');
    } else {
      setInputMode('voice');
      setInternalState('listening');
    }
  };

  // Process File List (used by file picker and drag-and-drop)
  const processFiles = useCallback((fileList: FileList | File[]) => {
    setLocalError(null);
    const validFiles: File[] = [];

    Array.from(fileList).forEach((file) => {
      if (file.size > MAX_FILE_SIZE_BYTES) {
        setLocalError(`File "${file.name}" exceeds the 20 MB size limit.`);
        return;
      }
      validFiles.push(file);
    });

    if (validFiles.length === 0) return;

    validFiles.forEach((file) => {
      const isImage = file.type.startsWith('image/');
      const fileId = `file-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;

      if (isImage) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const dataUrl = event.target?.result as string;
          const newFile: AttachedFile = {
            id: fileId,
            name: file.name,
            size: file.size,
            type: file.type || 'image/png',
            dataUrl,
          };
          setAttachedFiles((prev) => [...prev, newFile]);

          // Also set as attached vision context if none exists yet
          if (!attachedVision) {
            setAttachedVision({
              id: `vision-${Date.now()}`,
              title: file.name,
              previewUrl: dataUrl,
              timestamp: new Date().toLocaleTimeString(),
            });
          }
        };
        reader.readAsDataURL(file);
      } else {
        const newFile: AttachedFile = {
          id: fileId,
          name: file.name,
          size: file.size,
          type: file.type || 'application/octet-stream',
        };
        setAttachedFiles((prev) => [...prev, newFile]);
      }
    });

    setInputMode('attachment');
  }, [attachedVision]);

  // File Input Change
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(e.target.files);
      e.target.value = '';
    }
  };

  // Image / Vision Input Change
  const handleImageFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > MAX_FILE_SIZE_BYTES) {
        setLocalError(`Image "${file.name}" exceeds the 20 MB limit.`);
        return;
      }
      const reader = new FileReader();
      reader.onload = (event) => {
        const dataUrl = event.target?.result as string;
        setAttachedVision({
          id: `vision-${Date.now()}`,
          title: file.name,
          previewUrl: dataUrl,
          timestamp: new Date().toLocaleTimeString(),
        });
        setInputMode('vision');
        if (!commandText) {
          setCommandText(`Analyze attached image: ${file.name}`);
        }
      };
      reader.readAsDataURL(file);
      e.target.value = '';
    }
  };

  // Clipboard Paste Support (Supports Win+Shift+S pasted screenshots)
  const handlePaste = useCallback((e: React.ClipboardEvent<HTMLInputElement>) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      if (items[i].type.startsWith('image/')) {
        const file = items[i].getAsFile();
        if (file) {
          e.preventDefault();
          const reader = new FileReader();
          reader.onload = (event) => {
            const dataUrl = event.target?.result as string;
            setAttachedVision({
              id: `clipboard-vision-${Date.now()}`,
              title: `Pasted Screenshot (${new Date().toLocaleTimeString()})`,
              previewUrl: dataUrl,
              timestamp: new Date().toLocaleTimeString(),
            });
            setInputMode('vision');
            if (!commandText) {
              setCommandText('Inspect UI elements in active screenshot and summarize key observations');
            }
          };
          reader.readAsDataURL(file);
          return;
        }
      }
    }
  }, [commandText]);

  // Drag & Drop Handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files);
    }
  };

  // Removal Handlers
  const removeFile = (id: string) => {
    setAttachedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const removeVision = () => {
    setAttachedVision(null);
  };

  // Genuine Command Execution Submission (NO setTimeout mocks)
  const handleCommandSubmit = useCallback(
    async (overrideText?: string) => {
      const textToRun = (overrideText || commandText).trim();
      if (!textToRun && attachedFiles.length === 0 && !attachedVision) return;

      setLocalError(null);

      // Stop listening if voice was active
      if (isListening && onToggleVoice) {
        onToggleVoice();
      }

      // Determine accurate execution source mode
      const sourceMode = isListening
        ? 'voice'
        : attachedVision
        ? 'vision'
        : attachedFiles.length > 0
        ? 'attachment'
        : 'text';

      // 1. If parent provided an execution handler, delegate directly to parent
      if (onExecuteCommand) {
        try {
          await onExecuteCommand(textToRun, sourceMode, {
            files: attachedFiles,
            vision: attachedVision || undefined,
          });
        } catch (err: any) {
          setLocalError(err?.message || 'Command dispatch failed.');
        }
        return;
      }

      // 2. Standalone operation: Dispatch through real universal command hook
      setInternalState('processing');
      try {
        const cmdResult = await internalCommandEngine.processCommand(
          textToRun,
          sourceMode.toUpperCase() as any,
          {
            files: attachedFiles,
            vision: attachedVision || undefined,
          }
        );

        if (cmdResult) {
          if (cmdResult.executionState === 'AWAITING_APPROVAL') {
            setInternalState('waiting_for_permission');
          } else if (cmdResult.executionState === 'COMPLETED') {
            setInternalState('completed');
          } else if (cmdResult.executionState === 'FAILED') {
            setInternalState('failed');
            setLocalError(cmdResult.result?.message || 'Execution failed.');
          } else {
            setInternalState('idle');
          }
        } else {
          setInternalState('idle');
        }
      } catch (err: any) {
        setInternalState('failed');
        setLocalError(err?.message || 'Local command engine error.');
      }
    },
    [
      commandText,
      attachedFiles,
      attachedVision,
      isListening,
      onToggleVoice,
      onExecuteCommand,
      internalCommandEngine,
    ]
  );

  // Cancellation
  const handleCancelClick = () => {
    if (onCancel) {
      onCancel();
    } else {
      internalCommandEngine.cancelExecution();
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
    if (onClearVoiceError) onClearVoiceError();
    if (onRetry) onRetry();
  };

  // Helper formatting
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileIcon = (type: string) => {
    if (type.includes('image')) return ImageIcon;
    if (
      type.includes('code') ||
      type.includes('typescript') ||
      type.includes('javascript') ||
      type.includes('python') ||
      type.includes('json')
    )
      return FileCode;
    return FileText;
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={cn(
        'glass-panel p-4 sm:p-6 rounded-2xl sm:rounded-3xl border transition-all duration-300 relative overflow-hidden select-none',
        isDraggingOver
          ? 'border-cyan-400 bg-cyan-950/40 shadow-[0_0_40px_rgba(0,240,255,0.3)] ring-2 ring-cyan-400/50'
          : currentState === 'listening'
          ? 'border-purple-500/60 bg-slate-950/90 shadow-[0_0_35px_rgba(168,85,247,0.25)]'
          : currentState === 'waiting_for_permission'
          ? 'border-amber-500/60 bg-slate-950/90 shadow-[0_0_35px_rgba(245,158,11,0.2)]'
          : currentState === 'failed'
          ? 'border-rose-500/60 bg-slate-950/90 shadow-[0_0_35px_rgba(244,63,94,0.2)]'
          : currentState === 'completed'
          ? 'border-emerald-500/50 bg-slate-950/90 shadow-[0_0_35px_rgba(16,185,129,0.2)]'
          : 'border-cyan-500/20 hover:border-cyan-400/40 bg-slate-950/80 shadow-[0_4px_30px_rgba(0,0,0,0.8)]',
        className
      )}
    >
      {/* Hidden file and image inputs */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        multiple
        className="hidden"
        aria-label="Upload file attachment"
      />
      <input
        type="file"
        ref={imageInputRef}
        onChange={handleImageFileSelect}
        accept="image/*"
        className="hidden"
        aria-label="Upload screenshot or vision image"
      />

      {/* Subtle ambient cyan/purple glow */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-bl from-cyan-500/10 via-purple-600/5 to-transparent rounded-full blur-3xl pointer-events-none" />

      {/* Header bar with title, model status pill, and live vs demo indicator */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 sm:mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2 sm:p-2.5 bg-gradient-to-tr from-cyan-500/20 via-sky-500/20 to-purple-500/20 rounded-2xl text-cyan-300 border border-cyan-400/30 shadow-[0_0_15px_rgba(0,240,255,0.2)] shrink-0">
            <Sparkles className="w-5 h-5 text-cyan-400 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base sm:text-lg font-black text-slate-100 tracking-tight">
                Universal Command Area
              </h2>
              {/* Truthful Runtime Status Badge */}
              {isLiveExecution ? (
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                  <span>LIVE ({activeModelName})</span>
                </span>
              ) : (
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                  <span>STANDALONE READY</span>
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 font-mono">
              TEXT • VOICE ASSISTANT 2.0 • IMAGE VISION • MULTIMODAL EXECUTION
            </p>
          </div>
        </div>

        {/* State Badge Indicator */}
        <div className="flex items-center space-x-2 shrink-0">
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
              <span>PROCESSING INTENT</span>
            </span>
          )}

          {currentState === 'executing' && (
            <span className="inline-flex items-center space-x-1.5 text-[11px] font-mono font-bold px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/50">
              <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
              <span>EXECUTING ACTION</span>
            </span>
          )}

          {currentState === 'waiting_for_permission' && (
            <span className="inline-flex items-center space-x-1.5 text-[11px] font-mono font-bold px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/50">
              <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
              <span>APPROVAL REQUIRED</span>
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
            inputMode === 'voice' || isListening
              ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          )}
        >
          {isListening ? <MicOff className="w-3.5 h-3.5 text-purple-300" /> : <Mic className="w-3.5 h-3.5" />}
          <span>Voice Assistant</span>
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
            imageInputRef.current?.click();
          }}
          className={cn(
            'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer whitespace-nowrap focus:outline-none focus:ring-1 focus:ring-emerald-400',
            inputMode === 'vision' || attachedVision
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          )}
        >
          <Camera className="w-3.5 h-3.5" />
          <span>Vision Context</span>
        </button>
      </div>

      {/* Voice Error Banner */}
      <AnimatePresence>
        {voiceError && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-3 p-3 rounded-xl bg-rose-950/60 border border-rose-500/40 flex items-center justify-between text-xs font-mono text-rose-300"
          >
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>Voice Error: {voiceError}</span>
            </div>
            <button
              onClick={() => onClearVoiceError?.()}
              className="p-1 rounded-lg hover:bg-rose-900/50 text-rose-400 hover:text-rose-200 cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Local Attachment / Validation Error Banner */}
      <AnimatePresence>
        {localError && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-3 p-3 rounded-xl bg-amber-950/60 border border-amber-500/40 flex items-center justify-between text-xs font-mono text-amber-300"
          >
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
              <span>{localError}</span>
            </div>
            <button
              onClick={() => setLocalError(null)}
              className="p-1 rounded-lg hover:bg-amber-900/50 text-amber-400 hover:text-amber-200 cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Genuine Attachment Previews (With Real Image Thumbnails) */}
      {(attachedFiles.length > 0 || attachedVision) && (
        <div className="mb-3 flex items-center flex-wrap gap-2 pt-1 pb-1">
          {/* Vision Thumbnail Card */}
          {attachedVision && (
            <div className="flex items-center space-x-2.5 p-1.5 pr-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-mono group">
              {attachedVision.previewUrl ? (
                <div
                  onClick={() => setPreviewModalUrl(attachedVision.previewUrl)}
                  className="relative cursor-pointer group-hover:opacity-90"
                  title="Click to view full image"
                >
                  <img
                    src={attachedVision.previewUrl}
                    alt={attachedVision.title}
                    className="w-8 h-8 rounded-lg object-cover border border-emerald-500/40 shrink-0"
                  />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 rounded-lg flex items-center justify-center transition-opacity">
                    <Eye className="w-3.5 h-3.5 text-white" />
                  </div>
                </div>
              ) : (
                <Camera className="w-4 h-4 text-emerald-400 ml-1.5 shrink-0" />
              )}
              <div className="flex flex-col">
                <span className="font-bold truncate max-w-[160px]">{attachedVision.title}</span>
                <span className="text-[10px] text-emerald-400/80">Active Vision Context</span>
              </div>
              <button
                onClick={removeVision}
                className="hover:text-emerald-100 p-1 rounded-lg hover:bg-emerald-950/60 cursor-pointer transition-colors"
                title="Remove vision context"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Attached Files Badges (With Image Previews when applicable) */}
          {attachedFiles.map((file) => {
            const FileIcon = getFileIcon(file.type);
            const isImage = file.dataUrl || file.type.startsWith('image/');
            return (
              <div
                key={file.id}
                className="flex items-center space-x-2 p-1.5 pr-2.5 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs font-mono group"
              >
                {isImage && file.dataUrl ? (
                  <div
                    onClick={() => setPreviewModalUrl(file.dataUrl!)}
                    className="relative cursor-pointer group-hover:opacity-90"
                    title="Click to view full image"
                  >
                    <img
                      src={file.dataUrl}
                      alt={file.name}
                      className="w-8 h-8 rounded-lg object-cover border border-blue-500/40 shrink-0"
                    />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 rounded-lg flex items-center justify-center transition-opacity">
                      <Eye className="w-3 h-3 text-white" />
                    </div>
                  </div>
                ) : (
                  <FileIcon className="w-4 h-4 text-blue-400 ml-1.5 shrink-0" />
                )}
                <div className="flex flex-col">
                  <span className="truncate max-w-[150px] font-bold">{file.name}</span>
                  <span className="text-slate-500 text-[10px]">({formatFileSize(file.size)})</span>
                </div>
                <button
                  onClick={() => removeFile(file.id)}
                  className="hover:text-blue-100 p-1 rounded-lg hover:bg-blue-950/60 cursor-pointer transition-colors"
                  title="Remove attachment"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Voice Wave Visualizer when Listening (Reactive to real voice level) */}
      <AnimatePresence>
        {isListening && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-3 p-3.5 rounded-2xl bg-purple-950/40 border border-purple-500/40 flex items-center justify-between"
          >
            <div className="flex items-center space-x-3">
              <div className="w-2.5 h-2.5 rounded-full bg-purple-400 animate-ping shrink-0" />
              <span className="text-xs font-mono text-purple-200 font-semibold">
                Listening for speech... (Acoustic VAD Active)
              </span>
            </div>

            {/* Voice Waveform Bars Reactive to Volume Level */}
            <div className="flex items-center space-x-1 h-5 px-3">
              {[0.4, 0.8, 1.2, 0.9, 1.5, 1.8, 1.1, 0.6, 1.3, 0.7].map((scale, i) => {
                const dynamicHeight = Math.max(4, Math.min(22, (voiceLevel || 10) * scale * 0.4));
                return (
                  <motion.div
                    key={i}
                    animate={{ height: isListening ? [4, dynamicHeight, 4] : 4 }}
                    transition={{
                      duration: 0.35 + (i % 3) * 0.1,
                      repeat: Infinity,
                      repeatType: 'reverse',
                    }}
                    className="w-1 bg-purple-400 rounded-full"
                  />
                );
              })}
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

      {/* Main Command Input Box */}
      <div className="relative group">
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cyan-500/20 via-sky-500/20 to-purple-600/20 blur-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
        <div className="relative flex items-center bg-slate-950/95 rounded-2xl border border-slate-800 group-hover:border-cyan-500/50 transition-all p-2 shadow-inner focus-within:border-cyan-400 focus-within:ring-1 focus-within:ring-cyan-400/40">
          <Terminal className="w-5 h-5 text-cyan-400 ml-3 mr-2 shrink-0" />

          <input
            ref={inputRef}
            type="text"
            value={commandText}
            onChange={(e) => setCommandText(e.target.value)}
            onPaste={handlePaste}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleCommandSubmit();
              }
            }}
            disabled={currentState === 'processing' || currentState === 'executing'}
            placeholder={
              isListening
                ? 'Listening... speak now or type to override...'
                : inputMode === 'voice'
                ? 'Speak into microphone or enter voice command...'
                : inputMode === 'attachment'
                ? 'Enter instructions for attached documents...'
                : inputMode === 'vision'
                ? 'Enter vision analysis query for attached screenshot...'
                : 'Ask Nova anything or enter system command (paste screenshots with Ctrl+V)...'
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
              onClick={() => imageInputRef.current?.click()}
              className={cn(
                'p-2 rounded-xl border transition-all cursor-pointer',
                attachedVision
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-emerald-300 hover:border-slate-700'
              )}
              title="Attach Image or Screenshot Context"
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
                isListening
                  ? 'bg-rose-500 text-white border-rose-400 animate-pulse shadow-[0_0_15px_rgba(244,63,94,0.6)]'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-purple-300 hover:border-purple-500/40'
              )}
              title={isListening ? 'Stop Listening' : 'Activate Voice Command'}
              aria-label="Toggle Voice"
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </motion.button>

            {/* Speech Stop Button (When Nova is speaking) */}
            {isSpeakingProp && onStopSpeaking && (
              <button
                type="button"
                onClick={onStopSpeaking}
                className="p-2 rounded-xl bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 transition-all cursor-pointer"
                title="Stop Nova Speech Playback"
                aria-label="Stop Speaking"
              >
                <VolumeX className="w-4 h-4" />
              </button>
            )}

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
        {/* 1. Processing State Banner */}
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
              <span>
                Nova Intelligence Core is decomposing intent and routing capabilities...
              </span>
            </div>
            <button
              onClick={handleCancelClick}
              className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs hover:text-rose-300 transition-all cursor-pointer"
            >
              Cancel
            </button>
          </motion.div>
        )}

        {/* 2. Executing State Banner */}
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
                <span>Executing action pipeline: dispatching to model & runtime engines...</span>
              </div>
              <button
                onClick={handleCancelClick}
                className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-rose-300 text-xs transition-all cursor-pointer"
              >
                Cancel
              </button>
            </div>
          </motion.div>
        )}

        {/* 3. Waiting for Permission State Banner */}
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
                  The operation requires authorization to execute action:
                  <strong className="text-amber-300 font-mono ml-1">
                    {permissionDetails?.action || 'System Action'}
                  </strong>{' '}
                  on target:
                  <strong className="text-cyan-300 font-mono ml-1">
                    {permissionDetails?.resource || 'System Resources'}
                  </strong>
                </p>
                <div className="text-[11px] font-mono text-slate-400">
                  Risk Level:{' '}
                  <span className="uppercase text-amber-400 font-bold">
                    {permissionDetails?.riskLevel || 'Medium'}
                  </span>{' '}
                  • Security sandbox verification active
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

        {/* 4. Completed State Banner */}
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
                    `Execution completed: "${commandText || 'Command'}" processed.`}
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

        {/* 5. Failed State Banner */}
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
                  Execution Failed:{' '}
                  {externalErrorMessage || localError || 'Runtime operation returned an error.'}
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
              Check model connection, ensure Ollama/backend is reachable on localhost, or retry.
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

        {/* 6. Cancelled State Banner */}
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
              <span>Command execution was cancelled by operator.</span>
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

      {/* Full Image Preview Modal */}
      <AnimatePresence>
        {previewModalUrl && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setPreviewModalUrl(null)}
            className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.95 }}
              onClick={(e) => e.stopPropagation()}
              className="relative max-w-4xl max-h-[85vh] bg-slate-950 p-2 rounded-2xl border border-cyan-500/30 overflow-hidden shadow-2xl"
            >
              <button
                onClick={() => setPreviewModalUrl(null)}
                className="absolute top-4 right-4 p-2 rounded-xl bg-black/70 hover:bg-black text-white cursor-pointer z-10"
              >
                <X className="w-5 h-5" />
              </button>
              <img
                src={previewModalUrl}
                alt="Full Attachment Preview"
                className="max-h-[80vh] w-auto object-contain rounded-xl"
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UniversalCommandArea;
