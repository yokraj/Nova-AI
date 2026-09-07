import React from 'react';

interface SkillSuggestionCardProps {
  workflowGoal: string;
  repeatCount: number;
  onSaveSkill: () => void;
  onNotNow: () => void;
  onNeverAskAgain: () => void;
}

export const SkillSuggestionCard: React.FC<SkillSuggestionCardProps> = ({
  workflowGoal,
  repeatCount,
  onSaveSkill,
  onNotNow,
  onNeverAskAgain,
}) => {
  return (
    <div className="bg-gradient-to-r from-indigo-950/90 to-purple-950/90 border border-indigo-500/40 rounded-xl p-4 text-slate-100 shadow-2xl backdrop-blur-lg max-w-md">
      <div className="flex items-center space-x-2 mb-2">
        <span className="text-amber-400 text-sm font-bold">✨ NOVA SKILL SUGGESTION</span>
      </div>

      <p className="text-xs text-slate-300 mb-3 leading-relaxed">
        I noticed you&apos;ve performed this workflow <strong className="text-indigo-300 font-semibold">{repeatCount} times</strong>:
        <br />
        <span className="italic text-white font-mono text-[11px] block mt-1 bg-slate-900/60 p-2 rounded border border-slate-800">
          &quot;{workflowGoal}&quot;
        </span>
      </p>

      <p className="text-xs text-slate-400 mb-4">Would you like me to save it as a reusable, adaptable skill?</p>

      <div className="flex flex-col space-y-1.5">
        <button
          onClick={onSaveSkill}
          className="w-full text-xs font-medium py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-all shadow-md"
        >
          SAVE SKILL
        </button>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={onNotNow}
            className="text-xs py-1.5 bg-slate-800/80 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
          >
            NOT NOW
          </button>
          <button
            onClick={onNeverAskAgain}
            className="text-xs py-1.5 bg-slate-900/80 hover:bg-rose-950/50 text-rose-400 hover:text-rose-300 rounded-lg transition-colors border border-rose-900/30"
          >
            NEVER ASK AGAIN
          </button>
        </div>
      </div>
    </div>
  );
};
