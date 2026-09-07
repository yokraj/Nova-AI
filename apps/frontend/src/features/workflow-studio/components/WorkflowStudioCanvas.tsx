import React, { useState, useEffect } from 'react';
import { Play, Circle, Square, Plus, Users, Eye, CheckCircle2, Layers, Copy, Trash2, ShieldAlert, FileCode, Clock, RefreshCw } from 'lucide-react';
import { DemonstrationRecorder } from '../recorder/demonstrationRecorder.js';
import { WorkflowBuilder } from '../studio/workflowBuilder.js';
import { SwarmReplayEngine } from '../replay/swarmReplayEngine.js';
import { WorkflowDryRunEngine } from '../testing/workflowDryRunEngine.js';
import { WorkflowStore } from '../persistence/workflowStore.js';
import { WorkflowDefinition, WorkflowNode, ReplayExecutionResult, DryRunResult } from '../types/workflowStudio.js';

interface WorkflowStudioCanvasProps {
  initialWorkflow?: WorkflowDefinition;
}

export const WorkflowStudioCanvas: React.FC<WorkflowStudioCanvasProps> = ({ initialWorkflow }) => {
  const [recorder] = useState(() => new DemonstrationRecorder());
  const [store] = useState(() => new WorkflowStore());
  const [replayEngine] = useState(() => new SwarmReplayEngine());
  const [dryRunEngine] = useState(() => new WorkflowDryRunEngine());

  const [workflow, setWorkflow] = useState<WorkflowDefinition>(() => {
    if (initialWorkflow) return initialWorkflow;
    const builder = new WorkflowBuilder('Production Multimodal Workflow', 'Interactive cross-application workflow editor');
    builder.addNode({
      label: 'Trigger: Operator Request',
      type: 'TRIGGER',
      riskLevel: 'SAFE',
      requiresApproval: false,
      x: 80,
      y: 100,
    });
    return builder.getWorkflow();
  });

  const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordedCount, setRecordedCount] = useState<number>(0);
  const [dryRunResult, setDryRunResult] = useState<DryRunResult | null>(null);
  const [replayResult, setReplayResult] = useState<ReplayExecutionResult | null>(null);
  const [isReplaying, setIsReplaying] = useState<boolean>(false);
  const [skillConvertedMessage, setSkillConvertedMessage] = useState<string | null>(null);

  useEffect(() => {
    store.saveWorkflow(workflow);
  }, [workflow, store]);

  const handleStartRecord = () => {
    recorder.startRecording(workflow.name);
    setIsRecording(true);
    setRecordedCount(0);
  };

  const handleRecordStep = () => {
    const act = recorder.recordAction({
      actionType: 'DESKTOP_CLICK',
      capability: 'COMPUTER_CONTROL',
      toolName: 'click_coordinate',
      arguments: { x: 500, y: 300, query: '{{query}}' },
      activeApp: 'Chrome Browser',
    });
    if (act) {
      setRecordedCount((prev) => prev + 1);
    }
  };

  const handleStopRecord = () => {
    const session = recorder.stopRecording();
    setIsRecording(false);
    if (session) {
      const convertedWf = recorder.convertSessionToWorkflow(session);
      setWorkflow(convertedWf);
    }
  };

  const handleAddNode = (type: WorkflowNode['type']) => {
    const builder = WorkflowBuilder.fromDefinition(workflow);
    const newNode = builder.addNode({
      label: `New ${type} Node`,
      type,
      riskLevel: type === 'SWARM_PARALLEL' ? 'LOW' : 'SAFE',
      requiresApproval: false,
      x: 100 + workflow.nodes.length * 160,
      y: 100,
    });

    if (workflow.nodes.length > 0) {
      const lastNode = workflow.nodes[workflow.nodes.length - 1];
      builder.addEdge(lastNode.id, newNode.id);
    }

    setWorkflow(builder.getWorkflow());
    setSelectedNode(newNode);
  };

  const handleDuplicateNode = (id: string) => {
    const builder = WorkflowBuilder.fromDefinition(workflow);
    builder.duplicateNode(id);
    setWorkflow(builder.getWorkflow());
  };

  const handleDeleteNode = (id: string) => {
    const builder = WorkflowBuilder.fromDefinition(workflow);
    builder.deleteNode(id);
    setWorkflow(builder.getWorkflow());
    if (selectedNode?.id === id) setSelectedNode(null);
  };

  const handleDryRun = async () => {
    const res = await dryRunEngine.performDryRun(workflow);
    setDryRunResult(res);
  };

  const handleReplay = async () => {
    setIsReplaying(true);
    setReplayResult(null);

    const result = await replayEngine.replayWorkflow(workflow, {
      workflowId: workflow.id,
      enableSwarmDelegation: true,
      verifyVisualStates: true,
      pauseOnApproval: true,
      stepTimeoutMs: 15000,
    });

    setReplayResult(result);
    store.recordReplayExecution(result);
    setIsReplaying(false);
  };

  const handleSaveVersion = () => {
    const builder = WorkflowBuilder.fromDefinition(workflow);
    const newVer = builder.createNewVersion(`Version ${workflow.version + 1} Snapshot`);
    setWorkflow(builder.getWorkflow());
  };

  const handleConvertToSkill = () => {
    const res = store.convertWorkflowToSkill(workflow);
    setSkillConvertedMessage(`Successfully converted to ${res.name} (ID: ${res.skillId})`);
  };

  return (
    <div className="p-6 bg-slate-950 text-slate-100 border border-slate-800 rounded-3xl space-y-6 font-sans shadow-2xl">
      {/* Header & Recorder Controls */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div className="flex items-center space-x-3">
          <Layers className="w-6 h-6 text-cyan-400" />
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-slate-100">{workflow.name}</h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                v{workflow.version}
              </span>
            </div>
            <p className="text-xs text-slate-400">{workflow.description}</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {!isRecording ? (
            <button
              onClick={handleStartRecord}
              className="px-3.5 py-1.5 rounded-xl bg-rose-500/20 text-rose-300 border border-rose-500/30 hover:bg-rose-500/30 text-xs font-mono font-bold flex items-center space-x-2 cursor-pointer"
            >
              <Circle className="w-3.5 h-3.5 fill-rose-400 animate-pulse" />
              <span>Record</span>
            </button>
          ) : (
            <div className="flex items-center space-x-2">
              <button
                onClick={handleRecordStep}
                className="px-3 py-1.5 rounded-xl bg-slate-800 text-slate-200 hover:bg-slate-700 text-xs font-mono flex items-center space-x-1 cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Step ({recordedCount})</span>
              </button>
              <button
                onClick={handleStopRecord}
                className="px-3.5 py-1.5 rounded-xl bg-slate-800 text-rose-400 border border-rose-500/40 hover:bg-rose-500/20 text-xs font-mono font-bold flex items-center space-x-1.5 cursor-pointer"
              >
                <Square className="w-3.5 h-3.5 fill-rose-400" />
                <span>Stop</span>
              </button>
            </div>
          )}

          <button
            onClick={handleDryRun}
            className="px-3 py-1.5 rounded-xl bg-amber-500/20 text-amber-300 border border-amber-500/30 hover:bg-amber-500/30 text-xs font-mono font-bold flex items-center space-x-1.5 cursor-pointer"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Dry-Run</span>
          </button>

          <button
            onClick={handleReplay}
            disabled={isReplaying}
            className="px-4 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/30 text-xs font-mono font-bold flex items-center space-x-2 cursor-pointer disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-cyan-400" />
            <span>{isReplaying ? 'Replaying...' : 'Replay Workflow'}</span>
          </button>
        </div>
      </div>

      {/* Dry Run Banner */}
      {dryRunResult && (
        <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs font-mono">
          <div className="flex items-center space-x-2">
            <span
              className={`px-2 py-0.5 rounded font-bold ${
                dryRunResult.overallStatus === 'READY'
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : dryRunResult.overallStatus === 'WARNING'
                  ? 'bg-amber-500/20 text-amber-400'
                  : 'bg-rose-500/20 text-rose-400'
              }`}
            >
              DRY-RUN: {dryRunResult.overallStatus}
            </span>
            <span className="text-slate-300">{dryRunResult.summary}</span>
          </div>
          <span className="text-slate-500">Risk Score: {dryRunResult.totalRiskScore}</span>
        </div>
      )}

      {/* Workflow Canvas Stream */}
      <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-4">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400">
          <span>WORKFLOW DAG STEPS ({workflow.nodes.length})</span>
          <div className="flex items-center space-x-2">
            <button onClick={() => handleAddNode('DESKTOP_ACTION')} className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[10px] cursor-pointer">
              + Desktop Action
            </button>
            <button onClick={() => handleAddNode('VISION_GROUNDING')} className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[10px] cursor-pointer">
              + Vision Target
            </button>
            <button onClick={() => handleAddNode('SWARM_PARALLEL')} className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[10px] cursor-pointer">
              + Swarm Role
            </button>
          </div>
        </div>

        <div className="flex items-center space-x-3 overflow-x-auto pb-4 pt-2">
          {workflow.nodes.map((node, idx) => (
            <React.Fragment key={node.id}>
              <div
                onClick={() => setSelectedNode(node)}
                className={`p-4 min-w-[200px] rounded-2xl border transition-all cursor-pointer space-y-2 ${
                  selectedNode?.id === node.id
                    ? 'bg-cyan-950/40 border-cyan-400 shadow-lg shadow-cyan-500/10'
                    : 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="font-bold text-slate-200">{node.type}</span>
                  <div className="flex items-center space-x-1">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                        node.riskLevel === 'HIGH' || node.riskLevel === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-300'
                          : 'bg-emerald-500/20 text-emerald-300'
                      }`}
                    >
                      {node.riskLevel}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDuplicateNode(node.id);
                      }}
                      className="p-1 text-slate-400 hover:text-slate-200"
                    >
                      <Copy className="w-3 h-3" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteNode(node.id);
                      }}
                      className="p-1 text-slate-400 hover:text-rose-400"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </div>

                <div className="text-xs font-bold text-slate-100 truncate">{node.label}</div>

                {node.assignedAgentRole && (
                  <div className="flex items-center space-x-1 text-[10px] font-mono text-cyan-400">
                    <Users className="w-3 h-3" />
                    <span>{node.assignedAgentRole}</span>
                  </div>
                )}
              </div>

              {idx < workflow.nodes.length - 1 && (
                <div className="w-6 h-0.5 bg-slate-700 flex-shrink-0" />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Action Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-800">
        <div className="flex items-center space-x-3">
          <button
            onClick={handleSaveVersion}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-mono flex items-center space-x-1.5 cursor-pointer text-slate-300"
          >
            <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
            <span>Save New Version (v{workflow.version + 1})</span>
          </button>
          <button
            onClick={handleConvertToSkill}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-mono flex items-center space-x-1.5 cursor-pointer text-slate-300"
          >
            <FileCode className="w-3.5 h-3.5 text-emerald-400" />
            <span>Convert to Learned Skill</span>
          </button>
        </div>

        {skillConvertedMessage && (
          <span className="text-xs font-mono text-emerald-400">{skillConvertedMessage}</span>
        )}
      </div>
    </div>
  );
};
