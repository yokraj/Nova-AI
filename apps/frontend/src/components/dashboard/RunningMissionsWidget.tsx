import React, { useState } from 'react';
import {
  Target,
  Clock,
  Users,
  Play,
  Pause,
  Search,
  Filter,
  CheckCircle2,
  X,
  ChevronDown,
  ChevronUp,
  Layers,
  StopCircle,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { MissionItem } from '@/types/dashboard';
import { MOCK_MISSIONS } from '@/mock/mockDashboardData';

interface RunningMissionsWidgetProps {
  className?: string;
  missions?: MissionItem[];
  onSelectMission?: (mission: MissionItem) => void;
  onPauseMission?: (id: string) => Promise<boolean> | void;
  onResumeMission?: (id: string) => Promise<boolean> | void;
  onCancelMission?: (id: string) => Promise<boolean> | void;
  onApproveMission?: (id: string) => Promise<boolean> | void;
}

export const RunningMissionsWidget: React.FC<RunningMissionsWidgetProps> = ({
  className,
  missions = MOCK_MISSIONS,
  onSelectMission,
  onPauseMission,
  onResumeMission,
  onCancelMission,
  onApproveMission,
}) => {
  const [filter, setFilter] = useState<'all' | 'running' | 'queued' | 'completed'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [missionsList, setMissionsList] = useState<MissionItem[]>(missions);
  const [expandedMissionId, setExpandedMissionId] = useState<string | null>(null);
  const [selectedMissionForModal, setSelectedMissionForModal] = useState<MissionItem | null>(null);

  React.useEffect(() => {
    setMissionsList(missions);
  }, [missions]);

  const filteredMissions = missionsList.filter((m) => {
    const matchesFilter = filter === 'all' || m.status === filter;
    const matchesSearch =
      m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.category.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const toggleMissionPause = (id: string) => {
    const target = missionsList.find((m) => m.id === id);
    if (target?.status === 'running') {
      if (onPauseMission) onPauseMission(id);
    } else {
      if (onResumeMission) onResumeMission(id);
    }

    setMissionsList((prev) =>
      prev.map((m) => {
        if (m.id === id) {
          if (m.status === 'running') return { ...m, status: 'paused' };
          if (m.status === 'paused' || m.status === 'queued') return { ...m, status: 'running' };
        }
        return m;
      })
    );
  };

  const cancelMission = (id: string) => {
    if (onCancelMission) onCancelMission(id);
    setMissionsList((prev) =>
      prev.map((m) => (m.id === id ? { ...m, status: 'failed' } : m))
    );
  };

  const runningCount = missionsList.filter((m) => m.status === 'running').length;

  return (
    <div
      className={cn(
        'glass-panel p-5 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl space-y-4 shadow-xl select-none',
        className
      )}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-3 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20 shrink-0">
            <Target className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
              Autonomous Missions
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Multi-agent DAG task decomposition & pipeline orchestration
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {missionsList[0]?.isLive ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span>LIVE PIPELINE ({runningCount} ACTIVE)</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span>OFFLINE • CACHED ({runningCount} ACTIVE)</span>
            </span>
          )}
        </div>
      </div>

      {/* Search & Tabs Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div className="relative flex-1 max-w-sm">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search missions by title or category..."
            className="w-full pl-9 pr-8 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500/50 transition-all font-sans"
            aria-label="Search missions"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-[11px] font-mono">
          <Filter className="w-3 h-3 text-slate-500 ml-1 mr-0.5 shrink-0" />
          {(['all', 'running', 'queued', 'completed'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={cn(
                'px-2.5 py-1 rounded-lg uppercase tracking-wider transition-all cursor-pointer',
                filter === tab
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              )}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Missions List */}
      {filteredMissions.length === 0 ? (
        <div className="p-8 text-center rounded-2xl bg-slate-900/40 border border-slate-800/80 text-xs font-mono text-slate-500 space-y-1">
          <Target className="w-6 h-6 mx-auto text-slate-600 mb-2" />
          <p>No missions match filter "{searchQuery || filter}".</p>
          <button
            onClick={() => {
              setSearchQuery('');
              setFilter('all');
            }}
            className="text-purple-400 hover:text-purple-300 text-xs font-semibold cursor-pointer underline pt-1"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredMissions.map((mission) => {
            const isExpanded = expandedMissionId === mission.id;
            return (
              <div
                key={mission.id}
                className={cn(
                  'p-4 rounded-2xl bg-slate-900/80 border transition-all space-y-3',
                  mission.status === 'running'
                    ? 'border-purple-500/50 shadow-[0_0_15px_rgba(168,85,247,0.1)]'
                    : 'border-slate-800/90 hover:border-slate-700'
                )}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                        {mission.category}
                      </span>
                      <h4 className="text-xs font-bold text-slate-100 truncate">{mission.title}</h4>
                    </div>
                    <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400 flex-wrap">
                      <span className="flex items-center space-x-1">
                        <Users className="w-3 h-3 text-cyan-400" />
                        <span>{mission.assignedAgents} Agents</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <Clock className="w-3 h-3 text-purple-400" />
                        <span>{mission.elapsedTime}</span>
                      </span>
                      <span>
                        Subtasks: <strong className="text-slate-200">{mission.subtasksCompleted}/{mission.subtasksTotal}</strong>
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 shrink-0">
                    <span
                      className={cn(
                        'text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full border uppercase',
                        mission.status === 'running'
                          ? 'bg-cyan-500/15 border-cyan-500/30 text-cyan-300'
                          : mission.status === 'completed'
                          ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
                          : mission.status === 'paused'
                          ? 'bg-amber-500/15 border-amber-500/30 text-amber-400'
                          : mission.status === 'queued'
                          ? 'bg-blue-500/15 border-blue-500/30 text-blue-400'
                          : 'bg-rose-500/15 border-rose-500/30 text-rose-400'
                      )}
                    >
                      {mission.status}
                    </span>

                    {/* Pause / Resume Button */}
                    <button
                      onClick={() => toggleMissionPause(mission.id)}
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-300 text-xs transition-all cursor-pointer"
                      title={mission.status === 'running' ? 'Pause Mission' : 'Resume Mission'}
                    >
                      {mission.status === 'running' ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                    </button>

                    {/* Cancel Button */}
                    {mission.status === 'running' && (
                      <button
                        onClick={() => cancelMission(mission.id)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-rose-400 text-xs transition-all cursor-pointer"
                        title="Cancel Mission"
                      >
                        <StopCircle className="w-3.5 h-3.5" />
                      </button>
                    )}

                    {/* Details Toggle */}
                    <button
                      onClick={() => setExpandedMissionId(isExpanded ? null : mission.id)}
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 text-xs transition-all cursor-pointer"
                      title="Toggle DAG Subtasks"
                    >
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="space-y-1">
                  <div className="flex justify-between items-center text-[10px] font-mono text-slate-400">
                    <span>DAG Execution Progress</span>
                    <span className="text-cyan-300 font-bold">{mission.progress}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full transition-all duration-300"
                      style={{ width: `${mission.progress}%` }}
                    />
                  </div>
                </div>

                {/* Expandable DAG Subtask Breakdown */}
                {isExpanded && (
                  <div className="pt-2 border-t border-slate-800/80 space-y-2 text-xs font-mono">
                    <div className="flex items-center justify-between text-slate-400">
                      <span className="flex items-center space-x-1.5">
                        <Layers className="w-3.5 h-3.5 text-purple-400" />
                        <span>Subtask Execution Graph</span>
                      </span>
                      <button
                        onClick={() => {
                          setSelectedMissionForModal(mission);
                          if (onSelectMission) onSelectMission(mission);
                        }}
                        className="text-cyan-400 hover:text-cyan-300 underline cursor-pointer text-[11px]"
                      >
                        Inspect DAG Modal
                      </button>
                    </div>

                    <div className="space-y-1.5">
                      <div className="p-2 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                        <span className="text-slate-300">Phase 1: Architecture Synthesis & Scope Analysis</span>
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      </div>
                      <div className="p-2 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                        <span className="text-slate-300">Phase 2: Codebase Dependency Extraction</span>
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      </div>
                      <div className="p-2 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                        <span className="text-slate-300">Phase 3: Multi-agent Parallel Verification & Test Run</span>
                        {mission.status === 'completed' ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        ) : (
                          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Modal for Deep DAG Inspection */}
      {selectedMissionForModal && (
        <div
          className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedMissionForModal(null)}
        >
          <div
            className="w-full max-w-xl p-6 rounded-3xl bg-slate-950 border border-purple-500/40 shadow-2xl space-y-4 font-sans text-slate-100"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-3">
                <div className="p-2.5 rounded-2xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  <Target className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100">{selectedMissionForModal.title}</h3>
                  <p className="text-xs font-mono text-purple-400">
                    Category: {selectedMissionForModal.category} • {selectedMissionForModal.assignedAgents} Agents Assigned
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedMissionForModal(null)}
                className="p-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-100 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs font-mono">
              <div className="grid grid-cols-3 gap-2">
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <div className="text-slate-500">Status</div>
                  <div className="text-cyan-300 font-bold uppercase">{selectedMissionForModal.status}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <div className="text-slate-500">Elapsed Time</div>
                  <div className="text-purple-300 font-bold">{selectedMissionForModal.elapsedTime}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <div className="text-slate-500">Subtasks</div>
                  <div className="text-emerald-400 font-bold">
                    {selectedMissionForModal.subtasksCompleted} / {selectedMissionForModal.subtasksTotal}
                  </div>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex justify-between text-slate-400">
                  <span>Overall DAG Progress</span>
                  <span className="text-purple-300 font-bold">{selectedMissionForModal.progress}%</span>
                </div>
                <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full"
                    style={{ width: `${selectedMissionForModal.progress}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800 text-xs font-mono">
              <button
                onClick={() => setSelectedMissionForModal(null)}
                className="px-4 py-2 rounded-xl bg-purple-500 text-slate-950 font-bold transition-all cursor-pointer hover:bg-purple-400 shadow-sm"
              >
                Close DAG View
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RunningMissionsWidget;
