import React, { useState, useEffect } from 'react';
import { Activity, RefreshCw, X, ShieldCheck, AlertTriangle } from 'lucide-react';
import { diagnosticsService, RuntimeDiagnosticsSummary } from '../services/diagnostics/diagnosticsService';

interface RuntimeDiagnosticsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RuntimeDiagnosticsDrawer: React.FC<RuntimeDiagnosticsDrawerProps> = ({ isOpen, onClose }) => {
  const [summary, setSummary] = useState<RuntimeDiagnosticsSummary | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchDiagnostics = async () => {
    setLoading(true);
    try {
      const data = await diagnosticsService.runFullDiagnostics();
      setSummary(data);
    } catch {
      // Ignore fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchDiagnostics();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-slate-950 border-l border-slate-800 p-6 shadow-2xl z-50 overflow-y-auto font-sans">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-bold text-slate-100">Runtime Diagnostics</h2>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition-all"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="py-4 space-y-4">
        {/* Overall Status Banner */}
        <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-mono">Overall Health</div>
            <div className="text-sm font-bold text-slate-100 flex items-center gap-2 mt-1">
              {summary?.overallHealth === 'HEALTHY' ? (
                <>
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span className="text-emerald-400 font-mono">HEALTHY</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span className="text-amber-400 font-mono">{summary?.overallHealth || 'UNKNOWN'}</span>
                </>
              )}
            </div>
          </div>
          <button
            onClick={fetchDiagnostics}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 transition-all disabled:opacity-50"
            title="Refresh Diagnostics"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Component Health List */}
        <div className="space-y-3">
          <div className="text-xs font-mono text-slate-400 uppercase tracking-wider">Subsystem Readiness</div>
          {summary?.components.map((comp) => (
            <div key={comp.name} className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-200">{comp.name}</span>
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-mono border ${
                    comp.online
                      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                      : 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                  }`}
                >
                  {comp.status}
                </span>
              </div>
              <p className="text-[11px] text-slate-400">{comp.detail}</p>
              {comp.latencyMs !== undefined && (
                <div className="text-[10px] font-mono text-cyan-400">Latency: {comp.latencyMs}ms</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
