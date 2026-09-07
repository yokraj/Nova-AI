import React from 'react';
import { Skill } from '../types/skill';

interface SkillDetailPanelProps {
  skill: Skill;
  onRun?: (skill: Skill) => void;
  onDisable?: (id: string) => void;
  onEnable?: (id: string) => void;
  onDelete?: (id: string) => void;
  onClose?: () => void;
}

export const SkillDetailPanel: React.FC<SkillDetailPanelProps> = ({
  skill,
  onRun,
  onDisable,
  onEnable,
  onDelete,
  onClose,
}) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-slate-100 shadow-2xl max-w-xl w-full">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
        <div>
          <span className="text-xs font-mono uppercase tracking-wider text-indigo-400">{skill.category} SKILL</span>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <span>{skill.name}</span>
            <span className="text-xs bg-indigo-950 border border-indigo-700 text-indigo-300 px-2 py-0.5 rounded-full font-mono">
              v{skill.version}
            </span>
          </h2>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-slate-400 hover:text-white text-lg">
            ✕
          </button>
        )}
      </div>

      <p className="text-xs text-slate-300 mb-4 leading-relaxed">{skill.description}</p>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-2 bg-slate-950 p-3 rounded-lg mb-4 text-center border border-slate-800">
        <div>
          <span className="text-[10px] uppercase text-slate-500 block">Success Rate</span>
          <span className="text-sm font-semibold text-emerald-400 font-mono">{(skill.successRate * 100).toFixed(0)}%</span>
        </div>
        <div>
          <span className="text-[10px] uppercase text-slate-500 block">Used Count</span>
          <span className="text-sm font-semibold text-indigo-300 font-mono">{skill.usageCount}</span>
        </div>
        <div>
          <span className="text-[10px] uppercase text-slate-500 block">Status</span>
          <span
            className={`text-sm font-semibold capitalize font-mono ${
              skill.status === 'active' ? 'text-emerald-400' : 'text-amber-400'
            }`}
          >
            {skill.status}
          </span>
        </div>
      </div>

      {/* Variables */}
      {skill.variables.length > 0 && (
        <div className="mb-4">
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Variables ({skill.variables.length})</h4>
          <div className="space-y-1.5">
            {skill.variables.map((v) => (
              <div key={v.name} className="bg-slate-950/60 p-2 rounded border border-slate-850 flex items-center justify-between text-xs">
                <div>
                  <span className="font-mono text-indigo-300 font-medium">{v.name}</span>
                  <span className="text-slate-500 text-[10px] ml-2">({v.type})</span>
                </div>
                <span className="text-slate-400 text-[11px] font-mono">{v.defaultValue || v.examples?.[0] || 'required'}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Steps */}
      <div className="mb-5">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Steps ({skill.steps.length})</h4>
        <div className="space-y-2">
          {skill.steps.map((st) => (
            <div key={st.id} className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-xs">
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-slate-200">
                  {st.order}. {st.purpose}
                </span>
                <span className="font-mono text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">
                  {st.tool}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between gap-2 border-t border-slate-800 pt-4">
        {onRun && (
          <button
            onClick={() => onRun(skill)}
            disabled={skill.status === 'disabled'}
            className="flex-1 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-xs rounded-lg transition-all"
          >
            RUN SKILL
          </button>
        )}

        {skill.status === 'active' && onDisable && (
          <button
            onClick={() => onDisable(skill.id)}
            className="px-3 py-2 bg-amber-950/50 hover:bg-amber-900/60 text-amber-300 text-xs rounded-lg border border-amber-800/40 transition-colors"
          >
            DISABLE
          </button>
        )}

        {skill.status === 'disabled' && onEnable && (
          <button
            onClick={() => onEnable(skill.id)}
            className="px-3 py-2 bg-emerald-950/50 hover:bg-emerald-900/60 text-emerald-300 text-xs rounded-lg border border-emerald-800/40 transition-colors"
          >
            ENABLE
          </button>
        )}

        {onDelete && (
          <button
            onClick={() => onDelete(skill.id)}
            className="px-3 py-2 bg-rose-950/50 hover:bg-rose-900/60 text-rose-400 text-xs rounded-lg border border-rose-900/40 transition-colors"
          >
            DELETE
          </button>
        )}
      </div>
    </div>
  );
};
