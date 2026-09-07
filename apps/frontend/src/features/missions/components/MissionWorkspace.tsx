import React, { useState } from 'react';
import { Target, Sparkles } from 'lucide-react';
import { cn } from '@/utils/cn';
import { MOCK_MISSIONS } from '../mock/mockMissionData.js';
import { MockMissionEngine } from '../mock/mockMissionEngine.js';
import { MissionItem, AutonomyLevel } from '../types/mission.js';
import { MissionRecoveryManager } from '../runtime/missionRecoveryManager.js';
import { MissionCheckpointManager } from '../runtime/missionCheckpointManager.js';
import MissionCard from './MissionCard.js';
import MissionDetailPanel from './MissionDetailPanel.js';
import MissionCreateDialog from './MissionCreateDialog.js';
import MissionApprovalGate from './MissionApprovalGate.js';
import MissionReplanModal from './MissionReplanModal.js';

export const MissionWorkspace: React.FC = () => {
  const [engine] = useState(new MockMissionEngine());
  const [recoveryManager] = useState(new MissionRecoveryManager());
  const [checkpointManager] = useState(new MissionCheckpointManager());
  const [missions, setMissions] = useState<MissionItem[]>(MOCK_MISSIONS);
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedMission, setSelectedMission] = useState<MissionItem | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isApprovalOpen, setIsApprovalOpen] = useState(false);
  const [isReplanOpen, setIsReplanOpen] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const statuses = ['all', 'EXECUTING', 'COMPLETED', 'PAUSED', 'AWAITING_APPROVAL', 'FAILED'];

  const filtered = missions.filter(
    (m) => selectedStatus === 'all' || m.status === selectedStatus
  );

  const handleCreateMission = (goal: string, autonomyLevel: AutonomyLevel) => {
    const newMsn = engine.createMission(goal, autonomyLevel);
    checkpointManager.createCheckpoint({
      missionId: newMsn.id,
      executionId: `exec-${Date.now()}`,
      status: 'PLANNING',
      currentStep: 0,
      completedSteps: [],
      pendingSteps: ['step-1', 'step-2'],
      budgetState: recoveryManager.getDefaultBudget(),
    });
    setMissions((prev) => [newMsn, ...prev]);
  };

  const handlePause = (id: string) => {
    engine.pauseMission(id);
    const updated = engine.getMissionById(id);
    if (updated) {
      checkpointManager.createCheckpoint({
        missionId: updated.id,
        executionId: `exec-${Date.now()}`,
        status: 'PAUSED',
        currentStep: 1,
        completedSteps: ['step-1'],
        pendingSteps: ['step-2'],
        budgetState: recoveryManager.getDefaultBudget(),
      });
    }
    setMissions([...engine.listMissions()]);
    setActionMessage(`Mission ${id} paused cleanly with persistent checkpoint.`);
  };

  const handleResume = async (id: string) => {
    const target = engine.getMissionById(id);
    if (target) {
      const res = await recoveryManager.resumeMission(target);
      setActionMessage(res.message);
    }
    setMissions([...engine.listMissions()]);
  };

  const handleCancel = (id: string) => {
    engine.cancelMission(id);
    setMissions([...engine.listMissions()]);
    setActionMessage(`Mission ${id} cancelled by operator.`);
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
              Long-running autonomous checkpointing, crash-recovery, and approval-gated runtime
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs">
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-cyan-400 font-bold">{missions.filter((m) => m.status === 'EXECUTING').length}</span> Executing
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-amber-400 font-bold">{missions.filter((m) => m.status === 'AWAITING_APPROVAL').length}</span> Approvals
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-emerald-400 font-bold">{missions.filter((m) => m.status === 'COMPLETED').length}</span> Completed
          </div>
        </div>
      </div>

      {actionMessage && (
        <div className="p-3 rounded-2xl bg-slate-900 border border-cyan-500/40 text-xs font-mono text-cyan-300 flex items-center justify-between">
          <span>{actionMessage}</span>
          <button onClick={() => setActionMessage(null)} className="text-slate-400 hover:text-slate-200">
            Dismiss
          </button>
        </div>
      )}

      {/* Action & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 font-mono text-xs overflow-x-auto">
          {statuses.map((st) => (
            <button
              key={st}
              onClick={() => setSelectedStatus(st)}
              className={cn(
                'px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer capitalize text-[11px]',
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
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-bold text-xs flex items-center space-x-2 shadow-[0_0_20px_rgba(0,240,255,0.25)] hover:scale-[1.02] transition-all cursor-pointer"
        >
          <Sparkles className="w-4 h-4" />
          <span>New Long-Running Mission</span>
        </button>
      </div>

      {/* Mission Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((mission) => (
          <MissionCard
            key={mission.id}
            mission={mission}
            onClick={() => setSelectedMission(mission)}
            onPause={() => handlePause(mission.id)}
            onResume={() => handleResume(mission.id)}
            onCancel={() => handleCancel(mission.id)}
          />
        ))}
      </div>

      {/* Subsystem Modals & Detail Panel */}
      {selectedMission && (
        <MissionDetailPanel
          mission={selectedMission}
          onClose={() => setSelectedMission(null)}
          onPause={() => handlePause(selectedMission.id)}
          onResume={() => handleResume(selectedMission.id)}
          onCancel={() => handleCancel(selectedMission.id)}
          onReplan={() => handleReplan(selectedMission.id)}
        />
      )}

      <MissionCreateDialog
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onCreateMission={handleCreateMission}
      />

      {selectedMission && (
        <>
          <MissionApprovalGate
            isOpen={isApprovalOpen}
            missionTitle={selectedMission.title}
            toolName="native_execute"
            riskLevel="HIGH"
            reason="High-risk system modification requires explicit authorization."
            onApprove={() => {
              handleResume(selectedMission.id);
              setIsApprovalOpen(false);
            }}
            onReject={() => {
              handleCancel(selectedMission.id);
              setIsApprovalOpen(false);
            }}
          />

          <MissionReplanModal
            isOpen={isReplanOpen}
            missionTitle={selectedMission.title}
            failureReason="Step verification timed out due to missing target."
            proposedPlan={['Retry with alternative tool', 'Verify process status', 'Resume execution']}
            onConfirmReplan={() => {
              handleResume(selectedMission.id);
              setIsReplanOpen(false);
            }}
            onCancel={() => setIsReplanOpen(false)}
          />
        </>
      )}
    </div>
  );
};

export default MissionWorkspace;
