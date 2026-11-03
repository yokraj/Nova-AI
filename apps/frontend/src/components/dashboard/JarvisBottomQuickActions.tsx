import React from 'react';
import { motion } from 'framer-motion';
import { AppWindow, Play, Clock, PlusCircle, Sparkles } from 'lucide-react';
import { cn } from '@/utils/cn';

interface JarvisBottomQuickActionsProps {
  onActionClick?: (actionType: 'open_app' | 'run_task' | 'automate' | 'create', defaultPrompt: string) => void;
  className?: string;
}

export const JarvisBottomQuickActions: React.FC<JarvisBottomQuickActionsProps> = ({
  onActionClick,
  className,
}) => {
  const actions = [
    {
      type: 'open_app' as const,
      label: 'Open App',
      icon: AppWindow,
      prompt: 'Open Notepad on Windows workstation',
      badge: 'APP_LAUNCH',
      accent: 'border-cyan-500/30 hover:border-cyan-400 hover:text-cyan-300 shadow-[0_0_15px_rgba(0,240,255,0.15)]',
      iconColor: 'text-cyan-400',
    },
    {
      type: 'run_task' as const,
      label: 'Run Task',
      icon: Play,
      prompt: 'Execute codebase audit and verification suite',
      badge: 'DISPATCH',
      accent: 'border-sky-500/30 hover:border-sky-400 hover:text-sky-300 shadow-[0_0_15px_rgba(56,189,248,0.15)]',
      iconColor: 'text-sky-400',
    },
    {
      type: 'automate' as const,
      label: 'Automate',
      icon: Clock,
      prompt: 'Schedule autonomous file monitoring automation',
      badge: 'WORKFLOW',
      accent: 'border-amber-500/30 hover:border-amber-400 hover:text-amber-300 shadow-[0_0_15px_rgba(255,170,0,0.15)]',
      iconColor: 'text-amber-400',
    },
    {
      type: 'create' as const,
      label: 'Create',
      icon: PlusCircle,
      prompt: 'Create a new markdown document named project_notes.md',
      badge: 'NEW_FILE',
      accent: 'border-purple-500/30 hover:border-purple-400 hover:text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.15)]',
      iconColor: 'text-purple-400',
    },
  ];

  return (
    <div className={cn('flex items-center justify-center flex-wrap gap-2.5 sm:gap-4 select-none', className)}>
      {actions.map((act) => {
        const Icon = act.icon;
        return (
          <motion.button
            key={act.type}
            whileHover={{ y: -2, scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onActionClick?.(act.type, act.prompt)}
            className={cn(
              'px-3.5 sm:px-4 py-2 rounded-xl bg-slate-950/80 backdrop-blur-xl border text-xs font-mono tracking-wider text-slate-300 transition-all duration-200 cursor-pointer flex items-center space-x-2 group focus:outline-none',
              act.accent
            )}
            title={`Quick Action: ${act.label} ("${act.prompt}")`}
            aria-label={act.label}
          >
            <div className="p-1 rounded-md bg-slate-900 border border-slate-800 group-hover:border-slate-700">
              <Icon className={cn('w-3.5 h-3.5', act.iconColor)} />
            </div>
            <span className="font-semibold">{act.label}</span>
            <span className="text-[9px] text-slate-500 font-normal hidden sm:inline">
              [{act.badge}]
            </span>
          </motion.button>
        );
      })}
    </div>
  );
};

export default JarvisBottomQuickActions;

