import React from 'react';
import { SkillVersionHistoryItem } from '../types/skill';

interface SkillVersionHistoryProps {
  history: SkillVersionHistoryItem[];
  onRollback?: (version: number) => void;
}

export const SkillVersionHistory: React.FC<SkillVersionHistoryProps> = ({ history, onRollback }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-slate-100 max-w-md w-full">
      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Version History</h4>
      <div className="space-y-3 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
        {history.map((item) => (
          <div key={item.version} className="pl-6 relative text-xs">
            <span className="absolute left-0 top-1 w-4 h-4 rounded-full bg-indigo-950 border border-indigo-500 text-[10px] flex items-center justify-center font-mono text-indigo-300">
              v{item.version}
            </span>
            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-850">
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-slate-200">{item.changes}</span>
                <span className="text-[10px] text-slate-500 font-mono">
                  {new Date(item.timestamp).toLocaleDateString()}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mb-2">{item.reason}</p>
              {onRollback && (
                <button
                  onClick={() => onRollback(item.version)}
                  className="text-[10px] text-indigo-400 hover:text-indigo-300 underline font-mono"
                >
                  Rollback to v{item.version}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
