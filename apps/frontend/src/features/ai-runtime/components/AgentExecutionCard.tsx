import React from 'react';
import { Bot, CheckCircle2, AlertCircle, Loader2, StopCircle } from 'lucide-react';
import { ExecutionPlan } from '../types/executionPlan';
import { AgentState } from '../types/agentState';
import { cn } from '@/utils/cn';

interface AgentExecutionCardProps {
  goal: string;
  state: AgentState;
  plan?: ExecutionPlan | null;
  isLocalModelUsed?: boolean;
  onCancel?: () => void;
  className?: string;
}

export const AgentExecutionCard: React.FC<AgentExecutionCardProps> = ({
  goal,
  state,
  plan,
  isLocalModelUsed,
  onCancel,
  className,
}) => {
  const isRunning = state === 'EXECUTING' || state === 'PLANNING' || state === 'OBSERVING' || state === 'VERIFYING';
  const isSuccess = state === 'COMPLETED';
  const isFailed = state === 'FAILED' || state === 'TIMED_OUT' || state === 'CANCELLED';

  const completedSteps = plan?.steps.filter((s) => s.status === 'COMPLETED').length || 0;
  const totalSteps = plan?.steps.length || 1;
  const progressPercent = Math.round((completedSteps / totalSteps) * 100);

  return (
    <div className={cn('p-4 rounded-3xl border border-cyan-500/30 bg-slate-950/90 backdrop-blur-xl shadow-2xl space-y-3 font-mono text-xs text-slate-100', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-cyan-300 font-bold uppercase tracking-wider">
          <Bot className="w-4 h-4 text-cyan-400" />
          <span>AUTONOMOUS EXECUTION ENGINE</span>
        </div>
        <div className="flex items-center space-x-2">
          <span
            className={cn(
              'px-2 py-0.5 rounded-full text-[9px] font-bold uppercase border',
              isLocalModelUsed
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                : 'bg-purple-500/20 text-purple-300 border-purple-500/30'
            )}
          >
            {isLocalModelUsed ? 'REAL LOCAL LLM' : 'MOCK FALLBACK'}
          </span>
          <span
            className={cn(
              'px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border',
              isRunning && 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 animate-pulse',
              isSuccess && 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
              isFailed && 'bg-rose-500/20 text-rose-300 border-rose-500/40'
            )}
          >
            {state}
          </span>
        </div>
      </div>

      <div className="text-slate-200 text-xs font-sans font-medium">
        Goal: <strong className="text-cyan-200 font-mono">"{goal}"</strong>
      </div>

      {plan && (
        <div className="space-y-2 pt-1">
          <div className="flex justify-between text-[11px] text-slate-400">
            <span>Execution Progress</span>
            <span>{progressPercent}% ({completedSteps}/{totalSteps} steps)</span>
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-cyan-400 transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          <div className="space-y-1.5 pt-2">
            {plan.steps.map((step) => (
              <div key={step.id} className="flex items-center justify-between text-[11px] p-2 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center space-x-2">
                  {step.status === 'COMPLETED' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                  {step.status === 'EXECUTING' && <Loader2 className="w-3.5 h-3.5 text-cyan-400 animate-spin" />}
                  {step.status === 'FAILED' && <AlertCircle className="w-3.5 h-3.5 text-rose-400" />}
                  {step.status === 'PENDING' && <div className="w-3.5 h-3.5 rounded-full border border-slate-600" />}
                  <span className="text-slate-200">{step.title}</span>
                </div>
                <span className="text-[10px] text-slate-400">{step.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {isRunning && onCancel && (
        <div className="pt-2 flex justify-end">
          <button
            onClick={onCancel}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-rose-500/20 text-rose-300 border border-rose-500/40 hover:bg-rose-500/30 text-[11px] transition-colors"
          >
            <StopCircle className="w-3.5 h-3.5" />
            <span>Stop Autonomous Task</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default AgentExecutionCard;
