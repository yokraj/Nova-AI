import React, { useState } from 'react';
import { Target, Clock, Users, CheckCircle2, Play, AlertCircle } from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard } from '@/components/cards/Cards';
import { ProgressBar, StatusBadge } from '@/components/status/StatusIndicators';
import { MOCK_MISSIONS, MissionItem } from '@/mock/mockDashboardData';

export const RunningMissionsWidget: React.FC<{ className?: string }> = ({ className }) => {
  const [filter, setFilter] = useState<'all' | 'running' | 'queued' | 'completed'>('all');
  const [missionsList, setMissionsList] = useState<MissionItem[]>(MOCK_MISSIONS);
  const [selectedMission, setSelectedMission] = useState<string | null>(null);

  const filteredMissions = missionsList.filter((m) => {
    if (filter === 'all') return true;
    return m.status === filter;
  });

  const toggleMissionPause = (id: string) => {
    setMissionsList((prev) =>
      prev.map((m) => {
        if (m.id === id) {
          if (m.status === 'running') return { ...m, status: 'queued' };
          if (m.status === 'queued') return { ...m, status: 'running' };
        }
        return m;
      })
    );
  };

  return (
    <GlassCard className={cn('p-5 space-y-4', className)}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-3 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Target className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Autonomous Missions
            </h3>
            <p className="text-xs text-slate-400">Multi-agent DAG task decomposition & execution pipelines</p>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
          {(['all', 'running', 'queued', 'completed'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={cn(
                'px-2.5 py-1 rounded-lg text-[11px] font-semibold uppercase tracking-wider transition-all cursor-pointer',
                filter === tab ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' : 'text-slate-400 hover:text-slate-200'
              )}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Missions List */}
      <div className="space-y-3">
        {filteredMissions.map((mission) => {
          const isSelected = selectedMission === mission.id;
          return (
            <div
              key={mission.id}
              onClick={() => setSelectedMission(isSelected ? null : mission.id)}
              className={cn(
                'p-4 rounded-2xl bg-slate-900/80 border transition-all cursor-pointer space-y-3',
                isSelected
                  ? 'border-purple-500/60 bg-slate-900 shadow-[0_0_15px_rgba(168,85,247,0.15)]'
                  : 'border-slate-800/90 hover:border-slate-700'
              )}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      {mission.category}
                    </span>
                    <h4 className="text-xs font-bold text-slate-100">{mission.title}</h4>
                  </div>
                  <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400">
                    <span className="flex items-center space-x-1">
                      <Users className="w-3 h-3 text-cyan-400" />
                      <span>{mission.assignedAgents} Agents</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Clock className="w-3 h-3 text-purple-400" />
                      <span>{mission.elapsedTime}</span>
                    </span>
                    <span>Subtasks: {mission.subtasksCompleted}/{mission.subtasksTotal}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <StatusBadge
                    label={mission.status}
                    variant={
                      mission.status === 'running'
                        ? 'cyan'
                        : mission.status === 'completed'
                        ? 'success'
                        : mission.status === 'queued'
                        ? 'warning'
                        : 'danger'
                    }
                  />
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleMissionPause(mission.id);
                    }}
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-300 text-xs transition-all cursor-pointer"
                    title={mission.status === 'running' ? 'Pause Mission' : 'Resume Mission'}
                  >
                    {mission.status === 'running' ? <AlertCircle className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {/* Mission Progress Bar */}
              <div className="space-y-1">
                <div className="flex justify-between items-center text-[10px] font-mono text-slate-400">
                  <span>Overall DAG Completion</span>
                  <span className="text-cyan-300 font-bold">{mission.progress}%</span>
                </div>
                <ProgressBar progress={mission.progress} />
              </div>
            </div>
          );
        })}
      </div>
    </GlassCard>
  );
};

export default RunningMissionsWidget;
