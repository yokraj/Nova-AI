import React, { useState } from 'react';
import { cn } from '@/utils/cn';

export const Tooltip: React.FC<{ content: string; children: React.ReactNode; position?: 'top' | 'bottom' | 'left' | 'right'; className?: string }> = ({
  content,
  children,
  position = 'top',
  className,
}) => {
  const [visible, setVisible] = useState(false);

  const posClasses = {
    top: '-top-8 left-1/2 -translate-x-1/2',
    bottom: '-bottom-8 left-1/2 -translate-x-1/2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  return (
    <div className="relative inline-flex items-center" onMouseEnter={() => setVisible(true)} onMouseLeave={() => setVisible(false)}>
      {children}
      {visible && (
        <div className={cn('absolute z-50 px-2.5 py-1 text-[10px] font-mono font-bold text-cyan-300 bg-slate-900 border border-cyan-500/30 rounded-lg shadow-xl whitespace-nowrap pointer-events-none', posClasses[position], className)}>
          {content}
        </div>
      )}
    </div>
  );
};

export const Popover: React.FC<{ trigger: React.ReactNode; content: React.ReactNode; className?: string }> = ({ trigger, content, className }) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative inline-block">
      <div onClick={() => setOpen(!open)} className="cursor-pointer">
        {trigger}
      </div>
      {open && (
        <div className={cn('absolute z-50 mt-2 right-0 glass-panel-cyan p-4 rounded-xl shadow-2xl border border-cyan-500/30 w-64 space-y-2', className)}>
          {content}
        </div>
      )}
    </div>
  );
};
