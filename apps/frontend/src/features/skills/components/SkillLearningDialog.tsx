import React, { useState } from 'react';
import { Skill } from '../types/skill';

interface SkillLearningDialogProps {
  candidateSkill: Omit<Skill, 'id' | 'createdAt' | 'updatedAt' | 'usageCount' | 'successRate' | 'version' | 'history'>;
  onConfirmSave: (name: string, description: string) => void;
  onCancel: () => void;
}

export const SkillLearningDialog: React.FC<SkillLearningDialogProps> = ({
  candidateSkill,
  onConfirmSave,
  onCancel,
}) => {
  const [name, setName] = useState(candidateSkill.name);
  const [description, setDescription] = useState(candidateSkill.description);

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-slate-900 border border-indigo-500/30 rounded-xl p-6 text-slate-100 max-w-lg w-full shadow-2xl">
        <h3 className="text-lg font-bold text-white mb-1">Save New Learned Skill</h3>
        <p className="text-xs text-slate-400 mb-4">
          Nova extracted a structured reusable skill from your successful workflow.
        </p>

        <div className="space-y-3 mb-4 text-xs">
          <div>
            <label className="block text-slate-300 mb-1 font-medium">Skill Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white font-medium focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-slate-300 mb-1 font-medium">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div className="bg-slate-950 p-3 rounded-lg border border-slate-850">
            <span className="text-[11px] font-semibold text-indigo-400 block mb-1">
              Extracted Steps ({candidateSkill.steps.length})
            </span>
            <ul className="space-y-1 max-h-32 overflow-y-auto">
              {candidateSkill.steps.map((st) => (
                <li key={st.id} className="text-[11px] text-slate-300 flex items-center justify-between">
                  <span>{st.order}. {st.purpose}</span>
                  <span className="font-mono text-slate-500">{st.tool}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-800">
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-lg transition-colors"
          >
            CANCEL
          </button>
          <button
            onClick={() => onConfirmSave(name, description)}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-all"
          >
            SAVE SKILL
          </button>
        </div>
      </div>
    </div>
  );
};
