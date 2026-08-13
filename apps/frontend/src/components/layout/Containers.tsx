import React from 'react';
import { cn } from '@/utils/cn';

export interface ContainerProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
}

export const Panel: React.FC<ContainerProps> = ({ children, className, title }) => (
  <div className={cn('glass-panel p-6 rounded-2xl border border-slate-800/80 space-y-4', className)}>
    {title && <h3 className="text-lg font-bold text-slate-100">{title}</h3>}
    {children}
  </div>
);

export const Section: React.FC<ContainerProps> = ({ children, className, title }) => (
  <section className={cn('space-y-4', className)}>
    {title && (
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
        <h2 className="text-xl font-extrabold text-slate-100 tracking-tight">{title}</h2>
      </div>
    )}
    {children}
  </section>
);

export const Widget: React.FC<ContainerProps> = ({ children, className, title }) => (
  <div className={cn('bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-2', className)}>
    {title && <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">{title}</div>}
    {children}
  </div>
);

export const Window: React.FC<ContainerProps & { onClose?: () => void }> = ({ title, children, className, onClose }) => (
  <div className={cn('glass-panel rounded-2xl border border-cyan-500/20 shadow-[0_0_30px_rgba(0,0,0,0.5)] overflow-hidden', className)}>
    <div className="h-10 bg-slate-900/90 px-4 flex items-center justify-between border-b border-slate-800 select-none">
      <div className="flex items-center space-x-2">
        <div className="w-3 h-3 rounded-full bg-rose-500/80 cursor-pointer" onClick={onClose} />
        <div className="w-3 h-3 rounded-full bg-amber-500/80" />
        <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
        {title && <span className="ml-3 text-xs font-mono font-bold text-slate-300">{title}</span>}
      </div>
    </div>
    <div className="p-6">{children}</div>
  </div>
);

export const FloatingPanel: React.FC<ContainerProps> = ({ children, className }) => (
  <div className={cn('fixed bottom-6 right-6 glass-panel-cyan p-4 rounded-2xl shadow-2xl z-50 max-w-sm w-full', className)}>
    {children}
  </div>
);
