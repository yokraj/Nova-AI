import React from 'react';
import { cn } from '@/utils/cn';

export const Title: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <h1 className={cn('text-3xl font-extrabold text-slate-100 tracking-tight', className)}>{children}</h1>
);

export const Subtitle: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <p className={cn('text-sm text-slate-400 font-normal', className)}>{children}</p>
);

export const SectionTitle: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <h2 className={cn('text-xl font-bold text-slate-200 tracking-tight', className)}>{children}</h2>
);

export const BodyText: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <p className={cn('text-sm text-slate-300 leading-relaxed', className)}>{children}</p>
);

export const Label: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <span className={cn('text-xs font-bold text-slate-400 uppercase tracking-wider', className)}>{children}</span>
);

export const MetricText: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <span className={cn('font-mono font-bold text-cyan-400', className)}>{children}</span>
);

export const MetricValue: React.FC<{ value: string | number; label?: string; className?: string }> = ({ value, label, className }) => (
  <div className={cn('space-y-0.5', className)}>
    <div className="text-3xl font-extrabold font-mono text-cyan-400 cyber-glow-text">{value}</div>
    {label && <div className="text-xs text-slate-400 font-medium">{label}</div>}
  </div>
);

export const StatBlock: React.FC<{ label: string; value: string | number; subvalue?: string; className?: string }> = ({ label, value, subvalue, className }) => (
  <div className={cn('bg-slate-900/60 p-3 rounded-xl border border-slate-800 space-y-1', className)}>
    <div className="text-[11px] font-mono text-slate-500 uppercase">{label}</div>
    <div className="text-lg font-bold font-mono text-slate-100">{value}</div>
    {subvalue && <div className="text-[10px] font-mono text-cyan-400">{subvalue}</div>}
  </div>
);

export const DataLabel: React.FC<{ label: string; value: string | number; className?: string }> = ({ label, value, className }) => (
  <div className={cn('flex justify-between items-center text-xs font-mono py-1 border-b border-slate-800/60', className)}>
    <span className="text-slate-400">{label}:</span>
    <span className="font-semibold text-slate-200">{value}</span>
  </div>
);

export const CodeBlock: React.FC<{ code: string; language?: string; className?: string }> = ({ code, language = 'typescript', className }) => (
  <div className={cn('bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-cyan-300 overflow-x-auto relative', className)}>
    <span className="absolute right-3 top-2 text-[10px] text-slate-600 uppercase font-mono">{language}</span>
    <pre>{code}</pre>
  </div>
);

export const MarkdownContainer: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <div className={cn('prose prose-invert max-w-none text-sm text-slate-300 space-y-3', className)}>
    {children}
  </div>
);
