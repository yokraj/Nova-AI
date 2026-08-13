import React, { useState } from 'react';
import { Bot, Target, Users, Clock, Play, AlertCircle } from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard } from '@/components/cards/Cards';
import { ProgressBar, StatusBadge } from '@/components/status/StatusIndicators';
import { MOCK_ACTIVE_AGENTS_EXTENDED, MOCK_MISSIONS, MissionItem } from '@/mock/mockDashboardData';

export const ActiveWorkCenter: React.FC<{ className?: string }> = ({ className }) => {
  const [activeTab, setActiveTab] = useState<'agents' | 'missions'>('agents');
  const [missionsList, setMissionsList] = useState<MissionItem[]>(MOCK_MISSIONS);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  const toggleMissionPause = (id: string) => {
    setMissionsList((prev) =>
      prev.map((m) => {
        if (m.id === id) {
          const nextStatus = m.status === 'running' ? 'queued' : 'running';
          return { ...m, status: nextStatus };
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
              Active Work & Workforce Orchestration
            </h3>
            <p className="text-xs text-slate-400">67 Agents & autonomous mission DAG execution progress</p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('agents')}
            className={cn(
              'px-3 py-1 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer',
              activeTab === 'agents' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'
            )}
          >
            <Bot className="w-3.5 h-3.5" />
            <span>Active Agents (6)</span>
          </button>
          <button
            onClick={() => setActiveTab('missions')}
            className={cn(
              'px-3 py-1 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer',
              activeTab === 'missions' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' : 'text-slate-400 hover:text-slate-200'
            )}
          >
            <Target className="w-3.5 h-3.5" />
            <span>Active Missions (5)</span>
          </button>
        </div>
      </div>

      {/* Agents Tab */}
      {activeTab === 'agents' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {MOCK_ACTIVE_AGENTS_EXTENDED.map((agent) => (
            <div
              key={agent.id}
              onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
              className={cn(
                'p-3.5 rounded-2xl bg-slate-900/80 border transition-all cursor-pointer space-y-2.5',
                selectedAgent === agent.id
                  ? 'border-cyan-500/60 bg-slate-900 shadow-[0_0_15px_rgba(0,240,255,0.15)]'
                  : 'border-slate-800/90 hover:border-slate-700'
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-slate-950 font-black text-xs shadow-md">
                    {agent.avatar}
                  </div>
                  <div>
                    <div className="text-xs font-bold text-slate-100">{agent.name}</div>
                    <div className="text-[10px] font-mono text-slate-400">{agent.division}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-mono text-cyan-400 font-semibold">{agent.latencyMs}ms</span>
                  <StatusBadge
                    label={agent.status}
                    variant={agent.status === 'active' ? 'success' : agent.status === 'busy' ? 'warning' : 'info'}
                  />
                </div>
              </div>

              <div className="space-y-1 pt-1">
                <div className="text-xs text-slate-300 font-medium truncate flex items-center justify-between">
                  <span>Current Task: {agent.currentTask}</span>
                  <span className="text-[10px] font-mono text-cyan-300 font-bold ml-2">{agent.progress}%</span>
                </div>
                <ProgressBar progress={agent.progress} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Missions Tab */}
      {activeTab === 'missions' && (
        <div className="space-y-3">
          {missionsList.map((mission) => (
            <div
              key={mission.id}
              className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/90 hover:border-slate-700 transition-all space-y-3"
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
                    onClick={() => toggleMissionPause(mission.id)}
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-300 text-xs transition-all cursor-pointer"
                  >
                    {mission.status === 'running' ? <AlertCircle className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between items-center text-[10px] font-mono text-slate-400">
                  <span>DAG Execution Progress</span>
                  <span className="text-cyan-300 font-bold">{mission.progress}%</span>
                </div>
                <ProgressBar progress={mission.progress} />
              </div>
            </div>
          ))}
        </div>
      )}
    </GlassCard>
  );
};

export default ActiveWorkCenter;
