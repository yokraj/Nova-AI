import React from 'react';
import { Search, Command } from 'lucide-react';
import { cn } from '@/utils/cn';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({ label, error, className, ...props }) => (
  <div className="space-y-1.5 w-full">
    {label && <label className="text-xs font-bold uppercase tracking-wider text-slate-400">{label}</label>}
    <input
      className={cn(
        'w-full px-3.5 py-2 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/40 transition-all disabled:opacity-50',
        error && 'border-rose-500 focus:border-rose-500 focus:ring-rose-500/40',
        className
      )}
      {...props}
    />
    {error && <span className="text-[11px] text-rose-400 font-mono">{error}</span>}
  </div>
);

export const SearchInput: React.FC<InputProps> = ({ className, ...props }) => (
  <div className="relative w-full">
    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
    <input
      type="text"
      className={cn(
        'w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/40 transition-all',
        className
      )}
      placeholder="Search..."
      {...props}
    />
  </div>
);

export const CommandInput: React.FC<InputProps> = ({ className, ...props }) => (
  <div className="relative w-full">
    <Command className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-cyan-400" />
    <input
      type="text"
      className={cn(
        'w-full pl-9 pr-12 py-2 rounded-xl bg-slate-900 border border-cyan-500/30 text-xs font-mono text-cyan-300 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 shadow-[0_0_15px_rgba(0,240,255,0.1)] transition-all',
        className
      )}
      placeholder="Type a command or query..."
      {...props}
    />
    <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-mono bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">
      ↵
    </kbd>
  </div>
);

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
}

export const Textarea: React.FC<TextareaProps> = ({ label, className, ...props }) => (
  <div className="space-y-1.5 w-full">
    {label && <label className="text-xs font-bold uppercase tracking-wider text-slate-400">{label}</label>}
    <textarea
      className={cn(
        'w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/40 transition-all resize-none',
        className
      )}
      rows={4}
      {...props}
    />
  </div>
);

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: { value: string; label: string }[];
}

export const Select: React.FC<SelectProps> = ({ label, options, className, ...props }) => (
  <div className="space-y-1.5 w-full">
    {label && <label className="text-xs font-bold uppercase tracking-wider text-slate-400">{label}</label>}
    <select
      className={cn(
        'w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/60 transition-all',
        className
      )}
      {...props}
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value} className="bg-slate-950 text-slate-200">
          {opt.label}
        </option>
      ))}
    </select>
  </div>
);

export const Checkbox: React.FC<{ label?: string; checked?: boolean; onChange?: (checked: boolean) => void; className?: string }> = ({
  label,
  checked = false,
  onChange,
  className,
}) => (
  <label className={cn('flex items-center space-x-2.5 cursor-pointer text-xs text-slate-300 select-none', className)}>
    <input
      type="checkbox"
      checked={checked}
      onChange={(e) => onChange?.(e.target.checked)}
      className="w-4 h-4 rounded bg-slate-900 border-slate-800 text-cyan-400 focus:ring-cyan-500/40 accent-cyan-400 cursor-pointer"
    />
    {label && <span>{label}</span>}
  </label>
);

export const Switch: React.FC<{ checked?: boolean; onChange?: (checked: boolean) => void; label?: string; className?: string }> = ({
  checked = false,
  onChange,
  label,
  className,
}) => (
  <label className={cn('flex items-center justify-between cursor-pointer space-x-3 select-none', className)}>
    {label && <span className="text-xs font-medium text-slate-300">{label}</span>}
    <div
      onClick={() => onChange?.(!checked)}
      className={cn(
        'w-9 h-5 rounded-full p-0.5 transition-colors duration-200 ease-in-out',
        checked ? 'bg-cyan-500 shadow-[0_0_10px_rgba(0,240,255,0.5)]' : 'bg-slate-800'
      )}
    >
      <div
        className={cn(
          'w-4 h-4 rounded-full bg-slate-950 shadow-md transform transition-transform duration-200 ease-in-out',
          checked && 'translate-x-4 bg-slate-950'
        )}
      />
    </div>
  </label>
);

export const Toggle = Switch;

export const Slider: React.FC<{ value: number; min?: number; max?: number; onChange?: (val: number) => void; label?: string; className?: string }> = ({
  value,
  min = 0,
  max = 100,
  onChange,
  label,
  className,
}) => (
  <div className={cn('space-y-1.5 w-full', className)}>
    {label && (
      <div className="flex justify-between text-xs font-mono text-slate-400">
        <span>{label}</span>
        <span className="text-cyan-300 font-bold">{value}</span>
      </div>
    )}
    <input
      type="range"
      min={min}
      max={max}
      value={value}
      onChange={(e) => onChange?.(Number(e.target.value))}
      className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
    />
  </div>
);
