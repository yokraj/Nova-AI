import React from 'react';
import { cn } from '@/utils/cn';

export interface StatusBadgeProps {
  label: string;
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'cyan' | 'purple';
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ label, variant = 'info', className }) => {
  const variantStyles = {
    success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    danger: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    info: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    cyan: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
    purple: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
  };

  return (
    <span className={cn('text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border tracking-wide uppercase', variantStyles[variant], className)}>
      {label}
    </span>
  );
};

export const OnlineIndicator: React.FC<{ label?: string; className?: string }> = ({ label = 'ONLINE', className }) => (
  <div className={cn('flex items-center space-x-1.5 text-xs font-mono text-emerald-400', className)}>
    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
    <span className="font-bold">{label}</span>
  </div>
);

export const OfflineIndicator: React.FC<{ label?: string; className?: string }> = ({ label = 'OFFLINE', className }) => (
  <div className={cn('flex items-center space-x-1.5 text-xs font-mono text-slate-500', className)}>
    <span className="w-2 h-2 rounded-full bg-slate-600" />
    <span>{label}</span>
  </div>
);

export const HealthIndicator: React.FC<{ status?: 'healthy' | 'degraded' | 'critical'; className?: string }> = ({ status = 'healthy', className }) => (
  <div className={cn('flex items-center space-x-2', className)}>
    <span
      className={cn(
        'w-2.5 h-2.5 rounded-full',
        status === 'healthy' && 'bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]',
        status === 'degraded' && 'bg-amber-400',
        status === 'critical' && 'bg-rose-500 animate-ping'
      )}
    />
    <span className="text-xs font-mono font-bold uppercase text-slate-200">{status}</span>
  </div>
);

export const ProgressBar: React.FC<{ progress: number; className?: string }> = ({ progress, className }) => (
  <div className={cn('w-full h-2 rounded-full bg-slate-900 overflow-hidden border border-slate-800', className)}>
    <div
      className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 transition-all duration-300 shadow-[0_0_10px_rgba(0,240,255,0.5)]"
      style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
    />
  </div>
);

export const ProgressRing: React.FC<{ progress: number; size?: number; strokeWidth?: number; className?: string }> = ({
  progress,
  size = 48,
  strokeWidth = 4,
  className,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} stroke="#1e293b" strokeWidth={strokeWidth} fill="transparent" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#00f0ff"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
      </svg>
      <span className="absolute text-[10px] font-mono font-bold text-cyan-300">{Math.round(progress)}%</span>
    </div>
  );
};

export const CircularGauge: React.FC<{ value: number; label: string; max?: number; className?: string }> = ({ value, label, max = 100, className }) => (
  <div className={cn('flex flex-col items-center space-y-1', className)}>
    <ProgressRing progress={(value / max) * 100} size={56} strokeWidth={5} />
    <span className="text-[11px] font-mono text-slate-400 font-semibold">{label}</span>
  </div>
);
