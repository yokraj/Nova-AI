import React, { useState, useEffect } from 'react';
import { Clock, Play, Pause, XCircle, ShieldAlert, Activity } from 'lucide-react';
import { BackgroundRuntime } from '../runtime/backgroundRuntime';
import { ScheduledTask, TaskExecutionRecord } from '../types/scheduledTask';

interface BackgroundRuntimeDrawerProps {
  runtime?: BackgroundRuntime;
}

export const BackgroundRuntimeDrawer: React.FC<BackgroundRuntimeDrawerProps> = ({
  runtime: externalRuntime,
}) => {
  const [runtime] = useState<BackgroundRuntime>(() => externalRuntime || new BackgroundRuntime());
  const [tasks, setTasks] = useState<ScheduledTask[]>([]);
  const [history, setHistory] = useState<TaskExecutionRecord[]>([]);
  const [runtimeState, setRuntimeState] = useState<string>('RUNNING');

  useEffect(() => {
    const refreshData = () => {
      setTasks(runtime.getTaskStore().getAllTasks());
      setHistory(runtime.getTaskStore().getHistory());
      setRuntimeState(runtime.getRuntimeState());
    };
    refreshData();
    const interval = setInterval(refreshData, 2000);
    return () => clearInterval(interval);
  }, [runtime]);

  const handleApprove = (id: string) => {
    runtime.approveTask(id);
    setTasks(runtime.getTaskStore().getAllTasks());
  };

  const handlePause = (id: string) => {
    runtime.pauseTask(id);
    setTasks(runtime.getTaskStore().getAllTasks());
  };

  const handleResume = (id: string) => {
    runtime.resumeTask(id);
    setTasks(runtime.getTaskStore().getAllTasks());
  };

  const handleCancel = (id: string) => {
    runtime.cancelTask(id);
    setTasks(runtime.getTaskStore().getAllTasks());
  };

  const handleRunNow = async (task: ScheduledTask) => {
    await runtime.executeTask(task);
    setTasks(runtime.getTaskStore().getAllTasks());
  };

  return (
    <div className="p-5 bg-slate-950 text-slate-100 border border-slate-800 rounded-3xl space-y-5 font-sans shadow-2xl">
      {/* Header Badge */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div className="flex items-center space-x-3">
          <Activity className="w-5 h-5 text-cyan-400 animate-pulse" />
          <h2 className="text-sm font-bold tracking-wide">Background Automation Runtime</h2>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>{runtimeState}</span>
        </span>
      </div>

      {/* Task List */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400">
          <span>SCHEDULED TASKS ({tasks.length})</span>
          <span>QUEUE: {runtime.getQueue().getQueueLength()} QUEUED</span>
        </div>

        {tasks.length === 0 ? (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/60 text-center text-xs text-slate-500 font-mono">
            No background tasks scheduled.
          </div>
        ) : (
          tasks.map((t) => (
            <div
              key={t.id}
              className="p-3.5 rounded-2xl bg-slate-900/90 border border-slate-800/80 hover:border-slate-700 transition-all space-y-2"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xs font-bold text-slate-100">{t.name}</h3>
                  <p className="text-[11px] text-slate-400 truncate max-w-md">{t.goal}</p>
                </div>
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-mono border ${
                    t.status === 'RUNNING'
                      ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30'
                      : t.status === 'WAITING_APPROVAL'
                      ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                      : t.status === 'COMPLETED'
                      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                      : t.status === 'FAILED'
                      ? 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                      : 'bg-slate-800/60 text-slate-400 border-slate-700/60'
                  }`}
                >
                  {t.status}
                </span>
              </div>

              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                <span className="flex items-center space-x-1">
                  <Clock className="w-3 h-3 text-slate-500" />
                  <span>Next: {t.nextRunAt ? new Date(t.nextRunAt).toLocaleTimeString() : 'Manual / Event'}</span>
                </span>
                <span>Priority: {t.priority}</span>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end space-x-2 pt-1 border-t border-slate-800/50">
                {t.status === 'WAITING_APPROVAL' && (
                  <button
                    onClick={() => handleApprove(t.id)}
                    className="px-2.5 py-1 rounded-lg bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 text-[10px] font-mono font-bold flex items-center space-x-1 cursor-pointer"
                  >
                    <ShieldAlert className="w-3 h-3" />
                    <span>Approve Task</span>
                  </button>
                )}
                {t.status === 'PAUSED' ? (
                  <button
                    onClick={() => handleResume(t.id)}
                    className="px-2 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 text-[10px] font-mono flex items-center space-x-1 cursor-pointer"
                  >
                    <Play className="w-3 h-3" />
                    <span>Resume</span>
                  </button>
                ) : (
                  <button
                    onClick={() => handlePause(t.id)}
                    className="px-2 py-1 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 text-[10px] font-mono flex items-center space-x-1 cursor-pointer"
                  >
                    <Pause className="w-3 h-3" />
                    <span>Pause</span>
                  </button>
                )}
                <button
                  onClick={() => handleRunNow(t)}
                  className="px-2 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 text-[10px] font-mono flex items-center space-x-1 cursor-pointer"
                >
                  <Play className="w-3 h-3" />
                  <span>Run Now</span>
                </button>
                <button
                  onClick={() => handleCancel(t.id)}
                  className="px-2 py-1 rounded-lg bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 text-[10px] font-mono flex items-center space-x-1 cursor-pointer"
                >
                  <XCircle className="w-3 h-3" />
                  <span>Cancel</span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Timeline Execution History */}
      <div className="space-y-2 pt-2 border-t border-slate-800/80">
        <span className="text-xs font-mono text-slate-400">RECENT EXECUTION TIMELINE</span>
        <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
          {history.length === 0 ? (
            <div className="text-[11px] font-mono text-slate-500 italic">No execution history recorded.</div>
          ) : (
            history.map((h) => (
              <div key={h.executionId} className="flex items-center justify-between text-[11px] font-mono p-2 rounded-xl bg-slate-900/50 border border-slate-800/40">
                <span className="truncate max-w-xs text-slate-300">{h.summary}</span>
                <span className={`font-bold ${h.status === 'COMPLETED' ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {h.status} ({h.durationMs}ms)
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
