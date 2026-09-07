import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, Check } from 'lucide-react';
import { cn } from '@/utils/cn';

interface MissionApprovalGateProps {
  isOpen: boolean;
  taskTitle?: string;
  missionTitle?: string;
  toolName?: string;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  reason: string;
  onApprove: () => void;
  onReject: () => void;
  className?: string;
}

export const MissionApprovalGate: React.FC<MissionApprovalGateProps> = ({
  isOpen,
  taskTitle,
  missionTitle,
  toolName,
  riskLevel,
  reason,
  onApprove,
  onReject,
  className,
}) => {
  if (!isOpen) return null;

  const displayTitle = taskTitle || missionTitle || 'Pending High-Risk Step';

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
            <span className="uppercase tracking-wider">MISSION APPROVAL REQUIRED</span>
          </div>

          <div className="space-y-1">
            <div className="text-[10px] text-slate-400 uppercase font-bold">Pending Operation</div>
            <h4 className="text-sm font-bold font-sans text-slate-100">{displayTitle}</h4>
            {toolName && <div className="text-[11px] text-cyan-400 font-mono">Tool: {toolName}</div>}
          </div>

          <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <div className="flex justify-between text-[11px]">
              <span className="text-slate-400">Risk Assessment:</span>
              <span className="text-rose-400 font-bold uppercase">{riskLevel} RISK</span>
            </div>
            <p className="text-xs font-sans text-slate-300 leading-relaxed pt-1">{reason}</p>
          </div>

          <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
            <button
              onClick={onReject}
              className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-slate-100 font-bold cursor-pointer transition-all"
            >
              Reject Action
            </button>
            <button
              onClick={onApprove}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-600 text-slate-950 font-bold flex items-center space-x-1.5 shadow-[0_0_15px_rgba(245,158,11,0.3)] hover:scale-[1.02] cursor-pointer transition-all"
            >
              <Check className="w-4 h-4" />
              <span>Authorize & Resume</span>
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default MissionApprovalGate;
