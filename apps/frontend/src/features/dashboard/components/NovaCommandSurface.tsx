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
  Brain,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { PrimaryButton, IconButton } from '@/components/ui/Buttons';
import { CommandMode, CommandSimulationState } from '../types';

interface NovaCommandSurfaceProps {
  onExecuteCommand?: (command: string) => void;
  className?: string;
}

export const NovaCommandSurface: React.FC<NovaCommandSurfaceProps> = ({
  onExecuteCommand,
  className,
}) => {
  const [mode, setMode] = useState<CommandMode>('text');
  const [promptText, setPromptText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [simulation, setSimulation] = useState<CommandSimulationState>({ stage: 'idle', rawPrompt: '' });

  const commandSuggestions = [
    'Analyze my project',
    'Research a topic',
    'Create a presentation',
    'Summarize my files',
    'Run a mission',
    'Check my devices',
    'Start a workflow',
  ];

  const runSimulationPipeline = (rawCmd: string) => {
    if (!rawCmd.trim()) return;

    onExecuteCommand?.(rawCmd);

    // Step 1: Understanding
    setSimulation({
      stage: 'understanding',
      rawPrompt: rawCmd,
      statusMessage: 'Understanding request intent...',
    });

    // Step 2: Planning
    setTimeout(() => {
      setSimulation({
        stage: 'planning',
        rawPrompt: rawCmd,
        parsedIntent: `Goal: ${rawCmd} • Domain: Full-Stack Engineering`,
        statusMessage: 'Generating execution DAG plan...',
      });
    }, 600);

    // Step 3: Selecting Capabilities
    setTimeout(() => {
      setSimulation({
        stage: 'selecting_capabilities',
        rawPrompt: rawCmd,
        parsedIntent: `Goal: ${rawCmd}`,
        selectedAgents: ['Solution Architect', 'Backend Lead', 'QA Reviewer'],
        statusMessage: 'Assigning 3 specialized workforce agents...',
      });
    }, 1200);

    // Step 4: Mission Created & Running
    setTimeout(() => {
      const msnId = `msn_${Math.random().toString(16).substring(2, 8)}`;
      setSimulation({
        stage: 'running',
        rawPrompt: rawCmd,
        missionId: msnId,
        selectedAgents: ['Solution Architect', 'Backend Lead', 'QA Reviewer'],
        statusMessage: `Mission ${msnId} created and running autonomously.`,
      });
    }, 1800);
  };

  const handleSend = () => {
    runSimulationPipeline(promptText);
  };

  const handleSuggestion = (s: string) => {
    setPromptText(s);
    runSimulationPipeline(s);
  };

  const toggleMic = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      setPromptText('Listening... (Voice macro active)');
    } else {
      setPromptText('Hey Nova, analyze project microservices and check security');
    }
  };

  return (
    <div className={cn('p-6 rounded-3xl bg-slate-900/90 border border-cyan-500/40 shadow-[0_0_40px_rgba(0,240,255,0.12)] relative overflow-hidden', className)}>
      {/* Glow background accent */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-gradient-to-br from-cyan-500/10 via-purple-600/10 to-transparent rounded-full blur-3xl pointer-events-none" />

      {/* Main Command Surface Header */}
      <div className="flex flex-col items-center justify-center text-center space-y-2 mb-6">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-mono font-bold">
          <Sparkles className="w-3.5 h-3.5 animate-pulse" />
          <span>NOVA AI OPERATING SYSTEM</span>
        </div>
        <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight">
          What can Nova do for you?
        </h2>
        <p className="text-xs text-slate-400 font-mono">
          Enter a prompt or select a capability to orchestrate conversation, code, research & device tasks
        </p>
      </div>

      {/* Mode Selectors */}
      <div className="flex items-center justify-center space-x-1.5 mb-4">
        {[
          { id: 'text', label: 'Text', icon: MessageSquare },
          { id: 'voice', label: 'Voice', icon: Mic },
          { id: 'vision', label: 'Vision', icon: Camera },
          { id: 'file', label: 'File', icon: Paperclip },
          { id: 'command', label: 'Command', icon: Terminal },
        ].map((m) => {
          const ModeIcon = m.icon;
          const isSelected = mode === m.id;
          return (
            <button
              key={m.id}
              onClick={() => setMode(m.id as CommandMode)}
              className={cn(
                'px-3.5 py-1.5 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer border',
                isSelected
                  ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-[0_0_12px_rgba(0,240,255,0.2)]'
                  : 'bg-slate-950/60 text-slate-400 border-slate-800 hover:text-slate-200 hover:border-slate-700'
              )}
            >
              <ModeIcon className="w-3.5 h-3.5" />
              <span>{m.label}</span>
            </button>
          );
        })}
      </div>

      {/* Command Input Area */}
      <div className="relative group max-w-4xl mx-auto">
        <div className="relative flex items-center bg-slate-950 rounded-2xl border border-slate-800 group-hover:border-cyan-500/50 transition-all p-2 shadow-inner">
          <Terminal className="w-5 h-5 text-cyan-400 ml-3 mr-2 shrink-0" />

          <input
            type="text"
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={
              mode === 'voice'
                ? 'Speak voice command or enter prompt...'
                : mode === 'vision'
                ? 'Point vision feed or enter visual task...'
                : mode === 'file'
                ? 'Attach code/pdf file or prompt...'
                : mode === 'command'
                ? 'Enter OS macro or system command...'
                : 'Ask Nova anything...'
            }
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none py-2 px-1 font-sans"
            aria-label="Universal Command Input"
          />

          <div className="flex items-center space-x-2 mr-1">
            <IconButton
              icon={Paperclip}
              size="sm"
              className={cn('text-slate-400 hover:text-cyan-300', mode === 'file' && 'text-cyan-300 bg-cyan-500/20')}
              title="Attachment"
              onClick={() => setMode('file')}
            />
            <IconButton
              icon={Camera}
              size="sm"
              className={cn('text-slate-400 hover:text-cyan-300', mode === 'vision' && 'text-cyan-300 bg-cyan-500/20')}
              title="Camera / Vision"
              onClick={() => setMode('vision')}
            />
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={toggleMic}
              className={cn(
                'p-2 rounded-xl transition-all cursor-pointer border flex items-center justify-center',
                isRecording
                  ? 'bg-rose-500 text-white border-rose-400 animate-pulse'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-purple-300'
              )}
              title="Microphone"
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </motion.button>
            <PrimaryButton
              size="md"
              disabled={!promptText.trim() || simulation.stage === 'understanding' || simulation.stage === 'planning'}
              onClick={handleSend}
              icon={Send}
            >
              Send
            </PrimaryButton>
          </div>
        </div>
      </div>

      {/* Suggested Commands Chips */}
      <div className="mt-4 flex items-center justify-center flex-wrap gap-2 max-w-4xl mx-auto">
        <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider">Suggested:</span>
        {commandSuggestions.map((s, idx) => (
          <button
            key={idx}
            onClick={() => handleSuggestion(s)}
            className="px-3 py-1 rounded-xl bg-slate-950/80 text-slate-300 hover:text-cyan-300 hover:bg-cyan-500/10 border border-slate-800 hover:border-cyan-500/30 text-xs transition-all cursor-pointer font-sans"
          >
            + {s}
          </button>
        ))}
      </div>

      {/* Simulated Pipeline Execution UI */}
      <AnimatePresence>
        {simulation.stage !== 'idle' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-6 p-4 rounded-2xl bg-slate-950/90 border border-cyan-500/40 text-xs font-mono max-w-4xl mx-auto space-y-3"
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <div className="flex items-center space-x-2 text-cyan-300 font-bold">
                <Brain className="w-4 h-4 text-cyan-400 animate-pulse" />
                <span>Nova Interaction Pipeline</span>
              </div>
              <button
                onClick={() => setSimulation({ stage: 'idle', rawPrompt: '' })}
                className="text-slate-500 hover:text-slate-200"
              >
                <XCircle className="w-4 h-4" />
              </button>
            </div>

            {/* Pipeline Stage Indicators */}
            <div className="grid grid-cols-4 gap-2 text-center text-[11px]">
              <div className={cn('p-2 rounded-xl border', simulation.stage === 'understanding' ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300' : 'bg-slate-900 border-slate-800 text-slate-400')}>
                1. Understand
              </div>
              <div className={cn('p-2 rounded-xl border', simulation.stage === 'planning' ? 'bg-purple-500/20 border-purple-500/50 text-purple-300' : 'bg-slate-900 border-slate-800 text-slate-400')}>
                2. Plan
              </div>
              <div className={cn('p-2 rounded-xl border', simulation.stage === 'selecting_capabilities' ? 'bg-blue-500/20 border-blue-500/50 text-blue-300' : 'bg-slate-900 border-slate-800 text-slate-400')}>
                3. Capabilities
              </div>
              <div className={cn('p-2 rounded-xl border', simulation.stage === 'running' ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300' : 'bg-slate-900 border-slate-800 text-slate-400')}>
                4. Execute
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800/80 flex items-center justify-between text-slate-300">
              <div className="flex items-center space-x-2">
                {simulation.stage === 'running' ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : (
                  <Loader2 className="w-4 h-4 animate-spin text-cyan-400 shrink-0" />
                )}
                <span>{simulation.statusMessage}</span>
              </div>
              {simulation.missionId && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  {simulation.missionId} (QUEUED & RUNNING)
                </span>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default NovaCommandSurface;
