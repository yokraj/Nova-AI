import React, { useState } from 'react';
import { Skill, SkillCategory } from '../types/skill';

interface SkillListDrawerProps {
  skills: Skill[];
  isOpen: boolean;
  onClose: () => void;
  onSelectSkill: (skill: Skill) => void;
  onToggleStatus: (id: string, currentStatus: string) => void;
}

export const SkillListDrawer: React.FC<SkillListDrawerProps> = ({
  skills,
  isOpen,
  onClose,
  onSelectSkill,
  onToggleStatus,
}) => {
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  if (!isOpen) return null;

  const filtered = skills.filter((s) => {
    const matchesSearch =
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.description.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || s.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories: Array<SkillCategory | 'all'> = [
    'all',
    'automation',
    'browser',
    'filesystem',
    'system',
    'development',
    'general',
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/50 backdrop-blur-xs flex justify-end">
      <div className="bg-slate-900 border-l border-slate-800 w-full max-w-md h-full flex flex-col p-5 text-slate-100 shadow-2xl animate-in slide-in-from-right">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <span>⚡ NOVA LEARNED SKILLS</span>
              <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-2 py-0.5 rounded-full font-mono">
                {skills.length}
              </span>
            </h2>
            <p className="text-xs text-slate-400">Structured workflow automations learned by Nova.</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-lg">
            ✕
          </button>
        </div>

        {/* Search & Filters */}
        <div className="space-y-2 mb-4">
          <input
            type="text"
            placeholder="Search learned skills..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
          />

          <div className="flex gap-1 overflow-x-auto pb-1 text-[10px] no-scrollbar">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-2.5 py-1 rounded-md capitalize font-mono border transition-all ${
                  selectedCategory === cat
                    ? 'bg-indigo-600 text-white border-indigo-500 font-semibold'
                    : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Skill List */}
        <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
          {filtered.length === 0 ? (
            <div className="text-center py-10 text-slate-500 text-xs">
              No skills found matching filter.
            </div>
          ) : (
            filtered.map((skill) => (
              <div
                key={skill.id}
                onClick={() => onSelectSkill(skill)}
                className="bg-slate-950 p-3 rounded-xl border border-slate-800 hover:border-indigo-500/50 transition-all cursor-pointer group"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-white group-hover:text-indigo-300 transition-colors">
                    {skill.name}
                  </span>
                  <span className="text-[10px] font-mono text-indigo-400 bg-indigo-950 px-1.5 py-0.5 rounded border border-indigo-900">
                    v{skill.version}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-2 mb-2">{skill.description}</p>
                <div className="flex items-center justify-between text-[10px] text-slate-500 border-t border-slate-900 pt-2">
                  <span>{skill.steps.length} steps • {(skill.successRate * 100).toFixed(0)}% success</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleStatus(skill.id, skill.status);
                    }}
                    className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold uppercase ${
                      skill.status === 'active'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        : 'bg-amber-950 text-amber-400 border border-amber-800'
                    }`}
                  >
                    {skill.status}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
