import React from 'react';
import { Bot, User, Layers, ChevronRight } from 'lucide-react';
import { cn } from '@/utils/cn';

export const UserAvatar: React.FC<{ name?: string; src?: string; size?: 'sm' | 'md' | 'lg'; className?: string }> = ({ name = 'Admin', src, size = 'md', className }) => {
  const sizes = { sm: 'w-6 h-6 text-[10px]', md: 'w-8 h-8 text-xs', lg: 'w-10 h-10 text-sm' };
  return (
    <div className={cn('rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-slate-950 font-bold shadow-md overflow-hidden', sizes[size], className)}>
      {src ? <img src={src} alt={name} className="w-full h-full object-cover" /> : name.charAt(0)}
    </div>
  );
};

export const AgentAvatar: React.FC<{ name?: string; size?: 'sm' | 'md' | 'lg'; className?: string }> = ({ name = 'Agent', size = 'md', className }) => {
  const sizes = { sm: 'w-6 h-6 text-[10px]', md: 'w-8 h-8 text-xs', lg: 'w-10 h-10 text-sm' };
  return (
    <div className={cn('rounded-xl bg-gradient-to-tr from-purple-500 to-cyan-500 flex items-center justify-center text-slate-950 font-bold shadow-md', sizes[size], className)}>
      <Bot className="w-4 h-4 text-slate-950" />
    </div>
  );
};

export const WorkspaceAvatar: React.FC<{ name?: string; className?: string }> = ({ name = 'Nova', className }) => (
  <div className={cn('w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-cyan-400 font-bold font-mono text-xs', className)}>
    <Layers className="w-4 h-4" />
  </div>
);

export const CyberDivider: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('w-full h-px bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent my-4', className)} />
);

export const GradientDivider: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('w-full h-px bg-gradient-to-r from-transparent via-slate-800 to-transparent my-4', className)} />
);

export const TabBar: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <div className={cn('flex items-center space-x-1 border-b border-slate-800 pb-1', className)}>{children}</div>
);

export const Tab: React.FC<{ label: string; active?: boolean; onClick?: () => void; icon?: React.ElementType; className?: string }> = ({
  label,
  active = false,
  onClick,
  icon: Icon,
  className,
}) => (
  <button
    onClick={onClick}
    className={cn(
      'flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer',
      active
        ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-[0_0_10px_rgba(0,240,255,0.1)]'
        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60',
      className
    )}
  >
    {Icon && <Icon className="w-3.5 h-3.5" />}
    <span>{label}</span>
  </button>
);

export const Breadcrumb: React.FC<{ items: string[]; className?: string }> = ({ items, className }) => (
  <div className={cn('flex items-center space-x-2 text-xs font-mono text-slate-400', className)}>
    {items.map((item, idx) => (
      <React.Fragment key={idx}>
        {idx > 0 && <ChevronRight className="w-3 h-3 text-slate-600" />}
        <span className={cn(idx === items.length - 1 ? 'text-cyan-300 font-bold' : 'hover:text-slate-200 cursor-pointer')}>{item}</span>
      </React.Fragment>
    ))}
  </div>
);

export const Menu: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <div className={cn('glass-panel p-1.5 rounded-xl border border-slate-800 space-y-0.5 shadow-xl w-48', className)}>
    {children}
  </div>
);

export const ContextMenu = Menu;
