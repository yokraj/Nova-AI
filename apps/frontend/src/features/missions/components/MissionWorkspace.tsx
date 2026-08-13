import React, { useState } from 'react';
import { Target, Sparkles } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MOCK_MISSIONS } from '../mock/mockMissionData';
import { MockMissionEngine } from '../mock/mockMissionEngine';
import { MissionItem, AutonomyLevel } from '../types/mission';
import MissionCard from './MissionCard';
import MissionDetailPanel from './MissionDetailPanel';
import MissionCreateDialog from './MissionCreateDialog';
import MissionApprovalGate from './MissionApprovalGate';
import MissionReplanModal from './MissionReplanModal';

export const MissionWorkspace: React.FC = () => {
  const [engine] = useState(new MockMissionEngine());
  const [missions, setMissions] = useState<MissionItem[]>(MOCK_MISSIONS);
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedMission, setSelectedMission] = useState<MissionItem | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isApprovalOpen, setIsApprovalOpen] = useState(false);
  const [isReplanOpen, setIsReplanOpen] = useState(false);

  const statuses = ['all', 'EXECUTING', 'COMPLETED', 'PAUSED'];

  const filtered = missions.filter(
    (m) => selectedStatus === 'all' || m.status === selectedStatus
  );

  const handleCreateMission = (goal: string, autonomyLevel: AutonomyLevel) => {
    const newMsn = engine.createMission(goal, autonomyLevel);
    setMissions((prev) => [newMsn, ...prev]);
  };

  const handlePause = (id: string) => {
    engine.pauseMission(id);
    setMissions([...engine.listMissions()]);
  };

  const handleResume = (id: string) => {
    engine.resumeMission(id);
    setMissions([...engine.listMissions()]);
  };

  const handleCancel = (id: string) => {
    engine.cancelMission(id);
    setMissions([...engine.listMissions()]);
  };

  const handleReplan = (id: string) => {
    engine.replanMission(id);
    setMissions([...engine.listMissions()]);
    setIsReplanOpen(true);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header Stat Panel */}
      <div className="p-6 rounded-3xl bg-slate-900/90 border border-cyan-500/30 flex flex-col md:flex-row items-center justify-between gap-4 shadow-2xl">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Target className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Nova Mission Control</h1>
            <p className="text-xs text-slate-400 font-mono">
              High-level goal-driven autonomous DAG mission orchestration
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs">
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-cyan-400 font-bold">2</span> Executing
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-emerald-400 font-bold">11</span> Completed
          </div>
        </div>
      </div>

      {/* Action & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 font-mono text-xs">
          {statuses.map((st) => (
            <button
              key={st}
              onClick={() => setSelectedStatus(st)}
              className={cn(
                'px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer capitalize',
                selectedStatus === st
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              )}
            >
              {st}
            </button>
          ))}
        </div>

        <button
          onClick={() => setIsCreateOpen(true)}
          className="px-4 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 font-bold font-mono text-xs transition-all cursor-pointer flex items-center space-x-1.5"
        >
          <Sparkles className="w-4 h-4" />
          <span>New Autonomous Mission</span>
        </button>
      </div>

      {/* Mission Roster Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((mission) => (
          <MissionCard
            key={mission.id}
            mission={mission}
            onSelect={() => setSelectedMission(mission)}
          />
        ))}
      </div>

      {/* Modals */}
      <MissionDetailPanel
        mission={selectedMission}
        tasks={selectedMission ? engine.getTasksForMission(selectedMission.id) : []}
        onClose={() => setSelectedMission(null)}
        onPause={handlePause}
        onResume={handleResume}
        onCancel={handleCancel}
        onReplan={handleReplan}
      />

      <MissionCreateDialog
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onCreateMission={handleCreateMission}
      />

      <MissionApprovalGate
        isOpen={isApprovalOpen}
        taskTitle="Deploy Portfolio Web Application to Production"
        riskLevel="HIGH"
        reason="This action modifies live production environment deployment configuration."
        onApprove={() => setIsApprovalOpen(false)}
        onReject={() => setIsApprovalOpen(false)}
      />

      <MissionReplanModal
        isOpen={isReplanOpen}
        failedTaskTitle="Deploy Portfolio Application to Staging"
        failureReason="Staging server credentials unavailable."
        onConfirmReplan={() => setIsReplanOpen(false)}
        onClose={() => setIsReplanOpen(false)}
      />
    </div>
  );
};

export default MissionWorkspace;
