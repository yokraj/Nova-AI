import React from 'react';
import { cn } from '@/utils/cn';
import { DeviceStatus } from '../types/device';

interface DeviceStatusBadgeProps {
  status: DeviceStatus;
  className?: string;
}

export const DeviceStatusBadge: React.FC<DeviceStatusBadgeProps> = ({ status, className }) => {
  const styles: Record<DeviceStatus, string> = {
    ONLINE: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold',
    OFFLINE: 'bg-slate-800 text-slate-500 border-slate-700',
    CONNECTING: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30 animate-pulse',
    DISCONNECTED: 'bg-slate-800 text-slate-500 border-slate-700',
    BUSY: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    LOCKED: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    PERMISSION_REQUIRED: 'bg-amber-500/30 text-amber-200 border-amber-500/50 font-bold animate-pulse',
    UNKNOWN: 'bg-slate-800 text-slate-500 border-slate-700',
  };

  return (
    <span className={cn('px-2.5 py-0.5 rounded-full text-[10px] font-mono border uppercase tracking-wider', styles[status], className)}>
      ● {status}
    </span>
  );
};

export default DeviceStatusBadge;
