import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/utils/cn';

export interface ButtonProps extends HTMLMotionProps<'button'> {
  children?: React.ReactNode;
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  isLoading?: boolean;
  disabled?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'px-2.5 py-1.5 text-xs rounded-lg space-x-1.5',
  md: 'px-4 py-2 text-xs font-semibold rounded-xl space-x-2',
  lg: 'px-5 py-2.5 text-sm font-bold rounded-xl space-x-2.5',
};

export const PrimaryButton: React.FC<ButtonProps> = ({
  children,
  icon: Icon,
  iconPosition = 'left',
  size = 'md',
  className,
  disabled,
  ...props
}) => (
  <motion.button
    whileHover={{ scale: disabled ? 1 : 1.02 }}
    whileTap={{ scale: disabled ? 1 : 0.98 }}
    disabled={disabled}
    className={cn(
      'inline-flex items-center justify-center bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-bold shadow-[0_0_15px_rgba(0,240,255,0.3)] hover:shadow-[0_0_25px_rgba(0,240,255,0.5)] transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed',
      sizeClasses[size],
      className
    )}
    {...props}
  >
    {Icon && iconPosition === 'left' && <Icon className="w-4 h-4" />}
    {children && <span>{children}</span>}
    {Icon && iconPosition === 'right' && <Icon className="w-4 h-4" />}
  </motion.button>
);

export const SecondaryButton: React.FC<ButtonProps> = ({
  children,
  icon: Icon,
  iconPosition = 'left',
  size = 'md',
  className,
  disabled,
  ...props
}) => (
  <motion.button
    whileHover={{ scale: disabled ? 1 : 1.02 }}
    whileTap={{ scale: disabled ? 1 : 0.98 }}
    disabled={disabled}
    className={cn(
      'inline-flex items-center justify-center bg-slate-900/90 text-slate-200 border border-slate-800 hover:border-cyan-500/40 hover:text-cyan-300 shadow-sm transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed',
      sizeClasses[size],
      className
    )}
    {...props}
  >
    {Icon && iconPosition === 'left' && <Icon className="w-4 h-4" />}
    {children && <span>{children}</span>}
    {Icon && iconPosition === 'right' && <Icon className="w-4 h-4" />}
  </motion.button>
);

export const GhostButton: React.FC<ButtonProps> = ({
  children,
  icon: Icon,
  iconPosition = 'left',
  size = 'md',
  className,
  disabled,
  ...props
}) => (
  <motion.button
    whileHover={{ scale: disabled ? 1 : 1.02 }}
    whileTap={{ scale: disabled ? 1 : 0.98 }}
    disabled={disabled}
    className={cn(
      'inline-flex items-center justify-center text-slate-400 hover:text-slate-100 hover:bg-slate-900/60 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed',
      sizeClasses[size],
      className
    )}
    {...props}
  >
    {Icon && iconPosition === 'left' && <Icon className="w-4 h-4" />}
    {children && <span>{children}</span>}
    {Icon && iconPosition === 'right' && <Icon className="w-4 h-4" />}
  </motion.button>
);

export const DangerButton: React.FC<ButtonProps> = ({
  children,
  icon: Icon,
  iconPosition = 'left',
  size = 'md',
  className,
  disabled,
  ...props
}) => (
  <motion.button
    whileHover={{ scale: disabled ? 1 : 1.02 }}
    whileTap={{ scale: disabled ? 1 : 0.98 }}
    disabled={disabled}
    className={cn(
      'inline-flex items-center justify-center bg-rose-500/15 text-rose-400 border border-rose-500/30 hover:bg-rose-500/25 shadow-[0_0_15px_rgba(244,63,94,0.2)] transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed',
      sizeClasses[size],
      className
    )}
    {...props}
  >
    {Icon && iconPosition === 'left' && <Icon className="w-4 h-4" />}
    {children && <span>{children}</span>}
    {Icon && iconPosition === 'right' && <Icon className="w-4 h-4" />}
  </motion.button>
);

export const IconButton: React.FC<Omit<ButtonProps, 'children'> & { icon: LucideIcon }> = ({
  icon: Icon,
  size = 'md',
  className,
  disabled,
  ...props
}) => (
  <motion.button
    whileHover={{ scale: disabled ? 1 : 1.05 }}
    whileTap={{ scale: disabled ? 1 : 0.95 }}
    disabled={disabled}
    className={cn(
      'p-2 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-400 hover:text-cyan-300 hover:border-slate-700 transition-all cursor-pointer flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed',
      className
    )}
    {...props}
  >
    <Icon className="w-4 h-4" />
  </motion.button>
);
