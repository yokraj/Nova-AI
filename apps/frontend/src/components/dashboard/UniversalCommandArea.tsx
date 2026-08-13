import React, { useState } from 'react';
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
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { PrimaryButton, SecondaryButton, IconButton } from '@/components/ui/Buttons';

interface UniversalCommandAreaProps {
  onExecuteCommand?: (command: string) => void;
  className?: string;
}

export const UniversalCommandArea: React.FC<UniversalCommandAreaProps> = ({
  onExecuteCommand,
  className,
}) => {
  const [inputMode, setInputMode] = useState<'text' | 'voice' | 'attachment' | 'vision'>('text');
  const [commandText, setCommandText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [simulationResponse, setSimulationResponse] = useState<string | null>(null);

  const commandSuggestions = [
    'Analyze my project',
    'Research this topic',
    'Open my workspace',
    'Create a presentation',
    'Summarize my documents',
    'Run my morning routine',
  ];

  const handleCommandSubmit = (cmd?: string) => {
    const textToRun = cmd || commandText;
    if (!textToRun.trim()) return;

    setIsProcessing(true);
    setSimulationResponse(null);

    if (onExecuteCommand) {
      onExecuteCommand(textToRun);
    }

    setTimeout(() => {
      setIsProcessing(false);
      setSimulationResponse(`Nova received command: "${textToRun}". Execution mission created.`);
    }, 1000);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setCommandText(suggestion);
    handleCommandSubmit(suggestion);
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      setCommandText('Listening... (Voice input simulation active)');
    } else {
      setCommandText('Hey Nova, analyze project dependencies and prepare report');
    }
  };

  return (
    <div className={cn('glass-panel p-6 rounded-3xl border border-cyan-500/30 relative overflow-hidden shadow-[0_0_30px_rgba(0,240,255,0.1)]', className)}>
      {/* Subtle glowing ambient background gradient */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-cyan-500/10 via-purple-600/10 to-transparent rounded-full blur-3xl pointer-events-none" />

      {/* Greeting & Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-gradient-to-tr from-cyan-500/20 to-purple-500/20 rounded-2xl text-cyan-300 border border-cyan-500/40 shadow-[0_0_15px_rgba(0,240,255,0.2)]">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h2 className="text-xl font-extrabold text-slate-100 tracking-tight flex items-center gap-2">
              <span>How can Nova assist your system today?</span>
            </h2>
            <p className="text-xs text-slate-400 font-mono">
              UNIVERSAL AI OPERATING SYSTEM COMMAND CENTER • ALL SUBSYSTEMS NOMINAL
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center space-x-1.5 text-[11px] font-mono font-bold px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>CORE: ONLINE (12ms)</span>
          </span>
        </div>
      </div>

      {/* Input Mode Selector Bar */}
      <div className="flex items-center space-x-1 mb-3 bg-slate-900/80 p-1 rounded-xl border border-slate-800/80 w-fit">
        <button
          onClick={() => setInputMode('text')}
          className={cn(
            'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer',
            inputMode === 'text' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'
          )}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Text Input</span>
        </button>
        <button
          onClick={() => setInputMode('voice')}
          className={cn(
            'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer',
            inputMode === 'voice' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' : 'text-slate-400 hover:text-slate-200'
          )}
        >
          <Mic className="w-3.5 h-3.5" />
          <span>Voice Mode</span>
        </button>
        <button
          onClick={() => setInputMode('attachment')}
          className={cn(
            'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer',
            inputMode === 'attachment' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' : 'text-slate-400 hover:text-slate-200'
          )}
        >
          <Paperclip className="w-3.5 h-3.5" />
          <span>Attachments</span>
        </button>
        <button
          onClick={() => setInputMode('vision')}
          className={cn(
            'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer',
            inputMode === 'vision' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200'
          )}
        >
          <Camera className="w-3.5 h-3.5" />
          <span>Vision Camera</span>
        </button>
      </div>

      {/* Main Command Input Box */}
      <div className="relative group">
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cyan-500/20 to-purple-600/20 blur-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
        <div className="relative flex items-center bg-slate-950/90 rounded-2xl border border-slate-800 group-hover:border-cyan-500/50 transition-all p-2 shadow-inner">
          <Terminal className="w-5 h-5 text-cyan-400 ml-3 mr-2 shrink-0" />

          <input
            type="text"
            value={commandText}
            onChange={(e) => setCommandText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCommandSubmit()}
            placeholder={
              inputMode === 'voice'
                ? 'Speak into microphone or type voice macro...'
                : inputMode === 'attachment'
                ? 'Attach document/code file or enter prompt...'
                : inputMode === 'vision'
                ? 'Point camera at screen/document or enter visual request...'
                : 'Ask Nova anything or enter a voice / system command...'
            }
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none py-2 px-1 font-sans"
          />

          <div className="flex items-center space-x-2 mr-1">
            {/* Attachment Button */}
            <IconButton
              icon={Paperclip}
              size="sm"
              className={cn('text-slate-400 hover:text-cyan-300', inputMode === 'attachment' && 'text-cyan-300 bg-cyan-500/20')}
              title="Attach File"
              onClick={() => setInputMode('attachment')}
            />

            {/* Vision Camera Button */}
            <IconButton
              icon={Camera}
              size="sm"
              className={cn('text-slate-400 hover:text-cyan-300', inputMode === 'vision' && 'text-cyan-300 bg-cyan-500/20')}
              title="Camera / Vision Feed"
              onClick={() => setInputMode('vision')}
            />

            {/* Voice Mic Button */}
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={toggleRecording}
              className={cn(
                'p-2 rounded-xl transition-all cursor-pointer border flex items-center justify-center',
                isRecording
                  ? 'bg-rose-500 text-white border-rose-400 animate-pulse shadow-[0_0_15px_rgba(244,63,94,0.6)]'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-purple-300 hover:border-purple-500/40'
              )}
              title={isRecording ? 'Stop Recording' : 'Voice Command Mic'}
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </motion.button>

            {/* Send Button */}
            <PrimaryButton
              size="md"
              disabled={isProcessing || !commandText.trim()}
              onClick={() => handleCommandSubmit()}
              icon={isProcessing ? Loader2 : Send}
              className={isProcessing ? 'animate-spin' : ''}
            >
              {isProcessing ? '' : 'Execute'}
            </PrimaryButton>
          </div>
        </div>
      </div>

      {/* Command Suggestions Chips */}
      <div className="mt-4 flex items-center space-x-2 overflow-x-auto pb-1 scrollbar-none">
        <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider shrink-0 mr-1">Suggestions:</span>
        {commandSuggestions.map((suggestion, idx) => (
          <button
            key={idx}
            onClick={() => handleSuggestionClick(suggestion)}
            className="px-3 py-1 rounded-xl bg-slate-900/90 text-slate-300 hover:text-cyan-300 hover:bg-cyan-500/10 border border-slate-800 hover:border-cyan-500/30 text-xs transition-all whitespace-nowrap cursor-pointer shrink-0"
          >
            + {suggestion}
          </button>
        ))}
      </div>

      {/* Interactive Simulation Response Feedback */}
      <AnimatePresence>
        {(isProcessing || simulationResponse) && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-4 p-3.5 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-200 flex items-center justify-between text-xs font-mono"
          >
            <div className="flex items-center space-x-3">
              {isProcessing ? (
                <Loader2 className="w-4 h-4 animate-spin text-cyan-400 shrink-0" />
              ) : (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              )}
              <span>{isProcessing ? 'Nova Intelligence Core orchestrating request...' : simulationResponse}</span>
            </div>
            {simulationResponse && (
              <button
                onClick={() => setSimulationResponse(null)}
                className="text-slate-400 hover:text-slate-200 ml-3"
              >
                <XCircle className="w-4 h-4" />
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UniversalCommandArea;
