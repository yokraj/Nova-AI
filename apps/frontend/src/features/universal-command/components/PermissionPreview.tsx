import React from 'react';
import { ShieldAlert, Check } from 'lucide-react';
import { cn } from '@/utils/cn';
import { CommandPermissionAssessment } from '../types/permission';

interface PermissionPreviewProps {
  permission: CommandPermissionAssessment;
  onApprove?: () => void;
  onReject?: () => void;
  className?: string;
}

export const PermissionPreview: React.FC<PermissionPreviewProps> = ({
  permission,
  onApprove,
  onReject,
  className,
}) => {
  const isHigh = permission.riskLevel === 'HIGH' || permission.riskLevel === 'CRITICAL';

  return (
    <div
      className={cn(
        'p-4.5 rounded-3xl border space-y-3 font-mono text-xs shadow-2xl',
        isHigh
          ? 'bg-slate-950 border-amber-500/50 text-slate-100'
          : 'bg-slate-950 border-slate-800 text-slate-300',
        className
      )}
    >
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 font-bold uppercase tracking-wider text-amber-300">
          <ShieldAlert className="w-4 h-4 text-amber-400" />
          <span>SECURITY & RISK ASSESSMENT</span>
        </div>
        <span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold border border-amber-500/30 uppercase">
          {permission.riskLevel} RISK
        </span>
      </div>

      <div className="space-y-1 text-[11px]">
        <div>Access Scope: <strong className="text-slate-200">{permission.scope}</strong></div>
        <div className="text-slate-400">{permission.reason}</div>
      </div>

      {permission.requiresApproval && (
        <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
          {onReject && (
            <button
              onClick={onReject}
              className="px-3.5 py-1.5 rounded-xl bg-slate-900 text-slate-300 hover:text-rose-300 border border-slate-800 font-bold transition-all cursor-pointer"
            >
              Deny
            </button>
          )}
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-3.5 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Authorize Action</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default PermissionPreview;
