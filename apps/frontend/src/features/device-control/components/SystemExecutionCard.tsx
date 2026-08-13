import React from 'react';
import { Monitor, ShieldAlert, CheckCircle2, AlertCircle } from 'lucide-react';
import { cn } from '@/utils/cn';

interface SystemExecutionCardProps {
  actionTitle: string;
  targetName: string;
  status: 'PENDING' | 'EXECUTING' | 'AWAITING_APPROVAL' | 'COMPLETED' | 'FAILED';
  riskLevel: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  resultMessage?: string;
  onApprove?: () => void;
  onCancel?: () => void;
  className?: string;
}

export const SystemExecutionCard: React.FC<SystemExecutionCardProps> = ({
  actionTitle,
  targetName,
  status,
  riskLevel,
  resultMessage,
  onApprove,
  onCancel,
  className,
}) => {
  const isHighRisk = riskLevel === 'HIGH' || riskLevel === 'CRITICAL';

  return (
    <div className={cn('p-4 rounded-3xl border border-cyan-500/30 bg-slate-950/90 backdrop-blur-xl shadow-2xl space-y-3 font-mono text-xs text-slate-100', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-cyan-300 font-bold uppercase tracking-wider">
          <Monitor className="w-4 h-4 text-cyan-400" />
          <span>WINDOWS OS AUTOMATION</span>
        </div>
        <div className="flex items-center space-x-2">
          <span
            className={cn(
              'px-2 py-0.5 rounded-full text-[9px] font-bold uppercase border',
              isHighRisk ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
            )}
          >
            {riskLevel} RISK
          </span>
          <span
            className={cn(
              'px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border',
              status === 'COMPLETED' && 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
              status === 'AWAITING_APPROVAL' && 'bg-amber-500/20 text-amber-300 border-amber-500/40 animate-pulse',
              status === 'FAILED' && 'bg-rose-500/20 text-rose-300 border-rose-500/40'
            )}
          >
            {status}
          </span>
        </div>
      </div>

      <div className="space-y-1">
        <div className="text-slate-300 text-xs">
          Action: <strong className="text-cyan-200">{actionTitle}</strong>
        </div>
        <div className="text-slate-400 text-[11px]">
          Target: <span className="text-slate-200">{targetName}</span>
        </div>
      </div>

      {resultMessage && (
        <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-[11px] text-slate-300 flex items-center space-x-2">
          {status === 'COMPLETED' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
          )}
          <span>{resultMessage}</span>
        </div>
      )}

      {status === 'AWAITING_APPROVAL' && (
        <div className="pt-2 flex items-center justify-between border-t border-slate-800">
          <div className="flex items-center space-x-1.5 text-amber-300 text-[11px]">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <span>High-risk action requires authorization</span>
          </div>
          <div className="flex space-x-2">
            {onCancel && (
              <button
                onClick={onCancel}
                className="px-3 py-1 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 text-[11px]"
              >
                Cancel
              </button>
            )}
            {onApprove && (
              <button
                onClick={onApprove}
                className="px-3 py-1 rounded-xl bg-amber-500 text-slate-950 font-bold hover:bg-amber-400 text-[11px]"
              >
                Approve
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemExecutionCard;
