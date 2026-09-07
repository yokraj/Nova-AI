import React, { useState } from 'react';
import { SkillVariable } from '../types/skill';

interface SkillVariableEditorProps {
  variables: SkillVariable[];
  onExecuteWithVariables: (boundValues: Record<string, any>) => void;
  onCancel: () => void;
}

export const SkillVariableEditor: React.FC<SkillVariableEditorProps> = ({
  variables,
  onExecuteWithVariables,
  onCancel,
}) => {
  const [values, setValues] = useState<Record<string, any>>(() => {
    const init: Record<string, any> = {};
    variables.forEach((v) => {
      init[v.name] = v.defaultValue !== undefined ? v.defaultValue : v.examples?.[0] || '';
    });
    return init;
  });

  const handleChange = (name: string, val: any) => {
    setValues((prev) => ({ ...prev, [name]: val }));
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-slate-100 max-w-md w-full shadow-2xl">
      <h3 className="text-base font-bold text-white mb-1">Configure Skill Variables</h3>
      <p className="text-xs text-slate-400 mb-4">
        Provide variable values to adapt this skill to your current goal.
      </p>

      <div className="space-y-3 mb-5 text-xs">
        {variables.map((v) => (
          <div key={v.name}>
            <div className="flex items-center justify-between mb-1">
              <label className="font-mono text-indigo-300 font-medium">{v.name}</label>
              <span className="text-[10px] text-slate-500">{v.type}</span>
            </div>
            <input
              type={v.type === 'number' ? 'number' : 'text'}
              value={values[v.name] ?? ''}
              onChange={(e) => handleChange(v.name, e.target.value)}
              placeholder={v.description}
              className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white text-xs focus:border-indigo-500 focus:outline-none"
            />
          </div>
        ))}
      </div>

      <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-800">
        <button
          onClick={onCancel}
          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-lg"
        >
          Cancel
        </button>
        <button
          onClick={() => onExecuteWithVariables(values)}
          className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg"
        >
          EXECUTE
        </button>
      </div>
    </div>
  );
};
