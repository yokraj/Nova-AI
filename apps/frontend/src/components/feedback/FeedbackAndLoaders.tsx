import React from 'react';
import { AlertTriangle, CheckCircle2, Info, XCircle, Clock } from 'lucide-react';
import { cn } from '@/utils/cn';

export const Spinner: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('w-5 h-5 border-2 border-slate-800 border-t-cyan-400 rounded-full animate-spin', className)} />
);

export const PulseLoader: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('flex space-x-1.5 items-center', className)}>
    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '0ms' }} />
    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '150ms' }} />
    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '300ms' }} />
  </div>
);

export const Skeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('bg-slate-900/80 animate-pulse rounded-lg border border-slate-800/50', className)} />
);

export const Shimmer: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('relative overflow-hidden bg-slate-900 rounded-lg', className)}>
    <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-cyan-500/10 to-transparent animate-[shimmer_1.5s_infinite]" />
  </div>
);

export interface ToastProps {
  title: string;
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  className?: string;
  onClose?: () => void;
}

export const Toast: React.FC<ToastProps> = ({ title, message, type = 'info', className }) => (
  <div className={cn('glass-panel-cyan p-4 rounded-xl border flex items-start space-x-3 shadow-xl max-w-sm', className)}>
    {type === 'success' && <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />}
    {type === 'info' && <Info className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />}
    {type === 'warning' && <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />}
    {type === 'error' && <XCircle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />}
    <div className="space-y-0.5">
      <div className="text-xs font-bold text-slate-100">{title}</div>
      <div className="text-xs text-slate-400">{message}</div>
    </div>
  </div>
);

export const Alert: React.FC<{ title: string; children?: React.ReactNode; type?: 'info' | 'success' | 'warning' | 'danger'; className?: string }> = ({
  title,
  children,
  type = 'info',
  className,
}) => {
  const alertStyles = {
    info: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300',
    success: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
    warning: 'bg-amber-500/10 border-amber-500/30 text-amber-300',
    danger: 'bg-rose-500/10 border-rose-500/30 text-rose-300',
  };

  return (
    <div className={cn('p-4 rounded-xl border space-y-1', alertStyles[type], className)}>
      <div className="text-xs font-bold uppercase tracking-wider">{title}</div>
      {children && <div className="text-xs opacity-90">{children}</div>}
    </div>
  );
};

export const Banner: React.FC<{ title: string; subtitle?: string; className?: string }> = ({ title, subtitle, className }) => (
  <div className={cn('glass-panel-cyan p-4 rounded-2xl flex items-center justify-between', className)}>
    <div className="space-y-0.5">
      <div className="text-sm font-extrabold text-cyan-300 cyber-glow-text">{title}</div>
      {subtitle && <div className="text-xs text-slate-400">{subtitle}</div>}
    </div>
  </div>
);

export const TimelineItem: React.FC<{ title: string; timestamp: string; description?: string; isLast?: boolean; className?: string }> = ({
  title,
  timestamp,
  description,
  isLast = false,
  className,
}) => (
  <div className={cn('relative pl-6 pb-4', !isLast && 'border-l border-slate-800', className)}>
    <div className="absolute -left-1.5 top-0 w-3 h-3 rounded-full bg-cyan-400 border-2 border-slate-950 shadow-[0_0_8px_rgba(0,240,255,0.8)]" />
    <div className="flex justify-between items-center text-xs">
      <span className="font-bold text-slate-200">{title}</span>
      <span className="font-mono text-[10px] text-slate-500">{timestamp}</span>
    </div>
    {description && <div className="text-xs text-slate-400 mt-0.5">{description}</div>}
  </div>
);
