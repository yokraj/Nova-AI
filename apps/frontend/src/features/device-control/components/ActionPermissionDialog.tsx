import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, Check } from 'lucide-react';
import { cn } from '@/utils/cn';
import { DeviceActionRequest } from '../types/deviceAction';

interface ActionPermissionDialogProps {
  action: DeviceActionRequest | null;
  onApprove: () => void;
  onReject: () => void;
  className?: string;
}

export const ActionPermissionDialog: React.FC<ActionPermissionDialogProps> = ({
  action,
  onApprove,
  onReject,
  className,
}) => {
  if (!action) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className={cn('w-full max-w-md bg-slate-950 border border-amber-500/40 rounded-3xl p-6 space-y-4 text-xs font-mono shadow-2xl text-slate-100', className)}
        >
          <div className="flex items-center space-x-2 text-amber-300 font-extrabold border-b border-amber-500/20 pb-3">
            <ShieldAlert className="w-5 h-5 text-amber-400 animate-pulse" />
            <span className="uppercase tracking-wider">ACTION REQUIRES APPROVAL</span>
          </div>

          <div className="space-y-1">
            <div className="text-[10px] text-slate-400 uppercase font-bold">Requested Operation</div>
            <h4 className="text-sm font-bold font-sans text-slate-100">"{action.commandText}"</h4>
          </div>

          <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800 space-y-1.5 font-mono text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-400">Target Device:</span>
              <span className="text-slate-200 font-bold">{action.targetDeviceName}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Required Capability:</span>
              <span className="text-purple-300 font-bold">{action.capabilityRequired}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Scope:</span>
              <span className="text-slate-300 font-bold">{action.scope}</span>
            </div>
            <div className="flex justify-between border-t border-slate-800 pt-1">
              <span className="text-slate-400">Risk Assessment:</span>
              <span className="text-rose-400 font-bold uppercase">{action.riskLevel} RISK</span>
            </div>
          </div>

          <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
            <button
              onClick={onReject}
              className="px-4 py-2 rounded-xl bg-slate-900 text-slate-300 hover:text-rose-300 border border-slate-800 font-bold transition-all cursor-pointer"
            >
              Reject
            </button>
            <button
              onClick={onApprove}
              className="px-4 py-2 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1"
            >
              <Check className="w-4 h-4" />
              <span>Approve Execution</span>
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ActionPermissionDialog;
