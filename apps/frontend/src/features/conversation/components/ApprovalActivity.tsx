import React from 'react';
import { ShieldAlert, Check, X, ShieldCheck } from 'lucide-react';
import { cn } from '@/utils/cn';
import { ApprovalRequestData } from '../types/message';

interface ApprovalActivityProps {
  data: ApprovalRequestData;
  onApprove?: () => void;
  onReject?: () => void;
  className?: string;
}

export const ApprovalActivity: React.FC<ApprovalActivityProps> = ({
  data,
  onApprove,
  onReject,
  className,
}) => {
  return (
    <div className={cn('my-3 p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-xs font-mono space-y-3', className)}>
      <div className="flex items-center justify-between border-b border-amber-500/20 pb-2">
        <div className="flex items-center space-x-2 text-amber-300 font-bold">
          <ShieldAlert className="w-4 h-4 text-amber-400 animate-pulse" />
          <span>APPROVAL REQUIRED • {data.riskLevel} RISK</span>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 uppercase font-bold">
          {data.status}
        </span>
      </div>

      <p className="text-slate-200 font-sans text-sm font-medium">{data.title}</p>

      {data.status === 'pending' ? (
        <div className="flex items-center space-x-2 pt-1">
          <button
            onClick={onApprove}
            className="px-3.5 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 font-bold flex items-center space-x-1 transition-all cursor-pointer"
          >
            <Check className="w-3.5 h-3.5" />
            <span>Approve Action</span>
          </button>
          <button
            onClick={onReject}
            className="px-3.5 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 font-bold flex items-center space-x-1 transition-all cursor-pointer"
          >
            <X className="w-3.5 h-3.5" />
            <span>Reject</span>
          </button>
        </div>
      ) : (
        <div className="flex items-center space-x-2 text-cyan-300 font-bold">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Status: Action {data.status.toUpperCase()} by owner.</span>
        </div>
      )}
    </div>
  );
};

export default ApprovalActivity;
