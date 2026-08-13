import React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/utils/cn';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export const GlassCard: React.FC<CardProps> = ({ children, className, onClick }) => (
  <div
    onClick={onClick}
    className={cn(
      'glass-panel p-5 rounded-2xl border border-slate-800/80 shadow-xl transition-all',
      onClick && 'cursor-pointer hover:border-slate-700/80',
      className
    )}
  >
    {children}
  </div>
);

export const CyberCard: React.FC<CardProps> = ({ children, className, onClick }) => (
  <div
    onClick={onClick}
    className={cn(
      'glass-panel-cyan p-5 rounded-2xl relative overflow-hidden transition-all',
      onClick && 'cursor-pointer hover:scale-[1.01]',
      className
    )}
  >
    <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-bl from-cyan-500/20 to-transparent pointer-events-none" />
    {children}
  </div>
);

export interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
  icon?: LucideIcon;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  isPositive = true,
  icon: Icon,
  className,
}) => (
  <GlassCard className={cn('space-y-3', className)}>
    <div className="flex items-center justify-between">
      <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</span>
      {Icon && (
        <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
          <Icon className="w-4 h-4" />
        </div>
      )}
    </div>
    <div>
      <div className="text-2xl font-extrabold text-slate-100 font-mono tracking-tight">{value}</div>
      {change && (
        <div
          className={cn(
            'text-[11px] font-medium font-mono mt-1',
            isPositive ? 'text-emerald-400' : 'text-rose-400'
          )}
        >
          {change}
        </div>
      )}
    </div>
  </GlassCard>
);

export interface StatusCardProps {
  title: string;
  status: string;
  subtitle?: string;
  type?: 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export const StatusCard: React.FC<StatusCardProps> = ({
  title,
  status,
  subtitle,
  type = 'info',
  className,
}) => {
  const typeColors = {
    success: 'text-emerald-400 bg-emerald-500/15 border-emerald-500/30',
    warning: 'text-amber-400 bg-amber-500/15 border-amber-500/30',
    danger: 'text-rose-400 bg-rose-500/15 border-rose-500/30',
    info: 'text-cyan-400 bg-cyan-500/15 border-cyan-500/30',
  };

  return (
    <GlassCard className={cn('flex items-center justify-between', className)}>
      <div className="space-y-0.5">
        <div className="text-xs font-bold text-slate-200">{title}</div>
        {subtitle && <div className="text-[11px] text-slate-400">{subtitle}</div>}
      </div>
      <span className={cn('text-xs font-mono font-bold px-2.5 py-1 rounded-full border', typeColors[type])}>
        {status}
      </span>
    </GlassCard>
  );
};

export interface AgentCardProps {
  name: string;
  role: string;
  status: 'active' | 'idle' | 'busy' | 'offline';
  tasksCompleted: number;
  avatar: string;
  className?: string;
}

export const AgentCard: React.FC<AgentCardProps> = ({
  name,
  role,
  status,
  tasksCompleted,
  avatar,
  className,
}) => (
  <GlassCard className={cn('space-y-3', className)}>
    <div className="flex items-center space-x-3">
      <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-slate-950 font-extrabold text-sm shadow-md">
        {avatar}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-bold text-slate-100 truncate">{name}</div>
        <div className="text-xs text-slate-400 truncate">{role}</div>
      </div>
      <span
        className={cn(
          'w-2.5 h-2.5 rounded-full',
          status === 'active' && 'bg-emerald-400 animate-pulse',
          status === 'busy' && 'bg-amber-400',
          status === 'idle' && 'bg-cyan-400',
          status === 'offline' && 'bg-slate-600'
        )}
      />
    </div>
    <div className="flex justify-between items-center text-xs font-mono text-slate-400 pt-2 border-t border-slate-800">
      <span>Tasks Completed:</span>
      <strong className="text-cyan-300">{tasksCompleted}</strong>
    </div>
  </GlassCard>
);

export const PanelCard: React.FC<CardProps & { title?: string }> = ({ title, children, className }) => (
  <div className={cn('glass-panel rounded-2xl border border-slate-800/80 overflow-hidden', className)}>
    {title && (
      <div className="px-5 py-3.5 border-b border-slate-800 bg-slate-900/40 text-xs font-bold uppercase tracking-wider text-slate-300">
        {title}
      </div>
    )}
    <div className="p-5">{children}</div>
  </div>
);
