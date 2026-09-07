import React from 'react';
import { SkillExecutionResult } from '../types/skill';

interface SkillExecutionCardProps {
  execution: SkillExecutionResult;
  skillName: string;
  onDismiss?: () => void;
}

export const SkillExecutionCard: React.FC<SkillExecutionCardProps> = ({ execution, skillName, onDismiss }) => {
  return (
    <div className="bg-slate-900/90 border border-indigo-500/30 rounded-xl p-4 text-slate-100 shadow-xl backdrop-blur-md max-w-md">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className={`w-2.5 h-2.5 rounded-full ${execution.success ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
          <h4 className="font-semibold text-sm tracking-wide text-indigo-300">NOVA SKILL EXECUTION</h4>
        </div>
        <span className="text-xs font-mono text-slate-400">v{execution.skillVersion}</span>
      </div>

      <div className="mb-3">
        <h3 className="font-medium text-base text-white">{skillName}</h3>
        <p className="text-xs text-slate-400 mt-0.5">{execution.summary}</p>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs bg-slate-950/60 p-2.5 rounded-lg mb-3 border border-slate-800">
        <div>
          <span className="text-slate-500 block">Steps Executed</span>
          <span className="font-mono text-slate-200">{execution.executedStepsCount}</span>
        </div>
        <div>
          <span className="text-slate-500 block">Duration</span>
          <span className="font-mono text-slate-200">{execution.durationMs} ms</span>
        </div>
      </div>

      {Object.keys(execution.adaptedVariables).length > 0 && (
        <div className="mb-3">
          <span className="text-xs text-slate-500 block mb-1">Bound Variables:</span>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(execution.adaptedVariables).map(([k, v]) => (
              <span key={k} className="text-xs bg-indigo-950/80 border border-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-md font-mono">
                {k}: {String(v)}
              </span>
            ))}
          </div>
        </div>
      )}

      {onDismiss && (
        <button
          onClick={onDismiss}
          className="w-full text-xs py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
        >
          Dismiss
        </button>
      )}
    </div>
  );
};
